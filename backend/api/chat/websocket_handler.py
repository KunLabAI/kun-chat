import logging
import json
from typing import Dict, Any
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from database import Database

from api.auth import decode_token
from .db_operations import save_message
from .message_processor import process_chat_messages, get_limited_history
from .client_pool import get_available_client

# 用于存储活跃的 WebSocket 连接
active_connections: Dict[str, WebSocket] = {}

async def get_current_user_from_token(token: str):
    """从token中获取当前用户信息"""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("无效的token")
        
        # 构建用户对象
        return {"id": user_id, "username": user_id}
    except Exception as e:
        logging.error(f"认证失败: {str(e)}")
        raise ValueError(f"认证失败: {str(e)}")

async def handle_websocket_connection(
    websocket: WebSocket,
    conversation_id: str,
    token: str,
    db: Database
):
    """处理WebSocket连接"""
    await websocket.accept()
    
    # 验证用户令牌
    current_user = None
    try:
        current_user = await get_current_user_from_token(token)
    except Exception as e:
        await websocket.send_json({"error": f"认证失败: {str(e)}"})
        await websocket.close()
        return

    # 验证会话存在性和权限
    try:
        # 修改为使用fetch_one方法查询对话，并使用username作为用户标识符
        conversation = await db.fetch_one(
            """
            SELECT id, model, user_id
            FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (conversation_id, current_user["username"])
        )
        
        if not conversation:
            await websocket.send_json({"error": "对话不存在或无权访问"})
            await websocket.close()
            return
    except Exception as e:
        await websocket.send_json({"error": f"获取对话失败: {str(e)}"})
        await websocket.close()
        return
    
    try:
        # 记录活跃连接
        active_connections[conversation_id] = websocket
        
        # 接收客户端发送的消息
        data = await websocket.receive_json()
        
        # 提取消息和模型信息
        messages = data.get("messages", [])
        # 从数据库记录中获取model字段，如果没有则使用默认模型
        model = data.get("model") or conversation["model"] or "llama2"
        web_search = data.get("web_search", False)
        
        # 检查消息格式是否正确
        if not messages or not isinstance(messages, list):
            await websocket.send_json({"error": "消息格式不正确"})
            await websocket.close()
            return
        
        # 获取对话历史记录，避免重复发送上下文
        try:
            # 直接从消息表获取历史记录
            history_messages = await db.fetch_all(
                """
                SELECT role, content, images, document, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id,)
            )
            
            # 将数据库查询结果转换为前端期望的消息格式
            history = []
            for msg in history_messages:
                message_dict = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                # 处理图片数据
                if msg["images"]:
                    try:
                        message_dict["image"] = msg["images"]
                    except:
                        # 如果解析失败，直接使用原始字符串
                        message_dict["image"] = str(msg["images"])
                
                # 处理文档数据
                if msg["document"]:
                    try:
                        message_dict["document"] = msg["document"]
                    except:
                        # 如果解析失败，直接使用原始字符串
                        message_dict["document"] = str(msg["document"])
                
                history.append(message_dict)
            
            # 获取有限的历史记录用作上下文
            history = get_limited_history(history, 20)  # 限制只使用最后20条消息作为上下文
        except Exception as e:
            history = []
            logging.error(f"获取历史记录失败: {e}")
            logging.exception(e)
        
        # 合并历史记录和新消息
        combined_messages = history + messages
        
        # 创建回应中
        response_content = ""
        user_message = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        user_image = messages[-1].get("image") if messages and messages[-1]["role"] == "user" else None
        user_document = messages[-1].get("document") if messages and messages[-1]["role"] == "user" else None
        
        # 记录用户消息到数据库
        try:
            await save_message(
                db, 
                conversation_id, 
                "user", 
                user_message, 
                images=user_image,
                document=user_document
            )
        except Exception as e:
            logging.error(f"保存用户消息失败: {e}")
        
        # 处理聊天消息
        try:
            logging.info(f"开始生成回复，使用模型 {model}...")
            
            # 先尝试获取客户端并预加载模型，通过传递websocket对象，可以发送模型加载状态
            try:
                client, client_id, semaphore = await get_available_client(model=model, websocket=websocket)
            except Exception as e:
                error_message = f"获取AI模型客户端失败: {str(e)}"
                logging.error(error_message)
                await websocket.send_json({"error": error_message})
                return
            
            # 异步生成回复内容
            async for chunk_json in process_chat_messages(
                combined_messages, 
                model, 
                web_search=web_search,
                username=current_user["username"],
                client=client,
                client_index=client_id,
                semaphore=semaphore
            ):
                # 解析JSON字符串为对象
                chunk_data = json.loads(chunk_json)
                
                # 检查是否有错误
                if "error" in chunk_data:
                    # 如果有错误，直接将错误发送给客户端
                    await websocket.send_json(chunk_data)
                    logging.error(f"生成过程中出错: {chunk_data['error']}")
                    continue
                
                # 提取内容并累加到响应中
                if "message" in chunk_data and "content" in chunk_data["message"]:
                    content = chunk_data["message"]["content"]
                    response_content += content
                    
                    # 发送消息内容给客户端
                    await websocket.send_json({
                        "message": {
                            "content": content
                        }
                    })
                
                # 检查是否完成
                if chunk_data.get("done", False):
                    await websocket.send_json({"done": True})
            
            logging.info(f"完成生成回复，总长度: {len(response_content)}")
        except Exception as e:
            error_message = f"生成回复失败: {str(e)}"
            logging.error(error_message)
            logging.exception(e)
            await websocket.send_json({"error": error_message})
            await websocket.close()
            return
        
        # 保存AI回复到数据库
        try:
            # 只有在有内容且没有错误的情况下才保存回复
            if response_content:
                await save_message(db, conversation_id, "assistant", response_content)
                
                # 更新对话的最后更新时间
                update_time = datetime.utcnow().isoformat()
                await db.execute(
                    """
                    UPDATE conversations
                    SET updated_at = ?
                    WHERE id = ?
                    """,
                    (update_time, conversation_id)
                )
                await db.commit()  # 确保更改被提交
        except Exception as e:
            logging.error(f"保存AI回复失败: {e}")
            logging.exception(e)
    
    except WebSocketDisconnect:
        logging.info("WebSocket连接断开")
    except Exception as e:
        error_message = f"处理WebSocket消息失败: {str(e)}"
        logging.error(error_message)
        logging.exception(e)
        try:
            await websocket.send_json({"error": error_message})
        except:
            pass
    finally:
        # 从活跃连接中移除
        active_connections.pop(conversation_id, None)
        # 关闭WebSocket连接
        try:
            await websocket.close()
        except:
            pass 