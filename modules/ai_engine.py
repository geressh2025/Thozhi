"""
AI Engine — LLM integration with full rule-based fallback.

Priority:
  1. Try LLM (Gemini / OpenAI / etc.) if LLM_API_KEY is set
  2. Fall back to rule-based responses (always works)

Never crashes if API is missing.
"""

import os
import json
import logging
from modules.intent_engine import detect_intent, detect_confusion, detect_language

logger = logging.getLogger(__name__)

# ─── System prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are THOZHI, a patient multilingual digital guide for first-time women users in India.

Your user may have no English knowledge and no prior digital experience.

Never assume the user understands digital terminology.

Ask only one question at a time.

Use simple, short language. Avoid technical words.

If the user expresses confusion, simplify your explanation.

Never shame or blame the user.

If the user asks what a technical term means, explain it using a familiar real-world example.

Do not invent government schemes, eligibility rules, application procedures, URLs, or official claims.

When information is uncertain, clearly say that it needs verification.

Your goal is not merely to answer questions. Your goal is to help the user understand the next action independently.

Always respond in JSON format:
{
  "language": "ta" or "en",
  "intent": "skill_training" | "employment" | "entrepreneurship" | "government_assistance" | "general_service" | "confused" | "unknown",
  "confusion_detected": true | false,
  "guidance_level": 1 | 2 | 3,
  "response": "Your response to the user in their language",
  "teach_mode": true | false
}"""


# ─── Rule-based fallback responses ───────────────────────────────────────────

FALLBACK_RESPONSES = {
    "ta": {
        "skill_training": "நிச்சயமாக! வீட்டிலிருந்தே புதிய திறன்களை கற்கலாம். உங்கள் வயதை சொல்ல முடியுமா?",
        "employment": "வேலை வாய்ப்பு பற்றி நான் உங்களுக்கு உதவுகிறேன். உங்கள் வயதை சொல்ல முடியுமா?",
        "entrepreneurship": "சொந்த தொழில் தொடங்குவது பற்றி நான் உங்களுக்கு உதவுகிறேன். உங்கள் வயதை சொல்ல முடியுமா?",
        "government_assistance": "அரசு உதவி பெற நான் உங்களுக்கு வழிகாட்டுகிறேன். உங்கள் வயதை சொல்ல முடியுமா?",
        "general_service": "அரசு சேவை பெற நான் உங்களுக்கு உதவுகிறேன். உங்கள் வயதை சொல்ல முடியுமா?",
        "confused": "பரவாயில்லை! நான் விளக்குகிறேன். கவலைப்பட வேண்டாம்.",
        "unknown": "வணக்கம்! நான் தோழி. உங்களுக்கு என்ன உதவி வேண்டும்?",
    },
    "en": {
        "skill_training": "Of course! You can learn new skills from home. May I know your age?",
        "employment": "I'll help you find work opportunities. May I know your age?",
        "entrepreneurship": "I'll help you start your own business. May I know your age?",
        "government_assistance": "I'll guide you to get government help. May I know your age?",
        "general_service": "I'll help you access government services. May I know your age?",
        "confused": "That's okay! I will explain. Please don't worry.",
        "unknown": "Hello! I am THOZHI. How can I help you today?",
    },
}


def _try_llm_response(user_message: str, conversation_history: list, lang: str) -> dict | None:
    """Attempt to get a response from the configured LLM. Returns None on any failure."""
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    model = os.environ.get("LLM_MODEL", "gemini-1.5-flash").strip()

    if not api_key:
        return None

    try:
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in conversation_history[-6:]:  # Last 3 turns
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        # Try Gemini via google-generativeai
        if "gemini" in model.lower():
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                gemini_model = genai.GenerativeModel(
                    model_name=model,
                    system_instruction=SYSTEM_PROMPT,
                )
                history_gemini = []
                for msg in conversation_history[-6:]:
                    role = "user" if msg["role"] == "user" else "model"
                    history_gemini.append({"role": role, "parts": [msg["content"]]})

                chat = gemini_model.start_chat(history=history_gemini)
                response = chat.send_message(user_message)
                raw = response.text.strip()

                # Strip markdown code fences if present
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                    raw = raw.strip()

                return json.loads(raw)
            except Exception as e:
                logger.warning(f"Gemini API error: {e}")
                return None

        # Try OpenAI-compatible API
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=400,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"OpenAI API error: {e}")
            return None

    except Exception as e:
        logger.warning(f"LLM call failed: {e}")
        return None


def get_ai_response(
    user_message: str,
    conversation_history: list,
    lang: str,
    guidance_level: int,
    confusion_count: int,
) -> dict:
    """
    Main entry point for AI responses.

    Returns a normalized dict:
    {
        "language": str,
        "intent": str,
        "confusion_detected": bool,
        "guidance_level": int,
        "response": str,
        "teach_mode": bool,
        "source": "llm" | "fallback"
    }
    """
    # Always run local detection first (fast, reliable)
    detected_lang = detect_language(user_message) if lang == "auto" else lang
    detected_intent = detect_intent(user_message, detected_lang)
    is_confused = detect_confusion(user_message, detected_lang)

    # Calculate new guidance level
    new_confusion_count = confusion_count + (1 if is_confused else 0)
    new_guidance = 1
    if new_confusion_count >= 2:
        new_guidance = 3
    elif new_confusion_count >= 1:
        new_guidance = 2
    else:
        new_guidance = guidance_level

    # Try LLM first
    llm_result = _try_llm_response(user_message, conversation_history, detected_lang)
    if llm_result and isinstance(llm_result, dict) and "response" in llm_result:
        llm_result["source"] = "llm"
        llm_result.setdefault("language", detected_lang)
        llm_result.setdefault("intent", detected_intent)
        llm_result.setdefault("confusion_detected", is_confused)
        llm_result.setdefault("guidance_level", new_guidance)
        llm_result.setdefault("teach_mode", new_guidance >= 3)
        return llm_result

    # Fallback — rule-based
    responses = FALLBACK_RESPONSES.get(detected_lang, FALLBACK_RESPONSES["en"])
    response_text = responses.get(detected_intent, responses["unknown"])

    if is_confused:
        response_text = responses.get("confused", response_text)

    return {
        "language": detected_lang,
        "intent": detected_intent,
        "confusion_detected": is_confused,
        "guidance_level": new_guidance,
        "response": response_text,
        "teach_mode": new_guidance >= 3,
        "source": "fallback",
    }
