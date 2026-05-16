"""
app.py  —  Para's Reading Adventure
AI-Enhanced Speech-to-Text Reading Assessment Tool

Child-friendly interface | Blue & Red theme | Main Menu
STT Engine: AssemblyAI Universal-3 Pro
NLP Engine: Python difflib SequenceMatcher

Course : ITE153 — Intro to AI and Expert Systems
"""

import streamlit as st
from stt import transcribe
from accuracy import calculate_accuracy

# ─────────────────────────────────────────────────────────────────────────────
#  Page Configuration
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Para's Reading Adventure",
    page_icon="🦋",
    layout="centered",
    initial_sidebar_state="expanded",
)

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
#  Sidebar — API Key
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    api_key = st.text_input(
        "AssemblyAI API Key",
        type="password",
        placeholder="Paste your API key here...",
        help="Get your free key at assemblyai.com/dashboard/api-keys",
    )
    if api_key:
        st.success("✅ API key entered!")
    else:
        st.warning("⚠️ Enter your API key to use the microphone/upload feature.")

    st.markdown("---")
    st.markdown(
        "**How to get a key:**\n\n"
        "1. Go to [assemblyai.com](https://www.assemblyai.com)\n"
        "2. Sign up for a free account\n"
        "3. Copy your API key from the dashboard\n"
        "4. Paste it in the box above"
    )
    st.markdown("---")
    st.caption("ITE153 — Intro to AI and Expert Systems")
    st.caption("AI: AssemblyAI Universal-3 Pro + NLP SequenceMatcher")

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
#  Global CSS — child-friendly game look, blue + red palette
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@400;600;700;800&display=swap');

