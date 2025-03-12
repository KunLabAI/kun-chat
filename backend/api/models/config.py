from fastapi import APIRouter, HTTPException
from typing import Dict
import logging
from database import db
from .schemas import ModelConfigUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{model_id}/configs")
async def get_model_configs(model_id: int) -> Dict[str, Dict[str, str]]:
    """获取模型配置"""
    try:
        configs = await db.get_model_configs(model_id)
        
        # 将配置按类型分组
        result = {
            'basic': {},
            'runtime': {},
            'generation': {},
            'system': {}
        }
        
        for config in configs:
            config_type = config['config_type']
            config_key = config['config_key']
            config_value = config['config_value']
            result[config_type][config_key] = config_value
            
        return result
    except Exception as e:
        logger.error(f"获取模型配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型配置失败: {str(e)}")

@router.put("/{model_id}/configs")
async def update_model_config(
    model_id: int,
    request: ModelConfigUpdate
) -> Dict[str, str]:
    """更新模型配置"""
    try:
        # 检查模型是否存在
        model = await db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
            
        # 检查配置类型是否有效
        if request.config_type not in ['basic', 'runtime', 'generation', 'system']:
            raise HTTPException(status_code=400, detail="无效的配置类型")
            
        # 更新配置
        await db.update_model_config(
            model_id,
            request.config_type,
            request.config_key,
            request.config_value
        )
        
        return {"message": "配置更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模型配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新模型配置失败: {str(e)}")
