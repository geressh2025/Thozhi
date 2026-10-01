"""
THOZHI — Adaptive Zero-Knowledge Government Service Assistant
SakhiStep AI | Hackathon Prototype

Run:  streamlit run app.py
"""

import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# ─── Module imports ────────────────────────────────────────────────────────────
from modules.language import get as t
from modules.intent_engine import (
    detect_language, detect_intent, detect_confusion,
    validate_phone, validate_age, map_intent_to_service_category,
)
from modules.guidance_engine import GuidanceEngine
from modules.ai_engine import get_ai_response
from modules.demo_mode import DEMO_SCRIPT, DEMO_STEPS_COUNT, get_demo_step

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="THOZHI — SakhiStep AI",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Load service data ────────────────────────────────────────────────────────
@st.cache_data
def load_services():
    services_path = Path("data/services.json")
    if services_path.exists():
        with open(services_path, "r", encoding="utf-8") as f:
            return {s["id"]: s for s in json.load(f)}
    return {}

SERVICES = load_services()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #fdf6ff 0%, #f0f4ff 50%, #fff5f9 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding-top: 1rem !important; max-width: 680px !important; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #ec4899 100%);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(124,58,237,0.25);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    animation: shimmer 4s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(180deg); }
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    color: white;
    letter-spacing: 2px;
    margin: 0;
    text-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.hero-tagline {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.92);
    margin: 0.5rem 0 0.25rem;
    font-weight: 600;
}
.hero-tagline-ta {
    font-size: 1rem;
    color: rgba(255,255,255,0.8);
    font-weight: 400;
}
.hero-subtitle {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.75);
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: white;
    border-radius: 20px;
    padding: 1.75rem;
    margin: 0.75rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(124,58,237,0.08);
}

/* ── Teach-Me card ── */
.teach-me-card {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-radius: 20px;
    padding: 1.75rem;
    margin: 0.75rem 0;
    border: 2px solid #f59e0b;
    box-shadow: 0 4px 20px rgba(245,158,11,0.2);
}
.teach-me-badge {
    display: inline-block;
    background: #f59e0b;
    color: white;
    font-weight: 800;
    font-size: 0.85rem;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    margin-bottom: 0.75rem;
    letter-spacing: 0.5px;
}

/* ── Guidance badge ── */
.guidance-bar {
    background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 14px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid #bae6fd;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.guidance-bar-teach {
    background: linear-gradient(90deg, #fef9c3 0%, #fef08a 100%);
    border-color: #fcd34d;
}

/* ── Step indicator ── */
.step-bar {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin: 1rem 0;
}
.step-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #e2e8f0;
    transition: all 0.3s;
}
.step-dot-active {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    box-shadow: 0 2px 8px rgba(124,58,237,0.4);
    transform: scale(1.3);
}
.step-dot-done {
    background: #10b981;
}
.step-label {
    text-align: center;
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

/* ── Chat bubbles ── */
.chat-user {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.9rem 1.2rem;
    margin: 0.4rem 0 0.4rem 3rem;
    font-size: 1rem;
    font-weight: 500;
    box-shadow: 0 2px 10px rgba(124,58,237,0.2);
}
.chat-ai {
    background: white;
    color: #1e293b;
    border-radius: 18px 18px 18px 4px;
    padding: 0.9rem 1.2rem;
    margin: 0.4rem 3rem 0.4rem 0;
    font-size: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border: 1px solid rgba(124,58,237,0.1);
}

/* ── Big buttons ── */
.stButton > button {
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.5rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.3) !important;
}

/* ── Primary button ── */
div[data-testid="stButton"]:first-of-type > button {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
    color: white !important;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 2px solid #e2e8f0 !important;
    font-size: 1.1rem !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Nunito', sans-serif !important;
    background: white !important;
    transition: border 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important;
}

