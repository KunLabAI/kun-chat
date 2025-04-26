import asyncio
import logging
import os
from typing import Dict, Tuple

from fastapi import WebSocket
from ollama.client import OllamaClient
from ollama.types import ChatMessage, ChatRequest

from config import API_CONFIG
from .schemas import ModelLoadingStatus

# 全局客户端池
client_pool = None

# 定义ClientPool类
class ClientPool:
    """Ollama客户端池，用于管理多个并发请求和模型加载"""
    
    def __init__(self, max_clients: int, semaphore: asyncio.Semaphore):
        """初始化客户端池
        Args:
            max_clients: 最大客户端数量
            semaphore: 用于限制并发请求的信号量
        """
        self.max_clients = max_clients
        self.semaphore = semaphore
        self.clients = [OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) for _ in range(max_clients)]
        self.model_locks = {}  # 模型加载锁
        self.model_client_map = {}  # 模型到客户端的映射
        self.client_model_map = {i: None for i in range(max_clients)}  # 客户端到模型的映射
        logging.info(f"已创建客户端池，包含 {max_clients} 个客户端")
    
    def get_default_client(self) -> Tuple[OllamaClient, int]:
        """获取默认客户端"""
        # 简单循环选择策略
        client_id = 0
        return self.clients[client_id], client_id
    
    async def get_client_for_model(self, model: str) -> int:
        """获取指定模型的客户端ID
        如果模型未加载，会加载模型
        Args:
            model: 模型名称
        Returns:
            客户端ID
        """
        # 如果模型已经分配给某个客户端，直接返回
        if model in self.model_client_map:
            return self.model_client_map[model]
        
        # 如果尚未为这个模型创建锁，创建一个
        if model not in self.model_locks:
            self.model_locks[model] = asyncio.Lock()
        
        # 使用锁确保模型只被加载一次
        async with self.model_locks[model]:
            # 双重检查模型是否已经分配
            if model in self.model_client_map:
                return self.model_client_map[model]
            
            # 查找空闲客户端
            for client_id, current_model in self.client_model_map.items():
                if current_model is None:
                    logging.info(f"为模型 {model} 分配空闲客户端 {client_id}")
                    # 分配模型
                    self.model_client_map[model] = client_id
                    self.client_model_map[client_id] = model
                    
                    # 确保模型已加载
                    await self._load_model(client_id, model)
                    return client_id
            
            # 如果没有空闲客户端，选择一个替换
            client_id = await self._select_client_to_replace(model)
            return client_id
    
    async def _load_model(self, client_id: int, model: str) -> None:
        """在指定客户端上加载模型
        Args:
            client_id: 客户端ID
            model: 模型名称
        """
        try:
            logging.info(f"在客户端 {client_id} 上加载模型 {model}")
            # 这里可以添加调用Ollama API加载模型的代码
            # 简单示例：发送一个简短的消息来预热模型
            client = self.clients[client_id]
            request = ChatRequest(
                model=model,
                messages=[ChatMessage(role="user", content="Hello")],
                stream=False
            )
            
            async for _ in client.chat(request):
                pass  # 忽略响应内容，只是为了加载模型
                
            logging.info(f"模型 {model} 已成功加载到客户端 {client_id}")
        except Exception as e:
            logging.error(f"加载模型 {model} 到客户端 {client_id} 失败: {e}")
            # 清除映射关系
            if model in self.model_client_map:
                del self.model_client_map[model]
            self.client_model_map[client_id] = None
            raise e
    
    async def _select_client_to_replace(self, model: str) -> int:
        """选择一个客户端替换其当前模型
        使用简单的循环策略
        Args:
            model: 新模型名称
        Returns:
            选中的客户端ID
        """
        client_id = 0  # 默认选择第一个客户端
        
        # 获取当前加载的模型
        old_model = self.client_model_map[client_id]
        logging.info(f"替换客户端 {client_id} 上的模型 {old_model} 为 {model}")
        
        # 如果有旧模型，更新映射
        if old_model and old_model in self.model_client_map:
            del self.model_client_map[old_model]
        
        # 更新新模型的映射
        self.model_client_map[model] = client_id
        self.client_model_map[client_id] = model
        
        # 加载新模型
        await self._load_model(client_id, model)
        return client_id

# 获取可用客户端
async def get_available_client(model: str = None, websocket: WebSocket = None) -> Tuple[OllamaClient, int, asyncio.Semaphore]:
    """
    获取可用的Ollama客户端
    如果指定了WebSocket，在模型加载时会发送加载状态
    """
    global client_pool
    
    # 初始化客户端池
    if client_pool is None:
        logging.info("初始化Ollama客户端池")
        
        # 从配置获取并发请求数
        max_concurrent = API_CONFIG.get("MAX_CONCURRENT_REQUESTS", 4)
        
        # 如果配置不存在，使用合理的默认值
        if not isinstance(max_concurrent, int) or max_concurrent <= 0:
            max_concurrent = os.cpu_count() or 4
            logging.info(f"使用默认并发数: {max_concurrent}")
        else:
            logging.info(f"使用配置的并发数: {max_concurrent}")
        
        # 初始化信号量
        request_semaphore = asyncio.Semaphore(max_concurrent)
        
        # 初始化客户端池
        client_pool = ClientPool(max_concurrent, request_semaphore)
    
    # 如果指定了模型，尝试获取对应的客户端
    if model:
        # 如果有WebSocket连接，发送模型加载状态
        if websocket:
            try:
                await websocket.send_json({
                    "type": "model_loading",
                    "status": ModelLoadingStatus.LOADING,
                    "message": f"正在加载模型 {model}...",
                    "progress": 0,
                    "model": model
                })
            except Exception as e:
                logging.error(f"发送模型加载状态失败: {e}")
        
        try:
            client_id = await client_pool.get_client_for_model(model)
            
            # 如果有WebSocket连接，发送模型加载完成状态
            if websocket:
                try:
                    await websocket.send_json({
                        "type": "model_loading",
                        "status": ModelLoadingStatus.READY,
                        "message": f"模型 {model} 加载完成",
                        "progress": 100,
                        "model": model
                    })
                except Exception as e:
                    logging.error(f"发送模型加载完成状态失败: {e}")
                    
            return client_pool.clients[client_id], client_id, client_pool.semaphore
        except Exception as e:
            logging.error(f"获取模型 {model} 客户端失败: {e}")
            
            # 如果有WebSocket连接，发送模型加载失败状态
            if websocket:
                try:
                    await websocket.send_json({
                        "type": "model_loading",
                        "status": ModelLoadingStatus.ERROR,
                        "message": f"模型 {model} 加载失败: {str(e)}",
                        "model": model
                    })
                except Exception as e:
                    logging.error(f"发送模型加载失败状态失败: {e}")
                    
            raise e
    
    # 如果没有指定模型，返回默认客户端
    client, client_id = client_pool.get_default_client()
    return client, client_id, client_pool.semaphore 