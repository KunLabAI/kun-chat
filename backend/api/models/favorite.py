from fastapi import APIRouter, HTTPException
from typing import List
import logging
from database import db
from .schemas import ModelResponse, ModelFavoriteResponse

# 不要在这里添加前缀，前缀会在__init__.py中统一添加
router = APIRouter()
logger = logging.getLogger(__name__)

# 将具体路由放在前面
@router.get("/favorites/{username}")
async def get_favorite_models(username: str) -> List[ModelResponse]:
    """获取用户收藏的模型列表"""
    try:
        models = await db.get_favorite_models(username)
        # 确保 options 字段是字典类型
        for model in models:
            if model.get('options') and isinstance(model['options'], str):
                try:
                    import json
                    model['options'] = json.loads(model['options'])
                except Exception as e:
                    logger.error(f"解析模型选项失败: {str(e)}")
                    model['options'] = {}
        return [ModelResponse(**model) for model in models]
    except Exception as e:
        logger.error(f"获取收藏模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取收藏模型列表失败: {str(e)}")

@router.get("/{model_id}/favorite/{username}")
async def check_favorite_status(
    model_id: int,
    username: str
) -> bool:
    """检查模型是否被用户收藏"""
    try:
        # 检查模型是否存在
        model = await db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
            
        # 检查收藏状态
        is_favorited = await db.is_model_favorited(username, model_id)
        return is_favorited
    except Exception as e:
        logger.error(f"检查收藏状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查收藏状态失败: {str(e)}")

@router.post("/{model_id}/favorite/{username}")
async def toggle_favorite(
    model_id: int,
    username: str
) -> ModelFavoriteResponse:
    """切换模型收藏状态"""
    try:
        # 检查模型是否存在
        model = await db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
            
        # 切换收藏状态
        is_favorited = await db.toggle_favorite(username, model_id)
        message = "收藏成功" if is_favorited else "取消收藏成功"
        return ModelFavoriteResponse(is_favorited=is_favorited, message=message)
    except Exception as e:
        logger.error(f"切换收藏状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"切换收藏状态失败: {str(e)}")
