from fastapi import APIRouter, UploadFile, File, HTTPException
from markitdown import MarkItDown
import os
import re

router = APIRouter()
md = MarkItDown()  # 初始化MarkItDown

def get_mime_type_from_filename(filename):
    """根据文件名获取 MIME 类型
    
    Args:
        filename: 文件名
        
    Returns:
        str: MIME 类型
    """
    # 根据文件扩展名确定文件类型
    file_extension = os.path.splitext(filename)[1].lower()
    if not file_extension:
        return 'text/markdown'
        
    # 根据文件扩展名映射 MIME 类型
    mime_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.7z': 'application/x-7z-compressed',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
    }
    return mime_types.get(file_extension, 'text/markdown')

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

            # 在 Markdown 内容开头添加文件信息
            file_info = f"# 文件: {file.filename}\n\n"
            markdown_content = file_info + result.text_content

            return {
                "name": file.filename,
                "content": markdown_content,
                "type": get_mime_type_from_filename(file.filename) or file.content_type or "text/markdown"
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
