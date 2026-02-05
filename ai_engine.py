import google.generativeai as genai
import json
import hashlib
import config
import os

# Setup Gemini
# Default to empty string if key is missing during build
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') 

async def detect_scam(message: str):
    prompt = f"{config.PROMPT_SCAM_DETECTOR}\n\nMessage: '{message}'"
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        print(f"🔍 DEBUG: Scam Detection: {text}") 
        return json.loads(text)
    except Exception as e:
        print(f"❌ ERROR in Scam Detection: {e}")
        return {"is_scam": False, "confidence": 0.0}

async def generate_agent_response(history_text: str, session_id: str):
    hash_val = int(hashlib.sha256(session_id.encode('utf-8')).hexdigest(), 16)
    selected_persona = config.PERSONA_LIST[hash_val % len(config.PERSONA_LIST)]
    
    prompt = f"{config.PROMPT_AGENT_PERSONA}\n\nCURRENT PERSONA:\n{selected_persona}\n\nCONVERSATION HISTORY:\n{history_text}\n\nYOUR REPLY:"
    
    try:
        response = await model.generate_content_async(prompt)
        print(f"🔍 DEBUG: Agent ({selected_persona[:15]}...) Reply: {response.text.strip()}")
        return response.text.strip()
    except Exception as e:
        print(f"❌ ERROR in Agent Gen: {e}")
        return "I am checking, please wait one minute."

async def extract_intelligence(text: str):
    prompt = f"{config.PROMPT_EXTRACTOR}\n\nAnalyze this text: '{text}'"
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {}