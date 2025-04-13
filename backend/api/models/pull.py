from fastapi import APIRouter, HTTPException, Path as FastAPIPath, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
import json
import logging
from datetime import datetime
import asyncio
from typing import Dict, Any

from config import API_CONFIG
from database import db
from ollama import OllamaClient, ModelPullRequest, ModelPullResponse
from .utils import safe_show_model

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 用于限制并发下载数量的信号量
download_semaphore = asyncio.Semaphore(1)

# 用于跟踪下载状态
download_status: Dict[str, Dict[str, Any]] = {}

# 设置是否显示详细日志
SHOW_DETAILED_LOGS = False

def parse_model_name(name: str) -> str:
    """
    解析和标准化模型名称
    支持以下格式：
    1. ollama默认格式：qwen2.5:0.5b-instruct-q3_K_M
    2. 带命名空间的格式：huihui_ai/deepseek-r1-abliterated
    3. HuggingFace格式：hf.co/username/repository 或 huggingface.co/username/repository
    4. 带量化值的格式：hf.co/username/repository:BF16
    5. 魔搭社区格式：modelscope.cn/username/model 或 ollama run modelscope.cn/username/model
    """
    # 移除可能包含的命令部分
    if "ollama run" in name:
        name = name.replace("ollama run", "").strip()
    
    # 处理HuggingFace格式
    if "hf.co/" in name or "huggingface.co/" in name:
        # 替换域名为标准格式
        name = name.replace("huggingface.co/", "hf.co/")
        
        # 处理量化值
        # 检查是否有量化值（以:分隔）
        parts = name.split(":")
        if len(parts) == 2:
            base_name = parts[0]
            quantization = parts[1].upper()  # 统一转为大写
            # 重新组合名称和量化值
            name = f"{base_name}:{quantization}"
        
        return name
    
    # 处理魔搭社区格式
    if "modelscope.cn/" in name:
        # 保留完整格式，确保包含域名前缀
        return name
    
    return name

