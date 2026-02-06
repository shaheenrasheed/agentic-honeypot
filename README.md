# 🕵️ Agentic Honeypot: AI-Powered Scam Intelligence System

> **Hackathon Submission:** Agentic AI Track
> **Status:** 🟢 Live Deployment

## 📜 Project Overview
Financial scams (UPI fraud, Phishing, KYC updates) are becoming increasingly adaptive. Traditional blockers just stop the message. **Agentic Honeypot** fights back.

This is an **Autonomous AI Agent** that intercepts scam messages, pretends to be a naive victim, engages the attacker in a realistic conversation to waste their time, and secretly **extracts actionable intelligence** (UPI IDs, Phone Numbers, Bank Accounts) to report to authorities.

---

## 🚀 Key Features

### 1. 🧠 The "Chameleon Engine" (Multi-Persona AI)
The system doesn't just reply; it **roleplays**. It dynamically selects a persona to match the scammer's tactic:
* **👴 "Grandma Amma":** 65-year-old, confused tech user. Misreads OTPs and asks simple questions.
* **💼 "Busy Professional":** Impatient, demands quick resolution, asks for UPI ID repeatedly.
* **👩‍💻 "Skeptical User":** Asks for "Employee IDs" and "Official Links" to verify the scammer.

### 2. 🪤 The "Honey-Link" Trap (Active Counter-Measure)
When a scammer demands proof of payment, the Agent sends a **fake screenshot link** (`/proof/payment-screenshot.jpg`).
* **The Trap:** If the scammer clicks this link, the system captures their **Real IP Address** and **Device Fingerprint**.
* **The Result:** We de-anonymize the attacker.

### 3. 🛡️ "Active Defense" Strategy
* **Never Refuse:** The bot never says "No". It says "Yes, but..." (stalling).
* **Disinformation:** It feeds **fake OTPs** and **fake Account Numbers** that look real but fail validation, frustrating the attacker.

### 4. 📊 Real-Time Command Center
A live dashboard that visualizes:
* Active conversations in real-time.
* Extracted Intelligence (Bank Accounts, UPIs).
* Threat Maps.

---

## 🛠️ Tech Stack

* **Core Engine:** Python 3.11, FastAPI (Async High Performance)
* **AI Model:** Google Gemini 2.0 Flash (Fast, Low Latency)
* **Intelligence Extraction:** Custom Regex + LLM Entity Recognition
* **Deployment:** Render Cloud (Auto-Scaling)
* **Frontend:** HTML5/TailwindCSS (Real-time Dashboard)

---

## ⚡ How It Works (Architecture)

1.  **Intercept:** Scammer sends SMS/WhatsApp → API Endpoint.
2.  **Detect:** `ai_engine.py` analyzes intent. If `is_scam == True`, the Honeypot activates.
3.  **Engage:** The AI selects a Persona and generates a context-aware reply.
4.  **Extract:** Background workers parse every message for `UPI IDs`, `URLs`, and `Phone Numbers`.
5.  **Report:** Final Intelligence is JSON-formatted and sent to the Central Evaluation Server.

---

## 📸 Screenshots

### **1. The Live Command Center**
*Real-time monitoring of all active scam attempts.*


### **2. The Simulator UI**
*A testing tool to simulate attacks and verify agent responses.*


---

## 🏃‍♂️ How to Run Locally

1.  **Clone the Repo**
    ```bash
    git clone [https://github.com/shaheenrasheed/agentic-honeypot.git](https://github.com/shaheenrasheed/agentic-honeypot.git)
    cd agentic-honeypot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Environment Variables** (Create `.env`)
    ```text
    GEMINI_API_KEY=your_google_key
    AUTH_TOKEN=secret123
    ```

4.  **Run Server**
    ```bash
    uvicorn main:app --reload
    ```

5.  **Access Dashboard:** `http://127.0.0.1:8000`

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/scam-check` | Main entry point for incoming messages. |
| `GET` | `/dashboard/stats` | JSON stats for the frontend. |
| `GET` | `/tester` | Interactive Simulator UI. |
| `GET` | `/proof/payment-screenshot.jpg` | **Honey Trap** link to catch IP addresses. |

---

**Built with ❤️ for a Safer Digital World.**