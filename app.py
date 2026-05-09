"""
app.py
------
🎮 Para's Reading Adventure - Child-Friendly Speech-to-Text Reading Game
A Streamlit application designed for children with a fun, game-like interface.
Records child's reading, transcribes via Google Web Speech API, and calculates
reading accuracy with colorful, engaging feedback.

AI Technique : Speech-to-Text (Google Web Speech API via SpeechRecognition)
              + NLP Text Comparison (difflib.SequenceMatcher)
Course       : ITE153 - Intro to AI and Expert Systems
"""

import streamlit as st
from stt import transcribe, word_count
from accuracy import (
    calculate_accuracy,
    get_accuracy_label,
    build_diff_html,
    LEVENSHTEIN_AVAILABLE,
)

# ─────────────────────────────────────────────
#  Page Configuration
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="🎮 Para's Reading Adventure",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  Child-Friendly Custom Styling (Blue & Red)
# ─────────────────────────────────────────────

st.markdown("""
<style>
    /* Main container background - light blue */
    .main {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    }
    
    /* Menu buttons - big and colorful */
    .menu-button {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E72 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 30px 40px;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        margin: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    
    .menu-button:hover {
        transform: scale(1.05);
    }
    
    .menu-button-blue {
        background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
    }

    /* Game title */
    .game-title {
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #1976D2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .game-subtitle {
        font-size: 24px;
        text-align: center;
        color: #1976D2;
        font-weight: bold;
        margin-bottom: 30px;
    }

    /* Card-style containers */
    .result-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #FFFFFF 100%);
        border-radius: 20px;
        padding: 25px 30px;
        margin: 15px 0;
        border: 3px solid #1976D2;
        box-shadow: 0 8px 16px rgba(25, 118, 210, 0.2);
    }

    /* Accuracy badge - big and fun */
    .accuracy-badge {
        font-size: 72px;
        font-weight: 900;
        text-align: center;
        padding: 20px 0;
    }
    
    .accuracy-label {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-top: -10px;
    }

    /* Legend pills */
    .legend-pill {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin: 5px 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Section title */
    .section-title {
        font-size: 28px;
        font-weight: 900;
        color: #FF6B6B;
        margin-top: 20px;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    
    .section-subtitle {
        font-size: 18px;
        color: #1976D2;
        font-weight: bold;
        margin-bottom: 10px;
    }

    /* Story passage box */
    .story-box {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFFFFF 100%);
        border-left: 6px solid #FF6B6B;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        font-size: 18px;
        line-height: 1.8;
        color: #333;
    }

    /* Streamlit metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #E3F2FD 100%);
        border: 3px solid #1976D2;
        border-radius: 15px;
        padding: 16px 20px;
        box-shadow: 0 4px 8px rgba(25, 118, 210, 0.15);
    }
    
    /* Info boxes */
    [data-testid="stInfo"] {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 100%);
        border-left: 6px solid #4CAF50;
        border-radius: 10px;
    }
    
    [data-testid="stWarning"] {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFFFFF 100%);
        border-left: 6px solid #FF9800;
        border-radius: 10px;
    }
    
    [data-testid="stError"] {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFFFFF 100%);
        border-left: 6px solid #FF6B6B;
        border-radius: 10px;
    }
    
    /* Success message */
    [data-testid="stSuccess"] {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 100%);
        border-left: 6px solid #4CAF50;
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
        color: white;
        border: none;
        border-radius: 15px;
        font-size: 16px;
        font-weight: bold;
        padding: 12px 24px;
        box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 16px rgba(25, 118, 210, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Session State Initialization
# ─────────────────────────────────────────────

if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "accuracy_result" not in st.session_state:
    st.session_state.accuracy_result = None
if "page" not in st.session_state:
    st.session_state.page = "menu"

# ─────────────────────────────────────────────
#  The Story - Para's Adventure
# ─────────────────────────────────────────────

PARA_STORY = """Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home. It is getting dark. There are many cars on the road because it is the end of the work day. Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing! Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man."""

# ─────────────────────────────────────────────
#  Main Menu Page
# ─────────────────────────────────────────────

def show_menu():
    # Title with gradient
    st.markdown("""
    <div class="game-title">🦜 Para's Reading Adventure 🦜</div>
    <div class="game-subtitle">Help Para practice reading! 📚</div>
    """, unsafe_allow_html=True)
    
    # Decorative spacing
    st.markdown("")
    st.markdown("")
    
    # Welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Welcome, Young Reader! 🌟
        
        Read Para's amazing story about her adventure in the market and 
        meeting a dancing police officer!
        
        Let's see how well you can read! 🎉
        """)
    
    st.markdown("")
    st.markdown("")
    
    # Menu buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎮 START GAME", use_container_width=True, key="btn_start"):
            st.session_state.page = "game"
            st.rerun()
    
    with col2:
        if st.button("📖 READ STORY", use_container_width=True, key="btn_read"):
            st.session_state.page = "read_story"
            st.rerun()
    
    with col3:
        if st.button("❓ HOW TO PLAY", use_container_width=True, key="btn_help"):
            st.session_state.page = "instructions"
            st.rerun()
    
    st.markdown("")
    st.markdown("")
    
    # Footer with decorative elements
    st.markdown("""
    <div style="text-align: center; color: #1976D2; font-size: 18px;">
    ✨ Made with ❤️ for amazing young readers! ✨
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Read Story Page
# ─────────────────────────────────────────────

def show_read_story():
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("◀ Back", key="btn_back_story"):
            st.session_state.page = "menu"
            st.rerun()
    
    st.markdown('<div class="section-title">📖 Para\'s Story</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-box">{PARA_STORY}</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Ready to Read? 🎮", use_container_width=True):
            st.session_state.page = "game"
            st.rerun()

# ─────────────────────────────────────────────
#  How to Play Page
# ─────────────────────────────────────────────

def show_instructions():
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("◀ Back", key="btn_back_instructions"):
            st.session_state.page = "menu"
            st.rerun()
    
    st.markdown('<div class="section-title">📚 How to Play</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Step 1: Listen to the Story 👂
    Read Para's exciting story about her adventure!
    
    ### Step 2: Record Your Voice 🎤
    Click the microphone button and read the story aloud as clearly as you can!
    
    ### Step 3: Check Your Reading 🔍
    The computer will check how well you read and show you:
    - ✅ Words you read correctly (green)
    - ⚠️ Words you said differently (orange)
    - ❌ Words you missed (red)
    - ➕ Extra words you added (blue)
    
    ### Step 4: See Your Score 🌟
    Get a score and see how you did! Try to get 95% to be a Reading Star! ⭐
    
    **Tips for Best Results:**
    - 🔇 Find a quiet place
    - 🗣️ Speak clearly and not too fast
    - 🎯 Read with feeling and expression!
    """)

