from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MessageContent(BaseModel):
    sender: str
    text: str
    # Accommodate both string and int timestamps just in case the evaluator sends either
    timestamp: Any 

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
    # GUVI Mandatory Grading Fields
    sessionId: str
    scamDetected: bool
    extractedIntelligence: Dict[str, List[str]]
    totalMessagesExchanged: int
    engagementDurationSeconds: int
    agentNotes: str
    scamType: str
    confidenceLevel: float