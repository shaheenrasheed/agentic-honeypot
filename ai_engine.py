import google.generativeai as genai
import json
import hashlib
import config
import os

# Setup Gemini
genai.configure(api_key=config.GEMINI_API_KEY)
# Use 2.0 Flash for speed and intelligence
model = genai.GenerativeModel('gemini-2.0-flash') 

async def detect_scam(message: str):
    """Phase 1: Detect"""
    prompt = f"{config.PROMPT_SCAM_DETECTOR}\n\nMessage: '{message}'"
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"is_scam": False, "confidence": 0.0}

async def generate_agent_response(history_text: str, session_id: str):
    """Phase 2: Engage with Strategy"""
    
    # 1. Pick Persona
    hash_val = int(hashlib.sha256(session_id.encode('utf-8')).hexdigest(), 16)
    selected_persona = config.PERSONA_LIST[hash_val % len(config.PERSONA_LIST)]
    
    # 2. Determine Strategy based on conversation length (approx lines)
    turns = len(history_text.split('\n'))
    current_strategy = "Play dumb and waste time."
    if turns > 4:
        current_strategy = "Ask for their UPI ID or Phone Number to 'verify' them."
    if turns > 8:
        current_strategy = "Pretend payment failed. Ask for their alternative Bank Account."

    # 3. Build Prompt
    full_prompt = f"""
    {config.PROMPT_AGENT_SYSTEM}
    
    CURRENT PERSONA:
    {selected_persona}
    
    CURRENT TACTIC:
    {current_strategy}
    
    CONVERSATION HISTORY:
    {history_text}
    
    YOUR SHORT REPLY:
    """
    
    try:
        response = await model.generate_content_async(full_prompt)
        reply = response.text.strip()
        print(f"🤖 AGENT: {reply}") # Debug log
        return reply
    except Exception as e:
        print(f"❌ Error: {e}")
        return "I am confused. Can you explain that again?"

async def extract_intelligence(text: str):
    """Phase 3: Extract"""
    prompt = f"{config.PROMPT_EXTRACTOR}\n\nAnalyze this text: '{text}'"
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {}