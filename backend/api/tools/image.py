from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import base64
import logging

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):
    """
    将上传的图片转换为base64格式
    
    参数:
    - file: 图片文件
    
    返回:
    ```json
    {
        "success": true,
        "image_data": "base64编码的图片数据"
    }
    ```
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="只允许上传图片文件"
            )
        
        # 读取图片内容
        content = await file.read()
        
        # 转换为 base64
        image_data = base64.b64encode(content).decode()
        base64_image = f"data:{file.content_type};base64,{image_data}"
        
        return {
            "success": True,
            "image_data": base64_image
        }
        
    except Exception as e:
        logging.error(f"图片上传错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"图片处理失败: {str(e)}"
        )
