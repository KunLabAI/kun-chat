from fastapi import APIRouter, HTTPException
from typing import List, Optional, Set
import logging
from datetime import datetime
from ollama import OllamaClient
from config import API_CONFIG
from database import db
from .schemas import ModelResponse
from ollama.types import ModelList
import json

router = APIRouter()
logger = logging.getLogger(__name__)

async def sync_models_with_ollama() -> Set[str]:
    """同步 Ollama 模型列表到数据库，并返回当前有效的模型名称集合"""
    current_model_names = set()
    try:
        async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
            try:
                models_info = await client.list_models()
                
                # 收集当前 Ollama 中的所有模型名称
                for model in models_info.models:
                    current_model_names.add(model.name)
                    
                    model_data = {
                        'name': model.name,
                        'modified_at': datetime.fromisoformat(model.modified_at.split('.')[0]),
                        'size': model.size,
                        'digest': model.digest,
                        'is_custom': 0
                    }
                    
                    if model.details:
                        if model.details.family:
                            model_data['family'] = model.details.family
                        if model.details.parameter_size:
                            model_data['parameter_size'] = model.details.parameter_size
                        if model.details.quantization_level:
                            model_data['quantization'] = model.details.quantization_level
                        if model.details.format:
                            model_data['format'] = model.details.format
                    
                    if model.options:
                        model_data['options'] = model.options.json()
                    
                    # 确保数据库连接有效
                    await db.ensure_connected()
                    
                    try:
                        existing_model = await db.get_model_by_name(model.name)
                        if existing_model:
                            await db.update_model(existing_model['id'], model_data)
                        else:
                            await db.create_model(model_data)
                    except Exception as db_err:
                        logger.error(f"更新模型 {model.name} 到数据库时出错: {db_err}")
                        # 继续处理其他模型
            except Exception as api_err:
                logger.error(f"从 Ollama API 获取模型列表时出错: {api_err}")
                raise
    except Exception as e:
        logger.error(f"同步 Ollama 模型时出错: {e}")
        raise
    
    return current_model_names

@router.get("/list")
async def get_models(include_custom: bool = True, username: Optional[str] = None) -> List[ModelResponse]:
    """获取可用模型列表"""
    try:
        # 确保数据库已连接
        await db.ensure_connected()
        
        # 同步 Ollama 模型列表并获取当前有效的模型名称
        try:
            current_model_names = await sync_models_with_ollama()
            
            # 清理已经不存在的非自定义模型
            all_db_models = await db.get_all_models(include_custom=True)
            for model in all_db_models:
                if not model['is_custom'] and model['name'] not in current_model_names:
                    await db.delete_model(model['id'])
        except Exception as sync_err:
            logger.warning(f"同步 Ollama 模型失败，将使用数据库中的现有模型: {sync_err}")
            # 即使同步失败，我们仍然继续获取数据库中的模型
        
        # 获取最新的模型列表
        models = await db.get_all_models(include_custom)
        
        # 如果提供了用户名，获取收藏信息
        if username:
            result = []
            for model in models:
                if isinstance(model.get('options'), str):
                    try:
                        model['options'] = json.loads(model['options'])
                    except json.JSONDecodeError:
                        model['options'] = {}
                
                model_response = ModelResponse(**model)
                model_response.is_favorited = await db.is_model_favorited(username, model['id'])
                result.append(model_response)
            return result
        else:
            for model in models:
                if isinstance(model.get('options'), str):
                    try:
                        model['options'] = json.loads(model['options'])
                    except json.JSONDecodeError:
                        model['options'] = {}
            
            return [ModelResponse(**model) for model in models]
            
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")
