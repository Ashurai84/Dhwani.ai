from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionStartRequest(BaseModel):
    channel: str

class InteractionStartResponse(BaseModel):
    session_id: str

class InteractionAudioRequest(BaseModel):
    session_id: str
    audio_file: str
    language: Optional[str] = "hi-IN"

class InteractionTextRequest(BaseModel):
    session_id: str
    text: str
    language: Optional[str] = "hi-IN"

class InteractionAudioResponse(BaseModel):
    transcription: str
    intent: str
    ai_response: str
    base_64_audio_response: str

class InteractionEndRequest(BaseModel):
    session_id: str

class InteractionEndResponse(BaseModel):
    report_id: str

class ReportResponse(BaseModel):
    interaction_id: str
    session_id: str
    intent: Optional[str]
    channel: str
    timestamp: datetime
    summary: str
    recommended_action: str
    confidence_score: float
    requires_human_review: bool

