import os
import json
import uuid
import tempfile
import subprocess
import logging
import aiohttp
from fastapi import APIRouter, HTTPException
from config import API_CONFIG
from api.models.schemas import CustomModelRequest, CustomModelResponse
from api.models.utils import validate_modelfile, ModelFileError, convert_model_name
from database import get_db
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

class ModelParameters(BaseModel):
    """模型参数"""
    temperature: Optional[float] = Field(None, description="控制输出的随机性")
    num_ctx: Optional[int] = Field(None, description="上下文窗口大小")
    top_k: Optional[int] = Field(None, description="从概率最高的K个token中采样")
    top_p: Optional[float] = Field(None, description="控制采样时的累积概率阈值")
    repeat_last_n: Optional[int] = Field(None, description="重复惩罚的上下文窗口大小")
    repeat_penalty: Optional[float] = Field(None, description="重复惩罚系数")
    mirostat: Optional[int] = Field(None, description="Mirostat采样控制")
    mirostat_eta: Optional[float] = Field(None, description="Mirostat学习率")
    mirostat_tau: Optional[float] = Field(None, description="Mirostat目标熵")

class CustomModelRequest(BaseModel):
    """创建自定义模型的请求"""
    name: str = Field(..., description="模型名称")
    modelfile: str = Field(..., description="Modelfile内容")
    parameters: Optional[ModelParameters] = Field(None, description="模型参数")
    force: Optional[bool] = Field(False, description="是否强制覆盖已有模型")

class CustomModelResponse(BaseModel):
    """创建自定义模型的响应"""
    status: str
    message: str
    data: Dict[str, Any]

def save_modelfile(name: str, content: str, display_name: str = None) -> str:
    """保存Modelfile到临时目录"""
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="modelfile_")
        
        # 确保内容以换行符结尾
        content = content.strip() + '\n'
        
        # 在 Modelfile 中添加自定义标签来保存显示名称
        if display_name:
            content = f"# DISPLAY_NAME: {display_name}\n{content}"
        
        # 创建Modelfile
        modelfile_path = os.path.join(temp_dir, "Modelfile")
        with open(modelfile_path, "w", encoding="utf-8", newline='\n') as f:
            f.write(content)
            
        # 读取文件内容并打印，用于调试
        with open(modelfile_path, "r", encoding="utf-8") as f:
            logger.info(f"Modelfile 内容:\n{f.read()}")
            
        return modelfile_path
        
    except Exception as e:
        raise ModelFileError(f"保存Modelfile失败: {str(e)}")

async def check_model_exists(session: aiohttp.ClientSession, base_url: str, model_name: str) -> bool:
    """检查模型是否存在"""
    try:
        async with session.get(f"{base_url}/api/show", params={"name": model_name}) as response:
            return response.status == 200
    except Exception as e:
        logger.error(f"检查模型时发生错误: {str(e)}")
        return False

