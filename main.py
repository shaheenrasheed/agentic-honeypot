from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import ScammerInput, AgentResponse
from memory import memory_store
import ai_engine
import config
import time

app = FastAPI(title="Agentic Honeypot V5 - Unified UI")
templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  
    memory_store.update_latency(process_time)
    return response

# --- SERVE SINGLE UNIFIED UI ---
@app.get("/", response_class=HTMLResponse)
async def read_unified_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard/stats")
async def get_stats():
    return memory_store.get_dashboard_stats()

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    return memory_store.get_session(session_id)

@app.get("/proof/payment-screenshot.jpg")
async def honey_trap(request: Request):
    print("🚨 TRAP HIT!")
    return HTMLResponse("<h1>Loading Receipt...</h1>")

async def run_background_process(sid: str, text: str):
    intel = await ai_engine.extract_intelligence(text)
    if intel: memory_store.update_intelligence(sid, intel)

@app.post("/scam-check", response_model=AgentResponse)
async def handle_scam_message(
    data: ScammerInput, 
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    sid = data.sessionId
    incoming_msg = data.message.text
    
    memory_store.log_interaction(sid, "scammer", incoming_msg)
    session = memory_store.get_session(sid)
    
    is_scam_now = session["is_scam"]
    if not is_scam_now:
        detection = await ai_engine.detect_scam(incoming_msg)
        if detection.get("is_scam"):
            memory_store.log_interaction(sid, "system", f"⚠️ THREAT DETECTED: {detection.get('reason')}", True, detection.get("confidence", 0.9))
            is_scam_now = True

    history_text = "\n".join([f"{entry['role']}: {entry['message']}" for entry in session['chat_log'][-5:]])
    agent_reply = await ai_engine.generate_response(history_text, sid, is_scam_now)
    
    memory_store.log_interaction(sid, "agent", agent_reply)
    
    if is_scam_now:
        background_tasks.add_task(run_background_process, sid, incoming_msg)

    return {"status": "success", "reply": agent_reply}