import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional, Union, Any
import aiohttp
from .types import (
    ModelInfo, ChatMessage, ChatRequest, ChatResponse,
    EmbeddingRequest, EmbeddingResponse,
    ModelList, ModelPullRequest, ModelPullResponse,
    ModelDeleteRequest, ModelCopyRequest,
    ModelCreateRequest, ModelCreateResponse,
    Options
)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            # 设置较长的超时时间，防止长时间下载过程中断开
            timeout = aiohttp.ClientTimeout(
                total=None,  # 禁用总超时
                connect=60.0,  # 连接超时为60秒
                sock_connect=60.0,  # 套接字连接超时为60秒
                sock_read=1800.0  # 套接字读取超时为30分钟
            )
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[Dict, AsyncGenerator[Dict, None]]:
        session = await self._ensure_session()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with session.request(method, url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"HTTP {response.status}: {error_text}"
                    )
                
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                yield json.loads(line.decode())
                            except json.JSONDecodeError as e:
                                raise aiohttp.ClientResponseError(
                                    response.request_info,
                                    response.history,
                                    status=response.status,
                                    message=f"Invalid JSON response: {line.decode()}"
                                )
                else:
                    # 删除操作不需要返回 JSON
                    if method == "DELETE":
                        yield {}
                    else:
                        try:
                            yield await response.json()
                        except json.JSONDecodeError as e:
                            text = await response.text()
                            raise aiohttp.ClientResponseError(
                                response.request_info,
                                response.history,
                                status=response.status,
                                message=f"Invalid JSON response: {text}"
                            )
        except aiohttp.ClientError as e:
            raise aiohttp.ClientResponseError(
                None,
                None,
                status=getattr(e, 'status', 500),
                message=f"Request failed: {str(e)}"
            )

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # 聊天对话
    async def chat(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        async for response in self._request("POST", "api/chat", request.dict(), stream=request.stream):
            yield ChatResponse(**response)

    # 生成嵌入向量
    async def embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        async for response in self._request("POST", "api/embeddings", request.dict(), stream=False):
            return EmbeddingResponse(**response)
        
    async def show_model(self, name: str, verbose: bool = False) -> Dict[str, Any]:
        async for response in self._request("POST", "api/show", {
            "name": name,
            "verbose": verbose
        }, stream=False):
            return response

    # 获取模型列表
    async def list_models(self) -> ModelList:
        async for response in self._request("GET", "api/tags", stream=False):
            return ModelList(**response)

    # 拉取模型
    async def pull_model(self, request: ModelPullRequest) -> AsyncGenerator[ModelPullResponse, None]:
        async for response in self._request("POST", "api/pull", {"name": request.name}, stream=True):
            yield ModelPullResponse(**response)

    # 删除模型
    async def delete_model(self, request: ModelDeleteRequest) -> None:
        async for _ in self._request("DELETE", "api/delete", {"name": request.name}, stream=False):
            return

    # 复制模型
    async def copy_model(self, request: ModelCopyRequest) -> None:
        async for _ in self._request("POST", "api/copy", request.dict(), stream=False):
            return

    # 创建模型
    async def create_model(self, request: ModelCreateRequest) -> ModelCreateResponse:
        async for response in self._request("POST", "api/create", request.dict(), stream=True):
            # 创建模型的响应是流式的，我们只需要最后一个响应
            continue
        # 如果没有错误发生，说明创建成功
        return ModelCreateResponse(status="success")

    # 简化的聊天方法
    async def chat_simple(
        self,
        model: str,
        content: str,
        system: Optional[str] = None,
        stream: bool = True,
        options: Optional[Options] = None
    ) -> AsyncGenerator[str, None]:
        messages = []
        if system:
            messages.append(ChatMessage(role="system", content=system))
        messages.append(ChatMessage(role="user", content=content))
        
        request = ChatRequest(
            model=model,
            messages=messages,
            stream=stream,
            options=options
        )
        
        async for response in self.chat(request):
            if response.message:
                yield response.message.content
