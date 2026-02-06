import time
from datetime import datetime

class ConversationManager:
    def __init__(self):
        self.sessions = {}
        # We keep a global log for the "Recent Activity" ticker
        self.global_activity = [] 

    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "start_time": time.time(),
                "last_active": datetime.now().strftime("%H:%M:%S"),
                "is_scam": False,
                "msg_count": 0,
                "agent_notes": "Monitoring...",
                "chat_log": [], # Stores full history for this specific scammer
                "intelligence": {
                    "bankAccounts": [], "upiIds": [], "phishingLinks": [], 
                    "phoneNumbers": [], "suspiciousKeywords": []
                }
            }
        return self.sessions[session_id]

    def log_interaction(self, session_id: str, sender: str, text: str, is_scam_flag: bool = False):
        session = self.get_session(session_id)
        session["msg_count"] += 1
        session["last_active"] = datetime.now().strftime("%H:%M:%S")
        
        if is_scam_flag:
            session["is_scam"] = True

        # Log to specific session history
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "role": sender,
            "message": text
        }
        session["chat_log"].append(entry)

        # Log to global ticker (for the sidebar pulse)
        self.global_activity.append({
            "id": session_id,
            "desc": f"{sender.upper()}: {text[:30]}..."
        })
        if len(self.global_activity) > 20:
            self.global_activity.pop(0)

    def update_intelligence(self, session_id: str, new_data: dict):
        session = self.get_session(session_id)
        current = session["intelligence"]
        for key in current.keys():
            if key in new_data:
                current[key] = list(set(current[key] + new_data[key]))
        
        if new_data.get("suspiciousKeywords"):
            keywords = ', '.join(new_data['suspiciousKeywords'][:3])
            session["agent_notes"] = f"THREAT: {keywords}. STRATEGY: Active stalling."

    def get_dashboard_stats(self):
        # Summarize all sessions for the dashboard
        active_sessions = []
        for sid, s in self.sessions.items():
            active_sessions.append({
                "id": sid,
                "is_scam": s["is_scam"],
                "last_active": s["last_active"],
                "msg_count": s["msg_count"]
            })

        # Calculate totals
        total_scams = sum(1 for s in self.sessions.values() if s["is_scam"])
        total_intel = sum(len(v) for s in self.sessions.values() for v in s["intelligence"].values())

        return {
            "summary": {
                "total_sessions": len(self.sessions),
                "scams_detected": total_scams,
                "total_intel": total_intel
            },
            "active_sessions": active_sessions, # List for Sidebar
            "recent_activity": self.global_activity # Ticker
        }

memory_store = ConversationManager()