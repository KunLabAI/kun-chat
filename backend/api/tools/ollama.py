"""
Ollama 连接管理 API
"""
import logging
import aiohttp
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.auth import get_current_user
from database import Database, get_db
from config import API_CONFIG

router = APIRouter()
logger = logging.getLogger(__name__)

# 定义请求模型
class OllamaSettings(BaseModel):
    host: Optional[str] = None
    checkInterval: Optional[int] = None
    enableAutoCheck: Optional[bool] = None
    showNotification: Optional[bool] = None

class CheckSettings(BaseModel):
    interval: Optional[int] = None
    enabled: Optional[bool] = None
    notification: Optional[bool] = None

# 获取 Ollama 连接设置
@router.get("/settings")
async def get_ollama_settings(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    获取 Ollama 连接设置
    """
    try:
        # 从数据库获取设置
        settings = {}
        
        # 获取主机设置
        host_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'ollama_host' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        # 使用环境变量中的 OLLAMA_BASE_URL 作为默认值
        default_host = API_CONFIG["OLLAMA_BASE_URL"].replace("http://", "").replace("https://", "")
        settings["host"] = host_setting["value"] if host_setting else default_host
        
        logger.info(f"获取 Ollama 设置，默认主机: {default_host}, 用户设置: {settings['host']}")
        
        # 获取检查间隔设置
        interval_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'ollama_check_interval' AND user_id = ?
            """,
            (current_user["username"],)
        )
        settings["checkInterval"] = int(interval_setting["value"]) if interval_setting else 60
        
        # 获取自动检查设置
        auto_check_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'ollama_auto_check' AND user_id = ?
            """,
            (current_user["username"],)
        )
        settings["enableAutoCheck"] = auto_check_setting["value"].lower() == "true" if auto_check_setting else True
        
        # 获取通知设置
        notification_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'ollama_notification' AND user_id = ?
            """,
            (current_user["username"],)
        )
        settings["showNotification"] = notification_setting["value"].lower() == "true" if notification_setting else True
        
        return settings
    except Exception as e:
        logger.error(f"获取 Ollama 设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取 Ollama 设置失败: {str(e)}")

# 更新 Ollama 连接设置
@router.put("/settings")
async def update_ollama_settings(
    settings: OllamaSettings,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新 Ollama 连接设置
    """
    try:
        # 更新主机设置
        if settings.host is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_host", settings.host, current_user["username"])
            )
        
        # 更新检查间隔设置
        if settings.checkInterval is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_check_interval", str(settings.checkInterval), current_user["username"])
            )
        
        # 更新自动检查设置
        if settings.enableAutoCheck is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_auto_check", str(settings.enableAutoCheck).lower(), current_user["username"])
            )
        
        # 更新通知设置
        if settings.showNotification is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_notification", str(settings.showNotification).lower(), current_user["username"])
            )
        
        await db.commit()
        return {"message": "Ollama 设置更新成功"}
    except Exception as e:
        logger.error(f"更新 Ollama 设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新 Ollama 设置失败: {str(e)}")

# 更新检查设置
@router.put("/check-settings")
async def update_check_settings(
    settings: CheckSettings,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新 Ollama 检查设置
    """
    try:
        # 更新检查间隔设置
        if settings.interval is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_check_interval", str(settings.interval), current_user["username"])
            )
        
        # 更新自动检查设置
        if settings.enabled is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_auto_check", str(settings.enabled).lower(), current_user["username"])
            )
        
        # 更新通知设置
        if settings.notification is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                ("ollama_notification", str(settings.notification).lower(), current_user["username"])
            )
        
        await db.commit()
        return {"message": "检查设置更新成功"}
    except Exception as e:
        logger.error(f"更新检查设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新检查设置失败: {str(e)}")

# 检查 Ollama 连接状态
@router.get("/check")
async def check_ollama_connection(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    检查 Ollama 连接状态
    """
    try:
        # 获取主机设置
        host_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'ollama_host' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        # 使用环境变量中的 OLLAMA_BASE_URL 作为默认值
        default_host = API_CONFIG["OLLAMA_BASE_URL"].replace("http://", "").replace("https://", "")
        host = host_setting["value"] if host_setting else default_host
        
        # 确保主机设置包含协议
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"
        
        logger.info(f"检查 Ollama 连接，使用地址: {host}")
        
        # 发送请求检查连接
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{host}/api/version", timeout=5) as response:
                    if response.status == 200:
                        version_data = await response.json()
                        version = version_data.get("version", "未知")
                        logger.info(f"Ollama 版本检测成功: {version}, 完整响应: {version_data}")
                        return {
                            "connected": True,
                            "version": version
                        }
                    else:
                        logger.error(f"Ollama 版本检测失败，HTTP 状态码: {response.status}")
                        return {
                            "connected": False,
                            "error": f"HTTP 错误: {response.status}"
                        }
        except aiohttp.ClientError as e:
            logger.error(f"Ollama 连接错误: {str(e)}")
            return {
                "connected": False,
                "error": f"连接错误: {str(e)}"
            }
    except Exception as e:
        logger.error(f"检查 Ollama 连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查 Ollama 连接失败: {str(e)}")