# ─────────────────────────────────────────────
#  Main Game Page
# ─────────────────────────────────────────────

def show_game():
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("◀ Back", key="btn_back_game"):
            st.session_state.page = "menu"
            st.rerun()
    
    st.markdown('<div class="section-title">🎮 Let\'s Play!</div>', unsafe_allow_html=True)
    
    # Display the story
    st.markdown('<div class="section-subtitle">📖 Read this story out loud:</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<div class="story-box">{PARA_STORY}</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Recording section
    st.markdown('<div class="section-subtitle">🎤 Record Your Reading</div>', 
                unsafe_allow_html=True)
    
    audio_value = st.audio_input(
        label="Click to record",
        label_visibility="collapsed",
        key="mic_input",
    )
    
    if audio_value is not None:
        st.audio(audio_value, format="audio/wav")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📊 Check My Reading", use_container_width=True, key="btn_transcribe"):
                with st.spinner("🤖 Computer is listening..."):
                    text, error = transcribe(audio_value.getvalue())
                if error:
                    st.error(f"❌ Oops! {error}")
                else:
                    st.session_state.transcribed_text = text
                    st.session_state.accuracy_result = None
                    st.success("✅ Got it! Now let me check your reading...")
                    st.rerun()
    
    st.markdown("")
    
    # Show transcribed text if available
    if st.session_state.transcribed_text:
        st.markdown('<div class="section-subtitle">🔍 What I Heard:</div>', 
                    unsafe_allow_html=True)
        transcribed_text = st.text_area(
            label="You can fix it if needed",
            label_visibility="collapsed",
            value=st.session_state.transcribed_text,
            height=100,
            key="transcribed_display",
        )
        st.session_state.transcribed_text = transcribed_text
        
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🌟 Calculate My Score", use_container_width=True, key="btn_calculate"):
                result = calculate_accuracy(PARA_STORY, transcribed_text)
                st.session_state.accuracy_result = result
                st.rerun()
    
    # Show results if available
    if st.session_state.accuracy_result:
        show_results(st.session_state.accuracy_result)

# ─────────────────────────────────────────────
#  Results Page
# ─────────────────────────────────────────────

def show_results(result):
    st.markdown("")
    st.divider()
    st.markdown("")
    
    pct = result["accuracy_pct"]
    label, color = get_accuracy_label(pct)
    
    # Big colorful score
    color_map = {
        "green": "#4CAF50",
        "blue": "#1976D2",
        "orange": "#FF9800",
        "red": "#FF6B6B",
    }
    badge_color = color_map.get(color, "#333")
    
    # Emoji based on score
    if pct >= 95:
        emoji = "🌟⭐🌟"
    elif pct >= 85:
        emoji = "⭐👏🎉"
    elif pct >= 70:
        emoji = "👍😊"
    else:
        emoji = "💪📚✨"
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <div class="accuracy-badge" style="color:{badge_color}">{pct}%</div>
        <div class="accuracy-label" style="color:{badge_color}">{label}</div>
        <div style="font-size: 40px; margin-top: 10px;">{emoji}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Word breakdown
    st.markdown('<div class="section-subtitle">📊 Your Reading Details:</div>', 
                unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Words", result["total_words"])
    c2.metric("✅ Correct", result["correct_words"])
    c3.metric("⚠️ Substituted", result["substituted_words"])
    c4.metric("❌ Missed", result["missed_words"])
    
    if result.get("extra_words", 0) > 0:
        st.info(f"➕ **Extra words added:** {result['extra_words']}")
    
    st.markdown("")
    
    # Word-by-word comparison
    st.markdown('<div class="section-subtitle">🔍 Word-by-Word Check:</div>', 
                unsafe_allow_html=True)
    
    st.markdown(
        '<span class="legend-pill" style="background:#E8F5E9;color:#2e7d32;">✅ Correct</span>'
        '<span class="legend-pill" style="background:#FFF3E0;color:#e65100;">⚠️ Substituted</span>'
        '<span class="legend-pill" style="background:#FFEBEE;color:#c62828;">❌ Missed</span>'
        '<span class="legend-pill" style="background:#E3F2FD;color:#1565c0;">➕ Extra</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")
    
    diff_html = build_diff_html(result["diff_tokens"])
    st.markdown(f'<div class="result-card">{diff_html}</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Encouraging message
    st.markdown('<div class="section-subtitle">💭 What This Means:</div>', 
                unsafe_allow_html=True)
    
    if pct >= 95:
        message = "🌟 **READING STAR!** You are an amazing reader! You read this perfectly! Keep up the excellent work!"
    elif pct >= 85:
        message = "⭐ **GREAT JOB!** You did really well! You're reading at a great level. Keep practicing!"
    elif pct >= 70:
        message = "👍 **GOOD EFFORT!** You're doing well! Practice the words that gave you trouble and you'll improve!"
    else:
        message = "💪 **KEEP GOING!** This story was challenging, but that's okay! Try it again and watch yourself improve!"
    
    st.success(message)
    
    st.markdown("")
    st.markdown("")
    
    # Buttons for next action
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Try Again", use_container_width=True, key="btn_retry"):
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result = None
            st.rerun()
    
    with col2:
        export_text = f"""🎮 PARA'S READING ADVENTURE - RESULTS
=====================================
Score: {pct}%
Level: {label}

Words Read:
- Total: {result["total_words"]}
- Correct: {result["correct_words"]}
- Substituted: {result["substituted_words"]}
- Missed: {result["missed_words"]}
- Extra: {result["extra_words"]}

--- ORIGINAL STORY ---
{PARA_STORY}
"""
        st.download_button(
            label="📥 Save My Results",
            data=export_text,
            file_name="para_reading_results.txt",
            mime="text/plain",
            use_container_width=True,
        )
    
    with col3:
        if st.button("🏠 Home Menu", use_container_width=True, key="btn_home"):
            st.session_state.page = "menu"
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result = None
            st.rerun()


# ─────────────────────────────────────────────
#  Page Router
# ─────────────────────────────────────────────

if st.session_state.page == "menu":
    show_menu()
elif st.session_state.page == "read_story":
    show_read_story()
elif st.session_state.page == "instructions":
    show_instructions()
elif st.session_state.page == "game":
    show_game()
else:
    st.session_state.page = "menu"
    st.rerun()