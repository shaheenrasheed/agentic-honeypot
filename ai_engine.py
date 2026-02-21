import google.generativeai as genai
import json
import hashlib
import config
import asyncio

# Setup Gemini
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') 

async def detect_scam(message: str):
    """Phase 1: Detect"""
    prompt = f"{config.PROMPT_SCAM_DETECTOR}\n\nMessage: '{message}'"
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"is_scam": False, "confidence": 0.0, "reason": "Error"}

async def generate_response(history_text: str, session_id: str, is_scam_confirmed: bool):
    """Phase 2: Engage (Dual Mode)"""
    
    # Mode A: SCAM BAITING (The Trap)
    if is_scam_confirmed:
        # Pick Persona based on Session ID
        hash_val = int(hashlib.sha256(session_id.encode('utf-8')).hexdigest(), 16)
        selected_persona = config.PERSONA_LIST[hash_val % len(config.PERSONA_LIST)]
        
        full_prompt = f"""
        {config.PROMPT_AGENT_SYSTEM}
        CURRENT PERSONA: {selected_persona}
        CONVERSATION HISTORY:
        {history_text}
        YOUR SHORT REPLY:
        """
    
    # Mode B: NORMAL CHAT (The Lure)
    else:
        full_prompt = f"""
        {config.PROMPT_NORMAL_CHAT}
        CONVERSATION HISTORY:
        {history_text}
        YOUR SHORT REPLY:
        """

    try:
        response = await model.generate_content_async(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "Sorry, I didn't catch that. Who is this?"

async def extract_intelligence(text: str):
    """Phase 3: Extract (Strict JSON)"""
    prompt = f"{config.PROMPT_EXTRACTOR}\n\nAnalyze this text: '{text}'"
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {}