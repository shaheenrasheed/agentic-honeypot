from pydantic import BaseModel
from typing import List, Optional

class MessageContent(BaseModel):
    sender: str
    text: str
    timestamp: int

class RequestMetadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class ScammerInput(BaseModel):
    sessionId: str
    message: MessageContent
    conversationHistory: List[MessageContent] = []
    metadata: Optional[RequestMetadata] = None

class AgentResponse(BaseModel):
    status: str
    reply: str