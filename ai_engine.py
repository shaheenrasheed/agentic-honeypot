import google.generativeai as genai
import json
import hashlib
import logging
import config

# Setup Robust Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') 

async def detect_scam(message: str) -> dict:
    """Analyzes message intent using strict JSON output formatting."""
    prompt = f"{config.PROMPT_SCAM_DETECTOR}\n\nMessage: '{message}'\n\nReturn ONLY a valid JSON object matching this schema: {{'is_scam': boolean, 'confidence': float, 'reason': 'string', 'scam_type': 'bank_fraud | upi_fraud | phishing | unknown'}}"
    
    try:
        # Force JSON response type to prevent parsing failures
        response = await model.generate_content_async(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Scam Detection Engine Error: {str(e)}")
        # Graceful fallback instead of crashing
        return {"is_scam": False, "confidence": 0.0, "reason": "System error during analysis", "scam_type": "unknown"}

async def generate_response(history_text: str, session_id: str, is_scam_confirmed: bool) -> str:
    """Generates context-aware, psychological responses to deepen engagement."""
    if is_scam_confirmed:
        hash_val = int(hashlib.sha256(session_id.encode('utf-8')).hexdigest(), 16)
        selected_persona = config.PERSONA_LIST[hash_val % len(config.PERSONA_LIST)]
        full_prompt = f"{config.PROMPT_AGENT_SYSTEM}\n\nCURRENT PERSONA: {selected_persona}\nCONVERSATION HISTORY:\n{history_text}\nYOUR REPLY:"
    else:
        full_prompt = f"{config.PROMPT_NORMAL_CHAT}\n\nCONVERSATION HISTORY:\n{history_text}\nYOUR REPLY:"

    try:
        response = await model.generate_content_async(full_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Response Generation Error: {str(e)}")
        return "I'm having trouble understanding. Can you explain?"

async def extract_intelligence(text: str) -> dict:
    """Extracts entities aggressively using JSON mode."""
    prompt = f"{config.PROMPT_EXTRACTOR}\n\nText: '{text}'\n\nReturn ONLY a valid JSON object matching this schema: {{'bankAccounts': [], 'upiIds': [], 'phishingLinks': [], 'phoneNumbers': [], 'emailAddresses': []}}"
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Intelligence Extraction Error: {str(e)}")
        return {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "emailAddresses": []}