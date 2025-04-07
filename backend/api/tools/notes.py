from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database import Database, get_db
from api.auth import get_current_user
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

# 笔记数据模型
class NoteBase(BaseModel):
    title: str
    content: Optional[str] = ""
    conversation_id: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    conversation_id: Optional[str] = None

class Note(BaseModel):
    id: int
    user_id: str
    title: str
    content: Optional[str] = None
    conversation_id: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {
        'from_attributes': True
    }

@router.post("/", response_model=Note)
async def create_note(
    note: NoteCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """创建新笔记"""
    try:
        logger.info(f"User {current_user['username']} attempting to create note: {note.title}")
        result = await db.create_note(
            user_id=current_user["username"],
            title=note.title,
            content=note.content,
            conversation_id=note.conversation_id
        )
        logger.info(f"Successfully created note with ID: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建笔记失败: {str(e)}"
        )

@router.get("/", response_model=List[Note])
async def get_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取当前用户的所有笔记"""
    try:
        logger.info(f"User {current_user['username']} attempting to retrieve notes")
        notes = await db.get_user_notes(current_user["username"], limit, skip)
        logger.info(f"Successfully retrieved {len(notes)} notes")
        return notes
    except Exception as e:
        logger.error(f"Error retrieving notes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取笔记失败: {str(e)}"
        )

@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取单个笔记详情"""
    try:
        logger.info(f"User {current_user['username']} attempting to retrieve note with ID: {note_id}")
        note = await db.get_note(note_id)
        if not note:
            logger.error(f"Note with ID {note_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )
        if note["user_id"] != current_user["username"]:
            logger.error(f"User {current_user['username']} does not have permission to access note with ID: {note_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限访问此笔记"
            )
        logger.info(f"Successfully retrieved note with ID: {note_id}")
        return note
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取笔记失败: {str(e)}"
        )

@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """更新笔记"""
    try:
        logger.info(f"User {current_user['username']} attempting to update note with ID: {note_id}")
        # 检查笔记是否存在及权限
        note = await db.get_note(note_id)
        if not note:
            logger.error(f"Note with ID {note_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )
        
        if note["user_id"] != current_user["username"]:
            logger.error(f"User {current_user['username']} does not have permission to update note with ID: {note_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改此笔记"
            )
        
        # 更新笔记
        update_data = note_update.dict(exclude_unset=True)
        updated_note = await db.update_note(note_id, update_data)
        
        if not updated_note:
            logger.error(f"Failed to update note with ID: {note_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新笔记失败"
            )
        
        logger.info(f"Successfully updated note with ID: {note_id}")
        return updated_note
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新笔记失败: {str(e)}"
        )

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """删除笔记"""
    try:
        logger.info(f"User {current_user['username']} attempting to delete note with ID: {note_id}")
        success = await db.delete_note(note_id, current_user["username"])
        
        if not success:
            logger.error(f"Note with ID {note_id} not found or permission denied")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在或没有权限"
            )
        
        logger.info(f"Successfully deleted note with ID: {note_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除笔记失败: {str(e)}"
        )

@router.get("/conversation/{conversation_id}", response_model=List[Note])
async def get_conversation_notes(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取与特定对话相关的笔记"""
    try:
        logger.info(f"User {current_user['username']} attempting to retrieve notes for conversation: {conversation_id}")
        notes = await db.get_conversation_notes(conversation_id)
        # 仅返回当前用户的笔记
        result = [note for note in notes if note["user_id"] == current_user["username"]]
        logger.info(f"Successfully retrieved {len(result)} notes for conversation: {conversation_id}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving conversation notes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话笔记失败: {str(e)}"
        ) 