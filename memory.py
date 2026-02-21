import time
from datetime import datetime

class ConversationManager:
    def __init__(self):
        self.sessions = {}
        self.latencies = [] 

    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "start_time": time.time(),
                "last_active": datetime.now().strftime("%H:%M:%S"),
                "is_scam": False,
                "confidence_level": 0.0,
                "threat_level": 0, 
                "msg_count": 0,
                "agent_notes": "Monitoring...",
                "chat_log": [],
                "intelligence": {
                    "bankAccounts": [], "upiIds": [], "phishingLinks": [],
                    "phoneNumbers": [], "emailAddresses": [], "scamType": "unknown"
                }
            }
        return self.sessions[session_id]

    def log_interaction(self, session_id: str, sender: str, text: str, is_scam_flag: bool = False, confidence: float = 0.0, scam_type: str = "unknown"):
        session = self.get_session(session_id)
        session["msg_count"] += 1
        session["last_active"] = datetime.now().strftime("%H:%M:%S")
        
        if is_scam_flag:
            session["is_scam"] = True
            session["confidence_level"] = confidence
            session["threat_level"] = int(confidence * 100) if confidence > 0 else 85
            if scam_type != "unknown":
                session["intelligence"]["scamType"] = scam_type

        session["chat_log"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "role": sender,
            "message": text
        })

    def update_intelligence(self, session_id: str, new_data: dict):
        session = self.get_session(session_id)
        current = session["intelligence"]
        
        intel_found = False
        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "emailAddresses"]:
            if key in new_data and new_data[key]:
                current[key] = list(set(current[key] + new_data[key]))
                intel_found = True

        if intel_found:
            session["threat_level"] = min(99, session["threat_level"] + 10) 

    def update_latency(self, ms: float):
        self.latencies.append(ms)
        if len(self.latencies) > 50: self.latencies.pop(0)

    def get_dashboard_stats(self):
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        total_scams = sum(1 for s in self.sessions.values() if s["is_scam"])
        total_messages = sum(s["msg_count"] for s in self.sessions.values())
        
        total_bank = sum(len(s["intelligence"]["bankAccounts"]) for s in self.sessions.values())
        total_upi = sum(len(s["intelligence"]["upiIds"]) for s in self.sessions.values())
        total_links = sum(len(s["intelligence"]["phishingLinks"]) for s in self.sessions.values())
        total_phones = sum(len(s["intelligence"]["phoneNumbers"]) for s in self.sessions.values())

        active_sessions = []
        for sid, s in self.sessions.items():
            active_sessions.append({
                "id": sid,
                "is_scam": s["is_scam"],
                "last_active": s["last_active"],
                "msg_count": s["msg_count"],
                "threat_level": s["threat_level"],
                "scam_type": s["intelligence"]["scamType"]
            })

        active_sessions.sort(key=lambda x: x["last_active"], reverse=True)

        return {
            "summary": {
                "total_messages": total_messages,
                "scams_detected": total_scams,
                "avg_latency_ms": round(avg_latency, 2), 
                "total_bank": total_bank,
                "total_upi": total_upi,
                "total_links": total_links,
                "total_phones": total_phones
            },
            "recent_sessions": active_sessions
        }

memory_store = ConversationManager()