async def _pull_model(name: str, force: bool = False) -> EventSourceResponse:
    """
    拉取模型并返回下载进度流
    """
    try:
        # 解析和标准化模型名称
        name = parse_model_name(name)
        
        async def event_generator():
            max_retries = 3  # 最大重试次数
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    async with download_semaphore:
                        async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
                            # 检查模型是否已存在
                            model_exists = await safe_show_model(client, name)
                            if model_exists and not force:
                                logger.info(f"模型 {name} 已存在，跳过拉取")
                                yield {
                                    "data": json.dumps({
                                        "name": name,
                                        "status": "exists",
                                        "message": "模型已存在",
                                        "progress": 100
                                    })
                                }
                                return
                            
                            # 初始化下载状态
                            initial_status = {
                                "name": name,
                                "status": "downloading",
                                "progress": 0,
                                "total_size": 0,
                                "downloaded_size": 0,
                                "details": []
                            }
                            download_status[name] = initial_status
                            logger.info(f"开始拉取模型: {name}")
                            yield {"data": json.dumps(initial_status)}
                            
                            try:
                                request = ModelPullRequest(name=name)
                                success_sent = False
                                last_status = None
                                last_total = None
                                last_completed = None
                                last_update_time = datetime.utcnow()
                                model_saved = False  # 添加标志位，确保只保存一次
                                
                                # 添加心跳任务，确保即使没有进度更新也能保持连接
                                last_heartbeat_time = datetime.utcnow()
                                
                                async for response in client.pull_model(request):
                                    try:
                                        # 检查是否已被取消
                                        if name in download_status and download_status[name]['status'] == 'cancelled':
                                            logger.info(f"下载任务已被取消: {name}")
                                            yield {
                                                "data": json.dumps({
                                                    "name": name,
                                                    "status": "cancelled",
                                                    "message": "下载已取消"
                                                })
                                            }
                                            return
                                            
                                        # 如果已经完成，忽略后续的状态更新
                                        if success_sent or model_saved:
                                            continue

                                        # 检查是否需要发送心跳
                                        current_time = datetime.utcnow()
                                        time_since_last_heartbeat = (current_time - last_heartbeat_time).total_seconds()
                                        
                                        # 如果超过10秒没有发送任何消息，发送一个心跳消息
                                        if time_since_last_heartbeat > 10:
                                            # 发送当前状态作为心跳
                                            current_status = download_status.get(name, initial_status)
                                            yield {"data": json.dumps(current_status)}
                                            last_heartbeat_time = current_time
                                            logger.debug(f"发送心跳消息: {name}")

                                        if isinstance(response, dict):
                                            response_dict = response
                                        else:
                                            response_dict = response.model_dump()
                                        
                                        # 使用debug级别记录详细的响应日志，而不是info级别
                                        if SHOW_DETAILED_LOGS:
                                            logger.info(f"Raw response: {response_dict}")
                                        else:
                                            logger.debug(f"Raw response: {response_dict}")
                                        
                                        # 检查错误响应
                                        if "error" in response_dict:
                                            error_msg = response_dict["error"]
                                            logger.error(f"下载失败: {error_msg}")
                                            yield {
                                                "data": json.dumps({
                                                    "name": name,
                                                    "status": "failed",
                                                    "error": error_msg
                                                })
                                            }
                                            return
                                        
                                        # 处理正常响应
                                        current_status = response_dict.get("status", "")
                                        if not current_status and "digest" in response_dict:
                                            current_status = "pulling manifest"
                                        
                                        current_total = response_dict.get("total", 0)
                                        current_completed = response_dict.get("completed", 0)
                                        
                                        # 计算进度
                                        progress = 0
                                        if current_total and current_total > 0:
                                            progress = min(99, int((current_completed or 0) * 100 / current_total))
                                        
                                        # 更新下载状态
                                        status_update = {
                                            "name": name,
                                            "status": "downloading",
                                            "progress": progress,
                                            "total_size": current_total,
                                            "downloaded_size": current_completed,
                                            "details": {
                                                "status": current_status,
                                                "digest": response_dict.get("digest"),
                                                "total": current_total,
                                                "completed": current_completed
                                            }
                                        }
                                        
                                        # 仅在进度发生显著变化时记录日志
                                        if (progress % 25 == 0 and progress > 0 and 
                                            (last_status is None or progress > last_status)):
                                            logger.info(f"模型 {name} 拉取进度: {progress}%")
                                            last_status = progress
                                        
                                        download_status[name] = status_update
                                        yield {"data": json.dumps(status_update)}
                                        
                                        # 如果下载完成
                                        if current_status == "success":
                                            success_sent = True
                                            status_update = {
                                                "name": name,
                                                "status": "completed",
                                                "progress": 100,
                                                "message": "下载完成"
                                            }
                                            download_status[name] = status_update
                                            # 记录完成状态的日志
                                            logger.info(f"模型 {name} 拉取完成")
                                            yield {"data": json.dumps(status_update)}
                                            return

                                    except Exception as e:
                                        logger.error(f"处理响应时出错: {str(e)}")
                                        raise
                                
                                # 下载完成
                                final_status = {
                                    "name": name,
                                    "status": "completed",
                                    "progress": 100,
                                    "message": "下载完成"
                                }
                                logger.info(f"模型 {name} 拉取完成")
                                yield {"data": json.dumps(final_status)}
                                return
                                
                            except Exception as e:
                                logger.error(f"下载过程中出错: {str(e)}")
                                if retry_count < max_retries - 1:
                                    retry_count += 1
                                    logger.info(f"尝试重新下载，第 {retry_count} 次重试")
                                    continue
                                else:
                                    error_status = {
                                        "name": name,
                                        "status": "failed",
                                        "error": str(e)
                                    }
                                    logger.error(f"模型 {name} 拉取失败: {str(e)}")
                                    yield {"data": json.dumps(error_status)}
                                    return
                                    
                except Exception as e:
                    logger.error(f"生成事件流时出错: {str(e)}")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        logger.info(f"尝试重新下载，第 {retry_count} 次重试")
                        continue
                    else:
                        error_status = {
                            "name": name,
                            "status": "failed",
                            "error": str(e)
                        }
                        yield {"data": json.dumps(error_status)}
                        return
                        
        # 设置 SSE 连接的 ping 间隔为 15 秒，防止连接超时
        return EventSourceResponse(
            event_generator(),
            ping=15,  # 每15秒发送一次 ping
            ping_message_factory=lambda: ServerSentEvent(data="keep-alive"),  # 发送可识别的keep-alive消息
            send_timeout=None  # 禁用发送超时
        )
        
    except Exception as e:
        logger.error(f"拉取模型时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/pull/{name:path}", operation_id="pull_model_get")
@router.post("/pull/{name:path}", operation_id="pull_model_post")
async def pull_model(
    name: str = FastAPIPath(..., description="模型名称"),
    force: bool = False
) -> EventSourceResponse:
    """拉取模型并返回下载进度流"""
    return await _pull_model(name, force)

@router.post("/pull/{name}/cancel")
async def cancel_pull(name: str = FastAPIPath(..., description="模型名称")):
    """取消模型下载"""
    try:
        if name not in download_status:
            raise HTTPException(
                status_code=404,
                detail=f"未找到模型 {name} 的下载任务"
            )

        # 标记下载状态为取消
        download_status[name]['status'] = "cancelled"
        
        # 向 Ollama 发送取消请求
        try:
            async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
                # 使用 DELETE 请求取消下载
                async for _ in client._request("DELETE", f"api/pull/{name}", stream=False):
                    pass  # 我们不需要处理响应
        except Exception as e:
            logger.error(f"向 Ollama 发送取消请求失败: {str(e)}")
            # 即使 Ollama 取消失败，我们也继续清理本地状态
        
        # 等待一小段时间确保其他连接已经关闭
        await asyncio.sleep(0.5)
        
        # 清理下载状态
        del download_status[name]
        
        # 释放信号量
        if not download_semaphore.locked():
            try:
                download_semaphore.release()
            except ValueError:
                pass  # 信号量已经被释放了

        return {"status": "success", "message": f"已取消模型 {name} 的下载"}

    except Exception as e:
        logger.error(f"取消下载失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取消下载失败: {str(e)}"
        )
