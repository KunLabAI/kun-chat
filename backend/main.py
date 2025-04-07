from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
from typing import List
from api import api_router
from config import API_CONFIG
import logging
from database import db  # 导入数据库实例
from contextlib import asynccontextmanager
from ensure_dirs import ensure_directories  # 导入目录确保函数
from data_path import get_avatars_dir, get_logs_dir  # 导入获取目录函数

# 确保必要的目录存在
ensure_directories()

# 配置日志
logs_dir = get_logs_dir()
log_file = logs_dir / "kunyu_backend.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# 设置uvicorn日志级别
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用的生命周期管理"""
    # 启动时连接数据库
    try:
        await db.connect()
        logging.info("Database connected at application startup.")
    except Exception as e:
        logging.error(f"Failed to connect to database at startup: {e}")
        # 即使数据库连接失败，应用也会继续启动
        # 后续请求会通过 ensure_connected 尝试重新连接
    
    yield
    
    # 关闭时断开数据库连接
    try:
        await db.disconnect()
        logging.info("Database disconnected at application shutdown.")
    except Exception as e:
        logging.error(f"Error disconnecting database at shutdown: {e}")

app = FastAPI(
    title="Kun-Lab Backend",
    description="基于Ollama的轻量级聊天应用后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
def get_allowed_origins():
    """获取允许的跨域来源列表，包括动态的局域网IP"""
    from api.tools.network import get_local_ip, get_frontend_port
    
    # 获取前端端口
    frontend_port = get_frontend_port()
    
    # 基本允许的来源
    base_origins = [
        f"http://localhost:{frontend_port}",  # 前端开发服务器
        f"http://127.0.0.1:{frontend_port}",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # 添加局域网IP地址
    local_ip = get_local_ip()
    if local_ip != "127.0.0.1":
        base_origins.append(f"http://{local_ip}:{frontend_port}")
        base_origins.append(f"http://{local_ip}:8000")
    
    return base_origins

origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Authorization"],
)

# 创建静态文件目录
avatars_dir = get_avatars_dir()
os.makedirs(avatars_dir, exist_ok=True)

# 挂载静态文件目录
if getattr(sys, 'frozen', False):
    # 打包环境：使用用户数据目录中的avatars目录作为静态文件目录
    app.mount("/static/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")
else:
    # 开发环境：使用用户数据目录中的avatars目录
    app.mount("/static/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")
    # 同时挂载项目目录中的static目录用于其他静态文件
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含API路由
app.include_router(api_router, prefix="/api")  # 添加全局 /api 前缀

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kun-Lab Backend Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 这里将添加与Ollama的集成逻辑
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        timeout_keep_alive=1200,  # 设置 keep-alive 超时为 1200 秒（20 分钟）
        ssl_keyfile=None,  # 生产环境建议配置SSL
        ssl_certfile=None
    )
