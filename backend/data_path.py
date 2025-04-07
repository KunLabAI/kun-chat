"""
数据路径管理模块
负责在打包环境和开发环境中提供一致的数据存储路径
"""
import os
import sys
import shutil
from pathlib import Path
import logging

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

def get_changelog_path():
    """
    获取CHANGELOG.md文件路径
    在打包环境中，尝试从应用目录获取
    在开发环境中，从项目根目录获取
    """
    logger = logging.getLogger(__name__)
    
    # 检查的路径列表
    possible_paths = []
    
    # 打包环境
    if getattr(sys, 'frozen', False):
        # 首先尝试在应用根目录查找
        app_dir = get_app_dir()
        possible_paths.extend([
            app_dir / "CHANGELOG.md",  # 应用根目录
            app_dir.parent / "CHANGELOG.md",  # 上级目录
            Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else '.') / "CHANGELOG.md",  # PyInstaller临时目录
            Path(os.path.dirname(sys.executable)) / "CHANGELOG.md",  # 可执行文件目录
            get_user_data_dir() / "CHANGELOG.md",  # 用户数据目录
            Path(os.path.abspath('.')) / "CHANGELOG.md",  # 当前工作目录
            Path(os.path.dirname(os.path.abspath(__file__))) / "CHANGELOG.md"  # 当前模块目录
        ])
        # 检查buildpath文件夹
        buildpath_dir = app_dir / "buildpath"
        if buildpath_dir.exists():
            possible_paths.append(buildpath_dir / "CHANGELOG.md")
    else:
        # 开发环境: 项目根目录
        backend_dir = Path(__file__).parent
        root_dir = backend_dir.parent
        possible_paths.extend([
            root_dir / "CHANGELOG.md",  # 项目根目录
            backend_dir / "CHANGELOG.md",  # backend目录
            Path(os.path.abspath('.')) / "CHANGELOG.md"  # 当前工作目录
        ])
        # 检查buildpath文件夹
        buildpath_dir = backend_dir / "buildpath"
        if buildpath_dir.exists():
            possible_paths.append(buildpath_dir / "CHANGELOG.md")
    
    # 检查所有可能的路径
    logger.info(f"正在查找CHANGELOG.md文件，环境: {'打包' if getattr(sys, 'frozen', False) else '开发'}")
    for path in possible_paths:
        logger.info(f"检查路径: {path}")
        if path.exists():
            logger.info(f"找到CHANGELOG.md文件: {path}")
            return path
    
    # 如果都找不到，记录日志并返回None
    logger.warning("未找到CHANGELOG.md文件，已尝试以下路径:")
    for path in possible_paths:
        logger.warning(f"  - {path}")
    return None

def ensure_default_avatar(avatars_dir):
    """确保默认头像存在"""
    # 在avatars目录下创建默认头像
    default_avatar_path = avatars_dir / "default-avatar.jpg"
    
    # 如果默认头像不存在，则复制
    if not default_avatar_path.exists():
        # 获取源文件路径
        if getattr(sys, 'frozen', False):
            # 打包环境：尝试多个可能的路径
            possible_paths = [
                Path(os.path.dirname(sys.executable)) / "default-avatar.jpg",  # 可执行文件目录
                Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else '.') / "default-avatar.jpg",  # PyInstaller临时目录
                Path(os.path.dirname(os.path.abspath(__file__))) / "default-avatar.jpg"  # 当前模块目录
            ]
            
            # 检查每个可能的位置
            source_path = None
            for path in possible_paths:
                if path.exists():
                    source_path = path
                    break
                    
            if not source_path:
                print(f"警告: 无法找到默认头像源文件，尝试过以下路径:")
                for path in possible_paths:
                    print(f"  - {path}")
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
