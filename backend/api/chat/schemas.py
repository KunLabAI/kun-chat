from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str
    timestamp: str
    images: Optional[List[str]] = None
    web_search: Optional[bool] = False

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    stream: bool = False
    web_search: Optional[bool] = False

class ConversationCreate(BaseModel):
    title: str = "New Conversation"
    model: Optional[str] = None

class ConversationUpdate(BaseModel):
    messages: List[Message]
    model: Optional[str] = None

class ModelUpdate(BaseModel):
    model: str
    
    model_config = {
        'protected_namespaces': ()
    }
