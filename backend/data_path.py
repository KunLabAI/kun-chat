"""
数据路径管理模块
负责在打包环境和开发环境中提供一致的数据存储路径
"""
import os
import sys
import shutil
from pathlib import Path

def get_app_name():
    """获取应用名称"""
    return "Kun-Lab"

def get_app_dir():
    """
    获取应用目录
    在打包环境中，使用可执行文件所在目录
    在开发环境中，使用项目目录
    """
    # 如果是打包后的应用
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包的情况下，使用临时目录的父目录
            # 即可执行文件所在目录
            app_dir = os.path.dirname(sys.executable)
        else:
            # 其他打包工具的情况
            app_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境: 项目目录
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    return Path(app_dir)

def get_user_data_dir():
    """
    获取用户数据目录
    在Electron环境中使用Electron的用户数据目录
    在开发环境中使用应用目录下的data文件夹
    """
    # 检查是否在Electron环境中
    electron_user_data = os.environ.get('ELECTRON_USER_DATA_DIR')
    if electron_user_data:
        # 在Electron环境中，使用Electron的用户数据目录
        data_dir = Path(electron_user_data) / "data"
    else:
        # 开发环境或非Electron环境：使用应用目录下的data文件夹
        app_dir = get_app_dir()
        data_dir = app_dir / "data"
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    return data_dir

def get_db_path():
    """获取数据库文件路径"""
    return get_user_data_dir() / "kun-lab.db"

def get_models_dir():
    """获取模型目录"""
    models_dir = get_user_data_dir() / "models"
    os.makedirs(models_dir, exist_ok=True)
    return models_dir

def get_prompts_dir():
    """获取提示词目录"""
    prompts_dir = get_user_data_dir() / "prompts"
    os.makedirs(prompts_dir, exist_ok=True)
    return prompts_dir

def get_chat_history_dir():
    """获取聊天历史目录"""
    chat_history_dir = get_user_data_dir() / "chat_history"
    os.makedirs(chat_history_dir, exist_ok=True)
    return chat_history_dir

def get_static_dir():
    """获取静态文件目录"""
    app_dir = get_app_dir()
    static_dir = app_dir / "static"
    os.makedirs(static_dir, exist_ok=True)
    return static_dir

def get_avatars_dir():
    """获取头像目录"""
    # 头像存储在用户数据目录的 avatars 中
    avatars_dir = get_user_data_dir() / "avatars"
    os.makedirs(avatars_dir, exist_ok=True)
    
    # 确保默认头像存在
    ensure_default_avatar(avatars_dir)
    
    return avatars_dir

def get_logs_dir():
    """获取日志目录"""
    logs_dir = get_user_data_dir() / "logs"
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def ensure_default_avatar(avatars_dir):
    """确保默认头像存在"""
    # 在avatars目录下创建默认头像
    default_avatar_path = avatars_dir / "default-avatar.jpg"
    
    # 如果默认头像不存在，则复制
    if not default_avatar_path.exists():
        # 获取源文件路径
        if getattr(sys, 'frozen', False):
            # 打包环境：从应用目录获取默认头像
            app_dir = get_app_dir()
            source_path = app_dir / "default-avatar.jpg"
            
            if not source_path.exists():
                print(f"警告: 默认头像源文件不存在: {source_path}")
                return
        else:
            # 开发环境
            source_path = Path(__file__).parent / "default-avatar.jpg"
        
        # 如果源文件存在，则复制
        if source_path.exists():
            shutil.copy2(source_path, default_avatar_path)
            print(f"已复制默认头像: {source_path} -> {default_avatar_path}")
        else:
            print(f"警告: 默认头像源文件不存在: {source_path}")
