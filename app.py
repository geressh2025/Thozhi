"""
THOZHI -- Adaptive Digital Guidance Assistant
Hackathon Prototype

Run:  streamlit run app.py
"""

import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from modules.language import get as t
from modules.intent_engine import (
    detect_language, detect_intent, detect_confusion,
    validate_phone, validate_age, map_intent_to_service_category,
)
from modules.guidance_engine import GuidanceEngine
from modules.ai_engine import get_ai_response
from modules.demo_mode import DEMO_SCRIPT, DEMO_STEPS_COUNT

st.set_page_config(
    page_title="THOZHI",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

@st.cache_data
def load_services():
    p = Path("data/services.json")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return {s["id"]: s for s in json.load(f)}
    return {}

SERVICES = load_services()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* ── Background ── */
.stApp {
    background: #f4f1ee;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container {
    padding-top: 2rem !important;
    max-width: 660px !important;
}

/* ── HERO ── */
.hero {
    background: #2d1b69;
    border-radius: 20px;
    padding: 2.8rem 2rem 2.4rem;
    text-align: center;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-stripe {
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #f97316, #fbbf24, #f97316);
}
.hero-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 3rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 3px;
    margin: 0 0 0.4rem;
    line-height: 1;
}
.hero-tagline {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.75);
    margin: 0 0 0.2rem;
    font-weight: 500;
}
.hero-tagline-alt {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.45);
    margin: 0 0 1.1rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(249,115,22,0.18);
    border: 1px solid rgba(249,115,22,0.4);
    border-radius: 6px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    color: #fed7aa;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* ── Compact hero ── */
.hero-compact {
    background: #2d1b69;
    border-radius: 16px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 1.25rem;
    border-left: 4px solid #f97316;
}
.hero-compact-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.4rem;
    font-weight: 800;
    color: white;
    letter-spacing: 2px;
    margin: 0;
    line-height: 1;
}
.hero-compact-tag {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.5);
    margin: 0.2rem 0 0;
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.5rem;
    margin: 0.75rem 0;
    border: 1px solid #e8e2dc;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ── Guidance bar ── */
.guidance-bar {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    background: #ffffff;
    border: 1px solid #ddd6fe;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 1rem;
}
.guidance-bar-teach {
    border-color: #fcd34d;
    background: #fffbeb;
}
.gb-label {
    font-weight: 600;
    font-size: 0.78rem;
    color: #4c1d95;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.gb-level {
    font-size: 0.88rem;
    color: #7c3aed;
    margin-left: auto;
    font-weight: 600;
}
.guidance-bar-teach .gb-level {
    color: #b45309;
}

