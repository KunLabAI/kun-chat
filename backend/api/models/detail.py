from fastapi import APIRouter, HTTPException
from typing import Optional, Dict
import logging
from database import db
from .schemas import ModelResponse, ModelDisplayNameUpdate
from ollama import OllamaClient
from config import API_CONFIG
from ollama.types import ModelDeleteRequest
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{model_id}")
async def get_model_info(model_id: int, username: Optional[str] = None) -> ModelResponse:
    """获取模型详细信息"""
    try:
        # 从数据库获取模型基本信息
        model = await db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        try:
            # 从Ollama API获取完整模型信息
            async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
                model_details = await client.show_model(model['name'])
                if not model_details:
                    raise Exception("无法从Ollama获取模型信息")
                
                # 保留原有的name，因为这是唯一标识符
                original_name = model['name']
                
                # 从model_details中提取基本信息
                base_info = {
                    "family": model_details.get("details", {}).get("family"),
                    "parameter_size": model_details.get("details", {}).get("parameter_size"),
                    "quantization": model_details.get("details", {}).get("quantization_level"),
                    "format": model_details.get("details", {}).get("format"),
                    "modified_at": model_details.get("modified_at"),
                    "digest": model_details.get("digest")
                }
                
                # 只在 size 字段存在且不为 None 时才更新
                if model_details.get("size") is not None:
                    base_info["size"] = int(model_details["size"])
                
                # 从model_details中提取高级参数
                advanced_params = {
                    "license": model_details.get("license"),
                    "modelfile": model_details.get("modelfile"),
                    "parameters": model_details.get("parameters"),
                    "template": model_details.get("template"),
                    "details": model_details.get("details"),
                    "model_info": model_details.get("model_info"),
                    "modified_at": model_details.get("modified_at")
                }
                
                # 更新模型信息，但保留原有的name
                model.update(base_info)
                model["advanced_parameters"] = advanced_params
                
                # 更新数据库，只更新非空字段
                update_info = {}
                for key, value in base_info.items():
                    if value is not None:
                        update_info[key] = value
                if advanced_params:
                    update_info["advanced_parameters"] = advanced_params
                
                # 确保不更新name字段
                if "name" in update_info:
                    del update_info["name"]
                    
                if update_info:
                    await db.update_model(model_id, update_info)
                
        except Exception as e:
            logger.warning(f"获取模型 {model['name']} 的详细信息失败: {str(e)}")
            # 如果获取失败，继续使用数据库中的信息
        
        # 创建响应对象
        model_response = ModelResponse(**model)
        
        # 如果提供了用户名，获取收藏信息
        if username:
            model_response.is_favorited = await db.is_model_favorited(username, model_id)
        
        return model_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")

@router.put("/{model_id}/display_name")
async def update_display_name(
    model_id: int,
    request: ModelDisplayNameUpdate
) -> ModelResponse:
    """更新模型显示名称"""
    try:
        await db.update_model_display_name(model_id, request.display_name)
        return await get_model_info(model_id)
    except Exception as e:
        logger.error(f"更新模型显示名称失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新模型显示名称失败: {str(e)}")

@router.delete("/{model_id}")
async def delete_model(model_id: int) -> Dict[str, str]:
    """删除模型"""
    try:
        # 获取模型信息
        model = await db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")

        # 从Ollama中删除模型
        async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
            delete_request = ModelDeleteRequest(name=model['name'])
            await client.delete_model(delete_request)

        # 从数据库中删除模型
        await db.delete_model(model_id)

        return {"message": f"模型 {model['name']} 已删除"}

    except Exception as e:
        logger.error(f"删除模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除模型失败: {str(e)}")
