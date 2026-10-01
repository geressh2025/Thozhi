# 🌸 THOZHI — SakhiStep AI

> **"Your voice. Your language. Your step."**
> உங்கள் குரல். உங்கள் மொழி. உங்கள் வழிகாட்டி.

---

## Overview

**THOZHI** is an **Adaptive Zero-Knowledge Government Service Assistant** built for first-time women digital users in India. It helps users independently navigate government services and skill resources through simple text or voice in their own language — without any prior digital knowledge.

The core insight: **Technology should adapt to the user — not the other way around.**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🌸 **Bilingual** | Tamil and English (extensible to more languages) |
| 🧠 **Adaptive Guidance** | Automatically escalates from Normal → Simplified → Teach-Me |
| 🧑‍🏫 **Teach-Me Mode** | Visual step-by-step explanations when confusion is detected |
| 🎬 **Demo Mode** | Pre-scripted hackathon demo — no setup required |
| 🔌 **Offline-first** | Works completely without an LLM API key |
| 🔐 **Privacy-safe** | No real sensitive data collection |

---

## 🎯 Core Innovation: Zero-Knowledge Adaptive Guidance

```
NORMAL MODE
     ↓ (confusion detected)
SIMPLIFIED MODE
     ↓ (repeated confusion)
🧑‍🏫 TEACH-ME MODE
```

When a user says "எப்படி?" (How?), "புரியவில்லை" (I don't understand), or "I don't know" — the interface **automatically simplifies** without the user needing to ask.

---

## 🛠 Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.10+
- **AI**: Google Gemini / OpenAI (optional) + Rule-based fallback
- **Languages**: Tamil, English

---

## 📂 Project Structure

```
Thozhi/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md
│
├── data/
│   └── services.json       # Demo service/resource data
│
├── modules/
│   ├── __init__.py
│   ├── ai_engine.py        # LLM integration + fallback
│   ├── intent_engine.py    # Rule-based intent/confusion detection
│   ├── guidance_engine.py  # Adaptive guidance state machine
│   ├── language.py         # Tamil/English string resources
│   └── demo_mode.py        # Pre-scripted hackathon demo
│
└── assets/
    └── icons/              # (Reserved for future icons)
```

---

## 🚀 Installation (Windows)

### 1. Prerequisites

Ensure Python 3.10+ is installed:
```powershell
python --version
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Set up environment variables (Optional — app runs without this)

```powershell
copy .env.example .env
```

Open `.env` and optionally fill in your LLM API key:
```
LLM_API_KEY=your-api-key-here
LLM_MODEL=gemini-1.5-flash
```

> **Note:** Leave `LLM_API_KEY` blank to use the built-in rule-based engine. The app works perfectly without it.

### 5. Run the application

```powershell
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 🎬 Demo Instructions (Hackathon)

### Recommended 2-minute demo flow:

1. Open THOZHI at `http://localhost:8501`
2. Select **தமிழ்** (Tamil)
3. Click **🎬 டெமோ முறையை முயற்சிக்கவும்** (Try Demo Mode)
4. Click **▶ Play Demo Step** repeatedly to walk through:
   - User asks in Tamil for skill training
   - AI identifies intent and asks one question
   - User expresses confusion → Guidance escalates to **Simplified**
   - User confused again → **🧑‍🏫 Teach-Me Mode** activates
   - AI explains using a real-world calendar example
   - Guided workflow continues step by step
   - Resource matched
   - 🎉 Completion screen
5. Show judges the **Guidance Level indicator** changing in real-time

### Manual demo (live):
1. Click **✍️ எழுதுங்கள்** (Type)
2. Type: `எனக்கு வீட்டிலிருந்து வேலை செய்ய கற்றுக்கொள்ள வேண்டும்`
3. Type: `புரியவில்லை` to trigger Teach-Me Mode

---

## 🗺 Future Roadmap

- More Indian languages (Hindi, Telugu, Kannada, Malayalam)
- Real government API integrations
- Verified government scheme database
- Offline / low-connectivity mode
- WhatsApp integration
- Regional voice models
- Document upload assistance
- Human support escalation
- Secure government authentication (DigiLocker)
- Accessibility for elderly users

---

## ⚠️ Disclaimer

> This is a **prototype simulation** built for a hackathon. All services shown are clearly labelled as **Demo / Simulated Resources**. No real government data, Aadhaar details, or sensitive credentials are collected or stored. Do not enter real personal information.

---

*Built with ❤️ for the first-time women digital users of India.*
