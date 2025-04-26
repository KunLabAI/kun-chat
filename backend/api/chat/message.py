from fastapi import APIRouter, WebSocket, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

from database import Database, get_db
from api.auth import get_current_user
from config import API_CONFIG

from .schemas import ChatCompletionRequest
from .client_pool import get_available_client
from .message_processor import process_chat_messages, get_limited_history
from .db_operations import save_message, verify_conversation_ownership
from .websocket_handler import handle_websocket_connection, active_connections

router = APIRouter()

# 默认模型名称
DEFAULT_MODEL_NAME = API_CONFIG.get("DEFAULT_MODEL", "llama2")

logger = logging.getLogger(__name__)

@router.post("/conversations/{conversation_id}/abort")
async def abort_generation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """中止指定对话的生成过程"""
    try:
        # 确保数据库连接有效
        await db.ensure_connected()
        
        # 检查对话是否存在且属于当前用户
        conversation = await db.fetch_one(
            """
            SELECT id FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (conversation_id, current_user["username"])
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在或您无权访问")
            
        # 检查用户是否有权限操作该对话
        if conversation_id not in active_connections:
            return {"status": "success", "message": "没有找到活跃的生成过程"}
            
        # 关闭 WebSocket 连接
        ws = active_connections[conversation_id]
        if ws and not ws.client_state.disconnected:
            await ws.close(code=1000, reason="用户请求停止生成")
            active_connections.pop(conversation_id, None)
            logging.info(f"已停止对话 {conversation_id} 的生成过程")
            
        return {"status": "success", "message": "已停止生成"}
    except Exception as e:
        error_msg = f"停止生成时出错: {str(e)}"
        logging.error(error_msg)
        logging.exception(e)
        raise HTTPException(status_code=500, detail=error_msg)

@router.websocket("/conversations/{conversation_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str,
    db: Database = Depends(get_db)
):
    """处理WebSocket连接，支持流式响应和思考状态"""
    await handle_websocket_connection(websocket, conversation_id, token, db)

@router.post("/conversations/{conversation_id}/chat")
async def chat(
    conversation_id: str,
    request: ChatCompletionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    try:
        # 验证对话所有权
        conversation = await db.fetch_one(
            """
            SELECT model FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (conversation_id, current_user["username"])
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        # 获取模型名称
        model = request.model or conversation["model"] or API_CONFIG["DEFAULT_MODEL"]
        logging.info(f"使用模型 {model} 处理对话 {conversation_id}")
        
        # 获取用户偏好设置
        user_prefs = await db.fetch_one(
            "SELECT preferences FROM users WHERE username = ?",
            (current_user["username"],)
        )
        user_preferences = json.loads(user_prefs["preferences"] or "{}")
        
        # 获取历史消息
        history_messages = await db.fetch_all(
            """
            SELECT role, content, images, document
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,)
        )
        
        # 构建完整的消息列表，包含历史消息
        all_messages = []
        
        # 分离系统消息和其他消息
        system_messages = []
        other_messages = []
        
        # 添加历史消息
        for msg in history_messages:
            message_dict = {
                "role": msg["role"],
                "content": msg["content"]
            }
            if msg["images"]:
                message_dict["image"] = msg["images"]
            if msg["document"]:
                message_dict["document"] = msg["document"]
            
            if msg["role"] == "system":
                system_messages.append(message_dict)
            else:
                other_messages.append(message_dict)
        
        # 如果用户偏好中启用了个人信息，添加系统消息
        if user_preferences.get("use_personal_info", True) and user_preferences.get("personal_info"):
            personal_info = user_preferences.get("personal_info", "").strip()
            
            # 获取用户昵称
            nickname = user_preferences.get("nickname")
            
            if personal_info:
                # 如果有昵称且个人信息中没有包含昵称信息，则添加昵称
                if nickname and nickname.strip() and not any(keyword in personal_info.lower() for keyword in [f"我叫{nickname}", f"我的名字是{nickname}", f"我是{nickname}"]):
                    personal_info = f"我的名字是{nickname}。{personal_info}"
                
                system_message = {
                    "role": "system",
                    "content": f"用户的个人信息：{personal_info}"
                }
                system_messages.append(system_message)
                logging.info("已添加用户个人偏好信息到系统消息")
        
        # 合并所有消息
        all_messages = system_messages + other_messages
        
        # 添加当前用户消息
        if request.messages and request.messages[-1].role == "user":
            message = request.messages[-1]
            # 获取文档数据
            document_data = None
            if hasattr(message, "document"):
                document_data = message.document
                # 如果 document_data 是 Document 对象，将其转换为字典
                if hasattr(document_data, "model_dump"):
                    document_data = document_data.model_dump()
                
                # 确保 document_data 是字符串类型
                if document_data and not isinstance(document_data, str):
                    try:
                        # 如果是字典类型，尝试将其转换为 Markdown 格式
                        if isinstance(document_data, dict):
                            if "content" in document_data:
                                document_content = document_data["content"]
                                # 如果有文件名，添加到内容开头（仅当内容中不包含文件名时）
                                if "name" in document_data and not document_content.startswith(f"# 文件: {document_data['name']}"):
                                    file_name = document_data["name"]
                                    document_content = f"# 文件: {file_name}\n\n{document_content}"
                                document_data = document_content
                            else:
                                # 如果没有 content 字段，转换为字符串
                                document_data = json.dumps(document_data)
                        else:
                            # 其他类型转换为字符串
                            document_data = str(document_data)
                    except Exception as e:
                        logging.error(f"处理文档数据时出错: {str(e)}")
                        document_data = str(document_data) if document_data is not None else None
            
            # 获取图片数据
            image_data = message.image if hasattr(message, "image") else None
            # 确保 image_data 是字符串类型
            if image_data and not isinstance(image_data, str):
                try:
                    image_data = json.dumps(image_data)
                except:
                    image_data = str(image_data)
            
            await save_message(
                db,
                conversation_id,
                "user",
                message.content,
                image_data,
                document_data
            )
            all_messages.append({
                "role": message.role,
                "content": message.content,
                "image": image_data,
                "document": document_data  # 直接传递完整的文档数据
            })
        
        # 限制发送给模型的历史消息数量
        limited_messages = get_limited_history(all_messages)
        
        if request.stream:
            # 流式响应 - 预先加载模型
            client, client_id, semaphore = await get_available_client(model=model)
            
            # 将过程封装在异步生成器中
            async def stream_response():
                try:
                    async for chunk in process_chat_messages(
                        limited_messages, 
                        model, 
                        request.web_search, 
                        username=current_user["username"],
                        client=client,
                        client_index=client_id,
                        semaphore=semaphore
                    ):
                        yield chunk
                except Exception as e:
                    error_msg = f"流式生成回复出错: {str(e)}"
                    logging.error(error_msg)
                    logging.exception(e)
                    yield json.dumps({
                        "error": error_msg,
                        "model": model,
                        "message": {
                            "role": "assistant",
                            "content": f"抱歉，生成回复时出错: {str(e)}"
                        }
                    })
            
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream"
            )
        else:
            # 完整响应
            full_response = ""
            error_occurred = False
            
            try:
                # 预先加载模型
                client, client_id, semaphore = await get_available_client(model=model)
                
                async for chunk_json in process_chat_messages(
                    limited_messages, 
                    model, 
                    request.web_search, 
                    username=current_user["username"],
                    client=client,
                    client_index=client_id,
                    semaphore=semaphore
                ):
                    # 解析JSON字符串为对象
                    chunk_data = json.loads(chunk_json)
                    
                    # 检查是否有错误
                    if "error" in chunk_data:
                        error_occurred = True
                        error_message = chunk_data["error"]
                        logging.error(f"生成回复时出错: {error_message}")
                        raise HTTPException(
                            status_code=500,
                            detail=error_message
                        )
                    
                    # 提取内容并累加到响应中
                    if "message" in chunk_data and "content" in chunk_data["message"]:
                        full_response += chunk_data["message"]["content"]
                
                # 只有在没有错误且有响应内容的情况下才保存到数据库
                if not error_occurred and full_response:
                    # 保存助手回复
                    await save_message(
                        db,
                        conversation_id,
                        "assistant",
                        full_response,
                        None,  # AI 回复没有图片
                        None   # AI 回复没有文档
                    )
                
                return {
                    "model": model,
                    "message": {
                        "role": "assistant",
                        "content": full_response
                    }
                }
            except HTTPException:
                # 直接重新抛出HTTP异常
                raise
            except Exception as e:
                # 其他异常转换为HTTP异常
                error_msg = f"处理对话请求时出错: {str(e)}"
                logging.error(error_msg)
                logging.exception(e)
                raise HTTPException(status_code=500, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"处理对话请求时出错: {str(e)}"
        logging.error(error_msg)
        logging.exception(e)
        raise HTTPException(status_code=500, detail=error_msg) 