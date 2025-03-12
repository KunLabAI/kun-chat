import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径配置
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
PROMPTS_DIR = DATA_DIR / "prompts"
CHAT_HISTORY_DIR = DATA_DIR / "chat_history"

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
