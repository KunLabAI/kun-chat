from typing import Dict, List, Optional, Union, Any, Sequence, Literal
from pydantic import BaseModel, Field
from datetime import datetime

Role = Literal["system", "user", "assistant"]

class Message(BaseModel):
    role: Role
    content: str
    image: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = Field(default=None, description="List of base64-encoded images")

class Options(BaseModel):
    # 加载时选项
    numa: Optional[bool] = Field(default=None, description="Enable NUMA optimizations")
    num_ctx: Optional[int] = Field(default=None, description="Size of the context window")
    num_batch: Optional[int] = Field(default=None, description="Number of batches to use during generation")
    num_gpu: Optional[int] = Field(default=None, description="Number of layers to send to GPU(s)")
    main_gpu: Optional[int] = Field(default=None, description="Main GPU to use")
    low_vram: Optional[bool] = Field(default=None, description="Enable low VRAM mode")
    f16_kv: Optional[bool] = Field(default=None, description="Use half-precision for key/value cache")
    logits_all: Optional[bool] = Field(default=None, description="Return logits for all tokens")
    vocab_only: Optional[bool] = Field(default=None, description="Only load the vocabulary")
    use_mmap: Optional[bool] = Field(default=None, description="Use memory mapping for the model")
    use_mlock: Optional[bool] = Field(default=None, description="Force the system to keep model in RAM")
    embedding_only: Optional[bool] = Field(default=None, description="Only return embeddings")
    num_thread: Optional[int] = Field(default=None, description="Number of threads to use during computation")

    # 运行时选项
    num_keep: Optional[int] = Field(default=None, description="Number of tokens to keep from initial prompt")
    seed: Optional[int] = Field(default=None, description="Random number seed")
    num_predict: Optional[int] = Field(default=None, description="Maximum number of tokens to predict")
    top_k: Optional[int] = Field(default=None, description="Top K sampling")
    top_p: Optional[float] = Field(default=None, description="Top P sampling")
    tfs_z: Optional[float] = Field(default=None, description="Tail free sampling parameter z")
    typical_p: Optional[float] = Field(default=None, description="Typical P sampling")
    repeat_last_n: Optional[int] = Field(default=None, description="Last N tokens to consider for penalize")
    temperature: Optional[float] = Field(default=None, description="Temperature for sampling")
    repeat_penalty: Optional[float] = Field(default=None, description="Penalize repeat sequence of tokens")
    presence_penalty: Optional[float] = Field(default=None, description="Penalize new tokens based on presence in text")
    frequency_penalty: Optional[float] = Field(default=None, description="Penalize new tokens based on frequency in text")
    mirostat: Optional[int] = Field(default=None, description="Enable Mirostat sampling")
    mirostat_tau: Optional[float] = Field(default=None, description="Mirostat target entropy")
    mirostat_eta: Optional[float] = Field(default=None, description="Mirostat learning rate")
    penalize_newline: Optional[bool] = Field(default=None, description="Penalize newline tokens")
    stop: Optional[List[str]] = Field(default=None, description="Stop sequences to use")

class ModelDetails(BaseModel):
    parent_model: Optional[str] = None
    format: Optional[str] = None
    family: Optional[str] = None
    families: Optional[List[str]] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None

class ModelInfo(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str
    details: Optional[ModelDetails] = None
    options: Optional[Options] = None

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = True
    options: Optional[Options] = None

class ChatResponse(BaseModel):
    model: str
    message: Optional[ChatMessage] = None
    done: bool = False
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_duration: Optional[int] = None
    prompt_tokens: Optional[int] = None
    eval_tokens: Optional[int] = None

class EmbeddingRequest(BaseModel):
    model: str
    prompt: str
    options: Optional[Options] = None

class EmbeddingResponse(BaseModel):
    embedding: List[float]

class ModelList(BaseModel):
    models: List[ModelInfo]

class ModelPullRequest(BaseModel):
    name: str
    insecure: bool = False
    stream: bool = True

class ModelPullResponse(BaseModel):
    status: str
    digest: Optional[str] = None
    total: Optional[int] = None
    completed: Optional[int] = None

class ModelPullStatus(BaseModel):
    """
    模型下载状态
    """
    name: str = Field(..., description="模型名称")
    status: Literal["downloading", "completed", "failed", "cancelled"] = Field(..., description="下载状态")
    progress: float = Field(..., description="下载进度（百分比）")
    total_size: Optional[int] = Field(default=None, description="总大小（字节）")
    downloaded_size: Optional[int] = Field(default=None, description="已下载大小（字节）")
    error: Optional[str] = Field(default=None, description="错误信息")
    details: List[Dict[str, Any]] = Field(default_factory=list, description="详细信息")

    model_config = {
        'protected_namespaces': ()
    }
    
class ModelDeleteRequest(BaseModel):
    """
    删除模型的请求
    """
    name: str = Field(..., description="要删除的模型名称")

class ModelCopyRequest(BaseModel):
    source: str
    destination: str

class ModelCreateRequest(BaseModel):
    name: str
    path: str
    modelfile: Optional[str] = None
    quantize: Optional[str] = None

class ModelCreateResponse(BaseModel):
    status: str
