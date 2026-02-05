from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import ScammerInput, AgentResponse
from memory import memory_store
import ai_engine
import config
import requests
import json
import os

app = FastAPI(title="Agentic Honeypot V3 - Production")
templates = Jinja2Templates(directory="templates")

# ==========================================
# 1. FRONTEND ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/tester", response_class=HTMLResponse)
async def tester_ui(request: Request):
    return templates.TemplateResponse("tester.html", {"request": request})

@app.get("/dashboard/stats")
async def get_stats():
    return memory_store.get_dashboard_stats()

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    if session_id in memory_store.sessions:
        return memory_store.get_session(session_id)
    return {"error": "Session not found"}

# ==========================================
# 2. THE HONEY TRAP (Fixed IP Logic)
# ==========================================

@app.get("/proof/payment-screenshot.jpg")
async def honey_trap(request: Request):
    # FIX: Ngrok/Render puts the real IP in the 'x-forwarded-for' header
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Get the first IP in the list (the real client)
        scammer_ip = forwarded_for.split(",")[0]
    else:
        # Fallback for local testing
        scammer_ip = request.client.host
        
    user_agent = request.headers.get('user-agent')
    
    print(f"🚨 TRAP TRIGGERED! IP: {scammer_ip} | Device: {user_agent}")
    
    memory_store.global_logs.append({
        "id": "TRAP_HIT",
        "timestamp": "JUST NOW",
        "role": "system",
        "message": f"🚨 SCAMMER CAUGHT! IP: {scammer_ip}",
        "is_scam": True
    })

    return HTMLResponse(content="<h1>Transaction Pending...</h1><p>Bank server is slow. Please wait 2 minutes.</p>")

# ==========================================
# 3. BACKGROUND TASKS
# ==========================================

def send_guvi_callback(session_id: str):
    session = memory_store.get_session(session_id)
    if not session["is_scam"]: return

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session["msg_count"],
        "extractedIntelligence": session["intelligence"],
        "agentNotes": session["agent_notes"]
    }
    try:
        requests.post(config.GUVI_CALLBACK_URL, json=payload, timeout=5)
    except: pass

async def run_background_process(sid: str, text: str):
    intel = await ai_engine.extract_intelligence(text)
    if intel: memory_store.update_intelligence(sid, intel)
    send_guvi_callback(sid)

# ==========================================
# 4. MAIN API ENDPOINT
# ==========================================

@app.post("/scam-check", response_model=AgentResponse)
async def handle_scam_message(
    data: ScammerInput, 
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    if x_api_key != config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    sid = data.sessionId
    incoming_msg = data.message.text
    
    memory_store.log_interaction(sid, "scammer", incoming_msg)
    
    session = memory_store.get_session(sid)
    is_scam = session["is_scam"]
    
    if not is_scam:
        detection = await ai_engine.detect_scam(incoming_msg)
        if detection.get("is_scam"):
            memory_store.log_interaction(sid, "system", "SCAM DETECTED", is_scam_flag=True)
            is_scam = True

    agent_reply = "..."
    if is_scam:
        history_text = ""
        for msg in data.conversationHistory:
            history_text += f"{msg.sender}: {msg.text}\n"
        history_text += f"scammer: {incoming_msg}\n"
        
        agent_reply = await ai_engine.generate_agent_response(history_text, sid)
        memory_store.log_interaction(sid, "agent", agent_reply)
        background_tasks.add_task(run_background_process, sid, incoming_msg)
    else:
        agent_reply = "I am sorry, I do not understand."

    return {
        "status": "success",
        "reply": agent_reply
    }