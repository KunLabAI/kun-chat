from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter()

@router.get("/changelog")
async def get_changelog():
    try:
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        changelog_path = os.path.join(root_dir, "CHANGELOG.md")
        
        # 读取更新日志文件
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read changelog file: {str(e)}")