"""
确保必要的数据目录存在
这个脚本在打包后的应用启动时运行，确保所有必要的目录都已创建
"""
import os
import sys
import shutil
from pathlib import Path
from data_path import get_user_data_dir, get_app_dir

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
    """确保所有必要的目录存在，并且包含必要的文件"""
    # 获取用户数据目录
    user_data_dir = get_user_data_dir()
    
    # 确保以下目录存在
    dirs_to_ensure = [
        user_data_dir / "models",
        user_data_dir / "prompts",
        user_data_dir / "chat_history",
        user_data_dir / "avatars",
        user_data_dir / "logs",
    ]
    
    # 创建目录
    for directory in dirs_to_ensure:
        os.makedirs(directory, exist_ok=True)
        
    # 如果是打包环境，确保CHANGELOG.md文件被复制到应用目录
    if getattr(sys, 'frozen', False):
        ensure_changelog_copied()
    
    return True

def ensure_changelog_copied():
    """确保CHANGELOG.md文件被复制到应用目录"""
    app_dir = get_app_dir()
    target_changelog = app_dir / "CHANGELOG.md"
    
    # 如果目标文件已存在，无需复制
    if target_changelog.exists():
        return
    
    # 尝试从可能的源位置复制
    source_locations = []
    
    # 如果是PyInstaller打包，检查资源目录
    if hasattr(sys, '_MEIPASS'):
        source_locations.append(Path(sys._MEIPASS) / "CHANGELOG.md")
    
    # 检查可执行文件同级目录
    source_locations.append(Path(sys.executable).parent / "CHANGELOG.md")
    
    # 尝试复制
    for source_path in source_locations:
        if source_path.exists():
            shutil.copy2(source_path, target_changelog)
            print(f"已复制更新日志: {source_path} -> {target_changelog}")
            return
    
    print("警告: 无法找到CHANGELOG.md文件源，更新日志功能可能不可用")

if __name__ == "__main__":
    ensure_directories()