async def create_model(session: aiohttp.ClientSession, base_url: str, name: str, path: str) -> bool:
    """创建模型"""
    try:
        logger.info(f"使用 ollama create 命令创建模型: {name}")
        
        # 使用 subprocess 运行 ollama create 命令
        process = subprocess.Popen(
            ["ollama", "create", name, "-f", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        logger.info(f"命令输出: {stdout}")
        if stderr:
            logger.info(f"命令错误输出: {stderr}")  # 改为 info，因为这可能包含进度信息
            
        if process.returncode != 0:
            raise Exception(f"创建模型失败: {stderr}")
            
        # 检查模型是否存在
        check_process = subprocess.Popen(
            ["ollama", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = check_process.communicate()
        if name in stdout:
            logger.info(f"模型 {name} 已成功创建")
            return True
        else:
            raise Exception(f"模型创建可能失败，在模型列表中未找到 {name}")
        
    except Exception as e:
        logger.error(f"创建模型时发生错误: {str(e)}")
        raise

async def wait_for_model_creation(session: aiohttp.ClientSession, base_url: str, model_name: str, max_retries: int = 30, retry_delay: float = 10.0) -> bool:
    """等待模型创建完成"""
    import asyncio
    
    logger.info(f"等待模型 {model_name} 创建完成...")
    for i in range(max_retries):
        logger.info(f"第 {i+1}/{max_retries} 次检查模型状态")
        if await check_model_exists(session, base_url, model_name):
            logger.info(f"模型 {model_name} 创建成功")
            return True
        logger.info(f"模型尚未就绪，等待 {retry_delay} 秒后重试...")
        await asyncio.sleep(retry_delay)
    
    logger.error(f"模型 {model_name} 创建超时")
    return False

async def get_model_info(session: aiohttp.ClientSession, base_url: str, name: str) -> dict:
    """从 Ollama API 获取模型信息"""
    try:
        # 确保模型名称有 :latest 后缀
        if not name.endswith(':latest'):
            name = f"{name}:latest"
            
        # 使用 list API 获取所有模型信息
        async with session.get(f"{base_url}/api/tags") as response:
            if response.status != 200:
                raise Exception(f"获取模型信息失败: HTTP {response.status}")
            data = await response.json()
            models = data.get('models', [])
            
            # 在列表中查找指定的模型
            for model in models:
                if model.get('name') == name:
                    return model
                    
            raise Exception(f"模型 {name} 未找到")
            
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise

@router.post("/custom")
async def custom_model(request: CustomModelRequest) -> CustomModelResponse:
    """创建自定义模型"""
    try:
        # 保存原始显示名称
        display_name = request.name
        logger.info(f"开始创建模型，显示名称: {display_name}")
        
        # 转换为 Ollama 兼容的名称
        safe_name = convert_model_name(display_name)
        logger.info(f"转换后的安全名称: {safe_name}")
        
        # 验证Modelfile内容
        logger.info("开始验证 Modelfile 内容...")
        is_valid, error = await validate_modelfile(request.modelfile)
        if not is_valid:
            logger.error(f"Modelfile 验证失败: {error}")
            raise HTTPException(
                status_code=400,
                detail=f"Modelfile验证失败: {error}"
            )
        logger.info("Modelfile 验证通过")
            
        # 保存Modelfile到临时文件，包含显示名称
        logger.info("保存 Modelfile 到临时文件...")
        modelfile_path = save_modelfile(safe_name, request.modelfile, display_name)
        logger.info(f"Modelfile 已保存到: {modelfile_path}")
        
        try:
            base_url = API_CONFIG["OLLAMA_BASE_URL"].rstrip('/')
            async with aiohttp.ClientSession() as session:
                # 检查模型是否已存在
                logger.info(f"检查模型 {safe_name} 是否已存在...")
                check_process = subprocess.Popen(
                    ["ollama", "list"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = check_process.communicate()
                if safe_name in stdout and not request.force:
                    logger.warning(f"模型 {display_name} ({safe_name}) 已存在")
                    raise HTTPException(
                        status_code=409,  # 使用 409 Conflict 更合适
                        detail=f"模型 {display_name} 已存在"
                    )
                
                # 如果模型存在且 force=True，先删除旧模型
                if safe_name in stdout and request.force:
                    logger.info(f"强制覆盖模型 {safe_name}，正在删除旧模型...")
                    delete_process = subprocess.Popen(
                        ["ollama", "rm", safe_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    delete_process.communicate()
                
                # 创建模型
                logger.info(f"开始创建模型 {safe_name}...")
                if await create_model(session, base_url, safe_name, modelfile_path):
                    # 获取完整的模型信息
                    logger.info(f"获取模型 {safe_name} 的完整信息...")
                    model_info = await get_model_info(session, base_url, safe_name)
                    
                    # 将模型信息保存到数据库
                    from datetime import datetime
                    model_data = {
                        "name": f"{safe_name}:latest",  # 添加 :latest 后缀
                        "display_name": display_name,
                        "family": model_info.get("family"),
                        "parameter_size": model_info.get("parameter_size"),
                        "quantization": model_info.get("quantization"),
                        "format": model_info.get("format"),
                        "size": model_info.get("size"),
                        "digest": model_info.get("digest"),
                        "is_custom": 1,
                        "status": "ready",
                        "created_at": datetime.utcnow().isoformat(),
                        "modified_at": datetime.utcnow().isoformat()
                    }
                    
                    # 如果有参数设置，添加到数据库
                    if request.parameters:
                        model_data["options"] = json.dumps(
                            request.parameters.model_dump(
                                exclude_none=True,  # 只保存非空参数
                                by_alias=True  # 使用字段别名
                            )
                        )
                    
                    # 使用异步上下文管理器来处理数据库连接
                    async for db in get_db():
                        model_id = await db.create_model(model_data)
                        logger.info(f"模型信息已保存到数据库，ID: {model_id}")
                        break  # 我们只需要执行一次
                    
                    logger.info(f"模型 {display_name} ({safe_name}) 创建成功")
                    return CustomModelResponse(
                        status="success",
                        message=f"模型 {display_name} 创建成功",
                        data={
                            "name": f"{safe_name}:latest",  # 添加 :latest 后缀
                            "display_name": display_name
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"模型 {display_name} 创建失败"
                    )
                
        finally:
            # 清理临时文件
            try:
                if os.path.exists(modelfile_path):
                    logger.info(f"清理临时文件: {modelfile_path}")
                    os.unlink(modelfile_path)
                    os.rmdir(os.path.dirname(modelfile_path))
                    logger.info("临时文件清理完成")
            except Exception as e:
                logger.error(f"清理临时文件失败: {str(e)}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建模型时发生未知错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建模型失败: {str(e)}"
        )
