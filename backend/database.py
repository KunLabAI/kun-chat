import aiosqlite
from pathlib import Path
import json
from typing import Optional, Any, Dict, List
import logging
import uuid
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保data目录存在
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据库文件路径
DB_PATH = DATA_DIR / "kun-lab.db"

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def ensure_connected(self) -> None:
        """确保数据库连接是活跃的"""
        try:
            if self._connection is None:
                await self.connect()
                return
                
            # 测试连接是否有效
            try:
                await self._connection.execute("SELECT 1")
            except Exception as e:
                logger.warning(f"Database connection test failed: {e}")
                # 尝试关闭现有连接（如果可能）
                try:
                    await self._connection.close()
                except Exception:
                    pass  # 忽略关闭错误
                
                # 重置连接并重新连接
                self._connection = None
                await self.connect()
        except Exception as e:
            logger.error(f"Failed to ensure database connection: {e}")
            # 最后的尝试：完全重置连接
            self._connection = None
            await self.connect()

    async def connect(self) -> None:
        """连接到数据库"""
        try:
            if not self._connection:
                logger.info(f"Connecting to database at {self.db_path}")
                self._connection = await aiosqlite.connect(self.db_path)
                await self._connection.execute("PRAGMA foreign_keys = ON")
                
                # 创建users表（如果不存在）
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        nickname TEXT,
                        email TEXT UNIQUE,
                        hashed_password TEXT NOT NULL,
                        security_question TEXT,
                        security_answer TEXT,
                        preferences TEXT DEFAULT '{}',
                        last_login TEXT,
                        avatar TEXT,
                        language TEXT DEFAULT 'zh-CN'
                    )
                """)
                
                # 检查email字段是否存在，如果不存在则添加
                try:
                    await self._connection.execute("""
                        ALTER TABLE users ADD COLUMN email TEXT UNIQUE
                    """)
                    await self._connection.commit()
                    logger.info("Added email column to users table")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        raise
                    logger.info("Email column already exists")
                
                # 检查avatar字段是否存在，如果不存在则添加
                try:
                    await self._connection.execute("""
                        ALTER TABLE users ADD COLUMN avatar TEXT
                    """)
                    await self._connection.commit()
                    logger.info("Added avatar column to users table")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        raise
                    logger.info("Avatar column already exists")
                
                # 检查language字段是否存在，如果不存在则添加
                try:
                    await self._connection.execute("""
                        ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'zh-CN'
                    """)
                    await self._connection.commit()
                    logger.info("Added language column to users table")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        raise
                    logger.info("Language column already exists")
                
                # 创建prompts表（如果不存在）
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS prompts (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT DEFAULT '[]',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
                    )
                """)
                
                # 创建conversations表
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        model TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
                    )
                """)
                
                # 创建messages表
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        images TEXT,                          -- JSON数组格式存储图片路径
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                    )
                """)
                
                # 创建models表
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS models (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        display_name TEXT,
                        family TEXT,
                        parameter_size TEXT,
                        quantization TEXT,
                        format TEXT,
                        size INTEGER,
                        digest TEXT,
                        is_custom INTEGER DEFAULT 0,
                        options TEXT,
                        status TEXT DEFAULT 'ready',
                        modified_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 创建model_favorites表
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS model_favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        model_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                        FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
                        UNIQUE(username, model_id)
                    )
                """)
                
                # 创建message_images表
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS message_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
                    )
                """)
                
                # 创建settings表
                await self._connection.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
                        UNIQUE(key, user_id)
                    )
                """)
                
                await self._connection.commit()
                logger.info("Database connection established and schema updated")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """断开数据库连接"""
        if not self._connection:
            logger.info("No active database connection to disconnect")
            return
            
        try:
            logger.info("Disconnecting from database")
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error disconnecting from database: {str(e)}")
            # 即使出错，也将连接对象设置为 None
            self._connection = None

    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """执行SQL查询"""
        await self.ensure_connected()
        try:
            logger.info(f"Executing query: {query} with params: {params}")
            return await self._connection.execute(query, params)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    async def executemany(self, query: str, params_list: list) -> aiosqlite.Cursor:
        """执行多个SQL查询"""
        await self.ensure_connected()
        try:
            logger.info(f"Executing multiple queries: {query} with params: {params_list}")
            return await self._connection.executemany(query, params_list)
        except Exception as e:
            logger.error(f"Error executing multiple queries: {str(e)}")
            raise

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        await self.ensure_connected()
        try:
            cursor = await self.execute(query, params)
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                result = dict(zip(columns, row))
                # 解析 tags 字段，确保返回的是列表
                if 'tags' in result:
                    try:
                        tags = json.loads(result['tags'])
                        # 如果是旧格式（字符串列表），转换为新格式（带颜色的对象）
                        if tags and isinstance(tags[0], str):
                            tags = [{"text": tag, "color": "#f50"} for tag in tags]
                        result['tags'] = tags
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding tags JSON: {result['tags']}")
                        result['tags'] = []
                return result
            return None
        except Exception as e:
            logger.error(f"Error fetching one record: {str(e)}")
            raise

    async def fetch_all(self, query: str, params: tuple = ()) -> list[Dict[str, Any]]:
        """获取所有记录"""
        await self.ensure_connected()
        try:
            cursor = await self.execute(query, params)
            rows = await cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                results = []
                for row in rows:
                    result = dict(zip(columns, row))
                    # 解析 tags 字段，确保返回的是列表
                    if 'tags' in result:
                        try:
                            tags = json.loads(result['tags'])
                            # 如果是旧格式（字符串列表），转换为新格式（带颜色的对象）
                            if tags and isinstance(tags[0], str):
                                tags = [{"text": tag, "color": "#f50"} for tag in tags]
                            result['tags'] = tags
                        except json.JSONDecodeError:
                            logger.error(f"Error decoding tags JSON: {result['tags']}")
                            result['tags'] = []
                    results.append(result)
                return results
            return []
        except Exception as e:
            logger.error(f"Error fetching all records: {str(e)}")
            raise

    async def commit(self) -> None:
        """提交事务"""
        await self.ensure_connected()
        try:
            if self._connection:
                logger.info("Committing transaction")
                await self._connection.commit()
                logger.info("Transaction committed")
        except Exception as e:
            logger.error(f"Error committing transaction: {str(e)}")
            raise

    async def rollback(self) -> None:
        """回滚事务"""
        await self.ensure_connected()
        try:
            if self._connection:
                logger.info("Rolling back transaction")
                await self._connection.rollback()
                logger.info("Transaction rolled back")
        except Exception as e:
            logger.error(f"Error rolling back transaction: {str(e)}")
            raise

    def generate_prompt_id(self) -> str:
        """生成提示词ID"""
        return f"prompt_{str(uuid.uuid4())}"

    async def create_prompt(self, user_id: str, title: str, content: str, tags: list = None) -> Dict[str, Any]:
        """创建新的提示词
        
        Args:
            user_id: 用户ID
            title: 提示词标题
            content: 提示词内容
            tags: 标签列表，每个标签应该是一个包含 text 和 color 的字典
        """
        await self.ensure_connected()
        try:
            if tags is None:
                tags = []
            prompt_id = self.generate_prompt_id()
            current_time = datetime.utcnow().isoformat()
            
            await self.execute(
                """
                INSERT INTO prompts (id, user_id, title, content, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (prompt_id, user_id, title, content, json.dumps(tags), current_time, current_time)
            )
            await self.commit()
            
            # 在提交后查询最新插入的记录
            result = await self.fetch_one(
                "SELECT * FROM prompts WHERE id = ?",
                (prompt_id,)
            )
            return result
        except Exception as e:
            await self.rollback()
            logger.error(f"Error creating prompt: {str(e)}")
            raise

    async def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """获取单个提示词"""
        await self.ensure_connected()
        try:
            return await self.fetch_one(
                "SELECT * FROM prompts WHERE id = ?",
                (prompt_id,)
            )
        except Exception as e:
            logger.error(f"Error getting prompt: {str(e)}")
            raise

    async def get_user_prompts(self, user_id: str) -> list[Dict[str, Any]]:
        """获取用户的所有提示词"""
        await self.ensure_connected()
        try:
            return await self.fetch_all(
                "SELECT * FROM prompts WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
        except Exception as e:
            logger.error(f"Error getting user prompts: {str(e)}")
            raise

    async def update_prompt(self, prompt_id: str, user_id: str, title: str, content: str, tags: list = None) -> Optional[Dict[str, Any]]:
        """更新提示词
        
        Args:
            prompt_id: 提示词ID
            user_id: 用户ID
            title: 提示词标题
            content: 提示词内容
            tags: 标签列表，每个标签应该是一个包含 text 和 color 的字典
        """
        await self.ensure_connected()
        try:
            if tags is None:
                tags = []
            current_time = datetime.utcnow().isoformat()
            
            await self.execute(
                """
                UPDATE prompts
                SET title = ?, content = ?, tags = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (title, content, json.dumps(tags), current_time, prompt_id, user_id)
            )
            await self.commit()
            
            return await self.get_prompt(prompt_id)
        except Exception as e:
            await self.rollback()
            logger.error(f"Error updating prompt: {str(e)}")
            raise

    async def delete_prompt(self, prompt_id: str, user_id: str) -> bool:
        """删除提示词"""
        await self.ensure_connected()
        try:
            cursor = await self.execute(
                "DELETE FROM prompts WHERE id = ? AND user_id = ?",
                (prompt_id, user_id)
            )
            await self.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting prompt: {str(e)}")
            raise

    # Models相关方法
    async def get_all_models(self, include_custom: bool = True) -> List[Dict[str, Any]]:
        """获取所有模型列表"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            query = "SELECT * FROM models"
            if not include_custom:
                query += " WHERE is_custom = 0"
            query += " ORDER BY created_at DESC"

            async with self._connection.execute(query) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            raise

    async def get_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """通过名称获取模型"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            async with self._connection.execute(
                "SELECT * FROM models WHERE name = ?",
                (name,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None

        except Exception as e:
            logger.error(f"获取模型失败: {str(e)}")
            raise

    async def create_model(self, model_data: Dict[str, Any]) -> int:
        """创建新模型"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            # 准备SQL语句和参数
            columns = ', '.join(model_data.keys())
            placeholders = ', '.join(['?' for _ in model_data])
            values = tuple(model_data.values())

            query = f"INSERT INTO models ({columns}) VALUES ({placeholders})"
            
            async with self._connection.execute(query, values) as cursor:
                await self._connection.commit()
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"创建模型失败: {str(e)}")
            raise

    async def get_model(self, model_id: int) -> Optional[Dict[str, Any]]:
        """获取模型信息"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()
                
            async with self._connection.execute(
                """
                SELECT id, name, display_name, family, parameter_size, quantization, format,
                       size, digest, is_custom, options, status, modified_at, created_at
                FROM models
                WHERE id = ?
                """,
                (model_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    model = {
                        "id": row[0],
                        "name": row[1],
                        "display_name": row[2],
                        "family": row[3],
                        "parameter_size": row[4],
                        "quantization": row[5],
                        "format": row[6],
                        "size": row[7],
                        "digest": row[8],
                        "is_custom": bool(row[9]),
                        "options": json.loads(row[10]) if row[10] else None,
                        "status": row[11],
                        "modified_at": row[12],
                        "created_at": row[13]
                    }
                    return model
                return None
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            raise

    async def update_model(self, model_id: int, model_info: Dict[str, Any]) -> None:
        """更新模型信息"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()
                
            # 准备更新字段
            update_fields = []
            params = []
            
            field_mapping = {
                "name": "name",
                "display_name": "display_name",
                "family": "family",
                "parameter_size": "parameter_size",
                "quantization": "quantization",
                "format": "format",
                "size": "size",
                "digest": "digest",
                "is_custom": "is_custom",
                "options": "options",
                "status": "status",
                "modified_at": "modified_at"
            }
            
            for key, field in field_mapping.items():
                if key in model_info:
                    value = model_info[key]
                    if key in ["options"] and value is not None:
                        value = json.dumps(value)
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if update_fields:
                query = f"""
                    UPDATE models
                    SET {", ".join(update_fields)}
                    WHERE id = ?
                """
                params.append(model_id)
                await self._connection.execute(query, params)
                await self._connection.commit()
        except Exception as e:
            logger.error(f"更新模型信息失败: {str(e)}")
            raise

    async def is_model_favorited(self, username: str, model_id: int) -> bool:
        """检查模型是否被用户收藏"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()
                
            async with self._connection.execute(
                "SELECT 1 FROM model_favorites WHERE username = ? AND model_id = ?",
                (username, model_id)
            ) as cursor:
                result = await cursor.fetchone()
                return bool(result)
        except Exception as e:
            logger.error(f"检查模型收藏状态失败: {str(e)}")
            raise

    async def delete_model(self, model_id: int) -> bool:
        """删除模型"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            async with self._connection.execute(
                "DELETE FROM models WHERE id = ?",
                (model_id,)
            ) as cursor:
                await self._connection.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"删除模型失败: {str(e)}")
            raise

    # User Favorites相关方法
    async def add_favorite(self, username: str, model_id: int) -> None:
        """添加收藏"""
        await self.ensure_connected()
        try:
            await self._connection.execute(
                "INSERT INTO model_favorites (username, model_id) VALUES (?, ?)",
                (username, model_id)
            )
            await self._connection.commit()
        except Exception as e:
            logger.error(f"添加收藏失败: {e}")
            raise

    async def remove_favorite(self, username: str, model_id: int) -> None:
        """移除收藏"""
        await self.ensure_connected()
        try:
            await self._connection.execute(
                "DELETE FROM model_favorites WHERE username = ? AND model_id = ?",
                (username, model_id)
            )
            await self._connection.commit()
        except Exception as e:
            logger.error(f"移除收藏失败: {e}")
            raise

    async def is_model_favorited(self, username: str, model_id: int) -> bool:
        """检查模型是否被收藏"""
        await self.ensure_connected()
        try:
            async with self._connection.execute(
                "SELECT 1 FROM model_favorites WHERE username = ? AND model_id = ?",
                (username, model_id)
            ) as cursor:
                result = await cursor.fetchone()
                return bool(result)
        except Exception as e:
            logger.error(f"检查收藏状态失败: {e}")
            raise

    async def get_favorite_models(self, username: str) -> List[Dict[str, Any]]:
        """获取用户收藏的所有模型"""
        await self.ensure_connected()
        try:
            async with self._connection.execute(
                """
                SELECT m.* FROM models m
                JOIN model_favorites f ON m.id = f.model_id
                WHERE f.username = ?
                ORDER BY f.created_at DESC
                """,
                (username,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"获取收藏模型列表失败: {e}")
            raise

    async def toggle_favorite(self, username: str, model_id: int) -> bool:
        """切换模型收藏状态"""
        await self.ensure_connected()
        try:
            # 检查当前收藏状态
            is_favorited = await self.is_model_favorited(username, model_id)
            
            if is_favorited:
                # 如果已收藏，则取消收藏
                await self._connection.execute(
                    "DELETE FROM model_favorites WHERE username = ? AND model_id = ?",
                    (username, model_id)
                )
                await self._connection.commit()
                return False
            else:
                # 如果未收藏，则添加收藏
                await self._connection.execute(
                    """
                    INSERT INTO model_favorites (username, model_id, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (username, model_id)
                )
                await self._connection.commit()
                return True
        except Exception as e:
            logger.error(f"切换收藏状态失败: {e}")
            raise

    # Model Configs相关方法
    async def set_model_config(self, model_id: int, config_type: str, 
                             config_key: str, config_value: str) -> bool:
        """设置模型配置"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            async with self._connection.execute("""
                INSERT INTO model_configs (model_id, config_type, config_key, config_value)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(model_id, config_type, config_key) 
                DO UPDATE SET config_value = excluded.config_value
            """, (model_id, config_type, config_key, config_value)) as cursor:
                await self._connection.commit()
                return True

        except Exception as e:
            logger.error(f"设置模型配置失败: {str(e)}")
            raise

    async def get_model_configs(self, model_id: int, config_type: Optional[str] = None) -> list:
        """获取模型配置"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            if config_type:
                async with self._connection.execute(
                    "SELECT * FROM model_configs WHERE model_id = ? AND config_type = ?",
                    (model_id, config_type)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
            else:
                async with self._connection.execute(
                    "SELECT * FROM model_configs WHERE model_id = ?",
                    (model_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]

        except Exception as e:
            logger.error(f"获取模型配置失败: {str(e)}")
            raise

    async def delete_model_configs(self, model_id: int, config_type: Optional[str] = None) -> bool:
        """删除模型配置"""
        await self.ensure_connected()
        try:
            if not self._connection:
                await self.connect()

            if config_type:
                async with self._connection.execute(
                    "DELETE FROM model_configs WHERE model_id = ? AND config_type = ?",
                    (model_id, config_type)
                ) as cursor:
                    await self._connection.commit()
                    return True
            else:
                async with self._connection.execute(
                    "DELETE FROM model_configs WHERE model_id = ?",
                    (model_id,)
                ) as cursor:
                    await self._connection.commit()
                    return True

        except Exception as e:
            logger.error(f"删除模型配置失败: {str(e)}")
            raise

# 创建全局数据库实例
db = Database()

async def get_db():
    """获取数据库连接的异步上下文管理器"""
    try:
        await db.ensure_connected()
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    # 移除这里的 finally 块，不在每次请求结束后关闭连接
    # 数据库连接将由应用程序生命周期管理