/* ── Base ───────────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }
.stApp { background: #dbeafe; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 700px; padding-top: 1.5rem; padding-bottom: 3rem; }
h1, h2, h3 { font-family: 'Fredoka', sans-serif !important; }

/* ── Sidebar styling ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #1e3a8a !important;
}
[data-testid="stSidebar"] * {
    color: #fff !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: #1d4ed8 !important;
    color: #fff !important;
    border: 2px solid #60a5fa !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
}
[data-testid="stSidebar"] .stAlert {
    background: rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebarContent"] h2 {
    color: #fff !important;
    font-family: 'Fredoka', sans-serif !important;
}

/* ── Primary button → Red game button ──────────────────────────────────── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #dc2626 !important;
    color: #fff !important;
    font-family: 'Fredoka', sans-serif !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 14px 40px !important;
    box-shadow: 0 6px 0 #991b1b !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
    width: 100% !important;
    letter-spacing: 0.4px;
}
[data-testid="stButton"] > button[kind="primary"]:hover  { background: #ef4444 !important; }
[data-testid="stButton"] > button[kind="primary"]:active {
    box-shadow: 0 2px 0 #991b1b !important;
    transform: translateY(4px) !important;
}

/* ── Secondary button → Blue game button ────────────────────────────────── */
[data-testid="stButton"] > button[kind="secondary"] {
    background: #1d4ed8 !important;
    color: #fff !important;
    font-family: 'Fredoka', sans-serif !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 32px !important;
    box-shadow: 0 5px 0 #1e3a8a !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover  { background: #2563eb !important; }
[data-testid="stButton"] > button[kind="secondary"]:active {
    box-shadow: 0 2px 0 #1e3a8a !important;
    transform: translateY(3px) !important;
}
[data-testid="stButton"] > button:disabled {
    background: #94a3b8 !important;
    box-shadow: 0 4px 0 #64748b !important;
    color: #e2e8f0 !important;
}

/* ── Text area ──────────────────────────────────────────────────────────── */
.stTextArea textarea {
    font-family: 'Nunito', sans-serif !important;
    font-size: 15px !important;
    border-radius: 16px !important;
    border: 2.5px solid #93c5fd !important;
    background: #fff !important;
    color: #1e3a8a !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    border-radius: 20px 20px 0 0 !important;
    padding: 8px 24px !important;
    color: #1d4ed8 !important;
    background: #bfdbfe !important;
}
.stTabs [aria-selected="true"] {
    background: #1d4ed8 !important;
    color: #fff !important;
}

/* ── Metric cards ───────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #fff !important;
    border: 2.5px solid #93c5fd !important;
    border-radius: 18px !important;
    padding: 14px 10px !important;
    box-shadow: 0 5px 0 #bfdbfe !important;
    text-align: center !important;
}
[data-testid="metric-container"] label {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 14px !important;
    color: #1d4ed8 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 30px !important;
    color: #1e3a8a !important;
}

/* ── Alerts ─────────────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 16px !important;
    border: none !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}
hr { border-color: #93c5fd !important; }
.stExpander {
    border: 2px solid #93c5fd !important;
    border-radius: 16px !important;
    background: #fff !important;
}

/* ── Spinner ────────────────────────────────────────────────────────────── */
.stSpinner p {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 18px !important;
    color: #1d4ed8 !important;
}

/* ── Animations ─────────────────────────────────────────────────────────── */
@keyframes bounce {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-16px); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes starPop {
    0%   { transform: scale(0) rotate(-15deg); opacity: 0; }
    70%  { transform: scale(1.25) rotate(5deg); }
    100% { transform: scale(1) rotate(0); opacity: 1; }
}

/* ── Custom HTML blocks ─────────────────────────────────────────────────── */
.game-card {
    background: #fff;
    border-radius: 24px;
    padding: 28px 30px;
    border: 3px solid #93c5fd;
    box-shadow: 0 8px 0 #bfdbfe;
    margin-bottom: 20px;
    animation: fadeUp 0.5s ease;
}
.passage-card {
    background: #1e3a8a;
    border-radius: 24px;
    padding: 26px 30px;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    line-height: 2.2;
    margin: 14px 0 20px;
    box-shadow: 0 8px 0 #1e40af;
    animation: fadeUp 0.5s ease;
    border: 3px solid #3b82f6;
}
.page-title {
    font-family: 'Fredoka', sans-serif;
    font-size: 46px;
    font-weight: 700;
    color: #1e3a8a;
    text-align: center;
    line-height: 1.2;
    margin: 0 0 6px;
    text-shadow: 3px 3px 0 #bfdbfe;
    animation: fadeUp 0.5s ease;
}
.hero-char {
    font-size: 96px;
    text-align: center;
    display: block;
    margin: 8px 0;
    animation: bounce 2.2s ease-in-out infinite;
}
.step-label {
    font-family: 'Fredoka', sans-serif;
    font-size: 22px;
    font-weight: 600;
    color: #1d4ed8;
    margin: 16px 0 6px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.step-num {
    background: #dc2626;
    color: #fff;
    font-family: 'Fredoka', sans-serif;
    font-size: 15px;
    font-weight: 700;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 3px 0 #991b1b;
}
.score-number {
    font-family: 'Fredoka', sans-serif;
    font-size: 88px;
    font-weight: 700;
    text-align: center;
    line-height: 1;
    margin-bottom: 4px;
}
.score-msg {
    font-family: 'Fredoka', sans-serif;
    font-size: 28px;
    font-weight: 600;
    text-align: center;
    margin-top: 2px;
}
.stars-row {
    font-size: 46px;
    text-align: center;
    margin: 6px 0 10px;
    animation: starPop 0.6s cubic-bezier(.36,.07,.19,.97) both;
}
.diff-legend { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0 14px; }
.diff-pill {
    border-radius: 99px;
    padding: 4px 14px;
    font-family: 'Nunito', sans-serif;
    font-size: 13px;
    font-weight: 800;
    border: 2px solid transparent;
}
.page-header {
    background: #1e3a8a;
    border-radius: 20px;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    box-shadow: 0 5px 0 #1e40af;
}
.how-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 10px 0;
    font-size: 16px;
    font-weight: 700;
    color: #1e3a8a;
}
.how-icon { font-size: 26px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def score_to_stars(pct: float) -> tuple[str, str, str]:
    """Returns (star_emojis, message, hex_color)."""
    if pct >= 95:
        return "⭐⭐⭐⭐⭐", "Amazing Reader!",   "#15803d"
    elif pct >= 85:
        return "⭐⭐⭐⭐",   "Great Job!",         "#1d4ed8"
    elif pct >= 70:
        return "⭐⭐⭐",     "Good Try!",          "#d97706"
    elif pct >= 50:
        return "⭐⭐",       "Keep Practicing!",   "#c2410c"
    else:
        return "⭐",         "Let's Try Again!",   "#b91c1c"


def build_child_diff_html(diff_tokens: list) -> str:
    """Renders color-coded word diff in a child-friendly style."""
    COLOR = {"correct":"#15803d", "substituted":"#c2410c", "missed":"#b91c1c", "extra":"#1d4ed8"}
    BG    = {"correct":"#dcfce7", "substituted":"#ffedd5", "missed":"#fee2e2", "extra":"#dbeafe"}
    parts = []
    for token in diff_tokens:
        w   = token["word"]
        tag = token["tag"]
        parts.append(
            f'<span style="background:{BG[tag]};color:{COLOR[tag]};'
            f'padding:4px 9px;border-radius:10px;font-weight:700;'
            f'margin:3px 2px;display:inline-block;font-size:17px;">{w}</span>'
        )
    return (
        "<p style='font-family:Nunito,sans-serif;"
        "line-height:2.6;font-size:17px;'>" + " ".join(parts) + "</p>"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Page: Main Menu
# ─────────────────────────────────────────────────────────────────────────────

def show_menu():
    st.markdown('<span class="hero-char">🦋</span>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Para\'s Reading<br>Adventure!</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;font-size:19px;color:#1d4ed8;'
        'font-weight:700;margin:6px 0 30px;">'
        'Read the story out loud and earn your stars! 📚✨</p>',
        unsafe_allow_html=True,
    )

    if not api_key:
        st.warning("⚠️ Please enter your **AssemblyAI API key** in the sidebar (⚙️ Settings) before starting!")

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("▶  Start Reading!", type="primary", key="btn_start"):
            st.session_state.page = "reading"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📖  How to Play"):
        st.markdown("""
<div class="how-item"><span class="how-icon">0️⃣</span>
<span>Enter your <b style="color:#dc2626">AssemblyAI API key</b> in the sidebar on the left first.</span></div>

<div class="how-item"><span class="how-icon">1️⃣</span>
<span>Read the story shown on the next screen carefully.</span></div>

<div class="how-item"><span class="how-icon">2️⃣</span>
<span>Press the <b style="color:#dc2626">microphone button</b> and read the story out loud.</span></div>

<div class="how-item"><span class="how-icon">3️⃣</span>
<span>Press <b style="color:#dc2626">Transcribe</b> to turn your voice into words on the screen.</span></div>

<div class="how-item"><span class="how-icon">4️⃣</span>
<span>Press <b style="color:#dc2626">Check My Score!</b> to see how many stars you earned.</span></div>

<div class="how-item"><span class="how-icon">⭐</span>
<span>Try to earn <b>5 stars!</b> You can do it!</span></div>
""", unsafe_allow_html=True)

    st.markdown(
        '<p style="text-align:center;font-size:13px;color:#60a5fa;margin-top:36px;">'
        'Powered by AssemblyAI Universal-3 Pro &nbsp;|&nbsp; ITE153 — Intro to AI and Expert Systems</p>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Page: Reading Assessment
# ─────────────────────────────────────────────────────────────────────────────

def show_reading():
    # ── Top bar ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="page-header">'
        '<span style="font-family:Fredoka,sans-serif;font-size:22px;font-weight:700;color:#fff;">'
        '🦋 Para\'s Story</span>'
        '<span style="font-size:26px;">📖</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Menu", type="secondary", key="back_menu"):
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result  = None
            st.session_state.page = "menu"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 1: Read the Passage ─────────────────────────────────────────────
    st.markdown(
        '<div class="step-label"><span class="step-num">1</span> Read this passage out loud!</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="passage-card">{PASSAGE}</div>', unsafe_allow_html=True)

    # ── Step 2: Record or Upload ─────────────────────────────────────────────
    st.markdown(
        '<div class="step-label"><span class="step-num">2</span> Record yourself reading!</div>',
        unsafe_allow_html=True,
    )

    if not api_key:
        st.error("⚠️ Please enter your AssemblyAI API key in the **sidebar** (⚙️ Settings) to use this feature.")

    tab_mic, tab_file = st.tabs(["🎙️  Microphone", "📂  Upload File"])

    with tab_mic:
        st.caption("Press the microphone button, read the story aloud, then press it again to stop.")
        audio_val = st.audio_input("Record", label_visibility="collapsed", key="mic_input")
        if audio_val is not None:
            st.audio(audio_val, format="audio/wav")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔊  Transcribe My Recording", type="primary", key="btn_mic",
                         disabled=not api_key):
                with st.spinner("✨ AssemblyAI is listening to your reading..."):
                    text, err = transcribe(audio_val.getvalue(), api_key)
                if err:
                    st.error(f"Oops! {err}")
                else:
                    st.session_state.transcribed_text = text
                    st.session_state.accuracy_result  = None
                    st.success("Got it! 🎉 Scroll down to check your reading!")

    with tab_file:
        st.caption("Upload a WAV or MP3 recording of yourself reading.")
        uploaded = st.file_uploader(
            "Upload audio", type=["wav", "mp3", "ogg", "m4a"],
            label_visibility="collapsed", key="file_upload",
        )
        if uploaded is not None:
            st.audio(uploaded, format=uploaded.type)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔊  Transcribe File", type="primary", key="btn_file",
                         disabled=not api_key):
                with st.spinner("✨ AssemblyAI is listening to your reading..."):
                    text, err = transcribe(uploaded.read(), api_key)
                if err:
                    st.error(f"Oops! {err}")
                else:
                    st.session_state.transcribed_text = text
                    st.session_state.accuracy_result  = None
                    st.success("Got it! 🎉 Scroll down to check your reading!")

    # ── Step 3: Review Transcription ─────────────────────────────────────────
    st.markdown(
        '<div class="step-label"><span class="step-num">3</span> What the computer heard:</div>',
        unsafe_allow_html=True,
    )
    st.caption("You can fix any mistakes here before checking your score.")

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
    if st.button("⭐  Check My Score!", type="primary", disabled=not can_score, key="btn_score"):
        result = calculate_accuracy(PASSAGE, transcribed)
        st.session_state.accuracy_result = result
        st.session_state.page = "results"
        st.rerun()

    if not can_score:
        st.caption("🎙️ Record and transcribe your reading first, then press Check My Score!")


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
        '<span style="font-family:Fredoka,sans-serif;font-size:22px;font-weight:700;color:#fff;">'
        '🏆 Your Results</span><span style="font-size:26px;">🎉</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Score card ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="game-card" style="border-color:{color}55;box-shadow:0 8px 0 {color}33;">'
        f'<div class="stars-row">{stars}</div>'
        f'<div class="score-number" style="color:{color};">{pct}%</div>'
        f'<div class="score-msg" style="color:{color};">{msg}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Word breakdown ───────────────────────────────────────────────────────
    st.markdown(
        '<h3 style="font-family:Fredoka,sans-serif;color:#1e3a8a;margin-top:4px;">📊 Word Breakdown</h3>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Words",   result["total_words"])
    c2.metric("✅ Correct",    result["correct_words"])
    c3.metric("⚠️ Different",  result["substituted_words"])
    c4.metric("❌ Skipped",    result["missed_words"])

    # ── Word diff ────────────────────────────────────────────────────────────
    st.markdown(
        '<h3 style="font-family:Fredoka,sans-serif;color:#1e3a8a;margin-top:20px;">🔍 Word by Word</h3>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="diff-legend">'
        '<span class="diff-pill" style="background:#dcfce7;border-color:#86efac;color:#15803d;">✅ Read correctly</span>'
        '<span class="diff-pill" style="background:#ffedd5;border-color:#fdba74;color:#c2410c;">⚠️ Read differently</span>'
        '<span class="diff-pill" style="background:#fee2e2;border-color:#fca5a5;color:#b91c1c;">❌ Skipped</span>'
        '<span class="diff-pill" style="background:#dbeafe;border-color:#93c5fd;color:#1d4ed8;">➕ Extra word</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    diff_html = build_child_diff_html(result["diff_tokens"])
    st.markdown(f'<div class="game-card">{diff_html}</div>', unsafe_allow_html=True)

    # ── Encouragement ────────────────────────────────────────────────────────
    if pct >= 95:
        note = "🌟 You read almost every word perfectly! You are a reading superstar!"
    elif pct >= 85:
        note = "🎉 Fantastic reading! Just a few words to practice and you'll be perfect!"
    elif pct >= 70:
        note = "👍 Good job! Look at the orange and red words above and practice those!"
    elif pct >= 50:
        note = "💪 Nice try! Read the passage again and focus on each word carefully."
    else:
        note = "🤗 Keep going! Reading gets better with practice. Try again — you can do it!"

    st.info(note)
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
        '<p style="text-align:center;font-size:13px;color:#60a5fa;margin-top:16px;">'
        'Powered by AssemblyAI Universal-3 Pro &nbsp;|&nbsp; ITE153 — Intro to AI and Expert Systems</p>',
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
