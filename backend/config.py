import os
import sys
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from data_path import get_user_data_dir, get_models_dir, get_prompts_dir, get_chat_history_dir

# 加载环境变量
load_dotenv()

# 获取应用基础路径
def get_base_dir():
    """获取应用程序基础目录"""
    # 如果是打包后的应用，使用应用所在目录
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    # 否则使用脚本所在目录
    return Path(__file__).resolve().parent

# 基础路径配置
BASE_DIR = get_base_dir()
DATA_DIR = get_user_data_dir()
MODELS_DIR = get_models_dir()
PROMPTS_DIR = get_prompts_dir()
CHAT_HISTORY_DIR = get_chat_history_dir()

# 创建必要的目录
for dir_path in [DATA_DIR, MODELS_DIR, PROMPTS_DIR, CHAT_HISTORY_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API配置
API_CONFIG: Dict[str, Any] = {
    "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "DEFAULT_MODEL": "llama2",
    "MAX_TOKENS": 2000,
    "TEMPERATURE": 0.7,
}

# 安全配置
SECURITY_CONFIG = {
    "SECRET_KEY": "your-secret-key-please-change-in-production",  # 在生产环境中修改此密钥
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 43200,  # 30天
    "PERSISTENT_TOKEN_EXPIRE_DAYS": 365    # 持久化token有效期为1年
}

ERROR_MESSAGES = {
    "invalid_credentials": "用户名或密码错误",
    "user_exists": "用户名已被注册",
    "invalid_token": "登录已过期，请重新登录",
    "inactive_user": "用户账号已禁用",
    "password_incorrect": "当前密码错误",
    "password_changed": "密码修改成功",
    "preferences_updated": "偏好设置已更新"
}

# WebSocket配置
WEBSOCKET_CONFIG = {
    "PING_INTERVAL": 30,  # 秒
    "PING_TIMEOUT": 10,   # 秒
}

# 文件存储配置
STORAGE_CONFIG = {
    "MAX_HISTORY_SIZE": 1000,  # 每个用户最大历史记录数
    "MAX_PROMPT_SIZE": 500,    # 提示词库最大容量
}
