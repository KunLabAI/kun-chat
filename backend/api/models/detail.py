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

def transform_model_details(model_details):
    """
    将Ollama API返回的模型详情转换为符合前端期望格式的结构
    """
    # 提取基本信息
    details = model_details.get("details", {})
    model_info = model_details.get("model_info", {})
    
    base_info = {
        "family": details.get("family"),
        "parameter_size": details.get("parameter_size"),
        "quantization": details.get("quantization_level") or details.get("quantization"),
        "format": details.get("format"),
        "modified_at": model_details.get("modified_at"),
        "digest": model_details.get("digest")
    }
    
    # 只在 size 字段存在且不为 None 时才更新
    if model_details.get("size") is not None:
        base_info["size"] = int(model_details["size"])
    
    # 确保quantization字段有值
    if base_info["quantization"] is None:
        # 尝试从模型名称提取可能的量化信息
        model_name = model_details.get("model", "")
        if ":" in model_name:
            possible_quant = model_name.split(":")[-1].upper()
            if any(q in possible_quant for q in ["Q2", "Q3", "Q4", "Q5", "Q6", "Q8"]):
                base_info["quantization"] = possible_quant
        # 或者从model_info中提取量化信息
        elif model_info.get("general.quantization_version"):
            base_info["quantization"] = f"Q{model_info.get('general.quantization_version')}"
    
    # 初始化高级参数结构
    advanced_params = {
        "license": model_details.get("license"),
        "modelfile": model_details.get("modelfile"),
        "parameters": model_details.get("parameters"),
        "template": model_details.get("template"),
        "model_info": model_info,
    }
    
    # 默认初始化结构
    architecture = {
        "context_length": None,
        "embedding_length": None,
        "feed_forward": None,
        "head_count": None,
        "kv_head_count": None,
        "layer_count": None,
        "vocabulary_size": None,
        "parameter_count": None,
        "size_label": None,
        "version": None,
        "organization": None,
        "repository_url": None,
        "base_model": None,
        "tags": None,
        "languages": None
    }
    
    attention = {
        "rope_dimension": None,
        "rope_freq_base": None,
        "sliding_window": None,
        "key_length": None,
        "value_length": None,
        "layer_norm_epsilon": None
    }
    
    tokenizer = {
        "type": model_info.get("tokenizer.ggml.model"),
        "model": model_info.get("tokenizer.ggml.model"),
        "tokens": None
    }
    
    # 根据数据源填充结构
    if model_info:
        # 动态检测模型前缀
        model_architecture = model_info.get("general.architecture")
        model_prefix = None
        
        # 从所有键中寻找模型前缀
        if model_architecture:
            # 检查是否有以model_architecture为前缀的键
            for key in model_info.keys():
                if key.startswith(f"{model_architecture}."):
                    model_prefix = f"{model_architecture}."
                    break
        
        # 如果找到了模型前缀，从对应字段提取信息
        if model_prefix:
            # 从模型特定的model_info中提取架构信息
            architecture.update({
                "context_length": model_info.get(f"{model_prefix}context_length"),
                "embedding_length": model_info.get(f"{model_prefix}embedding_length"),
                "feed_forward": model_info.get(f"{model_prefix}feed_forward_length"),
                "head_count": model_info.get(f"{model_prefix}attention.head_count"),
                "kv_head_count": model_info.get(f"{model_prefix}attention.head_count_kv"),
                "layer_count": model_info.get(f"{model_prefix}block_count")
            })
            
            # 提取rope相关参数（如果存在）
            attention.update({
                "rope_dimension": model_info.get(f"{model_prefix}rope.dimension_count"),
                "rope_freq_base": model_info.get(f"{model_prefix}rope.freq_base")
            })
            
            # 添加模型特有参数
            special_attention_fields = [
                ("sliding_window", f"{model_prefix}attention.sliding_window"),
                ("key_length", f"{model_prefix}attention.key_length"),
                ("value_length", f"{model_prefix}attention.value_length"),
                ("layer_norm_epsilon", f"{model_prefix}attention.layer_norm_rms_epsilon")
            ]
            
            for field_name, field_key in special_attention_fields:
                if field_key in model_info:
                    attention[field_name] = model_info.get(field_key)
        
        # 设置tokenizer和vocabulary信息
        tokenizer_tokens = model_info.get("tokenizer.ggml.tokens")
        if tokenizer_tokens:
            tokenizer["tokens"] = tokenizer_tokens
            architecture["vocabulary_size"] = tokenizer_tokens
        elif "general.vocab_size" in model_info:
            vocab_size = model_info.get("general.vocab_size")
            tokenizer["tokens"] = vocab_size
            architecture["vocabulary_size"] = vocab_size
            
        # 添加模型通用信息
        general_fields = [
            ("parameter_count", "general.parameter_count"),
            ("size_label", "general.size_label"),
            ("version", "general.version"),
            ("organization", "general.organization"),
            ("repository_url", "general.license.link"),
            ("base_model", "general.basename"),
            ("tags", "general.tags"),
            ("languages", "general.languages")
        ]
        
        for field_name, field_key in general_fields:
            if field_key in model_info:
                architecture[field_name] = model_info.get(field_key)
    
    elif "details" in model_details:
        # 如果没有model_info但有details，使用details中的数据
        architecture = {
            "context_length": details.get("context_length"),
            "embedding_length": details.get("embedding_length"),
            "feed_forward": details.get("feed_forward"),
            "head_count": details.get("head_count"),
            "kv_head_count": details.get("kv_head_count"),
            "layer_count": details.get("layer_count"),
            "vocabulary_size": details.get("vocabulary_size")
        }
        
        attention = {
            "rope_dimension": details.get("rope_dimension"),
            "rope_freq_base": details.get("rope_freq_base")
        }
        
        tokenizer = {
            "type": details.get("tokenizer_type"),
            "model": details.get("tokenizer_model"),
            "tokens": details.get("vocabulary_size")
        }
    
    # 添加到advanced_params
    advanced_params["architecture"] = architecture
    advanced_params["attention"] = attention
    advanced_params["tokenizer"] = tokenizer
    
    # 记录转换后的结果以便调试
    logger.debug(f"转换后的基本信息: {base_info}")
    logger.debug(f"转换后的高级参数: {advanced_params}")
    
    return base_info, advanced_params

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
                    logger.warning(f"无法从Ollama获取模型 {model['name']} 的信息")
                else:
                    # 使用转换函数处理模型详情
                    base_info, advanced_params = transform_model_details(model_details)
                    
                    # 只更新非空字段
                    update_info = {k: v for k, v in base_info.items() if v is not None}
                    
                    if update_info:
                        # 确保不更新name字段
                        update_info.pop('name', None)
                        
                        # 更新模型信息
                        model.update(update_info)
                        
                    if advanced_params:
                        update_info["advanced_parameters"] = advanced_params
                        model["advanced_parameters"] = advanced_params
                    
                    # 如果有需要更新的内容，则更新数据库
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
        try:
            async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
                delete_request = ModelDeleteRequest(name=model['name'])
                await client.delete_model(delete_request)
        except Exception as e:
            logger.error(f"从Ollama删除模型 {model['name']} 失败: {str(e)}")
            # 继续从数据库中删除，即使从Ollama中删除失败

        # 从数据库中删除模型
        await db.delete_model(model_id)
        return {"message": f"模型 {model['name']} 已删除"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除模型失败: {str(e)}")
