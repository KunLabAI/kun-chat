from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
from database import Database, get_db
from api.auth import get_current_user

# 设置路由器
router = APIRouter()

# 主题设置模型
class ThemeSettings(BaseModel):
    theme_is_dark: Optional[bool] = None
    theme_source: Optional[str] = None

# 获取主题设置
@router.get("/settings")
async def get_theme_settings(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    获取用户主题设置
    """
    try:
        # 获取主题是否为深色模式
        theme_is_dark_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'theme_is_dark' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        # 获取主题来源设置
        theme_source_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'theme_source' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        # 构建返回结果
        settings = {}
        
        if theme_is_dark_setting:
            # 将字符串转换为布尔值
            theme_is_dark_value = theme_is_dark_setting["value"].lower()
            settings["theme_is_dark"] = theme_is_dark_value == "true"
        
        if theme_source_setting:
            settings["theme_source"] = theme_source_setting["value"]
        
        return settings
    except Exception as e:
        logging.error(f"获取主题设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取主题设置失败: {str(e)}"
        )

# 更新主题设置
@router.post("/settings")
async def update_theme_settings(
    settings: ThemeSettings,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新用户主题设置
    """
    try:
        # 更新主题是否为深色模式
        if settings.theme_is_dark is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """,
                ("theme_is_dark", str(settings.theme_is_dark).lower(), current_user["username"])
            )
        
        # 更新主题来源
        if settings.theme_source is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """,
                ("theme_source", settings.theme_source, current_user["username"])
            )
        
        await db.commit()
        return {"message": "主题设置更新成功"}
    except Exception as e:
        logging.error(f"更新主题设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新主题设置失败: {str(e)}"
        )
