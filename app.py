"""
app.py  —  Para's Reading Adventure
AI-Enhanced Speech-to-Text Reading Assessment Tool

Cartoon theme | Green & Yellow accents | Child-friendly design
STT Engine: AssemblyAI Universal-3 Pro
NLP Engine: Python difflib SequenceMatcher

Course : ITE153 — Intro to AI and Expert Systems
"""

import streamlit as st
from stt import transcribe
from accuracy import calculate_accuracy

# ─────────────────────────────────────────────────────────────────────────────
#  ✏️  PASTE YOUR ASSEMBLYAI API KEY HERE
# ─────────────────────────────────────────────────────────────────────────────

ASSEMBLYAI_API_KEY = "a8c5f199bd1a48c0a286b61f4f063641"

# ─────────────────────────────────────────────────────────────────────────────
#  Fixed Reading Passage
# ─────────────────────────────────────────────────────────────────────────────

PASSAGE = (
    "Para flies away from the houses and into the market. "
    "She must look for some fruits and food she can eat. "
    "She is having fun, but wants to go home. "
    "It is getting dark. "
    "There are many cars on the road because it is the end of the work day. "
    "Then, she sees something! "
    "Para stops flying and lands on top of a parked car. "
    "She sees a police officer and he is directing traffic. "
    "He is also dancing! "
    "Para has never seen a police officer dance. "
    "The police officer is smiling. "
    "Para wants to learn more about this man."
)

# ─────────────────────────────────────────────────────────────────────────────
#  Page Configuration
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Para's Reading Adventure",
    page_icon="🦋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  Session State
# ─────────────────────────────────────────────────────────────────────────────

_defaults = {
    "page"            : "menu",
    "transcribed_text": "",
    "accuracy_result" : None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  Global CSS — Cartoon Green Theme, Child-Friendly
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Fredoka+One&display=swap');

/* ── Base ───────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Baloo 2', cursive !important;
    color: #2D5016 !important;
}
.stApp {
    background: linear-gradient(180deg, #E8F5E9 0%, #C8E6C9 30%, #A5D6A7 60%, #E8F5E9 100%) !important;
    background-attachment: fixed !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 750px;
    padding-top: 1rem;
    padding-bottom: 3rem;
    background: transparent;
}
h1, h2, h3, h4 {
    font-family: 'Fredoka One', cursive !important;
    color: #2D5016 !important;
}
p, span, label, div {
    color: #2D5016;
}

/* ── Hide sidebar toggle ────────────────────────────────────────────────── */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }

/* ── Floating leaves decoration ─────────────────────────────────────────── */
.stApp::before {
    content: "🍃 🌿 🍂 🌱";
    position: fixed;
    top: 10px;
    left: 10px;
    font-size: 30px;
    opacity: 0.15;
    pointer-events: none;
    z-index: 0;
    animation: floatLeaves 20s linear infinite;
}
.stApp::after {
    content: "🌸 🌻 🌼 🍀";
    position: fixed;
    bottom: 10px;
    right: 10px;
    font-size: 30px;
    opacity: 0.15;
    pointer-events: none;
    z-index: 0;
    animation: floatLeaves 25s linear infinite reverse;
}

