"""
Intent Engine — Rule-based intent and confusion detection.
Works entirely offline — no API key required.
"""

import re

# ─── Intent keyword maps ────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "government_assistance": {
        "ta": ["அரசு உதவி", "அரசு திட்டம்", "திட்டம்", "உதவி வேண்டும்", "அரசாங்க", "நலத்திட்டம்"],
        "en": ["government help", "government scheme", "govt", "welfare", "assistance", "support scheme"],
    },
    "skill_training": {
        "ta": ["கற்றுக்கொள்ள", "கற்க", "படிக்க", "திறன்", "பயிற்சி", "கோர்ஸ்", "course", "training",
               "வீட்டிலிருந்து", "online"],
        "en": ["learn", "skill", "training", "course", "study", "education", "digital skill", "online class"],
    },
    "employment": {
        "ta": ["வேலை", "வேலைவாய்ப்பு", "வேலை வேண்டும்", "சம்பளம்", "job", "வேலை தேட"],
        "en": ["job", "work", "employment", "career", "salary", "earn", "find work"],
    },
    "entrepreneurship": {
        "ta": ["தொழில்", "சொந்த தொழில்", "வியாபாரம்", "business", "கடை", "தொடங்க"],
        "en": ["business", "entrepreneur", "start business", "self employed", "shop", "startup"],
    },
    "confused": {
        "ta": ["எப்படி", "தெரியவில்லை", "புரியவில்லை", "தெரியல", "என்ன செய்ய வேண்டும்",
               "எப்படி செய்வது", "உதவி", "help", "புரிய", "விளக்க", "கஷ்டமாக"],
        "en": ["how", "i don't know", "i dont know", "don't understand", "dont understand",
               "confused", "help", "what do i do", "not sure", "explain", "i'm confused", "help me"],
    },
    "general_service": {
        "ta": ["அரசு சேவை", "சேவை", "சான்றிதழ்", "certificate", "form", "படிவம்"],
        "en": ["government service", "certificate", "form", "application", "document"],
    },
}

CONFUSION_PHRASES_TA = [
    "எப்படி", "தெரியவில்லை", "புரியவில்லை", "தெரியல",
    "என்ன செய்ய வேண்டும்", "எப்படி செய்வது", "புரிய வில்லை",
    "என்ன", "எங்கு", "எங்க", "விளக்க முடியுமா", "கஷ்டமாக இருக்கு",
]
CONFUSION_PHRASES_EN = [
    "how", "i don't know", "i dont know", "don't understand", "dont understand",
    "confused", "help me", "what do i do", "not sure", "i'm confused",
    "what is this", "i don't get it",
]


def detect_language(text: str) -> str:
    """Detect if text is Tamil or English based on Unicode range."""
    tamil_chars = sum(1 for c in text if "\u0B80" <= c <= "\u0BFF")
    return "ta" if tamil_chars > 2 else "en"


def detect_intent(text: str, lang: str = "en") -> str:
    """Return the best-matching intent for the user's message."""
    text_lower = text.lower()

    scores = {intent: 0 for intent in INTENT_PATTERNS}

    for intent, patterns in INTENT_PATTERNS.items():
        keywords = patterns.get(lang, []) + patterns.get("en", [])
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[intent] += 1

    # Pick highest score
    best_intent = max(scores, key=scores.get)
    if scores[best_intent] == 0:
        return "unknown"
    return best_intent


def detect_confusion(text: str, lang: str = "en") -> bool:
    """Return True if the user's message indicates confusion."""
    text_lower = text.lower().strip()

    phrases = CONFUSION_PHRASES_EN[:]
    if lang == "ta":
        phrases += CONFUSION_PHRASES_TA

    for phrase in phrases:
        if phrase.lower() in text_lower:
            return True

    # Short messages that are questions often indicate confusion
    if len(text_lower.split()) <= 3 and ("?" in text_lower or text_lower in ["?", "how", "what", "why", "எப்படி", "என்ன"]):
        return True

    return False


def validate_phone(text: str) -> bool:
    """Validate a 10-digit Indian mobile number."""
    digits = re.sub(r"\D", "", text)
    return len(digits) == 10 and digits[0] in "6789"


def validate_age(text: str) -> tuple[bool, int]:
    """Extract and validate age from text. Returns (valid, age)."""
    numbers = re.findall(r"\d+", text)
    if not numbers:
        return False, 0
    age = int(numbers[0])
    if 5 <= age <= 110:
        return True, age
    return False, 0


def map_intent_to_service_category(intent: str) -> str:
    """Map detected intent to a service category ID."""
    mapping = {
        "skill_training": "skill_demo",
        "employment": "employment_demo",
        "entrepreneurship": "entrepreneur_demo",
        "government_assistance": "govt_assist_demo",
        "general_service": "govt_assist_demo",
        "confused": "govt_assist_demo",
        "unknown": "skill_demo",
    }
    return mapping.get(intent, "skill_demo")
