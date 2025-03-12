import sqlite3
import os
from pathlib import Path
import bcrypt
import logging

# 确保data目录存在
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据库文件路径
DB_PATH = DATA_DIR / "kun-lab.db"

# 日志配置
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('migration.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def migrate_models_table(cursor):
    """迁移models表数据"""
    try:
        # 删除旧表
        cursor.execute("DROP TABLE IF EXISTS models")
        cursor.execute("DROP TABLE IF EXISTS user_favorites")
        cursor.execute("DROP TABLE IF EXISTS model_configs")
        
        # 创建新的models表
        cursor.execute('''
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
        ''')
        
        # 创建新的model_favorites表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            model_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
            FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
            UNIQUE(user_id, model_id)
        )
        ''')
        
        logger.info("Models tables recreated with new structure")
    except Exception as e:
        logger.error(f"Error migrating models table: {str(e)}")
        raise

def migrate_messages_table(cursor):
    """迁移messages表数据，添加image_path字段"""
    try:
        # 删除临时表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS messages_new")
        
        # 创建临时表
        cursor.execute('''
        CREATE TABLE messages_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            images TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
        ''')
        
        # 从旧表迁移数据到新表
        cursor.execute("""
        INSERT INTO messages_new (id, conversation_id, role, content, images, created_at)
        SELECT id, conversation_id, role, content, '[]', CURRENT_TIMESTAMP
        FROM messages
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE messages")
        
        # 重命名新表
        cursor.execute("ALTER TABLE messages_new RENAME TO messages")
        
        logger.info("Messages table migrated successfully")
    except Exception as e:
        logger.error(f"Error migrating messages table: {str(e)}")
        raise

def migrate_model_favorites_table(cursor):
    """修改 model_favorites 表，将 user_id 改为 username"""
    try:
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(model_favorites)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 如果表不存在或结构已经是新的，则直接创建新表
        if 'user_id' not in column_names:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                model_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
                UNIQUE(username, model_id)
            )
            ''')
            logger.info("Created new model_favorites table with username field")
            return
        
        # 如果是旧表结构，则进行迁移
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_favorites_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            model_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
            FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
            UNIQUE(username, model_id)
        )
        ''')
        
        # 从旧表迁移数据到新表
        cursor.execute("""
        INSERT INTO model_favorites_new (username, model_id, created_at)
        SELECT user_id, model_id, created_at
        FROM model_favorites
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE model_favorites")
        
        # 重命名新表
        cursor.execute("ALTER TABLE model_favorites_new RENAME TO model_favorites")
        
        logger.info("Model favorites table migrated successfully")
    except Exception as e:
        logger.error(f"Error migrating model_favorites table: {str(e)}")
        raise

def migrate_conversations_table(cursor):
    """迁移 conversations 表结构"""
    try:
        # 删除临时表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS conversations_new")
        
        # 创建临时表
        cursor.execute('''
        CREATE TABLE conversations_new (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model TEXT,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
        )
        ''')
        
        # 从旧表迁移数据到新表
        cursor.execute("""
        INSERT INTO conversations_new (id, title, model, user_id, created_at, updated_at)
        SELECT id, title, model, user_id, created_at, updated_at
        FROM conversations
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE conversations")
        
        # 重命名新表
        cursor.execute("ALTER TABLE conversations_new RENAME TO conversations")
        
        logger.info("Conversations table migrated successfully")
    except Exception as e:
        logger.error(f"Error migrating conversations table: {str(e)}")
        raise

def init_db():
    """初始化数据库"""
    try:
        # 确保数据库文件所在目录存在
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            nickname TEXT,
            email TEXT UNIQUE,
            hashed_password TEXT NOT NULL,
            security_question TEXT NOT NULL,
            security_answer TEXT NOT NULL,
            preferences TEXT DEFAULT '{}',
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建对话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model TEXT,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
        )
        ''')

        # 创建消息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            images TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
        ''')

        # 迁移表结构
        migrate_models_table(cursor)
        migrate_messages_table(cursor)
        migrate_model_favorites_table(cursor)
        migrate_conversations_table(cursor)
        
        # 提交更改
        conn.commit()
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database migration: {str(e)}")
        raise
    finally:
        # 关闭连接
        conn.close()

if __name__ == "__main__":
    init_db()
    print(f"数据库初始化完成：{DB_PATH}")