/* ── Teach-Me card ── */
.teach-card {
    background: #fffbeb;
    border: 2px solid #fcd34d;
    border-radius: 14px;
    padding: 1.5rem;
    margin: 0.75rem 0;
    border-left: 5px solid #f59e0b;
}
.teach-badge {
    display: inline-block;
    background: #f59e0b;
    color: white;
    font-weight: 700;
    font-size: 0.73rem;
    padding: 0.22rem 0.75rem;
    border-radius: 5px;
    margin-bottom: 0.6rem;
    letter-spacing: 0.3px;
}
.teach-icon { font-size: 1.75rem; display: block; margin-bottom: 0.3rem; }
.teach-title { font-size: 1.15rem; font-weight: 700; color: #92400e; margin: 0.15rem 0; }
.teach-body { color: #78350f; font-size: 0.95rem; line-height: 1.65; margin: 0.4rem 0 0; }
.teach-explain {
    background: #fef3c7;
    border-radius: 8px;
    padding: 0.75rem 0.9rem;
    margin-top: 0.75rem;
    color: #92400e;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── Step progress ── */
.step-hdr { text-align: center; margin: 0.5rem 0 1.25rem; }
.step-lbl {
    font-size: 0.7rem;
    font-weight: 600;
    color: #9ca3af;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 0.6rem;
}
.step-track { display: flex; align-items: center; justify-content: center; }
.sn {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700;
}
.sn-done { background: #059669; color: white; }
.sn-active { background: #2d1b69; color: white; box-shadow: 0 0 0 3px rgba(45,27,105,0.2); }
.sn-pending { background: #e5e7eb; color: #9ca3af; border: 2px solid #d1d5db; }
.sc { height: 2px; width: 36px; background: #e5e7eb; }
.sc-done { background: #059669; }

/* ── Chat bubbles ── */
.bubble-user {
    background: #2d1b69;
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.85rem 1.2rem;
    margin-left: 15%;
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
    line-height: 1.55;
    font-weight: 500;
}
.bubble-ai {
    background: white;
    border: 1px solid #e8e2dc;
    color: #1c1c1e;
    border-radius: 18px 18px 18px 4px;
    padding: 0.85rem 1.2rem;
    margin-right: 15%;
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 10px !important;
    color: #1c1c1e !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.18s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: #9ca3af !important; }
.stTextInput label, .stNumberInput label, .stTextArea label {
    color: #374151 !important; font-weight: 600 !important; font-size: 0.82rem !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.72rem 1.2rem !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
    background: #ffffff !important;
    color: #374151 !important;
    border: 1.5px solid #d1d5db !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}
.stButton > button:hover {
    background: #f9fafb !important;
    border-color: #9ca3af !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    background: #f3f4f6 !important;
}

/* ── Service card ── */
.service-card {
    background: #f0fdf4;
    border: 1.5px solid #86efac;
    border-radius: 14px;
    padding: 1.5rem;
    margin: 0.75rem 0;
    border-left: 5px solid #16a34a;
}
.s-name { font-size: 1.1rem; font-weight: 700; color: #14532d; margin: 0 0 0.35rem; }
.s-cat {
    display: inline-block;
    background: #dcfce7; border: 1px solid #86efac;
    color: #166534; font-size: 0.7rem; font-weight: 600;
    padding: 0.2rem 0.65rem; border-radius: 4px; margin-bottom: 0.65rem;
    letter-spacing: 0.3px; text-transform: uppercase;
}
.s-desc { color: #374151; font-size: 0.88rem; line-height: 1.6; margin-bottom: 0.6rem; }
.req-item { display: flex; align-items: center; gap: 0.45rem; color: #374151; font-size: 0.86rem; padding: 0.18rem 0; }
.req-dot { width: 5px; height: 5px; border-radius: 50%; background: #16a34a; flex-shrink: 0; }
.s-row {
    display: flex; justify-content: space-between;
    padding: 0.4rem 0; border-top: 1px solid #bbf7d0;
    margin-top: 0.4rem; font-size: 0.82rem; color: #6b7280;
}
.s-val { color: #15803d; font-weight: 600; }

/* ── Demo badge ── */
.demo-badge {
    display: flex; align-items: center; justify-content: center; gap: 0.4rem;
    background: #fff7ed; border: 1px solid #fed7aa;
    border-radius: 8px; padding: 0.5rem 0.9rem;
    color: #c2410c; font-size: 0.78rem; font-weight: 600; margin: 0.5rem 0;
}

/* ── Demo screen ── */
.demo-hdr {
    background: #2d1b69;
    border-radius: 14px; padding: 1.1rem 1.5rem;
    margin-bottom: 1rem; border-left: 4px solid #f97316;
}
.demo-hdr h2 { color: white !important; font-size: 1.15rem !important; margin: 0 0 0.2rem !important; font-family: 'Sora', sans-serif !important; }
.demo-hdr p { color: rgba(255,255,255,0.55); font-size: 0.8rem; margin: 0; }
.d-user {
    background: #f5f3ff; border: 1px solid #ddd6fe;
    border-left: 3px solid #7c3aed; border-radius: 0 10px 10px 0;
    padding: 0.75rem 1.1rem; margin: 0.35rem 0;
    color: #4c1d95; font-style: italic; font-size: 0.88rem;
}
.d-ai {
    background: #ffffff; border: 1px solid #e8e2dc;
    border-left: 3px solid #2d1b69; border-radius: 0 10px 10px 0;
    padding: 0.75rem 1.1rem; margin: 0.35rem 0;
    color: #1c1c1e; font-size: 0.88rem; line-height: 1.6;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.d-tag { font-size: 0.66rem; color: #9ca3af; margin-top: 0.2rem; font-style: normal; display: block; }

/* ── Complete screen ── */
.complete-wrap {
    background: #ffffff;
    border: 1px solid #e8e2dc;
    border-radius: 18px;
    padding: 2.5rem 1.75rem;
    text-align: center;
    border-top: 4px solid #7c3aed;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
}
.c-emoji { font-size: 3.5rem; display: block; margin-bottom: 0.6rem; }
.c-title { font-family: 'Sora', sans-serif !important; font-size: 1.9rem; font-weight: 800; color: #1c1c1e; margin: 0 0 0.3rem; }
.c-sub { color: #7c3aed; font-size: 0.95rem; font-weight: 600; margin: 0 0 1.5rem; }
.check-list {
    background: #fafaf8; border-radius: 10px;
    padding: 1rem; text-align: left; margin: 0 auto 1.25rem;
    border: 1px solid #e8e2dc;
}
.c-row {
    display: flex; align-items: center; gap: 0.65rem;
    padding: 0.4rem 0; font-size: 0.9rem; font-weight: 500;
    color: #374151; border-bottom: 1px solid #f3f4f6;
}
.c-row:last-child { border-bottom: none; }
.c-icon {
    width: 22px; height: 22px; border-radius: 50%;
    background: #059669; display: flex; align-items: center;
    justify-content: center; font-size: 0.68rem; color: white; flex-shrink: 0;
}
.c-disc { font-size: 0.7rem; color: #9ca3af; margin-top: 1rem; }

/* ── Misc ── */
.divider {
    height: 1px; background: #e8e2dc; margin: 1.25rem 0; border: none;
}
.section-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: #9ca3af; margin: 1rem 0 0.5rem;
}
.privacy-note {
    background: #fffbeb; border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0; padding: 0.55rem 0.9rem;
    font-size: 0.77rem; color: #92400e; margin: 0.5rem 0; line-height: 1.5;
}
.voice-note {
    text-align: center; font-size: 0.72rem; color: #9ca3af;
    margin-top: 0.4rem;
}
.how-title {
    font-size: 0.95rem; font-weight: 600; color: #374151;
    text-align: center; margin: 0.5rem 0 0.75rem;
}
.lang-section {
    background: #ffffff; border: 1px solid #e8e2dc;
    border-radius: 10px; padding: 0.85rem 1.25rem;
    text-align: center; margin: 0.75rem 0;
}
.lang-title {
    color: #9ca3af; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0.6rem;
}
.input-wrap {
    background: #f9fafb; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 1.1rem; margin-top: 0.5rem;
}
.stAlert {
    background: #fff7ed !important; border: 1px solid #fed7aa !important;
    border-radius: 8px !important; color: #92400e !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "screen": "home",
        "lang": "ta",
        "guidance_level": 1,
        "confusion_count": 0,
        "conversation": [],
        "intent": None,
        "workflow_step": 0,
        "user_data": {},
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


def go_home():
    for key in ["screen", "guidance_level", "confusion_count", "conversation",
                "intent", "workflow_step", "user_data", "matched_service",
                "demo_step_idx", "teach_me_active"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# ── Helpers ──────────────────────────────────────────────────────────────────
def render_hero(lang="ta", compact=False):
    tagline = t("tagline", lang)
    tagline_alt = t("tagline", "ta" if lang == "en" else "en")
    subtitle = t("subtitle", lang)

    if compact:
        st.markdown(
            f'<div class="hero-compact">'
            f'<span style="font-size:1.75rem;">🌸</span>'
            f'<div>'
            f'<p class="hero-compact-title">THOZHI</p>'
            f'<p class="hero-compact-tag">{tagline}</p>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="hero">'
            f'<div class="hero-stripe"></div>'
            f'<p style="font-size:2.5rem;margin:0 0 0.3rem;line-height:1;">🌸</p>'
            f'<h1 class="hero-title">THOZHI</h1>'
            f'<p class="hero-tagline">{tagline}</p>'
            f'<p class="hero-tagline-alt">{tagline_alt}</p>'
            f'<span class="hero-badge">{subtitle}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_guidance_bar(lang, level):
    label = GuidanceEngine.level_label(level, lang)
    guide_label = t("guidance_label", lang)
    is_teach = level >= 3
    cls = "guidance-bar-teach" if is_teach else ""
    st.markdown(
        f'<div class="guidance-bar {cls}">'
        f'<span>🌱</span>'
        f'<span class="gb-label">{guide_label}</span>'
        f'<span class="gb-level">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if is_teach:
        badge = t("teach_me_badge", lang)
        intro = t("teach_me_intro", lang)
        st.markdown(
            f'<div class="teach-card">'
            f'<span class="teach-badge">🧑‍🏫 {badge}</span>'
            f'<p class="teach-body" style="font-weight:600;margin:0;">{intro}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_step_dots(current: int, total: int):
    lang = st.session_state.lang
    label = t("step_label", lang, current=current + 1, total=total)
    nodes = ""
    for i in range(total):
        if i < current:
            nodes += f'<div class="sn sn-done">✓</div>'
        elif i == current:
            nodes += f'<div class="sn sn-active">{i+1}</div>'
        else:
            nodes += f'<div class="sn sn-pending">{i+1}</div>'
        if i < total - 1:
            cls = "sc sc-done" if i < current else "sc"
            nodes += f'<div class="{cls}"></div>'

    st.markdown(
        f'<div class="step-hdr">'
        f'<span class="step-lbl">{label}</span>'
        f'<div class="step-track">{nodes}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Screen: HOME ─────────────────────────────────────────────────────────────
def screen_home():
    lang = st.session_state.lang
    render_hero(lang)

    # Language selector
    st.markdown(
        f'<div class="lang-section">'
        f'<p class="lang-title">{t("select_language", lang)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇮🇳  தமிழ்", key="lang_ta", use_container_width=True):
            st.session_state.lang = "ta"
            st.rerun()
    with col2:
        if st.button("🇬🇧  English", key="lang_en", use_container_width=True):
            st.session_state.lang = "en"
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    render_guidance_bar(lang, st.session_state.guidance_level)
    st.markdown(
        f'<p style="font-size:0.72rem;color:#9ca3af;text-align:center;margin-top:-0.4rem;margin-bottom:0.5rem;">'
        f'{t("guidance_auto", lang)}</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f'<p class="how-title">{t("how_to_start", lang)}</p>', unsafe_allow_html=True)

    # Primary speak button styled inline
    st.markdown("""
    <style>
    section[data-testid="stVerticalBlock"] > div:has(> [data-testid="stButton"][id*="start_voice"]) button,
    div[data-testid="stButton"]:has(button[kind="secondary"]:first-of-type) button {
        background: #2d1b69 !important;
        color: white !important;
        border-color: #2d1b69 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button(t("speak_btn", lang), key="start_voice", use_container_width=True):
        st.session_state.screen = "chat"
        st.rerun()

    if st.button(t("type_btn", lang), key="start_type", use_container_width=True):
        st.session_state.screen = "chat"
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button(t("demo_btn", lang), key="demo_start", use_container_width=True):
        st.session_state.screen = "demo"
        st.session_state.demo_step_idx = 0
        st.rerun()


# ── Screen: CHAT ─────────────────────────────────────────────────────────────
def screen_chat():
    lang = st.session_state.lang
    render_hero(lang, compact=True)
    render_guidance_bar(lang, st.session_state.guidance_level)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if not st.session_state.conversation:
        greeting = t("greeting", lang)
        st.markdown(f'<div class="bubble-ai">🌸 {greeting}</div>', unsafe_allow_html=True)

    for msg in st.session_state.conversation:
        if msg["role"] == "user":
            st.markdown(f'<div class="bubble-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            txt = msg["content"]
            teach = msg.get("teach_mode", False)
            if teach:
                badge = t("teach_me_badge", lang)
                st.markdown(
                    f'<div class="teach-card">'
                    f'<span class="teach-badge">🧑‍🏫 {badge}</span>'
                    f'<p class="teach-body">{txt}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="bubble-ai">🌸 {txt}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-size:0.78rem;font-weight:600;color:#6b7280;margin-bottom:0.4rem;">'
        f'{t("type_your_need", lang)}</p>',
        unsafe_allow_html=True,
    )

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            label="",
            placeholder=t("placeholder", lang),
            key="chat_input",
            label_visibility="collapsed",
        )
        col1, col2 = st.columns([4, 1])
        with col1:
            submitted = st.form_submit_button(t("send_btn", lang), use_container_width=True)
        with col2:
            voiced = st.form_submit_button("🎤", use_container_width=True)

    if submitted or voiced:
        if not user_input or not user_input.strip():
            st.warning(t("empty_input", lang))
            return

        detected_lang = detect_language(user_input)
        if detected_lang != lang:
            st.session_state.lang = detected_lang
            lang = detected_lang

        st.session_state.conversation.append({"role": "user", "content": user_input})

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

        if result.get("confusion_detected"):
            st.session_state.confusion_count += 1
        st.session_state.guidance_level = result.get("guidance_level", st.session_state.guidance_level)
        st.session_state.teach_me_active = result.get("teach_mode", False)

        if result.get("intent") and result["intent"] not in ("confused", "unknown"):
            st.session_state.intent = result["intent"]

        st.session_state.conversation.append({
            "role": "ai",
            "content": result["response"],
            "teach_mode": result.get("teach_mode", False),
        })

        user_turns = sum(1 for m in st.session_state.conversation if m["role"] == "user")
        if user_turns >= 2 and st.session_state.intent:
            st.session_state.matched_service = map_intent_to_service_category(st.session_state.intent)
            st.session_state.screen = "workflow"

        st.rerun()

    st.markdown(
        f'<p class="voice-note">🎤 {t("voice_unavailable", lang)}</p>',
        unsafe_allow_html=True,
    )

    if st.button(t("home_btn", lang), key="chat_home", use_container_width=True):
        go_home()


# ── Screen: WORKFLOW ─────────────────────────────────────────────────────────
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

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if GuidanceEngine.is_teach_me(level):
        badge = t("teach_me_badge", lang)
        explain = step_content.get("teach_explanation", "")
        st.markdown(
            f'<div class="teach-card">'
            f'<span class="teach-badge">🧑‍🏫 {badge}</span>'
            f'<span class="teach-icon">{icon}</span>'
            f'<p class="teach-title">{step_content["title"]}</p>'
            f'<p class="teach-body">{step_content["prompt"]}</p>'
            + (f'<div class="teach-explain">{explain}</div>' if explain else "")
            + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="card">'
            f'<p style="font-size:1.75rem;margin:0 0 0.3rem;">{icon}</p>'
            f'<h3 style="font-size:1.15rem;font-weight:700;color:#1c1c1e;margin:0 0 0.35rem;">'
            f'{step_content["title"]}</h3>'
            f'<p style="color:#6b7280;font-size:0.95rem;margin:0;">'
            f'{step_content["prompt"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if step_name == "phone":
        st.markdown(
            f'<div class="privacy-note">🔒 {t("phone_warning", lang)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    with st.form(f"wf_{step_idx}"):
        if step_name == "age":
            val = st.number_input(
                label="",
                min_value=5, max_value=110, value=25, step=1,
                label_visibility="collapsed", key=f"inp_{step_name}",
            )
        else:
            val = st.text_input(
                label="",
                placeholder="...",
                label_visibility="collapsed",
                key=f"inp_{step_name}",
            )
        help_lbl = "உதவி ❓" if lang == "ta" else "❓ Help"
        col1, col2 = st.columns([3, 2])
        with col1:
            submitted = st.form_submit_button(t("next_btn", lang), use_container_width=True)
        with col2:
            confused_btn = st.form_submit_button(help_lbl, use_container_width=True)

    if confused_btn:
        st.session_state.confusion_count += 1
        st.session_state.guidance_level = GuidanceEngine.escalate(level, st.session_state.confusion_count)
        st.session_state.teach_me_active = st.session_state.guidance_level >= 3
        st.rerun()

    if submitted:
        val_str = str(val).strip()
        if not val_str:
            st.warning(t("empty_input", lang))
            return
        if step_name == "phone" and not validate_phone(val_str):
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

    if GuidanceEngine.is_teach_me(level):
        if st.button(t("understand_btn", lang), key="understand_btn", use_container_width=True):
            st.rerun()

    if st.button(t("home_btn", lang), key="wf_home", use_container_width=True):
        go_home()


# ── Screen: SERVICE MATCH ─────────────────────────────────────────────────────
def screen_match():
    lang = st.session_state.lang
    level = st.session_state.guidance_level
    render_hero(lang, compact=True)
    render_guidance_bar(lang, level)

    service_id = st.session_state.matched_service or "skill_demo"
    service = SERVICES.get(service_id, list(SERVICES.values())[0] if SERVICES else {})

    nk = "name_ta" if lang == "ta" else "name"
    ck = "category_ta" if lang == "ta" else "category"
    dk = "description_ta" if lang == "ta" else "description"
    wk = "why_relevant_ta" if lang == "ta" else "why_relevant"
    rk = "requirements_ta" if lang == "ta" else "requirements"

    st.markdown(f'<div class="demo-badge">🔬 {t("demo_badge", lang)}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div style="margin:0.75rem 0 0.5rem;">'
        f'<p style="font-size:0.72rem;font-weight:600;color:#9ca3af;letter-spacing:1.5px;'
        f'text-transform:uppercase;margin:0 0 0.25rem;">MATCHED RESOURCE</p>'
        f'<h2 style="font-size:1.3rem;font-weight:700;color:#1c1c1e;margin:0;">'
        f'{t("match_found", lang)}</h2>'
        f'</div>',
        unsafe_allow_html=True,
    )

    reqs = service.get(rk, service.get("requirements", []))
    req_html = "".join(
        f'<div class="req-item"><div class="req-dot"></div>{r}</div>' for r in reqs
    )

    why = service.get(wk, service.get("why_relevant", ""))
    if len(why) > 60:
        why = why[:60] + "..."

    st.markdown(
        f'<div class="service-card">'
        f'<p class="s-name">{service.get(nk, service.get("name",""))}</p>'
        f'<span class="s-cat">{service.get(ck, service.get("category",""))}</span>'
        f'<p class="s-desc">{service.get(dk, service.get("description",""))}</p>'
        f'<p style="font-size:0.72rem;font-weight:600;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.5px;margin:0.5rem 0 0.3rem;">{t("match_requirements", lang)}</p>'
        f'{req_html}'
        f'<div class="s-row"><span>{t("match_why", lang)}</span>'
        f'<span class="s-val">{why}</span></div>'
        f'<div class="s-row"><span>{t("match_steps", lang)}</span>'
        f'<span class="s-val">{service.get("steps", 4)} steps</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="demo-badge">⚠️ {t("demo_notice", lang)}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button(t("continue_btn", lang), key="match_cont", use_container_width=True):
        st.session_state.screen = "complete"
        st.rerun()

    if st.button(t("home_btn", lang), key="match_home", use_container_width=True):
        go_home()


# ── Screen: COMPLETE ─────────────────────────────────────────────────────────
def screen_complete():
    lang = st.session_state.lang

    checks = [
        t("complete_understood", lang),
        t("complete_identified", lang),
        t("complete_explained", lang),
        t("complete_prepared", lang),
    ]
    rows_html = "".join(
        f'<div class="c-row"><div class="c-icon">✓</div>{c}</div>'
        for c in checks
    )

    st.markdown(
        f'<div class="complete-wrap">'
        f'<span class="c-emoji">🎉</span>'
        f'<h1 class="c-title">{t("complete_title", lang)}</h1>'
        f'<p class="c-sub">{t("complete_subtitle", lang)}</p>'
        f'<div class="check-list">{rows_html}</div>'
        f'<p class="c-disc">{t("complete_disclaimer", lang)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("start_again_btn", lang), key="cr", use_container_width=True):
            go_home()
    with col2:
        if st.button(t("home_btn", lang), key="ch", use_container_width=True):
            go_home()


# ── Screen: DEMO ─────────────────────────────────────────────────────────────
def screen_demo():
    lang = st.session_state.lang
    render_hero(lang, compact=True)

    st.markdown(
        f'<div class="demo-hdr">'
        f'<h2>🎬 {t("demo_mode_title", lang)}</h2>'
        f'<p>{t("demo_mode_desc", lang)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    current_idx = st.session_state.demo_step_idx
    played = DEMO_SCRIPT[:current_idx]

    for step in played:
        actor = step["actor"]
        text = step["text"]
        teach = step.get("teach_mode", False)
        level = step.get("guidance_level", 1)
        gl = GuidanceEngine.level_label(level, lang)

        if actor == "user":
            st.markdown(f'<div class="d-user">🧑 {text}</div>', unsafe_allow_html=True)
        else:
            if teach or level >= 3:
                badge = t("teach_me_badge", lang)
                st.markdown(
                    f'<div class="teach-card" style="margin:0.35rem 0;">'
                    f'<span class="teach-badge">🧑‍🏫 {badge}</span>'
                    f'<p class="teach-body">🌸 {text}</p>'
                    f'<span class="d-tag">{gl}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            elif level == 2:
                st.markdown(
                    f'<div class="d-ai" style="border-left-color:#f59e0b;">'
                    f'🌸 {text}<span class="d-tag">{gl}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="d-ai">🌸 {text}<span class="d-tag">{gl}</span></div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if current_idx < DEMO_STEPS_COUNT:
        nxt = DEMO_SCRIPT[current_idx]
        desc = nxt.get("description", "")
        st.markdown(
            f'<p style="font-size:0.75rem;color:#9ca3af;font-style:italic;margin-bottom:0.4rem;">'
            f'Next: {desc}</p>',
            unsafe_allow_html=True,
        )
        label = t("demo_step_label", lang, n=current_idx + 1, total=DEMO_STEPS_COUNT)
        if st.button(f"▶  {label}", key="dn", use_container_width=True):
            st.session_state.demo_step_idx += 1
            st.rerun()
    else:
        st.markdown(
            f'<div class="complete-wrap" style="padding:1.75rem;">'
            f'<span class="c-emoji">🎉</span>'
            f'<p class="c-title" style="font-size:1.6rem;">{t("demo_complete", lang)}</p>'
            f'<p class="c-disc">{t("complete_disclaimer", lang)}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(t("demo_restart", lang), key="dr", use_container_width=True):
            st.session_state.demo_step_idx = 0
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("start_again_btn", lang), key="dr2", use_container_width=True):
            st.session_state.demo_step_idx = 0
            st.rerun()
    with col2:
        if st.button(t("home_btn", lang), key="dh", use_container_width=True):
            go_home()


# ── Router ────────────────────────────────────────────────────────────────────
scr = st.session_state.screen
if scr == "home":
    screen_home()
elif scr == "chat":
    screen_chat()
elif scr == "workflow":
    screen_workflow()
elif scr == "match":
    screen_match()
elif scr == "complete":
    screen_complete()
elif scr == "demo":
    screen_demo()
else:
    go_home()
