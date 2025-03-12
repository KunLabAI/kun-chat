from fastapi import APIRouter, UploadFile, File, HTTPException
from markitdown import MarkItDown
import os

router = APIRouter()
md = MarkItDown()  # 初始化MarkItDown

class MarkitdownService:
    async def convert_document(self, file: UploadFile) -> dict:
        """转换文件为Markdown格式"""
        try:
            # 保存上传的文件到临时目录
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            # 使用MarkItDown转换文件
            result = md.convert(temp_path)
            
            # 删除临时文件
            os.remove(temp_path)

            return {
                "original_filename": file.filename,
                "markdown_content": result.text_content
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# 创建服务实例
service = MarkitdownService()

@router.post("/convert")
async def convert_document(file: UploadFile = File(...)):
    """转换文档API端点
    
    将上传的文档转换为Markdown格式
    """
    return await service.convert_document(file)
