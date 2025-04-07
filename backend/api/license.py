from fastapi import APIRouter, HTTPException
import os
import sys

router = APIRouter()

@router.get("/license")
async def get_license():
    try:
        # 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            base_path = os.path.dirname(sys.executable)
            # 尝试在 _internal 目录下查找
            internal_path = os.path.join(base_path, "_internal")
            if os.path.exists(internal_path):
                base_path = internal_path
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 尝试多个可能的路径
        possible_paths = [
            os.path.join(base_path, "license.md"),
            os.path.join(base_path, "..", "license.md"),
            os.path.join(base_path, "..", "..", "license.md"),
            os.path.join(base_path, "_internal", "license.md"),
            os.path.join(base_path, "..", "_internal", "license.md"),
            os.path.join(base_path, "..", "..", "_internal", "license.md"),
            os.path.join(os.path.dirname(os.path.dirname(base_path)), "license.md")  # 添加根目录路径
        ]
        
        content = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                break
        
        if content is None:
            raise FileNotFoundError("无法找到许可证文件")
            
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read license file: {str(e)}")