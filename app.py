"""
THOZHI -- Adaptive Zero-Knowledge Government Service Assistant
SakhiStep AI | Hackathon Prototype

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
    page_title="THOZHI -- SakhiStep AI",
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

# ── Premium Dark CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400&family=Space+Grotesk:wght@500;600;700&display=swap');

*, html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

.stApp { background: #08081a; min-height: 100vh; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding-top: 1.5rem !important; max-width: 700px !important; }

/* ── Animated ambient orbs ── */
.orb-bg {
    position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;
}
.orb {
    position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.45;
}
.orb-1 {
    width: 60vw; height: 60vw; top: -25%; left: -20%;
    background: radial-gradient(circle, #7c3aed 0%, transparent 65%);
    animation: o1 9s ease-in-out infinite alternate;
}
.orb-2 {
    width: 50vw; height: 50vw; bottom: -20%; right: -15%;
    background: radial-gradient(circle, #db2777 0%, transparent 65%);
    animation: o2 11s ease-in-out infinite alternate;
}
.orb-3 {
    width: 35vw; height: 35vw; top: 40%; left: 55%; opacity: 0.2;
    background: radial-gradient(circle, #0ea5e9 0%, transparent 65%);
    animation: o3 13s ease-in-out infinite alternate;
}
@keyframes o1 { to { transform: translate(5vw, 6vh) scale(1.15); } }
@keyframes o2 { to { transform: translate(-5vw, -5vh) scale(1.12); } }
@keyframes o3 { to { transform: translate(-4vw, 4vh); } }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #2e0f63 0%, #6d28d9 42%, #a855f7 72%, #be185d 100%);
    border-radius: 28px;
    padding: 3rem 2.5rem 2.6rem;
    text-align: center;
    margin-bottom: 1.75rem;
    box-shadow: 0 28px 80px rgba(109,40,217,0.55), 0 0 0 1px rgba(255,255,255,0.07);
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse at 22% 18%, rgba(255,255,255,0.18) 0%, transparent 45%),
        radial-gradient(ellipse at 78% 82%, rgba(219,39,119,0.22) 0%, transparent 45%);
    pointer-events: none;
}
.hero-banner::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 80px;
    background: linear-gradient(to top, rgba(8,8,26,0.35), transparent);
    pointer-events: none;
}
.hero-glow {
    position: absolute;
    width: 60%; height: 50px; bottom: -15px; left: 20%;
    background: radial-gradient(ellipse, rgba(168,85,247,0.5) 0%, transparent 70%);
    filter: blur(22px);
}
.hero-emoji {
    font-size: 4rem; display: block; margin-bottom: 0.5rem;
    animation: fe 3.5s ease-in-out infinite;
    filter: drop-shadow(0 8px 20px rgba(255,255,255,0.3));
    position: relative; z-index: 1;
}
@keyframes fe {
    0%,100% { transform: translateY(0) rotate(-3deg); }
    50%      { transform: translateY(-12px) rotate(3deg); }
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 3.2rem; font-weight: 700; color: white;
    letter-spacing: 5px; margin: 0 0 0.45rem;
    text-shadow: 0 4px 24px rgba(0,0,0,0.3); line-height: 1;
    position: relative; z-index: 1;
}
.hero-tagline {
    font-size: 1rem; color: rgba(255,255,255,0.9); margin: 0 0 0.2rem; font-weight: 600;
    position: relative; z-index: 1;
}
.hero-tagline-alt {
    font-size: 0.85rem; color: rgba(255,255,255,0.5); margin: 0 0 1rem;
    position: relative; z-index: 1;
}
.hero-pill {
    display: inline-block;
    background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.18); border-radius: 50px;
    padding: 0.38rem 1.2rem; font-size: 0.78rem; color: rgba(255,255,255,0.8);
    position: relative; z-index: 1;
}

/* ── Compact hero ── */
.hero-compact {
    background: linear-gradient(135deg, #2e0f63 0%, #7c3aed 60%, #be185d 100%);
    border-radius: 20px; padding: 1.1rem 1.75rem;
    display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem;
    box-shadow: 0 8px 36px rgba(109,40,217,0.5), 0 0 0 1px rgba(255,255,255,0.06);
}
.hero-compact-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.55rem; font-weight: 700; color: white; letter-spacing: 2px; margin: 0;
}
.hero-compact-tag { font-size: 0.73rem; color: rgba(255,255,255,0.5); margin: 0.1rem 0 0; }

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.042);
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.09); border-radius: 20px;
    padding: 1.75rem; margin: 0.75rem 0;
    box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.07);
}

/* ── Language section ── */
.lang-section {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1rem 1.5rem; text-align: center; margin: 0.75rem 0;
}
.lang-title {
    color: rgba(255,255,255,0.4); font-size: 0.7rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.75rem;
}

/* ── Guidance bar ── */
.guidance-bar {
    display: flex; align-items: center; gap: 0.7rem;
    background: linear-gradient(90deg, rgba(109,40,217,0.2) 0%, rgba(168,85,247,0.08) 100%);
    border: 1px solid rgba(109,40,217,0.35); border-radius: 14px;
    padding: 0.85rem 1.25rem; margin-bottom: 1rem;
}
.guidance-bar-teach {
    background: linear-gradient(90deg, rgba(245,158,11,0.22) 0%, rgba(251,191,36,0.08) 100%);
    border-color: rgba(245,158,11,0.45);
}
.gb-label { font-weight: 700; font-size: 0.8rem; color: rgba(255,255,255,0.8); }
.gb-level { font-size: 0.96rem; color: #c4b5fd; margin-left: auto; }
.guidance-bar-teach .gb-level { color: #fbbf24; }

/* ── Teach-Me card ── */
.teach-card {
    background: linear-gradient(135deg, rgba(245,158,11,0.17) 0%, rgba(251,191,36,0.06) 100%);
    border: 2px solid rgba(245,158,11,0.42); border-radius: 20px;
    padding: 1.75rem; margin: 0.75rem 0;
    box-shadow: 0 8px 36px rgba(245,158,11,0.14);
    position: relative; overflow: hidden;
}
.teach-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 50%, #f59e0b 100%);
    background-size: 200%; animation: sBar 2.5s linear infinite;
}
@keyframes sBar { 0%{background-position:0%} 100%{background-position:200%} }
.teach-badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white; font-weight: 800; font-size: 0.74rem;
    padding: 0.28rem 0.85rem; border-radius: 50px; margin-bottom: 0.7rem;
    box-shadow: 0 4px 14px rgba(245,158,11,0.4);
}
.teach-icon { font-size: 2rem; margin-bottom: 0.35rem; display: block; }
.teach-title { font-size: 1.35rem; font-weight: 800; color: #fef3c7; margin: 0.2rem 0; }
.teach-body { color: rgba(254,243,199,0.88); font-size: 1rem; line-height: 1.65; margin: 0.5rem 0 0; }
.teach-explain {
    background: rgba(0,0,0,0.22); border-radius: 12px;
    padding: 0.85rem 1rem; margin-top: 0.75rem;
    color: #fde68a; font-size: 0.9rem; line-height: 1.6;
    border-left: 3px solid rgba(245,158,11,0.6);
}

/* ── Step progress ── */
.step-hdr { text-align: center; margin: 0.25rem 0 1.25rem; }
.step-lbl {
    color: rgba(255,255,255,0.35); font-size: 0.7rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.65rem;
    display: block;
}
.step-track { display: flex; align-items: center; justify-content: center; }
.sn {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 800; transition: all 0.3s ease;
    position: relative; flex-shrink: 0;
}
.sn-done {
    background: linear-gradient(135deg, #10b981, #059669); color: white;
    box-shadow: 0 0 16px rgba(16,185,129,0.55);
}
.sn-active {
    background: linear-gradient(135deg, #7c3aed, #a855f7); color: white;
    box-shadow: 0 0 22px rgba(124,58,237,0.7);
    animation: pn 2s ease-in-out infinite;
}
.sn-pending {
    background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.08);
}
@keyframes pn { 0%,100%{box-shadow:0 0 14px rgba(124,58,237,0.5)} 50%{box-shadow:0 0 30px rgba(124,58,237,0.85)} }
.sc { height: 2px; width: 38px; background: rgba(255,255,255,0.07); }
.sc-done { background: linear-gradient(90deg, #10b981, #059669); }

/* ── Chat ── */
.bubble-user {
    background: linear-gradient(135deg, #6d28d9, #a855f7);
    color: white; border-radius: 20px 20px 6px 20px;
    padding: 0.9rem 1.3rem; margin-left: 16%; margin-bottom: 0.5rem;
    font-size: 0.97rem; font-weight: 500; line-height: 1.55;
    box-shadow: 0 6px 24px rgba(109,40,217,0.42);
}
.bubble-ai {
    background: rgba(255,255,255,0.065); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.9);
    border-radius: 20px 20px 20px 6px;
    padding: 0.9rem 1.3rem; margin-right: 16%; margin-bottom: 0.5rem;
    font-size: 0.97rem; line-height: 1.55;
    box-shadow: 0 4px 20px rgba(0,0,0,0.28);
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.065) !important;
    border: 2px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important; color: white !important;
    font-size: 1.05rem !important; padding: 0.8rem 1.1rem !important;
    font-family: 'Nunito', sans-serif !important;
    transition: all 0.22s ease !important; caret-color: #a855f7 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #a855f7 !important;
    background: rgba(168,85,247,0.1) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.2), 0 4px 20px rgba(0,0,0,0.3) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: rgba(255,255,255,0.28) !important; }
.stNumberInput > div > div > input { color: white !important; }
.stNumberInput button { color: rgba(255,255,255,0.6) !important; background: rgba(255,255,255,0.07) !important; border-color: rgba(255,255,255,0.08) !important; }
.stTextInput label, .stNumberInput label, .stTextArea label {
    color: rgba(255,255,255,0.5) !important; font-weight: 600 !important; font-size: 0.82rem !important;
}

/* ── Buttons -- glass base ── */
.stButton > button {
    border-radius: 14px !important; font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    padding: 0.8rem 1.25rem !important; width: 100% !important;
    letter-spacing: 0.3px !important;
    background: rgba(255,255,255,0.07) !important; color: rgba(255,255,255,0.88) !important;
    border: 1px solid rgba(255,255,255,0.11) !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.13) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.2) !important;
}
.stButton > button:active { transform: scale(0.97) translateY(0) !important; }

/* ── Service card ── */
.service-card {
    background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(5,150,105,0.04) 100%);
    border: 1.5px solid rgba(16,185,129,0.28); border-radius: 20px;
    padding: 1.75rem; margin: 0.75rem 0;
    box-shadow: 0 8px 32px rgba(16,185,129,0.08);
    position: relative; overflow: hidden;
}
.service-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #10b981, #34d399, #10b981);
}
.s-name { font-size: 1.25rem; font-weight: 800; color: #6ee7b7; margin: 0 0 0.4rem; }
.s-cat {
    display: inline-block;
    background: rgba(16,185,129,0.18); border: 1px solid rgba(16,185,129,0.3);
    color: #6ee7b7; font-size: 0.7rem; font-weight: 700;
    padding: 0.2rem 0.7rem; border-radius: 50px; margin-bottom: 0.75rem;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.s-desc { color: rgba(255,255,255,0.62); font-size: 0.88rem; line-height: 1.6; margin-bottom: 0.75rem; }
.req-item { display: flex; align-items: center; gap: 0.5rem; color: rgba(255,255,255,0.68); font-size: 0.87rem; padding: 0.2rem 0; }
.req-dot { width: 5px; height: 5px; border-radius: 50%; background: #34d399; flex-shrink: 0; }
.s-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0; border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 0.5rem; font-size: 0.83rem; color: rgba(255,255,255,0.5);
}
.s-val { color: #a7f3d0; font-weight: 700; }

/* ── Demo badge ── */
.demo-badge {
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    background: rgba(251,146,60,0.12); border: 1px solid rgba(251,146,60,0.28);
    border-radius: 12px; padding: 0.55rem 1rem;
    color: #fdba74; font-size: 0.78rem; font-weight: 700; margin: 0.5rem 0;
}

/* ── Demo screen ── */
.demo-hdr {
    background: linear-gradient(135deg, #1e1b4b, #312e81, #4c1d95);
    border: 1px solid rgba(99,102,241,0.28); border-radius: 20px;
    padding: 1.2rem 1.75rem; text-align: center; margin-bottom: 1rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.18);
}
.demo-hdr h2 { color: white !important; font-size: 1.25rem !important; margin: 0 0 0.2rem !important; font-family: 'Space Grotesk', sans-serif !important; }
.demo-hdr p { color: rgba(255,255,255,0.5); font-size: 0.82rem; margin: 0; }
.d-user {
    background: rgba(167,139,250,0.09); border: 1px solid rgba(167,139,250,0.18);
    border-left: 3px solid #a78bfa; border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem; margin: 0.4rem 0;
    color: rgba(255,255,255,0.68); font-style: italic; font-size: 0.88rem;
}
.d-ai {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #7c3aed; border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem; margin: 0.4rem 0;
    color: rgba(255,255,255,0.85); font-size: 0.88rem; line-height: 1.6;
}
.d-tag { font-size: 0.66rem; color: rgba(255,255,255,0.32); margin-top: 0.22rem; font-style: normal; }

/* ── Complete screen ── */
.complete-wrap {
    background: linear-gradient(135deg, rgba(109,40,217,0.17) 0%, rgba(219,39,119,0.11) 100%);
    border: 1px solid rgba(168,85,247,0.22); border-radius: 28px;
    padding: 2.75rem 2rem; text-align: center;
    box-shadow: 0 24px 72px rgba(109,40,217,0.18);
    position: relative; overflow: hidden;
}
.complete-wrap::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899, #a855f7, #7c3aed);
    background-size: 200%; animation: rBar 3s linear infinite;
}
@keyframes rBar { 0%{background-position:0%} 100%{background-position:200%} }
.c-emoji {
    font-size: 4.5rem; display: block; margin-bottom: 0.75rem;
    animation: bIn 0.65s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes bIn { 0%{transform:scale(0);opacity:0} 100%{transform:scale(1);opacity:1} }
.c-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2.2rem; font-weight: 700; color: white; margin: 0 0 0.35rem;
}
.c-sub { color: #c4b5fd; font-size: 1rem; font-weight: 600; margin: 0 0 1.75rem; }
.check-list {
    background: rgba(255,255,255,0.05); border-radius: 16px;
    padding: 1.1rem 1.25rem; text-align: left; margin: 0 auto 1.5rem;
}
.c-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.45rem 0; font-size: 0.92rem; font-weight: 600;
    color: rgba(255,255,255,0.82); border-bottom: 1px solid rgba(255,255,255,0.05);
}
.c-row:last-child { border-bottom: none; }
.c-icon {
    width: 24px; height: 24px; border-radius: 50%;
    background: linear-gradient(135deg, #10b981, #059669);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(16,185,129,0.4);
}
.c-disc { font-size: 0.71rem; color: rgba(255,255,255,0.27); margin-top: 1.25rem; }

/* ── Misc ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.25), transparent);
    margin: 1.25rem 0; border: none;
}
.section-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: rgba(255,255,255,0.32); margin: 1rem 0 0.5rem;
}
.privacy-note {
    background: rgba(234,179,8,0.08); border-left: 3px solid rgba(234,179,8,0.45);
    border-radius: 0 10px 10px 0; padding: 0.6rem 1rem;
    font-size: 0.77rem; color: #fef08a; margin: 0.5rem 0; line-height: 1.5;
}
.voice-note {
    text-align: center; font-size: 0.72rem; color: rgba(255,255,255,0.26);
    margin-top: 0.5rem; font-style: italic;
}
.how-title {
    font-size: 1.05rem; font-weight: 700; color: rgba(255,255,255,0.82);
    text-align: center; margin: 0.25rem 0 0.75rem;
}
.stAlert {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important; color: rgba(255,255,255,0.75) !important;
}
/* ── Input wrap container ── */
.input-wrap {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px; padding: 1.25rem; margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Inject animated orb background once
st.markdown(
    '<div class="orb-bg"><div class="orb orb-1"></div>'
    '<div class="orb orb-2"></div><div class="orb orb-3"></div></div>',
    unsafe_allow_html=True,
)

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
    name_en = "THOZHI"
    name_ta = "\u0ba4\u0bcb\u0bb4\u0bbf"
    display = name_ta if lang == "ta" else name_en
    tagline = t("tagline", lang)
    tagline_alt = t("tagline", "ta" if lang == "en" else "en")
    subtitle = t("subtitle", lang)

    if compact:
        st.markdown(
            f'<div class="hero-compact">'
            f'<span style="font-size:2rem;">🌸</span>'
            f'<div>'
            f'<p class="hero-compact-title">{display}</p>'
            f'<p class="hero-compact-tag">{tagline}</p>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="hero-banner">'
            f'<div class="hero-glow"></div>'
            f'<span class="hero-emoji">🌸</span>'
            f'<h1 class="hero-title">{display}</h1>'
            f'<p class="hero-tagline">{tagline}</p>'
            f'<p class="hero-tagline-alt">{tagline_alt}</p>'
            f'<span class="hero-pill">{subtitle}</span>'
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
        f'<span style="font-size:1.3rem;">🌱</span>'
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
            f'<span class="teach-badge">🧑‍🏫 {badge}</span><br>'
            f'<span style="color:rgba(254,243,199,0.85);font-size:1rem;font-weight:600;">{intro}</span>'
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

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    render_guidance_bar(lang, st.session_state.guidance_level)
    st.markdown(
        f'<p style="font-size:0.73rem;color:rgba(255,255,255,0.3);text-align:center;margin-top:-0.5rem;">'
        f'{t("guidance_auto", lang)}</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
    st.markdown(f'<p class="how-title">{t("how_to_start", lang)}</p>', unsafe_allow_html=True)

    # CTA buttons with special gradient for primary
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stButton"]:nth-of-type(1)) button {
        background: linear-gradient(135deg, #6d28d9 0%, #a855f7 100%) !important;
        color: white !important; border-color: transparent !important;
        box-shadow: 0 8px 30px rgba(109,40,217,0.55) !important;
        font-size: 1.1rem !important; padding: 0.95rem 1.25rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    speak_label = t("speak_btn", lang)
    type_label = t("type_btn", lang)
    demo_label = t("demo_btn", lang)

    if st.button(speak_label, key="start_voice", use_container_width=True):
        st.session_state.screen = "chat"
        st.rerun()

    if st.button(type_label, key="start_type", use_container_width=True):
        st.session_state.screen = "chat"
        st.rerun()

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    if st.button(demo_label, key="demo_start", use_container_width=True):
        st.session_state.screen = "demo"
        st.session_state.demo_step_idx = 0
        st.rerun()


# ── Screen: CHAT ─────────────────────────────────────────────────────────────
def screen_chat():
    lang = st.session_state.lang
    render_hero(lang, compact=True)
    render_guidance_bar(lang, st.session_state.guidance_level)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # Greeting
    if not st.session_state.conversation:
        greeting = t("greeting", lang)
        st.markdown(f'<div class="bubble-ai">🌸 {greeting}</div>', unsafe_allow_html=True)

    # Conversation
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
                    f'<span class="teach-badge">🧑‍🏫 {badge}</span><br>'
                    f'<span class="teach-body">{txt}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="bubble-ai">🌸 {txt}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    st.markdown(
        f'<div class="input-wrap">'
        f'<p style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.45);margin:0 0 0.6rem;">'
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

    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

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
            + f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="glass-card">'
            f'<p style="font-size:2rem;margin:0 0 0.35rem;">{icon}</p>'
            f'<h2 style="font-size:1.35rem;font-weight:800;color:white;margin:0 0 0.4rem;">'
            f'{step_content["title"]}</h2>'
            f'<p style="color:rgba(255,255,255,0.68);font-size:1rem;margin:0;">'
            f'{step_content["prompt"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if step_name == "phone":
        st.markdown(
            f'<div class="privacy-note">🔒 {t("phone_warning", lang)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

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
        f'<div style="text-align:center;margin:0.75rem 0;">'
        f'<span style="font-size:2rem;">✨</span>'
        f'<h2 style="font-size:1.45rem;font-weight:800;color:white;margin:0.25rem 0 0;">'
        f'{t("match_found", lang)}</h2>'
        f'</div>',
        unsafe_allow_html=True,
    )

    reqs = service.get(rk, service.get("requirements", []))
    req_html = "".join(f'<div class="req-item"><div class="req-dot"></div>{r}</div>' for r in reqs)

    st.markdown(
        f'<div class="service-card">'
        f'<p class="s-name">{service.get(nk, service.get("name",""))}</p>'
        f'<span class="s-cat">{service.get(ck, service.get("category",""))}</span>'
        f'<p class="s-desc">{service.get(dk, service.get("description",""))}</p>'
        f'<p style="font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.45);'
        f'text-transform:uppercase;letter-spacing:1px;margin:0.5rem 0 0.3rem;">'
        f'{t("match_requirements", lang)}</p>'
        f'{req_html}'
        f'<div class="s-row"><span>{t("match_why", lang)}</span>'
        f'<span class="s-val">{service.get(wk, service.get("why_relevant",""))[:50]}...</span></div>'
        f'<div class="s-row"><span>{t("match_steps", lang)}</span>'
        f'<span class="s-val">{service.get("steps", 4)} steps</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="demo-badge">⚠️ {t("demo_notice", lang)}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

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

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
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

        if actor == "user":
            st.markdown(f'<div class="d-user">🧑 {text}</div>', unsafe_allow_html=True)
        else:
            gl = GuidanceEngine.level_label(level, lang)
            if teach or level >= 3:
                badge = t("teach_me_badge", lang)
                st.markdown(
                    f'<div class="teach-card" style="margin:0.4rem 0;">'
                    f'<span class="teach-badge">🧑‍🏫 {badge}</span>'
                    f'<p class="teach-body">🌸 {text}</p>'
                    f'<span class="d-tag">{gl}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            elif level == 2:
                st.markdown(
                    f'<div class="d-ai" style="border-left-color:#f59e0b;">'
                    f'🌸 {text}<br><span class="d-tag" style="color:#92400e;">{gl}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="d-ai">🌸 {text}<br><span class="d-tag">{gl}</span></div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    if current_idx < DEMO_STEPS_COUNT:
        nxt = DEMO_SCRIPT[current_idx]
        desc = nxt.get("description", "")
        st.markdown(
            f'<p style="font-size:0.78rem;color:rgba(255,255,255,0.35);font-style:italic;margin-bottom:0.5rem;">'
            f'⏭ {desc}</p>',
            unsafe_allow_html=True,
        )
        label = t("demo_step_label", lang, n=current_idx + 1, total=DEMO_STEPS_COUNT)
        if st.button(f"▶  {label}", key="dn", use_container_width=True):
            st.session_state.demo_step_idx += 1
            st.rerun()
    else:
        st.markdown(
            f'<div class="complete-wrap" style="padding:2rem;">'
            f'<span class="c-emoji">🎉</span>'
            f'<p class="c-title" style="font-size:1.8rem;">{t("demo_complete", lang)}</p>'
            f'<p class="c-disc">{t("complete_disclaimer", lang)}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(t("demo_restart", lang), key="dr", use_container_width=True):
            st.session_state.demo_step_idx = 0
            st.rerun()

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
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
