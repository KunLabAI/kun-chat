from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database import Database, get_db
from api.auth import get_current_user
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["prompts"])

class TagModel(BaseModel):
    text: str
    color: str

class PromptBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[TagModel]] = []

class PromptCreate(PromptBase):
    pass

class PromptUpdate(PromptBase):
    pass

class Prompt(PromptBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    model_config = {
        'from_attributes': True
    }

@router.post("/prompts", response_model=Prompt)
async def create_prompt(
    prompt: PromptCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """创建新的提示词"""
    try:
        logger.info(f"User {current_user['username']} attempting to create prompt: {prompt.title}")
        result = await db.create_prompt(
            user_id=current_user["username"],
            title=prompt.title,
            content=prompt.content,
            tags=[tag.dict() for tag in prompt.tags] if prompt.tags else []
        )
        logger.info(f"Successfully created prompt with ID: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Error creating prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建提示词失败: {str(e)}"
        )

@router.get("/prompts", response_model=List[Prompt])
async def get_prompts(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取当前用户的所有提示词"""
    try:
        logger.info(f"User {current_user['username']} attempting to retrieve prompts")
        result = await db.get_user_prompts(current_user["username"])
        logger.info(f"Successfully retrieved {len(result)} prompts")
        return result
    except Exception as e:
        logger.error(f"Error retrieving prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取提示词失败: {str(e)}"
        )

@router.get("/prompts/{prompt_id}", response_model=Prompt)
async def get_prompt(
    prompt_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """获取单个提示词"""
    try:
        logger.info(f"User {current_user['username']} attempting to retrieve prompt with ID: {prompt_id}")
        prompt = await db.get_prompt(prompt_id)
        if not prompt:
            logger.error(f"Prompt with ID {prompt_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提示词不存在"
            )
        if prompt["user_id"] != current_user["username"]:
            logger.error(f"User {current_user['username']} does not have permission to access prompt with ID: {prompt_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限访问此提示词"
            )
        logger.info(f"Successfully retrieved prompt with ID: {prompt_id}")
        return prompt
    except Exception as e:
        logger.error(f"Error retrieving prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取提示词失败: {str(e)}"
        )

@router.put("/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(
    prompt_id: str,
    prompt_update: PromptUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """更新提示词"""
    try:
        logger.info(f"User {current_user['username']} attempting to update prompt with ID: {prompt_id}")
        existing_prompt = await db.get_prompt(prompt_id)
        if not existing_prompt:
            logger.error(f"Prompt with ID {prompt_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提示词不存在"
            )
        if existing_prompt["user_id"] != current_user["username"]:
            logger.error(f"User {current_user['username']} does not have permission to update prompt with ID: {prompt_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改此提示词"
            )
        updated_prompt = await db.update_prompt(
            prompt_id=prompt_id,
            user_id=current_user["username"],
            title=prompt_update.title,
            content=prompt_update.content,
            tags=[tag.dict() for tag in prompt_update.tags] if prompt_update.tags else []
        )
        logger.info(f"Successfully updated prompt with ID: {prompt_id}")
        return updated_prompt
    except Exception as e:
        logger.error(f"Error updating prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新提示词失败: {str(e)}"
        )

@router.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """删除提示词"""
    try:
        logger.info(f"User {current_user['username']} attempting to delete prompt with ID: {prompt_id}")
        existing_prompt = await db.get_prompt(prompt_id)
        if not existing_prompt:
            logger.error(f"Prompt with ID {prompt_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提示词不存在"
            )
        if existing_prompt["user_id"] != current_user["username"]:
            logger.error(f"User {current_user['username']} does not have permission to delete prompt with ID: {prompt_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限删除此提示词"
            )
        success = await db.delete_prompt(prompt_id, current_user["username"])
        if not success:
            logger.error(f"Failed to delete prompt with ID: {prompt_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除提示词失败"
            )
        logger.info(f"Successfully deleted prompt with ID: {prompt_id}")
    except Exception as e:
        logger.error(f"Error deleting prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除提示词失败: {str(e)}"
        )
