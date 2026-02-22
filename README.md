# 🕵️ BalmAI: Agentic Honeypot for Scam Intelligence

> **Hackathon Submission:** GUVI Agentic AI Track
> **Status:** 🟢 Live Deployment on Render

## 📜 Project Overview
Financial scams (UPI fraud, Phishing, KYC updates) are becoming increasingly adaptive. Traditional blockers just stop the message. **BalmAI** fights back.

This is an **Autonomous AI Agent** that intercepts scam messages, pretends to be a naive victim, engages the attacker in a realistic conversation to waste their time, and secretly **extracts actionable intelligence** (UPI IDs, Phone Numbers, Bank Accounts, Phishing Links) to automate reporting to financial authorities.

---

## 🚀 Key Features

### 1. 🧠 The "Chameleon Engine" (Multi-Persona AI)
The system doesn't just reply; it **roleplays**. It dynamically selects a persona to match the scammer's tactic:
* **👴 "Grandma Amma":** 68-year-old, confused tech user. Misreads OTPs and asks simple questions about font sizes.
* **💼 "Busy Professional":** Impatient, demands quick resolution, asks for official Employee IDs.
* **🏪 "Nervous Shopkeeper":** Anxious, technologically slow, constantly asks for reassurance.

### 2. 🚨 Automated Remediation & Syndicate Mapping (Action Taken)
BalmAI doesn't just collect data; it weaponizes it.
* **Dynamic Bank Mapping:** Automatically parses extracted UPI handles and phishing URLs to identify the targeted institution, queueing alerts for specific bank compliance emails (e.g., `phishing@hdfcbank.com`).
* **1930 Cybercrime Integration:** Prepares payloads for the National Cybercrime Portal.
* **Syndicate Tracking:** Cross-references linguistic footprints and geolocated IP nodes to flag known fraud clusters (e.g., Jamtara, Mewat).

### 3. 🪤 The "Honey-Link" Trap (Active Counter-Measure)
When a scammer demands proof of payment, the Agent sends a **fake screenshot link** (`/proof/payment-screenshot.jpg`).
* **The Trap:** If the scammer clicks this link, the system captures their **Real IP Address** and **Device Fingerprint** to de-anonymize them.

### 4. 📊 Unified Command Center (SPA)
A sleek, real-time dashboard featuring:
* **Dashboard Tab:** High-level metrics, threat detection rates, and historical session logs.
* **Live Chat Console:** Watch the AI engage scammers in real-time alongside a live "Risk Probability" meter and extracted entity feed.
* **Remediation Workflow:** Visualizes the exact data payloads prepared for law enforcement.

---

## 🛠️ Tech Stack

* **Core Engine:** Python 3.11, FastAPI (Async High Performance)
* **AI Model:** Google Gemini 2.0 Flash (Fast, Low Latency execution for <30s auto-grader limits)
* **Intelligence Extraction:** Synchronous LLM Entity Recognition (Strict JSON schema compliance)
* **Deployment:** Render Cloud
* **Frontend:** HTML5, TailwindCSS, Vanilla JS (No build-step required)

---

## ⚡ How It Works (Architecture)

1. **Intercept:** Scammer sends message → `POST /scam-check`.
2. **Detect:** `ai_engine.py` analyzes intent, flags red words, and assigns a confidence score.
3. **Extract:** Synchronously parses the text for `bankAccounts`, `upiIds`, `phishingLinks`, etc., to satisfy the evaluator pipeline.
4. **Engage:** The AI selects a Persona, identifies scammer red flags, asks investigative questions, and generates a context-aware reply.
5. **Report:** Returns the exact 10-point JSON schema demanded by the GUVI Evaluation System (including `engagementDurationSeconds` and `scamDetected`).

---

## 🏃‍♂️ How to Run Locally

1. **Clone the Repo**
   ```bash
   git clone [https://github.com/shaheenrasheed/agentic-honeypot.git](https://github.com/shaheenrasheed/agentic-honeypot.git)
   cd agentic-honeypot

2. Install Dependencies

Bash
pip install -r requirements.txt
Set Environment Variables (Create .env)

Plaintext
GEMINI_API_KEY=your_google_gemini_key
AUTH_TOKEN=secret123

3. Run Server

Bash
uvicorn main:app --reload
Access Command Center: Open http://127.0.0.1:8000 in your browser.