/* ── Demo badge ── */
.demo-warning {
    background: linear-gradient(90deg, #fff7ed, #ffedd5);
    border: 2px solid #fb923c;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #9a3412;
    font-weight: 700;
    text-align: center;
    margin: 0.5rem 0;
}

/* ── Service card ── */
.service-card {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 2px solid #86efac;
    border-radius: 20px;
    padding: 1.5rem;
    margin: 0.75rem 0;
}

/* ── Completion screen ── */
.complete-card {
    background: linear-gradient(135deg, #fdf4ff 0%, #fce7f3 50%, #ede9fe 100%);
    border-radius: 24px;
    padding: 2rem;
    text-align: center;
    border: 2px solid rgba(168,85,247,0.2);
    box-shadow: 0 8px 32px rgba(168,85,247,0.12);
}

/* ── Privacy notice ── */
.privacy-note {
    background: #fef9c3;
    border-left: 4px solid #eab308;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
    color: #713f12;
    margin: 0.5rem 0;
}

/* ── Lang switch ── */
.lang-pill {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
}

/* ── Demo step card ── */
.demo-step-ai {
    background: white;
    border-left: 4px solid #7c3aed;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    font-size: 1rem;
}
.demo-step-user {
    background: #f5f3ff;
    border-left: 4px solid #a855f7;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1.25rem;
    margin: 0.5rem 0;
    font-size: 0.95rem;
    color: #4c1d95;
    font-style: italic;
}

/* ── Divider ── */
.thozhi-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.2), transparent);
    margin: 1.25rem 0;
}

/* ── Check items ── */
.check-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0;
    font-size: 1rem;
    color: #166534;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ─── Session state initialization ─────────────────────────────────────────────
