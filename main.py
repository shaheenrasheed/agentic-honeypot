from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import ScammerInput, AgentResponse
from memory import memory_store
import ai_engine
import config
import requests
import json

app = FastAPI(title="Agentic Honeypot V3 - Complete System")
templates = Jinja2Templates(directory="templates")

# ==========================================
# 1. FRONTEND ROUTES (Dashboard & Tester)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    """The Mission Control Dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/tester", response_class=HTMLResponse)
async def tester_ui(request: Request):
    """The Scam Simulator UI"""
    return templates.TemplateResponse("tester.html", {"request": request})

@app.get("/dashboard/stats")
async def get_stats():
    """API for the Dashboard to fetch live stats"""
    return memory_store.get_dashboard_stats()

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    """API for the Tester UI to show Guvi-style JSON"""
    if session_id in memory_store.sessions:
        return memory_store.get_session(session_id)
    return {"error": "Session not found"}

# ==========================================
# 2. THE HONEY TRAP (Unique Feature)
# ==========================================

@app.get("/proof/payment-screenshot.jpg")
async def honey_trap(request: Request):
    """
    Catches scammers who click the fake proof link.
    Logs their IP and User Agent.
    """
    scammer_ip = request.client.host
    user_agent = request.headers.get('user-agent')
    
    print(f"🚨 TRAP TRIGGERED! IP: {scammer_ip} | Device: {user_agent}")
    
    # Log this victory to the dashboard
    memory_store.global_logs.append({
        "id": "TRAP_HIT",
        "timestamp": "JUST NOW",
        "role": "system",
        "message": f"🚨 SCAMMER CAUGHT! IP: {scammer_ip}",
        "is_scam": True
    })

    # Return a fake error so they don't get suspicious
    return HTMLResponse(content="<h1>Transaction Pending...</h1><p>Bank server is slow. Please wait 2 minutes.</p>")

# ==========================================
# 3. BACKGROUND TASKS (Reporting)
# ==========================================

def send_guvi_callback(session_id: str):
    """Sends the mandatory evaluation report to GUVI"""
    session = memory_store.get_session(session_id)
    
    # Only send if we have actually engaged or found something
    if not session["is_scam"]:
        return

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session["msg_count"],
        "extractedIntelligence": session["intelligence"],
        "agentNotes": session["agent_notes"]
    }

    try:
        # We ignore SSL errors for hackathon environments sometimes
        # Timeout set to 5s so it doesn't hang our server
        requests.post(config.GUVI_CALLBACK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Callback Error (Expected if Guvi offline): {e}")

async def run_background_process(sid: str, text: str):
    """Runs extraction and reporting without slowing down the API response"""
    # 1. Extract Intel from text
    intel = await ai_engine.extract_intelligence(text)
    if intel:
        memory_store.update_intelligence(sid, intel)
    
    # 2. Report to Judges
    send_guvi_callback(sid)

# ==========================================
# 4. MAIN API ENDPOINT (The Core)
# ==========================================

@app.post("/scam-check", response_model=AgentResponse)
async def handle_scam_message(
    data: ScammerInput, 
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    # 1. Security Check
    if x_api_key != config.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    sid = data.sessionId
    incoming_msg = data.message.text
    
    # 2. Log User Message to Memory
    memory_store.log_interaction(sid, "scammer", incoming_msg)
    
    # 3. Check Session State
    session = memory_store.get_session(sid)
    is_scam = session["is_scam"]
    
    # 4. Detect Scam (If not already marked)
    if not is_scam:
        detection = await ai_engine.detect_scam(incoming_msg)
        if detection.get("is_scam"):
            memory_store.log_interaction(sid, "system", "SCAM DETECTED", is_scam_flag=True)
            is_scam = True

    # 5. Generate Response
    agent_reply = "..."
    if is_scam:
        # Construct History for AI Context
        history_text = ""
        for msg in data.conversationHistory:
            history_text += f"{msg.sender}: {msg.text}\n"
        history_text += f"scammer: {incoming_msg}\n"

        # Generate Reply (Pass SID for Persona Consistency)
        agent_reply = await ai_engine.generate_agent_response(history_text, sid)
        memory_store.log_interaction(sid, "agent", agent_reply)

        # Trigger Background Tasks (Extraction + Reporting)
        background_tasks.add_task(run_background_process, sid, incoming_msg)
    else:
        # Neutral response if no scam detected yet
        agent_reply = "I am sorry, I do not understand what you mean."

    # 6. Return Standard JSON
    return {
        "status": "success",
        "reply": agent_reply
    }