@keyframes floatLeaves {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(5deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}

/* ── Primary button → Green ─────────────────────────────────────────────── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #4CAF50 !important;
    color: #ffffff !important;
    font-family: 'Fredoka One', cursive !important;
    font-size: 22px !important;
    font-weight: 400 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 16px 40px !important;
    box-shadow: 0 8px 0 #2E7D32, 0 10px 20px rgba(0,0,0,0.1) !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
    width: 100% !important;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
}
[data-testid="stButton"] > button[kind="primary"]::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.3s;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #66BB6A !important;
    box-shadow: 0 8px 0 #2E7D32, 0 12px 24px rgba(0,0,0,0.15) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover::after {
    opacity: 1;
}
[data-testid="stButton"] > button[kind="primary"]:active {
    box-shadow: 0 3px 0 #2E7D32, 0 5px 10px rgba(0,0,0,0.1) !important;
    transform: translateY(5px) !important;
}

/* ── Secondary button → Yellow ──────────────────────────────────────────── */
[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFB300 !important;
    color: #4E342E !important;
    font-family: 'Fredoka One', cursive !important;
    font-size: 18px !important;
    font-weight: 400 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 14px 32px !important;
    box-shadow: 0 6px 0 #F57F17, 0 8px 16px rgba(0,0,0,0.1) !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #FFC107 !important;
}
[data-testid="stButton"] > button[kind="secondary"]:active {
    box-shadow: 0 2px 0 #F57F17 !important;
    transform: translateY(4px) !important;
}
[data-testid="stButton"] > button:disabled {
    background: #BDBDBD !important;
    box-shadow: 0 4px 0 #9E9E9E !important;
    color: #757575 !important;
}

/* ── Text area ──────────────────────────────────────────────────────────── */
.stTextArea textarea {
    font-family: 'Baloo 2', cursive !important;
    font-size: 16px !important;
    border-radius: 18px !important;
    border: 3px solid #81C784 !important;
    background: #ffffff !important;
    color: #2D5016 !important;
}
.stTextArea textarea:focus {
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 4px rgba(76,175,80,0.15) !important;
}
.stTextArea label {
    color: #2D5016 !important;
    font-weight: 700 !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Fredoka One', cursive !important;
    font-size: 17px !important;
    font-weight: 400 !important;
    border-radius: 25px 25px 0 0 !important;
    padding: 10px 24px !important;
    color: #2D5016 !important;
    background: #C8E6C9 !important;
    border: 3px solid #A5D6A7 !important;
}
.stTabs [aria-selected="true"] {
    background: #4CAF50 !important;
    color: #ffffff !important;
    border-color: #4CAF50 !important;
}

/* ── Metric cards ───────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 3px solid #A5D6A7 !important;
    border-radius: 20px !important;
    padding: 16px 10px !important;
    box-shadow: 0 6px 0 #C8E6C9, 0 8px 16px rgba(0,0,0,0.05) !important;
    text-align: center !important;
}
[data-testid="metric-container"] label {
    font-family: 'Fredoka One', cursive !important;
    font-size: 14px !important;
    color: #4E8C2E !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Fredoka One', cursive !important;
    font-size: 32px !important;
    color: #2D5016 !important;
}

/* ── Alerts ─────────────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 18px !important;
    font-family: 'Baloo 2', cursive !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #2D5016 !important;
    border: 3px solid #A5D6A7 !important;
}
.stAlert p { color: #2D5016 !important; }

/* ── Expander ────────────────────────────────────────────────────────────── */
.stExpander {
    border: 3px solid #A5D6A7 !important;
    border-radius: 20px !important;
    background: #ffffff !important;
    box-shadow: 0 6px 0 #C8E6C9 !important;
}
details summary {
    font-family: 'Fredoka One', cursive !important;
    font-size: 18px !important;
    color: #4CAF50 !important;
    font-weight: 400 !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.stSpinner p {
    font-family: 'Fredoka One', cursive !important;
    font-size: 18px !important;
    color: #4CAF50 !important;
}

/* ── Caption / small text ───────────────────────────────────────────────── */
.stCaption, small, .caption {
    color: #4E8C2E !important;
    font-weight: 600 !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: #A5D6A7 !important; border-width: 2px !important; }

/* ── Animations ─────────────────────────────────────────────────────────── */
@keyframes bounce {
    0%,100% { transform: translateY(0px); }
    30%     { transform: translateY(-20px); }
    50%     { transform: translateY(0px); }
    70%     { transform: translateY(-10px); }
}
@keyframes wiggle {
    0%,100% { transform: rotate(0deg); }
    25%     { transform: rotate(-5deg); }
    75%     { transform: rotate(5deg); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes starPop {
    0%   { transform: scale(0) rotate(-15deg); opacity: 0; }
    60%  { transform: scale(1.3) rotate(5deg); }
    100% { transform: scale(1) rotate(0); opacity: 1; }
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%     { transform: translateY(-10px); }
}
@keyframes sparkle {
    0%,100% { opacity: 1; transform: scale(1); }
    50%     { opacity: 0.6; transform: scale(1.15); }
}

/* ── Custom HTML blocks ─────────────────────────────────────────────────── */

/* Cartoon card */
.game-card {
    background: #ffffff;
    border-radius: 24px;
    padding: 26px 28px;
    border: 4px solid #81C784;
    box-shadow: 0 8px 0 #66BB6A, 0 10px 20px rgba(0,0,0,0.08);
    margin-bottom: 18px;
    animation: fadeUp 0.5s ease;
    position: relative;
}
.game-card::before {
    content: '';
    position: absolute;
    top: -3px;
    left: 20px;
    right: 20px;
    height: 6px;
    background: #A5D6A7;
    border-radius: 0 0 10px 10px;
}

/* Passage card — green gradient */
.passage-card {
    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 50%, #81C784 100%);
    border-radius: 24px;
    padding: 24px 28px;
    color: #ffffff !important;
    font-size: 19px;
    font-weight: 600;
    line-height: 2.2;
    margin: 12px 0 18px;
    box-shadow: 0 8px 0 #388E3C, 0 10px 20px rgba(0,0,0,0.1);
    animation: fadeUp 0.5s ease;
    border: 4px solid #A5D6A7;
    position: relative;
}
.passage-card * {
    color: #ffffff !important;
}

/* Page title */
.page-title {
    font-family: 'Fredoka One', cursive !important;
    font-size: 46px;
    font-weight: 400;
    color: #2D5016;
    text-align: center;
    line-height: 1.2;
    margin: 0 0 6px;
    animation: fadeUp 0.5s ease;
    text-shadow: 3px 3px 0px rgba(76,175,80,0.2);
}

/* Bouncing butterfly */
.hero-char {
    font-size: 100px;
    text-align: center;
    display: block;
    margin: 8px 0;
    animation: bounce 2.5s ease-in-out infinite, wiggle 3s ease-in-out infinite;
    filter: drop-shadow(0 8px 10px rgba(0,0,0,0.15));
}

/* Numbered step label */
.step-label {
    font-family: 'Fredoka One', cursive;
    font-size: 24px;
    font-weight: 400;
    color: #2D5016;
    margin: 16px 0 6px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.step-num {
    background: #4CAF50;
    color: #ffffff;
    font-family: 'Fredoka One', cursive;
    font-size: 18px;
    font-weight: 400;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 5px 0 #2E7D32;
    border: 3px solid #A5D6A7;
}

/* Score page — big number */
.score-number {
    font-family: 'Fredoka One', cursive;
    font-size: 92px;
    font-weight: 400;
    text-align: center;
    line-height: 1;
    margin-bottom: 4px;
    text-shadow: 3px 3px 0px rgba(0,0,0,0.1);
}
.score-msg {
    font-family: 'Fredoka One', cursive;
    font-size: 30px;
    font-weight: 400;
    text-align: center;
    margin-top: 2px;
}
.stars-row {
    font-size: 50px;
    text-align: center;
    margin: 6px 0 10px;
    animation: starPop 0.7s cubic-bezier(.36,.07,.19,.97) both;
}

/* Diff legend pills */
.diff-legend { 
    display: flex; 
    gap: 8px; 
    flex-wrap: wrap; 
    margin: 10px 0 14px; 
    justify-content: center;
}
.diff-pill {
    border-radius: 99px;
    padding: 6px 16px;
    font-family: 'Baloo 2', cursive;
    font-size: 14px;
    font-weight: 700;
    border: 3px solid transparent;
    color: #2D5016;
    box-shadow: 0 3px 0 rgba(0,0,0,0.1);
}

/* Page header strip */
.page-header {
    background: linear-gradient(135deg, #4CAF50, #66BB6A);
    border-radius: 20px;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    box-shadow: 0 6px 0 #388E3C, 0 8px 16px rgba(0,0,0,0.1);
    border: 3px solid #A5D6A7;
}

/* How-to-play items */
.how-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin: 12px 0;
    font-size: 17px;
    font-weight: 600;
    color: #2D5016;
    padding: 10px 14px;
    background: #F1F8E9;
    border-radius: 16px;
    border: 2px solid #C8E6C9;
}
.how-icon { 
    font-size: 30px; 
    flex-shrink: 0;
    animation: float 3s ease-in-out infinite;
}

/* Menu card */
.menu-card {
    background: #ffffff;
    border-radius: 28px;
    padding: 30px;
    border: 4px solid #81C784;
    box-shadow: 0 10px 0 #66BB6A, 0 12px 24px rgba(0,0,0,0.08);
    text-align: center;
    margin: 10px 0;
    animation: fadeUp 0.6s ease;
}

/* Clouds decoration */
.cloud-decor {
    position: fixed;
    font-size: 40px;
    opacity: 0.12;
    pointer-events: none;
    z-index: 0;
    animation: float 6s ease-in-out infinite;
}

/* Audio input styling */
[data-testid="stAudioInput"] {
    background: #ffffff !important;
    border-radius: 20px !important;
    border: 3px solid #81C784 !important;
    padding: 10px !important;
    box-shadow: 0 5px 0 #A5D6A7 !important;
}

/* File uploader styling */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border-radius: 20px !important;
    border: 3px dashed #81C784 !important;
    padding: 10px !important;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
    .page-title {
        font-size: 32px;
    }
    .hero-char {
        font-size: 70px;
    }
    .score-number {
        font-size: 64px;
    }
    .score-msg {
        font-size: 22px;
    }
    .stars-row {
        font-size: 36px;
    }
    .passage-card {
        font-size: 16px;
        padding: 18px 16px;
    }
}
</style>

<!-- Decorative elements -->
<div class="cloud-decor" style="top: 5%; left: 3%;">☁️</div>
<div class="cloud-decor" style="top: 15%; right: 5%; animation-delay: 2s;">☁️</div>
<div class="cloud-decor" style="bottom: 20%; left: 8%; animation-delay: 4s; font-size: 30px;">☁️</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def score_to_stars(pct: float) -> tuple[str, str, str]:
    """Returns (star_emojis, message, hex_color)."""
    if pct >= 95:
        return "⭐⭐⭐⭐⭐", "Amazing Reader!",   "#2E7D32"
    elif pct >= 85:
        return "⭐⭐⭐⭐",   "Great Job!",         "#4CAF50"
    elif pct >= 70:
        return "⭐⭐⭐",     "Good Try!",          "#FFB300"
    elif pct >= 50:
        return "⭐⭐",       "Keep Practicing!",   "#FF8F00"
    else:
        return "⭐",         "Let's Try Again!",   "#EF6C00"


def build_child_diff_html(diff_tokens: list) -> str:
    """Renders color-coded word diff in a child-friendly style."""
    COLOR = {
        "correct"    : "#1B5E20",
        "substituted": "#E65100",
        "missed"     : "#B71C1C",
        "extra"      : "#0D47A1",
    }
    BG = {
        "correct"    : "#C8E6C9",
        "substituted": "#FFE0B2",
        "missed"     : "#FFCDD2",
        "extra"      : "#BBDEFB",
    }
    BORDER = {
        "correct"    : "#66BB6A",
        "substituted": "#FFB74D",
        "missed"     : "#EF5350",
        "extra"      : "#64B5F6",
    }
    parts = []
    for token in diff_tokens:
        w   = token["word"]
        tag = token["tag"]
        parts.append(
            f'<span style="background:{BG[tag]};color:{COLOR[tag]};'
            f'padding:5px 10px;border-radius:12px;font-weight:700;'
            f'margin:3px 3px;display:inline-block;font-size:17px;'
            f'border:2px solid {BORDER[tag]};'
            f'box-shadow: 0 2px 0 {BORDER[tag]};">{w}</span>'
        )
    return (
        "<p style='font-family:Baloo 2,cursive;"
        "line-height:2.8;font-size:17px;color:#2D5016;'>"
        + " ".join(parts) + "</p>"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Page: Main Menu
# ─────────────────────────────────────────────────────────────────────────────

def show_menu():
    # Hero section
    st.markdown('<span class="hero-char">🦋</span>', unsafe_allow_html=True)

    st.markdown(
        '<h1 class="page-title">Para\'s Reading<br>Adventure!</h1>',
        unsafe_allow_html=True,
    )
    
    # Welcome message in a cute card
    st.markdown("""
    <div class="menu-card">
        <p style="font-size:20px;font-weight:700;color:#2D5016;margin:0;line-height:1.6;">
            🌟 Welcome, little reader! 🌟
        </p>
        <p style="font-size:16px;color:#4E8C2E;margin:8px 0 0;font-weight:600;">
            Help Para the butterfly read her story!<br>
            Read out loud and earn shiny stars! ⭐
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Start button
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("🎮  Start Reading!", type="primary", key="btn_start"):
            st.session_state.page = "reading"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # How to Play expander
    with st.expander("📖  How to Play"):
        st.markdown("""
<div class="how-item">
    <span class="how-icon">1️⃣</span>
    <span>Read the story shown on the screen <b style="color:#4CAF50;">carefully</b>.</span>
</div>

<div class="how-item">
    <span class="how-icon">2️⃣</span>
    <span>Press the <b style="color:#4CAF50;">microphone button</b> 🎙️ and read the story out loud!</span>
</div>

<div class="how-item">
    <span class="how-icon">3️⃣</span>
    <span>Press <b style="color:#4CAF50;">Transcribe</b> to turn your voice into words on the screen.</span>
</div>

<div class="how-item">
    <span class="how-icon">4️⃣</span>
    <span>Press <b style="color:#4CAF50;">Check My Score!</b> to see how many stars you earned! ⭐</span>
</div>

<div class="how-item">
    <span class="how-icon">🏆</span>
    <span>Try to earn <b style="color:#FFB300;">5 stars!</b> You can do it, superstar! 🌟</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Fun facts or encouragement
    st.markdown("""
    <div style="text-align:center;padding:16px;background:#F1F8E9;border-radius:20px;
                border:3px solid #C8E6C9;box-shadow:0 5px 0 #A5D6A7;">
        <p style="font-size:16px;font-weight:700;color:#4CAF50;margin:0;">
            🦋 Did you know? Para means "butterfly" in some languages!
        </p>
        <p style="font-size:14px;color:#4E8C2E;margin:4px 0 0;font-weight:600;">
            Just like a butterfly, your reading will soar! 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="text-align:center;font-size:13px;color:#66BB6A;margin-top:36px;font-weight:600;">'
        'Powered by AssemblyAI Universal-3 Pro &nbsp;|&nbsp; '
        'ITE153 — Intro to AI and Expert Systems</p>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Page: Reading Assessment
# ─────────────────────────────────────────────────────────────────────────────

def show_reading():
    # ── Top bar ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="page-header">'
        '<span style="font-family:Fredoka One,cursive;font-size:24px;'
        'font-weight:400;color:#ffffff;">🦋 Para\'s Story</span>'
        '<span style="font-size:28px;">📖</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("🏠 Menu", type="secondary", key="back_menu"):
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result  = None
            st.session_state.page = "menu"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 1: Read the Passage ─────────────────────────────────────────────
    st.markdown(
        '<div class="step-label">'
        '<span class="step-num">1</span> 📚 Read this passage out loud!'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="passage-card">{PASSAGE}</div>', unsafe_allow_html=True)

    # ── Step 2: Record or Upload ─────────────────────────────────────────────
    st.markdown(
        '<div class="step-label">'
        '<span class="step-num">2</span> 🎙️ Record yourself reading!'
        '</div>',
        unsafe_allow_html=True,
    )

    tab_mic, tab_file = st.tabs(["🎙️  Microphone", "📂  Upload File"])

    with tab_mic:
        st.caption(
            "Press the microphone button, read the story aloud, "
            "then press it again to stop recording."
        )
        audio_val = st.audio_input("Record", label_visibility="collapsed", key="mic_input")
        if audio_val is not None:
            st.audio(audio_val, format="audio/wav")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔊  Transcribe My Recording", type="primary", key="btn_mic"):
                with st.spinner("✨ AssemblyAI is listening to your reading..."):
                    text, err = transcribe(audio_val.getvalue(), ASSEMBLYAI_API_KEY)
                if err:
                    st.error(f"Oops! {err}")
                else:
                    st.session_state.transcribed_text = text
                    st.session_state["trans_display"] = text
                    st.session_state.accuracy_result  = None
                    st.rerun()

    with tab_file:
        st.caption("Upload a WAV or MP3 recording of yourself reading.")
        uploaded = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "ogg", "m4a"],
            label_visibility="collapsed",
            key="file_upload",
        )
        if uploaded is not None:
            st.audio(uploaded, format=uploaded.type)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔊  Transcribe File", type="primary", key="btn_file"):
                with st.spinner("✨ AssemblyAI is listening to your reading..."):
                    text, err = transcribe(uploaded.read(), ASSEMBLYAI_API_KEY)
                if err:
                    st.error(f"Oops! {err}")
                else:
                    st.session_state.transcribed_text = text
                    st.session_state["trans_display"] = text
                    st.session_state.accuracy_result  = None
                    st.rerun()

    # ── Step 3: Review Transcription ─────────────────────────────────────────
    st.markdown(
        '<div class="step-label">'
        '<span class="step-num">3</span> ✏️ What the computer heard:'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("You can fix any mistakes here before checking your score. 🧐")

    transcribed = st.text_area(
        "Transcription",
        value=st.session_state.transcribed_text,
        placeholder="Your words will appear here after you transcribe your recording...",
        height=130,
        label_visibility="collapsed",
        key="trans_display",
    )
    st.session_state.transcribed_text = transcribed

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Check Score ──────────────────────────────────────────────────────────
    can_score = bool(transcribed.strip())
    
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button(
            "⭐  Check My Score!",
            type="primary",
            disabled=not can_score,
            key="btn_score",
        ):
            result = calculate_accuracy(PASSAGE, transcribed)
            st.session_state.accuracy_result = result
            st.session_state.page = "results"
            st.rerun()

    if not can_score:
        st.markdown("""
        <div style="text-align:center;padding:12px;background:#FFF9C4;border-radius:16px;
                    border:2px solid #FFE082;margin-top:10px;">
            <p style="font-size:15px;color:#F57F17;font-weight:700;margin:0;">
                🎙️ Record and transcribe your reading first, then press Check My Score!
            </p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Page: Results
# ─────────────────────────────────────────────────────────────────────────────

def show_results():
    result = st.session_state.accuracy_result
    if result is None:
        st.warning("No results yet. Go back and read the passage first!")
        if st.button("Go Back", type="secondary"):
            st.session_state.page = "reading"
            st.rerun()
        return

    pct   = result["accuracy_pct"]
    stars, msg, color = score_to_stars(pct)

    # ── Top bar ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="page-header">'
        '<span style="font-family:Fredoka One,cursive;font-size:24px;'
        'font-weight:400;color:#ffffff;">🏆 Your Results</span>'
        '<span style="font-size:28px;">🎉</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Score card ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="game-card" style="border-color:{color};box-shadow:0 8px 0 {color}66, 0 10px 20px rgba(0,0,0,0.08);">'
        f'<div class="stars-row">{stars}</div>'
        f'<div class="score-number" style="color:{color};">{pct}%</div>'
        f'<div class="score-msg" style="color:{color};">{msg}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Word breakdown ───────────────────────────────────────────────────────
    st.markdown(
        '<h3 style="font-family:Fredoka One,cursive;color:#2D5016;margin-top:4px;">'
        '📊 Word Breakdown</h3>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📖 Total",   result["total_words"])
    c2.metric("✅ Correct",    result["correct_words"])
    c3.metric("⚠️ Different",  result["substituted_words"])
    c4.metric("❌ Skipped",    result["missed_words"])

    # ── Word diff ────────────────────────────────────────────────────────────
    st.markdown(
        '<h3 style="font-family:Fredoka One,cursive;color:#2D5016;margin-top:20px;">'
        '🔍 Word by Word</h3>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="diff-legend">'
        '<span class="diff-pill" style="background:#C8E6C9;border-color:#66BB6A;color:#1B5E20;">✅ Read correctly</span>'
        '<span class="diff-pill" style="background:#FFE0B2;border-color:#FFB74D;color:#E65100;">⚠️ Read differently</span>'
        '<span class="diff-pill" style="background:#FFCDD2;border-color:#EF5350;color:#B71C1C;">❌ Skipped</span>'
        '<span class="diff-pill" style="background:#BBDEFB;border-color:#64B5F6;color:#0D47A1;">➕ Extra word</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    diff_html = build_child_diff_html(result["diff_tokens"])
    st.markdown(f'<div class="game-card">{diff_html}</div>', unsafe_allow_html=True)

    # ── Encouragement ────────────────────────────────────────────────────────
    if pct >= 95:
        note = "🌟 You read almost every word perfectly! You are a reading superstar! 🦋✨"
        enc_color = "#C8E6C9"
        enc_border = "#66BB6A"
    elif pct >= 85:
        note = "🎉 Fantastic reading! Just a few words to practice and you'll be perfect! 💪"
        enc_color = "#F1F8E9"
        enc_border = "#A5D6A7"
    elif pct >= 70:
        note = "👍 Good job! Look at the orange and red words above and practice those! 📚"
        enc_color = "#FFF9C4"
        enc_border = "#FFE082"
    elif pct >= 50:
        note = "💪 Nice try! Read the passage again and focus on each word carefully. 🎯"
        enc_color = "#FFE0B2"
        enc_border = "#FFB74D"
    else:
        note = "🤗 Keep going! Reading gets better with practice. Try again — you can do it! 🌈"
        enc_color = "#FFCDD2"
        enc_border = "#EF5350"

    st.markdown(f"""
    <div style="background:{enc_color};border-radius:20px;padding:20px;
                border:3px solid {enc_border};box-shadow:0 6px 0 {enc_border}66;margin:16px 0;">
        <p style="font-size:18px;font-weight:700;color:#2D5016;text-align:center;margin:0;">
            {note}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation ───────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄  Try Again!", type="primary", key="btn_retry"):
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result  = None
            st.session_state.page = "reading"
            st.rerun()
    with col2:
        if st.button("🏠  Main Menu", type="secondary", key="btn_home"):
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result  = None
            st.session_state.page = "menu"
            st.rerun()

    # ── Download ─────────────────────────────────────────────────────────────
    st.markdown("---")
    export_text = (
        f"READING ASSESSMENT RESULTS\n"
        f"==========================\n"
        f"Score            : {pct}%\n"
        f"Performance      : {msg}\n"
        f"Stars            : {stars}\n"
        f"STT Engine       : AssemblyAI Universal-3 Pro\n"
        f"---\n"
        f"Total Words      : {result['total_words']}\n"
        f"Correct Words    : {result['correct_words']}\n"
        f"Different Words  : {result['substituted_words']}\n"
        f"Skipped Words    : {result['missed_words']}\n"
        f"Extra Words      : {result['extra_words']}\n\n"
        f"--- ORIGINAL PASSAGE ---\n{PASSAGE}\n\n"
        f"--- STUDENT TRANSCRIPTION ---\n{st.session_state.transcribed_text}\n"
    )
    st.download_button(
        label="💾  Save Results (.txt)",
        data=export_text,
        file_name="para_reading_results.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown(
        '<p style="text-align:center;font-size:13px;color:#66BB6A;margin-top:16px;font-weight:600;">'
        'Powered by AssemblyAI Universal-3 Pro &nbsp;|&nbsp; '
        'ITE153 — Intro to AI and Expert Systems</p>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Router
# ─────────────────────────────────────────────────────────────────────────────

_page = st.session_state.page

if _page == "menu":
    show_menu()
elif _page == "reading":
    show_reading()
elif _page == "results":
    show_results()
