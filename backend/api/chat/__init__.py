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

class ConversationCreate(BaseModel):
    title: str = "New Conversation"
    model: Optional[str] = None

class ConversationUpdate(BaseModel):
    messages: List[Message]
    model: Optional[str] = None

# 导入功能模块
from .conversation import router as conversation_router
from .message import router as message_router, websocket_endpoint, chat, active_connections, abort_generation

router = APIRouter()

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

__all__ = ["router", "Message", "ChatCompletionRequest", "ConversationCreate", "ConversationUpdate"]
