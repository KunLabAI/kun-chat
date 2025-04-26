import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import HTTPException
from database import Database

async def save_message(
    db: Database,
    conversation_id: str,
    role: str,
    content: str,
    images: str = None,
    document: str = None
):
    """保存消息到数据库
    
    Args:
        db: 数据库连接
        conversation_id: 对话ID
        role: 消息角色
        content: 消息内容
        images: 图片数据，JSON数组格式存储图片路径
        document: 文档数据，Markdown 格式
    """
    timestamp = datetime.utcnow().isoformat()
    
    # 记录调试信息
    if images:
        logging.debug(f"Saving message with image data for conversation {conversation_id}")
        # 确保 images 是字符串类型
        if not isinstance(images, str):
            images = json.dumps(images) if images is not None else None
            
    if document:
        logging.debug(f"Saving message with document data for conversation {conversation_id}")
        # 确保 document 是字符串类型
        if not isinstance(document, str):
            try:
                document = json.dumps(document) if document is not None else None
            except:
                document = str(document) if document is not None else None
    
    # 打印参数类型，用于调试
    logging.debug(f"Parameter types: conversation_id={type(conversation_id)}, role={type(role)}, "
                  f"content={type(content)}, images={type(images)}, document={type(document)}, "
                  f"timestamp={type(timestamp)}")
    
    await db.execute(
        """
        INSERT INTO messages (conversation_id, role, content, images, document, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (conversation_id, role, content, images, document, timestamp)
    )
    
    # 更新对话的更新时间
    await db.execute(
        """
        UPDATE conversations
        SET updated_at = ?
        WHERE id = ?
        """,
        (timestamp, conversation_id)
    )
    await db.commit()

async def get_conversation_messages(
    db: Database,
    conversation_id: str,
    current_user: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """获取对话的所有消息"""
    # 验证对话所有权
    conversation = await db.fetch_one(
        """
        SELECT id FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, current_user["username"])
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 获取消息历史
    messages = await db.fetch_all(
        """
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
        """,
        (conversation_id,)
    )
    return messages

async def verify_conversation_ownership(
    db: Database,
    conversation_id: str,
    user_id: str
) -> Dict[str, Any]:
    """验证对话所有权并返回对话信息
    
    Args:
        db: 数据库连接
        conversation_id: 对话ID
        user_id: 用户ID
        
    Returns:
        对话信息
        
    Raises:
        HTTPException: 如果对话不存在或用户无权访问
    """
    conversation = await db.fetch_one(
        """
        SELECT id, model FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, user_id)
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在或您无权访问")
        
    return dict(conversation) 