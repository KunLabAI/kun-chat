"""
语言设置工具 - 为kun-lab提供多语言支持
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.auth import get_current_user
from database import Database, get_db

router = APIRouter()

# 定义请求模型
class LanguageSettings(BaseModel):
    language: str = "zh-CN"  # 默认为中文

# 获取语言设置
@router.get("/settings")
async def get_language_settings(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    获取用户语言设置
    """
    try:
        # 记录当前用户
        logging.info(f"获取用户 {current_user['username']} 的语言设置")
        
        # 从users表中获取语言设置
        user_data = await db.fetch_one(
            """
            SELECT language FROM users
            WHERE username = ?
            """,
            (current_user["username"],)
        )
        
        logging.info(f"从数据库获取到的用户语言设置: {user_data}")
        
        # 如果找到设置，返回它，否则返回默认值
        if user_data and user_data.get("language"):
            logging.info(f"返回用户语言设置: {user_data['language']}")
            return {"language": user_data["language"]}
        else:
            # 尝试从settings表获取（兼容旧数据）
            logging.info("用户表中没有语言设置，尝试从settings表获取")
            language_setting = await db.fetch_one(
                """
                SELECT value FROM settings
                WHERE key = 'language' AND user_id = ?
                """,
                (current_user["username"],)
            )
            
            if language_setting:
                # 找到旧设置，迁移到users表
                logging.info(f"从settings表找到语言设置: {language_setting['value']}，迁移到users表")
                await db.execute(
                    """
                    UPDATE users
                    SET language = ?
                    WHERE username = ?
                    """,
                    (language_setting["value"], current_user["username"])
                )
                await db.commit()
                return {"language": language_setting["value"]}
            else:
                logging.info("未找到任何语言设置，返回默认中文")
                # 将默认语言保存到用户表中
                await db.execute(
                    """
                    UPDATE users
                    SET language = ?
                    WHERE username = ?
                    """,
                    ("zh-CN", current_user["username"])
                )
                await db.commit()
                return {"language": "zh-CN"}  # 默认为中文
    except Exception as e:
        logging.error(f"获取语言设置失败: {str(e)}")
        # 返回默认设置而不是抛出异常
        return {"language": "zh-CN"}

# 更新语言设置
@router.post("/settings")
async def update_language_settings(
    settings: LanguageSettings,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新用户语言设置
    """
    try:
        # 记录当前用户和请求的语言设置
        logging.info(f"用户 {current_user['username']} 请求更新语言设置为: {settings.language}")
        
        # 验证语言设置
        if settings.language not in ["zh-CN", "en-US"]:
            logging.warning(f"不支持的语言设置: {settings.language}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的语言设置"
            )
            
        # 更新users表中的语言设置
        logging.info(f"更新users表中的语言设置为: {settings.language}")
        result = await db.execute(
            """
            UPDATE users
            SET language = ?
            WHERE username = ?
            """,
            (settings.language, current_user["username"])
        )
        await db.commit()
        
        # 检查更新是否成功
        if result:
            logging.info(f"users表语言设置更新成功: {settings.language}")
        else:
            logging.warning("users表语言设置更新可能未成功")
        
        # 同时更新settings表中的设置（兼容旧代码）
        logging.info(f"更新settings表中的语言设置为: {settings.language}")
        await db.execute(
            """
            INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            ("language", settings.language, current_user["username"])
        )
        await db.commit()
        
        # 再次从数据库获取语言设置，确认更新成功
        user_data = await db.fetch_one(
            """
            SELECT language FROM users
            WHERE username = ?
            """,
            (current_user["username"],)
        )
        logging.info(f"更新后从数据库获取到的用户语言设置: {user_data}")
        
        return {"status": "success", "message": "语言设置已更新", "language": settings.language}
    except HTTPException as e:
        # 重新抛出HTTP异常
        logging.error(f"HTTP异常: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"更新语言设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新语言设置失败: {str(e)}"
        )

# 获取支持的语言列表
@router.get("/supported")
async def get_supported_languages():
    """
    获取支持的语言列表
    """
    try:
        return {
            "languages": [
                {"code": "zh-CN", "name": "中文"},
                {"code": "en-US", "name": "English"}
            ]
        }
    except Exception as e:
        logging.error(f"获取支持的语言列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取支持的语言列表失败: {str(e)}"
        )
