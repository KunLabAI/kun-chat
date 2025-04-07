"""
确保必要的数据目录存在
这个脚本在打包后的应用启动时运行，确保所有必要的目录都已创建
"""
import os
import sys
from pathlib import Path

def get_app_dir():
    """获取应用程序目录"""
    # 如果是打包后的应用，使用应用所在目录
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller临时目录
            base_dir = Path(sys._MEIPASS)
            # 应用目录是可执行文件所在目录
            app_dir = Path(os.path.dirname(sys.executable))
        else:
            # 其他打包工具
            app_dir = Path(os.path.dirname(sys.executable))
    else:
        # 开发环境
        app_dir = Path(__file__).resolve().parent
    
    return app_dir

def ensure_directories():
    """确保所有必要的目录都存在"""
    # 获取应用目录
    app_dir = get_app_dir()
    
    # 定义需要创建的目录
    dirs_to_create = [
        "data",
        "data/models",
        "data/prompts",
        "data/chat_history",
        "data/logs",
        "static",
        "static/avatars"
    ]
    
    # 创建目录
    for dir_path in dirs_to_create:
        full_path = app_dir / dir_path
        os.makedirs(full_path, exist_ok=True)
        print(f"确保目录存在: {full_path}")

if __name__ == "__main__":
    ensure_directories()
