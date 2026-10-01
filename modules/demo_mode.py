"""
Demo Mode — Pre-scripted deterministic conversation for hackathon judging.

The demo shows the full THOZHI flow:
  1. User asks in Tamil for skill training
  2. AI asks clarifying question
  3. User expresses confusion → Guidance escalates to Simplified
  4. User again confused → Teach-Me Mode activates
  5. Guided workflow continues
  6. Resource matched
  7. Completion screen
"""

DEMO_SCRIPT = [
    {
        "step": 1,
        "actor": "user",
        "lang": "ta",
        "text": "எனக்கு வீட்டிலிருந்து வேலை செய்ய கற்றுக்கொள்ள வேண்டும்.",
        "description": "User (Tamil): Asks to learn skills to work from home",
    },
    {
        "step": 2,
        "actor": "ai",
        "lang": "ta",
        "text": "நிச்சயமாக! நான் உங்களுக்கு உதவுகிறேன். 🌸\n\nமுதலில் உங்கள் வயதை சொல்ல முடியுமா?",
        "intent": "skill_training",
        "confusion_detected": False,
        "guidance_level": 1,
        "teach_mode": False,
        "description": "AI identifies intent as Skill Training. Asks age (one question only).",
    },
    {
        "step": 3,
        "actor": "user",
        "lang": "ta",
        "text": "எனக்கு எப்படி செய்வது என்று தெரியவில்லை.",
        "description": "User expresses confusion — triggers guidance escalation",
    },
    {
        "step": 4,
        "actor": "ai",
        "lang": "ta",
        "text": "பரவாயில்லை! கவலைப்பட வேண்டாம். 😊\n\nவயது என்பது நீங்கள் எத்தனை வருடங்கள் வாழ்ந்திருக்கிறீர்கள் என்பது.\n\nஎடுத்துக்காட்டாக: என் வயது 28.",
        "intent": "confused",
        "confusion_detected": True,
        "guidance_level": 2,
        "teach_mode": False,
        "description": "Guidance → Simplified. AI gives a simple explanation with an example.",
    },
    {
        "step": 5,
        "actor": "user",
        "lang": "ta",
        "text": "புரியவில்லை",
        "description": "User still confused — second confusion triggers Teach-Me Mode",
    },
    {
        "step": 6,
        "actor": "ai",
        "lang": "ta",
        "text": "🧑‍🏫 சரி! நாம் சேர்ந்து செய்வோம்.\n\n🎂 உங்கள் பிறந்த ஆண்டு என்ன?\n\nவேறு வழியில் கேட்கிறேன்:\nகாலண்டரில் இப்போது 2026 — நீங்கள் 1998 ல் பிறந்தீர்கள் என்றால், உங்கள் வயது 28.\n\nதயவுசெய்து எண்ணை மட்டும் சொல்லுங்கள்.",
        "intent": "confused",
        "confusion_detected": True,
        "guidance_level": 3,
        "teach_mode": True,
        "description": "🧑‍🏫 TEACH-ME MODE activated. Explains age with a calendar example.",
    },
    {
        "step": 7,
        "actor": "user",
        "lang": "ta",
        "text": "28",
        "description": "User provides age — workflow continues",
    },
    {
        "step": 8,
        "actor": "ai",
        "lang": "ta",
        "text": "மிக்க நன்றி! 🌸\n\nநீங்கள் எந்த மாவட்டத்தில் வசிக்கிறீர்கள்?",
        "intent": "skill_training",
        "confusion_detected": False,
        "guidance_level": 3,
        "teach_mode": True,
        "description": "AI asks for district — stays in Teach-Me level for comfort.",
    },
    {
        "step": 9,
        "actor": "user",
        "lang": "ta",
        "text": "சென்னை",
        "description": "User provides district",
    },
    {
        "step": 10,
        "actor": "ai",
        "lang": "ta",
        "text": "நல்லது! ✨\n\nஉங்களுக்கு பொருத்தமான ஒரு வளம் கண்டுபிடிக்கப்பட்டுள்ளது.\n\n🌸 பெண்கள் திறன் மேம்பாட்டு வளம்\n\nதொடர்க →",
        "intent": "skill_training",
        "confusion_detected": False,
        "guidance_level": 3,
        "teach_mode": True,
        "service_matched": "skill_demo",
        "description": "Resource matched! Shows Women Skill Development Resource.",
    },
]

DEMO_STEPS_COUNT = len(DEMO_SCRIPT)


def get_demo_step(step_index: int) -> dict | None:
    """Return a demo script step by 0-based index. Returns None if out of range."""
    if 0 <= step_index < len(DEMO_SCRIPT):
        return DEMO_SCRIPT[step_index]
    return None


def get_demo_user_steps() -> list[dict]:
    """Return only user turns from the demo script."""
    return [s for s in DEMO_SCRIPT if s["actor"] == "user"]


def get_demo_ai_steps() -> list[dict]:
    """Return only AI turns from the demo script."""
    return [s for s in DEMO_SCRIPT if s["actor"] == "ai"]
