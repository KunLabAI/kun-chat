from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ModelDisplayNameUpdate(BaseModel):
    """更新模型显示名称的请求"""
    display_name: str = Field(..., description="新的显示名称")

class ModelFavoriteResponse(BaseModel):
    """收藏模型的响应"""
    is_favorited: bool = Field(..., description="是否已收藏")
    message: str = Field(..., description="操作结果消息")

class ModelConfigUpdate(BaseModel):
    """更新模型配置的请求"""
    config_type: str = Field(..., description="配置类型: basic, runtime, generation, system")
    config_key: str = Field(..., description="配置键")
    config_value: str = Field(..., description="配置值")

class ModelResponse(BaseModel):
    """模型信息响应"""
    id: int
    name: str
    display_name: Optional[str] = None
    family: Optional[str] = None
    parameter_size: Optional[str] = None
    quantization: Optional[str] = None
    format: Optional[str] = None
    modified_at: Optional[datetime] = None
    size: Optional[int] = None
    digest: Optional[str] = None
    is_custom: bool = False
    pull_time: Optional[datetime] = None
    status: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    is_favorited: Optional[bool] = None
    advanced_parameters: Optional[Dict[str, Any]] = None  # 添加高级参数字段

class AdvancedModelOptions(BaseModel):
    """高级模型选项"""
    template: Optional[str] = None
    system: Optional[str] = None
    adapter: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None

class CustomModelRequest(BaseModel):
    """扩展的自定义模型请求"""
    name: str = Field(..., description="模型名称")
    modelfile: str = Field(..., description="Modelfile内容")
    options: Optional[AdvancedModelOptions] = Field(None, description="可选的模型参数")

class CustomModelResponse(BaseModel):
    """自定义模型响应"""
    status: str
    message: Optional[str] = None

class ImportModelRequest(BaseModel):
    """导入模型请求"""
    name: str = Field(..., description="模型名称")
    file_path: str = Field(..., description="模型文件路径（必须是绝对路径，支持 .gguf 和 .safetensors 格式）")

class ImportModelResponse(BaseModel):
    """导入模型响应"""
    status: str = Field(..., description="状态：success, error")
    progress: int = Field(..., description="进度：0-100")
    message: Optional[str] = Field(None, description="状态消息或错误信息")
