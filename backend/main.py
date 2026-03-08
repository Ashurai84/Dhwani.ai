import os
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

import models
import schemas
import ai_service
from database import SessionLocal, engine, get_db, Base
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Banking Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_voice_test():
    return FileResponse("voice_test.html")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


@app.post("/interaction/start", response_model=schemas.InteractionStartResponse)
def start_interaction(req: schemas.InteractionStartRequest, db: Session = Depends(get_db)):
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    db_session = models.Session(session_id=session_id, channel=req.channel)
    db.add(db_session)
    db.commit()
    
    return schemas.InteractionStartResponse(session_id=session_id)


@app.post("/interaction/audio", response_model=schemas.InteractionAudioResponse)
async def process_audio(req: schemas.InteractionAudioRequest, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.session_id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    language = req.language or 'hi-IN'
    pipeline_result = await ai_service.process_audio_pipeline(req.audio_file, language)
    
    user_conv = models.Conversation(
        session_id=req.session_id,
        speaker="user",
        message=pipeline_result["raw_transcript"]
    )
    ai_conv = models.Conversation(
        session_id=req.session_id,
        speaker="ai",
        message=pipeline_result["ai_response"]
    )
    db.add(user_conv)
    db.add(ai_conv)
    db.commit()
    
    await manager.broadcast({
        "type": "conversation_update",
        "session_id": req.session_id,
        "transcript": pipeline_result["clean_transcript"],
        "ai_response": pipeline_result["ai_response"],
        "intent": pipeline_result["intent"],
        "confidence": pipeline_result["confidence"],
        "latency_ms": pipeline_result["routing_latency_ms"]
    })

    return schemas.InteractionAudioResponse(
        transcription=pipeline_result["clean_transcript"],
        intent=pipeline_result["intent"],
        ai_response=pipeline_result["ai_response"],
        base_64_audio_response=pipeline_result["base_64_audio_response"]
    )


@app.post("/interaction/text", response_model=schemas.InteractionAudioResponse)
async def process_text(req: schemas.InteractionTextRequest, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.session_id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pipeline_result = await ai_service.process_text_pipeline(req.text, req.language or 'hi-IN')
    
    user_conv = models.Conversation(session_id=req.session_id, speaker="user", message=req.text)
    ai_conv = models.Conversation(session_id=req.session_id, speaker="ai", message=pipeline_result["ai_response"])
    db.add(user_conv)
    db.add(ai_conv)
    db.commit()
    
    await manager.broadcast({
        "type": "conversation_update",
        "session_id": req.session_id,
        "transcript": req.text,
        "ai_response": pipeline_result["ai_response"],
        "intent": pipeline_result["intent"],
        "confidence": pipeline_result["confidence"],
        "latency_ms": pipeline_result["routing_latency_ms"]
    })
    
    return schemas.InteractionAudioResponse(
        transcription=req.text,
        intent=pipeline_result["intent"],
        ai_response=pipeline_result["ai_response"],
        base_64_audio_response=pipeline_result["base_64_audio_response"]
    )


@app.post("/interaction/end", response_model=schemas.InteractionEndResponse)
async def end_interaction(req: schemas.InteractionEndRequest, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.session_id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "completed"
    session.end_time = datetime.utcnow()
    
    conversations = db.query(models.Conversation).filter(
        models.Conversation.session_id == req.session_id
    ).order_by(models.Conversation.timestamp).all()
    
    full_transcript = "\n".join([f"{c.speaker}: {c.message}" for c in conversations])
    summary_data = await ai_service.generate_final_summary(full_transcript)
    
    report_id = f"REP_{uuid.uuid4().hex[:8]}"
    
    report = models.Report(
        report_id=report_id,
        session_id=req.session_id,
        intent=summary_data.get("intent", "unknown"),
        summary=summary_data.get("summary", "Summary unavailable."),
        recommended_action=summary_data.get("recommended_action", "Review needed."),
        confidence_score=0.9,
        requires_human_review=False
    )
    db.add(report)
    db.commit()
    
    await manager.broadcast({
        "type": "session_ended",
        "session_id": req.session_id,
        "report_id": report_id
    })
    
    return schemas.InteractionEndResponse(report_id=report_id)


@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(models.Report).all()
    return [{
        "interaction_id": r.report_id,
        "session_id": r.session_id,
        "intent": r.intent,
        "channel": r.session.channel if r.session else None,
        "timestamp": r.timestamp,
        "summary": r.summary,
        "recommended_action": r.recommended_action,
        "confidence_score": r.confidence_score,
        "requires_human_review": r.requires_human_review
    } for r in reports]


@app.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.Session).all()
    return [{
        "session_id": s.session_id,
        "channel": s.channel,
        "status": s.status,
        "start_time": s.start_time,
        "conversation_count": len(s.conversations)
    } for s in sessions]


@app.get("/conversations/{session_id}")
def get_conversations(session_id: str, db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).filter(
        models.Conversation.session_id == session_id
    ).order_by(models.Conversation.timestamp).all()
    return [{
        "speaker": c.speaker,
        "message": c.message,
        "timestamp": c.timestamp
    } for c in conversations]


@app.get("/report/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    conversations = db.query(models.Conversation).filter(
        models.Conversation.session_id == report.session_id
    ).order_by(models.Conversation.timestamp).all()
    
    return {
        "report": {
            "interaction_id": report.report_id,
            "session_id": report.session_id,
            "intent": report.intent,
            "summary": report.summary,
            "recommended_action": report.recommended_action,
            "confidence_score": report.confidence_score,
            "requires_human_review": report.requires_human_review,
            "timestamp": report.timestamp
        },
        "conversations": [{
            "speaker": c.speaker,
            "message": c.message,
            "timestamp": c.timestamp
        } for c in conversations]
    }


@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
