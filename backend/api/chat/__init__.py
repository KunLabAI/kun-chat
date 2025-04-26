from fastapi import APIRouter, Depends, WebSocket, HTTPException
from database import Database, get_db
from api.auth import get_current_user
from typing import Dict, Any
from pydantic import BaseModel
from typing import List, Optional

# 数据模型定义
class Message(BaseModel):
    role: str
    content: str
    timestamp: str
    images: Optional[List[str]] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    stream: bool = False

class ConversationUpdate(BaseModel):
    messages: List[Message]
    model: Optional[str] = None

class ConversationCreate(BaseModel):
    title: str = "New Conversation"
    model: Optional[str] = None

# 创建主路由
router = APIRouter()

# 创建API路由组
chat_router = APIRouter(prefix="/api/chat")

# 这些底层模块被其他模块依赖，所以先导入它们
from .client_pool import get_available_client
from .message_processor import process_chat_messages, get_limited_history
from .db_operations import save_message, verify_conversation_ownership
from .websocket_handler import handle_websocket_connection, active_connections

# 导入功能模块
from .conversation import router as conversation_router
from .message import router as message_router, websocket_endpoint, chat, abort_generation

# 包含会话管理路由
router.include_router(conversation_router)

# 包含消息处理路由
router.include_router(message_router)

# WebSocket聊天接口
router.websocket("/conversations/{conversation_id}/ws")(websocket_endpoint)

# HTTP聊天接口
@router.post("/conversations/{conversation_id}/chat")
async def chat_endpoint(
    conversation_id: str,
    request: ChatCompletionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return await chat(conversation_id, request, current_user, db)

# 中止对话生成接口
@router.post("/conversations/{conversation_id}/abort")
async def abort_endpoint(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return await abort_generation(conversation_id, current_user, db)

# 添加子路由
chat_router.include_router(message_router)
chat_router.include_router(conversation_router)

__all__ = ["router", "Message", "ChatCompletionRequest", "ConversationCreate", "ConversationUpdate"]