def init_state():
    defaults = {
        "screen": "home",          # home | chat | workflow | match | complete | demo
        "lang": "ta",
        "guidance_level": 1,
        "confusion_count": 0,
        "conversation": [],        # [{role, content, teach_mode}]
        "intent": None,
        "workflow_step": 0,        # 0=name, 1=phone, 2=age+district, 3=confirm
        "user_data": {},           # name, phone, age, district
        "matched_service": None,
        "demo_step_idx": 0,
        "teach_me_active": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

WORKFLOW_STEPS = ["name", "phone", "age", "district"]
WORKFLOW_ICONS = ["👩", "📱", "🎂", "📍"]


# ─── Helper: reset to home ─────────────────────────────────────────────────────
def go_home():
    for key in ["screen", "guidance_level", "confusion_count", "conversation",
                "intent", "workflow_step", "user_data", "matched_service",
                "demo_step_idx", "teach_me_active"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# ─── Helper: guidance bar ─────────────────────────────────────────────────────
def render_guidance_bar(lang, level):
    label = GuidanceEngine.level_label(level, lang)
    is_teach = level >= 3
    css_class = "guidance-bar-teach" if is_teach else ""
    st.markdown(
        f'<div class="guidance-bar {css_class}">'
        f'<span style="font-weight:700;font-size:0.9rem;">{t("guidance_label", lang)}</span>'
        f'&nbsp;&nbsp;<span style="font-size:0.95rem;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if is_teach:
        st.markdown(
            f'<div class="teach-me-card" style="margin-top:0;">'
            f'<div class="teach-me-badge">{t("teach_me_badge", lang)}</div>'
            f'<p style="margin:0.25rem 0 0;font-size:1rem;font-weight:600;">{t("teach_me_intro", lang)}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─── Helper: step dots ────────────────────────────────────────────────────────
def render_step_dots(current: int, total: int):
    dots = ""
    for i in range(total):
        if i < current:
            dots += '<div class="step-dot step-dot-done"></div>'
        elif i == current:
            dots += '<div class="step-dot step-dot-active"></div>'
        else:
            dots += '<div class="step-dot"></div>'
    lang = st.session_state.lang
    label = t("step_label", lang, current=current + 1, total=total)
    st.markdown(f'<p class="step-label">{label}</p><div class="step-bar">{dots}</div>', unsafe_allow_html=True)


# ─── Helper: hero banner ──────────────────────────────────────────────────────
def render_hero(lang="ta", compact=False):
    name = "🌸 THOZHI" if lang == "en" else "🌸 தோழி"
    tagline = t("tagline", lang)
    tagline_alt = t("tagline", "ta" if lang == "en" else "en")
    subtitle = t("subtitle", lang)

    if compact:
        st.markdown(
            f'<div class="hero-banner" style="padding:1.5rem 1.5rem;">'
            f'<h1 class="hero-title" style="font-size:2rem;">{name}</h1>'
            f'<p class="hero-tagline" style="font-size:0.9rem;">{tagline}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="hero-banner">'
            f'<h1 class="hero-title">{name}</h1>'
            f'<p class="hero-tagline">{tagline}</p>'
            f'<p class="hero-tagline-ta">{tagline_alt}</p>'
            f'<p class="hero-subtitle">{subtitle}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─── Screen: HOME ─────────────────────────────────────────────────────────────
def screen_home():
    lang = st.session_state.lang
    render_hero(lang)

    # Language selector
    st.markdown(f'<p style="text-align:center;font-weight:700;font-size:0.95rem;color:#64748b;">{t("select_language", lang)}</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇮🇳 தமிழ்", key="lang_ta", use_container_width=True):
            st.session_state.lang = "ta"
            st.rerun()
    with col2:
        if st.button("🇬🇧 English", key="lang_en", use_container_width=True):
            st.session_state.lang = "en"
            st.rerun()

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Guidance level display
    render_guidance_bar(lang, st.session_state.guidance_level)
    st.markdown(
        f'<p style="font-size:0.78rem;color:#94a3b8;text-align:center;">{t("guidance_auto", lang)}</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Main start options
    st.markdown(f'<p style="font-size:1.1rem;font-weight:700;text-align:center;color:#1e293b;">{t("how_to_start", lang)}</p>', unsafe_allow_html=True)

    if st.button(t("speak_btn", lang), key="start_voice", use_container_width=True):
        st.session_state.screen = "chat"
        st.rerun()

    if st.button(t("type_btn", lang), key="start_type", use_container_width=True):
        st.session_state.screen = "chat"
        st.rerun()

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    if st.button(t("demo_btn", lang), key="demo_start", use_container_width=True):
        st.session_state.screen = "demo"
        st.session_state.demo_step_idx = 0
        st.rerun()


# ─── Screen: CHAT ─────────────────────────────────────────────────────────────
def screen_chat():
    lang = st.session_state.lang
    render_hero(lang, compact=True)
    render_guidance_bar(lang, st.session_state.guidance_level)

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Show greeting on first visit
    if not st.session_state.conversation:
        greeting = t("greeting", lang)
        st.markdown(f'<div class="chat-ai">🌸 {greeting}</div>', unsafe_allow_html=True)

    # Render conversation history
    for msg in st.session_state.conversation:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            ai_text = msg["content"]
            teach = msg.get("teach_mode", False)
            if teach:
                st.markdown(
                    f'<div class="teach-me-card">'
                    f'<div class="teach-me-badge">{t("teach_me_badge", lang)}</div>'
                    f'<p style="margin:0.5rem 0 0;font-size:1rem;">{ai_text}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="chat-ai">🌸 {ai_text}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Input area
    st.markdown(f'<p style="font-size:0.85rem;font-weight:600;color:#64748b;">{t("type_your_need", lang)}</p>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            label="",
            placeholder=t("placeholder", lang),
            key="chat_input",
            label_visibility="collapsed",
        )
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button(t("send_btn", lang), use_container_width=True)
        with col2:
            voiced = st.form_submit_button("🎤", use_container_width=True)

    if submitted or voiced:
        if not user_input or not user_input.strip():
            st.warning(t("empty_input", lang))
            return

        # Detect language from input
        detected_lang = detect_language(user_input)
        if detected_lang != lang:
            st.session_state.lang = detected_lang
            lang = detected_lang

        # Add user message to history
        st.session_state.conversation.append({"role": "user", "content": user_input})

        # Get AI response
        result = get_ai_response(
            user_message=user_input,
            conversation_history=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.conversation
            ],
            lang=lang,
            guidance_level=st.session_state.guidance_level,
            confusion_count=st.session_state.confusion_count,
        )

        # Update state
        if result.get("confusion_detected"):
            st.session_state.confusion_count += 1
        st.session_state.guidance_level = result.get("guidance_level", st.session_state.guidance_level)
        st.session_state.teach_me_active = result.get("teach_mode", False)

        if result.get("intent") and result["intent"] not in ("confused", "unknown"):
            st.session_state.intent = result["intent"]

        # Add AI message
        st.session_state.conversation.append({
            "role": "ai",
            "content": result["response"],
            "teach_mode": result.get("teach_mode", False),
        })

        # After 2 exchanges, move to workflow if intent is known
        user_turns = sum(1 for m in st.session_state.conversation if m["role"] == "user")
        if user_turns >= 2 and st.session_state.intent:
            st.session_state.matched_service = map_intent_to_service_category(st.session_state.intent)
            st.session_state.screen = "workflow"

        st.rerun()

    # Voice note
    st.markdown(
        f'<p style="font-size:0.75rem;color:#94a3b8;text-align:center;margin-top:0.5rem;">'
        f'🎤 {t("voice_unavailable", lang)}</p>',
        unsafe_allow_html=True,
    )

    # Back button
    if st.button(t("home_btn", lang), key="chat_home"):
        go_home()


# ─── Screen: WORKFLOW ─────────────────────────────────────────────────────────
def screen_workflow():
    lang = st.session_state.lang
    level = st.session_state.guidance_level
    step_idx = st.session_state.workflow_step
    total_steps = len(WORKFLOW_STEPS)

    render_hero(lang, compact=True)
    render_guidance_bar(lang, level)

    if step_idx >= total_steps:
        st.session_state.screen = "match"
        st.rerun()
        return

    step_name = WORKFLOW_STEPS[step_idx]
    icon = WORKFLOW_ICONS[step_idx]

    render_step_dots(step_idx, total_steps)

    step_content = GuidanceEngine.get_response(step_name, level, lang)

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Step card
    if GuidanceEngine.is_teach_me(level):
        st.markdown(
            f'<div class="teach-me-card">'
            f'<div class="teach-me-badge">{t("teach_me_badge", lang)}</div>'
            f'<h2 style="margin:0.5rem 0 0.25rem;font-size:1.4rem;">{icon} {step_content["title"]}</h2>'
            f'<p style="margin:0;font-size:1.05rem;color:#78350f;">{step_content["prompt"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if step_content.get("teach_explanation"):
            st.info(step_content["teach_explanation"])
    else:
        st.markdown(
            f'<div class="card">'
            f'<h2 style="margin:0 0 0.5rem;font-size:1.4rem;">{icon} {step_content["title"]}</h2>'
            f'<p style="margin:0;font-size:1.05rem;color:#475569;">{step_content["prompt"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Privacy warning for phone step
    if step_name == "phone":
        st.markdown(
            f'<div class="privacy-note">{t("phone_warning", lang)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Input form
    with st.form(f"workflow_form_{step_idx}"):
        if step_name == "age":
            val = st.number_input(
                label="",
                min_value=5,
                max_value=110,
                value=25,
                step=1,
                label_visibility="collapsed",
                key=f"input_{step_name}",
            )
        else:
            val = st.text_input(
                label="",
                placeholder="...",
                label_visibility="collapsed",
                key=f"input_{step_name}",
            )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(t("next_btn", lang), use_container_width=True)
        with col2:
            confused_btn = st.form_submit_button("❓ " + ("உதவி" if lang == "ta" else "Help"), use_container_width=True)

    if confused_btn:
        st.session_state.confusion_count += 1
        st.session_state.guidance_level = GuidanceEngine.escalate(level, st.session_state.confusion_count)
        st.session_state.teach_me_active = st.session_state.guidance_level >= 3
        st.rerun()

    if submitted:
        # Validate
        val_str = str(val).strip()
        if not val_str:
            st.warning(t("empty_input", lang))
            return

        if step_name == "phone":
            if not validate_phone(val_str):
                st.warning(t("phone_invalid", lang))
                return

        if step_name == "age":
            valid, age = validate_age(val_str)
            if not valid:
                st.warning(t("age_invalid", lang))
                return
            val_str = str(age)

        st.session_state.user_data[step_name] = val_str
        st.session_state.workflow_step += 1

        if st.session_state.workflow_step >= total_steps:
            st.session_state.screen = "match"
        st.rerun()

    # Show understand button in teach-me mode
    if GuidanceEngine.is_teach_me(level):
        if st.button(t("understand_btn", lang), key="understand_btn"):
            # Allow skipping explanation and staying at same step
            st.rerun()

    if st.button(t("home_btn", lang), key="workflow_home"):
        go_home()


# ─── Screen: SERVICE MATCH ────────────────────────────────────────────────────
def screen_match():
    lang = st.session_state.lang
    level = st.session_state.guidance_level
    render_hero(lang, compact=True)
    render_guidance_bar(lang, level)

    service_id = st.session_state.matched_service or "skill_demo"
    service = SERVICES.get(service_id, list(SERVICES.values())[0] if SERVICES else {})

    name_key = "name_ta" if lang == "ta" else "name"
    cat_key = "category_ta" if lang == "ta" else "category"
    desc_key = "description_ta" if lang == "ta" else "description"
    why_key = "why_relevant_ta" if lang == "ta" else "why_relevant"
    req_key = "requirements_ta" if lang == "ta" else "requirements"

    st.markdown(
        f'<div class="demo-warning">{t("demo_badge", lang)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<h2 style="text-align:center;margin:1rem 0 0.25rem;">{t("match_found", lang)}</h2>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="service-card">'
        f'<h3 style="margin:0 0 0.5rem;font-size:1.3rem;">{service.get(name_key, service.get("name", ""))}</h3>'
        f'<p style="margin:0 0 0.75rem;font-size:0.85rem;color:#4b5563;">{t("match_category",lang)}: <strong>{service.get(cat_key, service.get("category",""))}</strong></p>'
        f'<p style="margin:0 0 0.5rem;">{service.get(desc_key, service.get("description",""))}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f'**{t("match_why", lang)}:** {service.get(why_key, service.get("why_relevant",""))}')

    reqs = service.get(req_key, service.get("requirements", []))
    st.markdown(f'**{t("match_requirements", lang)}:**')
    for r in reqs:
        st.markdown(f"• {r}")

    st.markdown(f'**{t("match_steps", lang)}:** {service.get("steps", 4)}')

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="demo-warning">{t("demo_notice", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    if st.button(t("continue_btn", lang), key="match_continue", use_container_width=True):
        st.session_state.screen = "complete"
        st.rerun()

    if st.button(t("home_btn", lang), key="match_home"):
        go_home()


# ─── Screen: COMPLETE ─────────────────────────────────────────────────────────
def screen_complete():
    lang = st.session_state.lang

    st.markdown(
        f'<div class="complete-card">'
        f'<h1 style="font-size:2.5rem;margin:0;">{t("complete_title", lang)}</h1>'
        f'<p style="font-size:1.1rem;color:#7c3aed;font-weight:600;margin:0.5rem 0 1.5rem;">{t("complete_subtitle", lang)}</p>'
        f'<div style="text-align:left;max-width:380px;margin:0 auto;">'
        f'<div class="check-item">✅ {t("complete_understood", lang)}</div>'
        f'<div class="check-item">✅ {t("complete_identified", lang)}</div>'
        f'<div class="check-item">✅ {t("complete_explained", lang)}</div>'
        f'<div class="check-item">✅ {t("complete_prepared", lang)}</div>'
        f'</div>'
        f'<p style="font-size:0.78rem;color:#94a3b8;margin-top:1.5rem;">{t("complete_disclaimer", lang)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("start_again_btn", lang), key="complete_restart", use_container_width=True):
            go_home()
    with col2:
        if st.button(t("home_btn", lang), key="complete_home", use_container_width=True):
            go_home()


# ─── Screen: DEMO MODE ────────────────────────────────────────────────────────
def screen_demo():
    lang = st.session_state.lang

    render_hero(lang, compact=True)

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:16px;'
        f'padding:1.25rem;text-align:center;margin:0.5rem 0;">'
        f'<h2 style="color:white;margin:0;font-size:1.4rem;">🎬 {t("demo_mode_title", lang)}</h2>'
        f'<p style="color:rgba(255,255,255,0.75);margin:0.25rem 0 0;font-size:0.9rem;">{t("demo_mode_desc", lang)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    current_idx = st.session_state.demo_step_idx
    played_steps = DEMO_SCRIPT[:current_idx]

    # Show conversation so far
    for step in played_steps:
        actor = step["actor"]
        text = step["text"]
        teach = step.get("teach_mode", False)
        level = step.get("guidance_level", 1)

        if actor == "user":
            st.markdown(
                f'<div class="demo-step-user">🧑 {text}</div>',
                unsafe_allow_html=True,
            )
        else:
            guidance_label = GuidanceEngine.level_label(level, lang)
            if teach or level >= 3:
                st.markdown(
                    f'<div class="teach-me-card">'
                    f'<div class="teach-me-badge">{t("teach_me_badge", lang)}</div>'
                    f'<p style="margin:0.5rem 0 0;">🌸 {text}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            elif level == 2:
                st.markdown(
                    f'<div class="demo-step-ai" style="border-left-color:#f59e0b;">'
                    f'🌸 {text}<br>'
                    f'<span style="font-size:0.75rem;color:#92400e;">{guidance_label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="demo-step-ai">🌸 {text}<br>'
                    f'<span style="font-size:0.75rem;color:#6b7280;">{guidance_label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    # Controls
    if current_idx < DEMO_STEPS_COUNT:
        next_step = DEMO_SCRIPT[current_idx]
        desc = next_step.get("description", "")
        st.markdown(
            f'<p style="font-size:0.8rem;color:#64748b;font-style:italic;">⏭ Next: {desc}</p>',
            unsafe_allow_html=True,
        )
        label = t("demo_step_label", lang, n=current_idx + 1, total=DEMO_STEPS_COUNT)
        if st.button(f"▶ {label}", key="demo_next", use_container_width=True):
            st.session_state.demo_step_idx += 1
            st.rerun()
    else:
        st.markdown(
            f'<div class="complete-card">'
            f'<h2 style="font-size:2rem;">🎉 {t("demo_complete", lang)}</h2>'
            f'<p style="color:#7c3aed;font-weight:600;">{t("complete_disclaimer", lang)}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(t("demo_restart", lang), key="demo_restart", use_container_width=True):
            st.session_state.demo_step_idx = 0
            st.rerun()

    st.markdown('<hr class="thozhi-divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("start_again_btn", lang), key="demo_restart2", use_container_width=True):
            st.session_state.demo_step_idx = 0
            st.rerun()
    with col2:
        if st.button(t("home_btn", lang), key="demo_home", use_container_width=True):
            go_home()


# ─── Screen router ────────────────────────────────────────────────────────────
screen = st.session_state.screen

if screen == "home":
    screen_home()
elif screen == "chat":
    screen_chat()
elif screen == "workflow":
    screen_workflow()
elif screen == "match":
    screen_match()
elif screen == "complete":
    screen_complete()
elif screen == "demo":
    screen_demo()
else:
    go_home()
