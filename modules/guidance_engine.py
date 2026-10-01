"""
Guidance Engine — Manages the adaptive guidance state machine.

Guidance Levels:
  1 = Normal
  2 = Simplified
  3 = Teach-Me Mode

Confusion counter drives level escalation.
"""

from modules.language import get as t


class GuidanceEngine:
    """Stateless guidance logic — state is stored in st.session_state externally."""

    LEVEL_NORMAL = 1
    LEVEL_SIMPLIFIED = 2
    LEVEL_TEACH_ME = 3

    CONFUSION_THRESHOLD_SIMPLIFIED = 1   # 1 confusion → simplified
    CONFUSION_THRESHOLD_TEACH_ME = 2     # 2 confusions → teach-me

    @staticmethod
    def escalate(current_level: int, confusion_count: int) -> int:
        """Return the new guidance level based on confusion count."""
        if confusion_count >= GuidanceEngine.CONFUSION_THRESHOLD_TEACH_ME:
            return GuidanceEngine.LEVEL_TEACH_ME
        elif confusion_count >= GuidanceEngine.CONFUSION_THRESHOLD_SIMPLIFIED:
            return GuidanceEngine.LEVEL_SIMPLIFIED
        return current_level

    @staticmethod
    def level_label(level: int, lang: str) -> str:
        """Return a human-readable label for the guidance level."""
        labels = {
            1: t("level_1", lang),
            2: t("level_2", lang),
            3: t("level_3", lang),
        }
        return labels.get(level, t("level_1", lang))

    @staticmethod
    def is_teach_me(level: int) -> bool:
        return level >= GuidanceEngine.LEVEL_TEACH_ME

    @staticmethod
    def get_response(
        step: str,
        level: int,
        lang: str,
        extra_context: dict = None
    ) -> dict:
        """
        Return the UI content for a given step and guidance level.

        Returns:
            {
                "icon": str,
                "title": str,
                "prompt": str,
                "teach_explanation": str | None,   # Only in teach-me
                "input_type": "text" | "number",
            }
        """
        extra_context = extra_context or {}

        # --- Name step ---
        if step == "name":
            base = {
                "icon": "👩",
                "title": t("step_name", lang),
                "prompt": t("enter_name", lang),
                "input_type": "text",
            }
            if level >= GuidanceEngine.LEVEL_SIMPLIFIED:
                base["prompt"] = (
                    "உங்கள் பெயரை சொல்லுங்கள்." if lang == "ta"
                    else "Just tell me what your name is."
                )
            if GuidanceEngine.is_teach_me(level):
                base["teach_explanation"] = (
                    "📝 " + t("teach_name_explain", lang)
                )
            return base

        # --- Phone step ---
        if step == "phone":
            base = {
                "icon": "📱",
                "title": t("step_phone", lang),
                "prompt": t("enter_phone", lang),
                "input_type": "tel",
            }
            if level >= GuidanceEngine.LEVEL_SIMPLIFIED:
                base["prompt"] = (
                    "உங்கள் கைப்பேசியில் 10 இலக்க எண் உள்ளது. அதை சொல்லுங்கள்." if lang == "ta"
                    else "Your phone has a 10-digit number. Please tell me that number."
                )
            if GuidanceEngine.is_teach_me(level):
                base["teach_explanation"] = (
                    "📱 " + t("teach_phone_explain", lang)
                )
            return base

        # --- Age step ---
        if step == "age":
            base = {
                "icon": "🎂",
                "title": t("teach_age", lang),
                "prompt": t("enter_age", lang),
                "input_type": "number",
            }
            if GuidanceEngine.is_teach_me(level):
                base["teach_explanation"] = "🎂 " + t("teach_age_explain", lang)
            return base

        # --- District step ---
        if step == "district":
            base = {
                "icon": "📍",
                "title": t("teach_district", lang),
                "prompt": t("enter_district", lang),
                "input_type": "text",
            }
            if GuidanceEngine.is_teach_me(level):
                base["teach_explanation"] = "📍 " + t("teach_district_explain", lang)
            return base

        # Fallback
        return {
            "icon": "💬",
            "title": "Input",
            "prompt": "Please respond.",
            "input_type": "text",
        }
