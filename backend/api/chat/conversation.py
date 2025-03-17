from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import uuid
import re
from database import Database, get_db
from api.auth import get_current_user
from .schemas import ConversationCreate, ConversationUpdate, ModelUpdate
import os
import json
import logging
from api.tools.doc_format import get_mime_type_from_filename

router = APIRouter()

async def get_conversations_list(
    current_user: Dict[str, Any],
    db: Database
) -> List[Dict[str, Any]]:
    """获取当前用户的所有对话列表"""
    conversations = await db.fetch_all(
        """
        SELECT id, title, model, created_at, updated_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (current_user["username"],)
    )
    return conversations

async def get_conversation_with_messages(
    conversation_id: str,
    current_user: Dict[str, Any],
    db: Database
) -> Dict[str, Any]:
    """获取指定对话的详细信息和消息历史"""
    # 获取对话基本信息
    conversation = await db.fetch_one(
        """
        SELECT id, title, model, created_at, updated_at
        FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, current_user["username"])
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 获取对话的消息历史
    messages = await db.fetch_all(
        """
        SELECT role, content, images, document, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
        """,
        (conversation_id,)
    )
    
    # 转换消息格式
    formatted_messages = []
    for msg in messages:
        message_dict = {
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg["created_at"]
        }
        
        # 处理图片数据
        if msg["images"]:
            try:
                # 尝试解析 JSON 字符串
                images_data = json.loads(msg["images"])
                if isinstance(images_data, list) and len(images_data) > 0:
                    # 将第一个图片数据赋值给 image 字段，保持与前端一致
                    message_dict["image"] = images_data[0]
                    logging.debug(f"处理历史消息图片数据: {images_data[0][:30]}...")
            except Exception as e:
                logging.error(f"解析图片数据时出错: {str(e)}")
                # 如果解析失败，保留原始数据
                message_dict["images"] = msg["images"]
        
        # 处理文档数据
        if msg["document"]:
            # 文档内容是 Markdown 文本
            document_content = msg["document"]
            
            # 尝试从文档内容中提取文件名
            file_name = "document.md"
            file_type = "text/markdown"
            
            # 从 Markdown 内容中提取文件名
            match = re.search(r"# 文件: (.+?)\n", document_content)
            if match:
                file_name = match.group(1)
                # 根据文件名获取 MIME 类型
                file_type = get_mime_type_from_filename(file_name)
            
            # 构建文档对象，用于前端显示
            message_dict["document"] = {
                "name": file_name,
                "content": document_content,
                "type": file_type
            }
            logging.debug(f"处理历史消息文档数据: {file_name}, 类型: {file_type}")
        
        formatted_messages.append(message_dict)
    
    return {
        **conversation,
        "messages": formatted_messages
    }

@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取当前用户的所有对话列表"""
    return await get_conversations_list(current_user, db)

@router.post("/conversations", response_model=Dict[str, Any])
async def create_conversation(
    conversation: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """创建新的对话"""
    from config import API_CONFIG
    
    conversation_id = str(uuid.uuid4())
    current_time = datetime.utcnow().isoformat()
    model = conversation.model or API_CONFIG["DEFAULT_MODEL"]
    
    await db.execute(
        """
        INSERT INTO conversations (id, user_id, title, model, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (conversation_id, current_user["username"], conversation.title, model, current_time, current_time)
    )
    await db.commit()
    
    return {
        "id": conversation_id,
        "title": conversation.title,
        "model": model,
        "created_at": current_time,
        "updated_at": current_time
    }

@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取指定对话的详细信息和消息历史"""
    return await get_conversation_with_messages(conversation_id, current_user, db)

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """删除指定的对话"""
    # 检查对话是否存在且属于当前用户
    conversation = await db.fetch_one(
        """
        SELECT id FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, current_user["username"])
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 删除对话及其所有消息
    await db.execute(
        "DELETE FROM messages WHERE conversation_id = ?",
        (conversation_id,)
    )
    await db.execute(
        "DELETE FROM conversations WHERE id = ?",
        (conversation_id,)
    )
    await db.commit()
    
    return {"message": "对话删除成功"}

@router.post("/conversations/{conversation_id}/clear")
async def clear_conversation_messages(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """清空指定对话的消息"""
    # 检查对话是否存在且属于当前用户
    conversation = await db.fetch_one(
        """
        SELECT id FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, current_user["username"])
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 只删除消息，保留对话
    await db.execute(
        "DELETE FROM messages WHERE conversation_id = ?",
        (conversation_id,)
    )
    await db.commit()
    
    return {"message": "对话消息已清空"}

@router.put("/conversations/{conversation_id}/model")
async def update_conversation_model(
    conversation_id: str,
    model_update: ModelUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """更新对话使用的模型"""
    # 检查对话是否存在且属于当前用户
    conversation = await db.fetch_one(
        """
        SELECT id FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, current_user["username"])
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 更新模型
    current_time = datetime.utcnow().isoformat()
    await db.execute(
        """
        UPDATE conversations
        SET model = ?, updated_at = ?
        WHERE id = ?
        """,
        (model_update.model, current_time, conversation_id)
    )
    await db.commit()
    
    return {"message": "模型更新成功"}
