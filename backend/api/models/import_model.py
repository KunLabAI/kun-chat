from fastapi import APIRouter, HTTPException
import logging
import json
import os
import tempfile
import hashlib
from datetime import datetime
from typing import Dict, Any
import asyncio
import subprocess
from config import API_CONFIG
from database import db
from .schemas import ImportModelRequest, ImportModelResponse

router = APIRouter()
logger = logging.getLogger(__name__)

def generate_modelfile(name: str, file_path: str) -> str:
    """生成简单的 Modelfile 内容"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.gguf':
        return f"FROM {os.path.abspath(file_path)}"
    elif ext == '.safetensors':
        return f"FROM llama2\nADAPTER {os.path.abspath(file_path)}"
    else:
        raise ValueError("不支持的文件格式")

async def run_command(cmd: str, cwd: str = None) -> tuple[int, str, str]:
    """异步运行命令并返回结果"""
    try:
        logger.info(f"执行命令: {cmd}")
        if cwd:
            logger.info(f"在目录: {cwd}")
            
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, stderr = await process.communicate()
        
        stdout_str = stdout.decode() if stdout else ""
        stderr_str = stderr.decode() if stderr else ""
        
        if stdout_str:
            logger.info(f"命令输出: {stdout_str}")
        if stderr_str:
            logger.error(f"命令错误: {stderr_str}")
            
        return (
            process.returncode,
            stdout_str,
            stderr_str
        )
    except Exception as e:
        logger.error(f"执行命令时出错: {str(e)}")
        raise

async def wait_for_model_creation(model_name: str, timeout: int = 300) -> bool:
    """等待模型创建完成"""
    start_time = datetime.now()
    while True:
        try:
            # 使用 ollama list 命令检查模型是否存在
            returncode, stdout, stderr = await run_command("ollama list")
            if returncode == 0 and model_name in stdout:
                logger.info(f"模型 {model_name} 创建成功")
                return True
        except Exception as e:
            logger.warning(f"检查模型状态时出错: {str(e)}")
        
        # 超时检查
        elapsed = (datetime.now() - start_time).total_seconds()
        if elapsed > timeout:
            logger.error(f"模型 {model_name} 创建超时，已等待 {elapsed} 秒")
            return False
            
        logger.info(f"等待模型创建中... 已等待 {elapsed} 秒")
        await asyncio.sleep(5)

@router.post("/import")
async def import_model(request: ImportModelRequest) -> ImportModelResponse:
    """导入模型"""
    try:
        logger.info(f"开始导入模型: {request.name}")
        
        # 获取绝对路径
        file_path = os.path.abspath(request.file_path)
        logger.info(f"模型文件绝对路径: {file_path}")
        
        # 验证文件路径
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=400,
                detail="文件不存在"
            )
            
        # 检查文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.gguf', '.safetensors']:
            raise HTTPException(
                status_code=400,
                detail="只支持 .gguf 和 .safetensors 格式的模型文件"
            )
            
        # 计算文件大小和摘要
        file_size = os.path.getsize(file_path)
        logger.info(f"模型文件大小: {file_size} 字节")
        with open(file_path, 'rb') as f:
            file_digest = hashlib.sha256(f.read()).hexdigest()
            
        # 生成简单的 Modelfile 内容
        modelfile_content = generate_modelfile(request.name, file_path)
        logger.info(f"生成的 Modelfile 内容:\n{modelfile_content}")
            
        # 保存 Modelfile 到临时文件
        temp_dir = tempfile.mkdtemp(prefix="import_model_")
        modelfile_path = os.path.join(temp_dir, "Modelfile")
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
            
        try:
            # 检查模型是否已存在
            returncode, stdout, stderr = await run_command("ollama list")
            if returncode == 0 and request.name in stdout:
                raise HTTPException(
                    status_code=400,
                    detail=f"模型 {request.name} 已存在"
                )
                
            # 使用 ollama create 命令创建模型
            logger.info(f"开始创建模型: {request.name}")
            try:
                returncode, stdout, stderr = await run_command(
                    f"ollama create {request.name}",
                    cwd=temp_dir
                )
                
                if returncode != 0:
                    error_msg = stderr or stdout or "未知错误"
                    logger.error(f"创建模型失败，返回码: {returncode}, 错误信息: {error_msg}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"创建模型失败: {error_msg}"
                    )
                    
                logger.info("模型创建请求已发送")
                
            except Exception as e:
                logger.error(f"执行 ollama create 命令时出错: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"创建模型失败: {str(e)}"
                )

            # 等待模型创建完成
            if not await wait_for_model_creation(request.name):
                raise HTTPException(
                    status_code=500,
                    detail=f"模型 {request.name} 创建超时，请检查 Ollama 服务日志"
                )
            
            # 创建模型记录
            model_data = {
                'name': request.name,
                'is_custom': True,
                'size': file_size,
                'digest': file_digest,
                'status': 'ready',
                'created_at': datetime.utcnow(),
                'options': None
            }
            
            await db.create_model(model_data)
            logger.info(f"模型 {request.name} 导入完成")
            
            return ImportModelResponse(
                status="success",
                progress=100,
                message=f"模型 {request.name} 导入成功"
            )
                
        finally:
            # 清理临时文件
            try:
                if os.path.exists(modelfile_path):
                    os.unlink(modelfile_path)
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导入模型失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"导入模型失败: {str(e)}"
        )
