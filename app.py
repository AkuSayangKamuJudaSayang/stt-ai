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
#  Ultra Fancy Child-Friendly Custom Styling (Blue & Red)
# ─────────────────────────────────────────────

st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    /* Main container background - animated gradient */
    .main {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    }

    /* Game title */
    .game-title {
        font-size: clamp(32px, 8vw, 56px);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #1976D2, #FF6B6B);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 20px 0;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .game-subtitle {
        font-size: clamp(18px, 5vw, 24px);
        text-align: center;
        color: #1976D2;
        font-weight: bold;
        margin-bottom: 30px;
    }

    /* Story Cards Grid */
    .story-cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .story-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
        border-radius: 25px;
        padding: 25px;
        border: 4px solid transparent;
        border-image: linear-gradient(135deg, #FF6B6B, #1976D2) 1;
        box-shadow: 0 12px 28px rgba(25, 118, 210, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .story-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .story-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(25, 118, 210, 0.35);
    }
    
    .story-card:hover::before {
        left: 100%;
    }
    
    .card-number {
        display: inline-block;
        background: linear-gradient(135deg, #FF6B6B, #FF8E72);
        color: white;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 20px;
        margin-bottom: 15px;
        box-shadow: 0 6px 12px rgba(255, 107, 107, 0.3);
    }
    
    .card-text {
        font-size: 16px;
        line-height: 1.8;
        color: #333;
        word-wrap: break-word;
    }
    
    .word {
        display: inline;
        padding: 2px 4px;
        border-radius: 4px;
        transition: all 0.2s ease;
        cursor: default;
    }
    
    .word.highlighted {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #333;
        font-weight: bold;
        box-shadow: 0 0 12px rgba(255, 165, 0, 0.6);
        animation: pulse 0.6s ease;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #FFFFFF 100%);
        border-radius: 20px;
        padding: 25px 30px;
        margin: 15px 0;
        border: 3px solid #1976D2;
        box-shadow: 0 8px 16px rgba(25, 118, 210, 0.2);
    }

    /* Accuracy badge */
    .accuracy-badge {
        font-size: clamp(48px, 12vw, 84px);
        font-weight: 900;
        text-align: center;
        padding: 20px 0;
        animation: bounce 1s ease-in-out;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    .accuracy-label {
        text-align: center;
        font-size: clamp(18px, 5vw, 28px);
        font-weight: bold;
        margin-top: -10px;
    }

    /* Legend pills */
    .legend-pill {
        display: inline-block;
        padding: 10px 18px;
        border-radius: 25px;
        font-size: clamp(12px, 3vw, 14px);
        font-weight: 600;
        margin: 8px 8px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }
    
    .legend-pill:hover {
        transform: translateY(-3px);
    }

    /* Section titles */
    .section-title {
        font-size: clamp(24px, 6vw, 32px);
        font-weight: 900;
        color: #FF6B6B;
        margin-top: 20px;
        margin-bottom: 20px;
        text-transform: uppercase;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .section-subtitle {
        font-size: clamp(16px, 4vw, 20px);
        color: #1976D2;
        font-weight: bold;
        margin-bottom: 15px;
    }

    /* Streamlit customizations */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #E3F2FD 100%);
        border: 3px solid #1976D2;
        border-radius: 15px;
        padding: 16px 20px;
        box-shadow: 0 4px 8px rgba(25, 118, 210, 0.15);
    }
    
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
        font-size: clamp(14px, 3vw, 16px);
        font-weight: bold;
        padding: clamp(8px, 2vw, 12px) clamp(16px, 4vw, 24px);
        box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 16px rgba(25, 118, 210, 0.4);
        transform: translateY(-2px);
    }
    
    /* Menu buttons */
    .menu-button-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 15px;
        border: 3px solid #1976D2;
        font-size: 16px;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .game-title {
            font-size: 32px;
        }
        
        .section-title {
            font-size: 24px;
        }
        
        .story-cards-container {
            grid-template-columns: 1fr;
        }
        
        .story-card {
            padding: 20px;
        }
        
        .card-text {
            font-size: 15px;
        }
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
if "highlighted_word_index" not in st.session_state:
    st.session_state.highlighted_word_index = None
if "spoken_words" not in st.session_state:
    st.session_state.spoken_words = []

# ─────────────────────────────────────────────
#  The Story - Para's Adventure (Split into 4 Cards)
# ─────────────────────────────────────────────

PARA_FULL_STORY = """Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home. It is getting dark. There are many cars on the road because it is the end of the work day. Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing! Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man."""

# Split story into 4 logical cards
STORY_CARDS = [
    {
        "number": 1,
        "emoji": "🏠",
        "text": "Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home."
    },
    {
        "number": 2,
        "emoji": "🌆",
        "text": "It is getting dark. There are many cars on the road because it is the end of the work day."
    },
    {
        "number": 3,
        "emoji": "🚗",
        "text": "Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing!"
    },
    {
        "number": 4,
        "emoji": "👮",
        "text": "Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man."
    }
]

# ─────────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────────

def get_words_from_text(text):
    """Extract words from text."""
    return text.lower().split()

def highlight_spoken_words(spoken_text):
    """
    Create HTML with real-time highlighting of spoken words.
    Compares spoken words with story words and highlights matches.
    """
    spoken_words = get_words_from_text(spoken_text)
    
    html_parts = []
    for card in STORY_CARDS:
        story_words = get_words_from_text(card["text"])
        card_html = f'<div style="margin-bottom: 15px; padding: 15px; background: rgba(255,255,255,0.5); border-radius: 10px;">'
        
        for idx, word in enumerate(story_words):
            # Clean punctuation for comparison
            clean_word = ''.join(c for c in word if c.isalnum())
            is_spoken = any(clean_word in spoken_word for spoken_word in spoken_words)
            
            if is_spoken:
                card_html += f'<span class="word highlighted">{word}</span> '
            else:
                card_html += f'<span class="word">{word}</span> '
        
        card_html += '</div>'
        html_parts.append(card_html)
    
    return ''.join(html_parts)

def display_story_cards(highlight_text=None):
    """Display the 4 story cards with optional highlighting."""
    st.markdown('<div class="story-cards-container">', unsafe_allow_html=True)
    
    for card in STORY_CARDS:
        with st.container():
            st.markdown(f"""
            <div class="story-card">
                <div class="card-number">{card['number']}</div>
                <div class="card-text">{card['text']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show highlighting if text is provided
    if highlight_text and highlight_text.strip():
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">✨ Words You Read (Highlighted):</div>', 
                    unsafe_allow_html=True)
        st.markdown(highlight_spoken_words(highlight_text), unsafe_allow_html=True)


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
    
    # Welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 🌟 Welcome, Young Reader! 🌟
        
        Get ready for an exciting adventure with Para! 🦜
        
        Read Para's amazing story about flying through the market 
        and meeting a dancing police officer!
        
        **Let's see how well you can read!** 🎉
        """)
    
    st.markdown("")
    st.markdown("")
    
    # Preview of story
    st.markdown('<div class="section-title">📖 Story Preview</div>', unsafe_allow_html=True)
    display_story_cards()
    
    st.markdown("")
    st.markdown("")
    
    # Menu buttons
    st.markdown('<div class="section-title">🎮 Choose an Option</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
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
    <div style="text-align: center; color: #1976D2; font-size: 18px; margin-top: 50px;">
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
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(25,118,210,0.1)); 
                border-radius: 20px; padding: 20px; margin: 20px 0; border-left: 6px solid #FF6B6B;">
    <p style="font-size: 16px; line-height: 1.8; color: #333; margin: 0;">
    Read the story below at your own pace. Take your time and enjoy Para's adventure! 🦜
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    display_story_cards()
    
    st.markdown("")
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎮 Ready to Read? Let's Go!", use_container_width=True):
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Step 1: Listen & Read 👂
        Read Para's exciting story about her adventure!
        The story is split into 4 exciting parts!
        
        ### 🎤 Step 2: Record Your Voice 🎤
        Click the microphone button and read the story 
        aloud as clearly as you can!
        
        ### 🔍 Step 3: Real-Time Highlighting ✨
        As you speak, watch the words light up when 
        the computer recognizes them!
        """)
    
    with col2:
        st.markdown("""
        ### 🔍 Step 4: Check Your Reading 🔍
        The computer will check how well you read and show you:
        
        - ✅ **Green** - Words you read correctly!
        - ⚠️ **Orange** - Words you said differently
        - ❌ **Red** - Words you missed
        - ➕ **Blue** - Extra words you added
        
        ### 🌟 Step 5: See Your Score 🌟
        Get a score and see how you did! 
        Try to get 95% to be a **Reading Star!** ⭐
        """)
    
    st.markdown("")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E8F5E9, #FFFFFF); 
                border-radius: 20px; padding: 20px; border-left: 6px solid #4CAF50; margin: 20px 0;">
    <h3 style="color: #2e7d32; margin-top: 0;">💡 Tips for Best Results</h3>
    <ul style="font-size: 16px; line-height: 1.8;">
    <li>🔇 Find a quiet place to read</li>
    <li>🗣️ Speak clearly and not too fast</li>
    <li>🎯 Read with feeling and expression!</li>
    <li>⏸️ Take a breath between sentences</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Display the story in 4 cards
    st.markdown('<div class="section-subtitle">📖 Read this story out loud:</div>', 
                unsafe_allow_html=True)
    display_story_cards()
    
    st.markdown("")
    st.divider()
    st.markdown("")
    
    # Recording section
    st.markdown('<div class="section-subtitle">🎤 Record Your Reading</div>', 
                unsafe_allow_html=True)
    
    st.info("🎙️ Click the microphone icon below and read the story clearly. Watch the words highlight as you speak! ✨")
    
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
        
        col1, col2 = st.columns([3, 1])
        with col1:
            transcribed_text = st.text_area(
                label="You can fix it if needed",
                label_visibility="collapsed",
                value=st.session_state.transcribed_text,
                height=100,
                key="transcribed_display",
            )
            st.session_state.transcribed_text = transcribed_text
        
        # Show real-time highlighting
        display_story_cards(highlight_text=transcribed_text)
        
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🌟 Calculate My Score", use_container_width=True, key="btn_calculate"):
                result = calculate_accuracy(PARA_FULL_STORY, transcribed_text)
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
        celebration = "READING SUPERSTAR! 🚀"
    elif pct >= 85:
        emoji = "⭐👏🎉"
        celebration = "GREAT JOB! 👏"
    elif pct >= 70:
        emoji = "👍😊"
        celebration = "GOOD EFFORT! 💪"
    else:
        emoji = "💪📚✨"
        celebration = "KEEP GOING! 📚"
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <div class="accuracy-badge" style="color:{badge_color}">{pct}%</div>
        <div class="accuracy-label" style="color:{badge_color}">{label}</div>
        <div style="font-size: 48px; margin: 20px 0;">{emoji}</div>
        <div style="font-size: 28px; font-weight: bold; color: {badge_color};">{celebration}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Word breakdown
    st.markdown('<div class="section-subtitle">📊 Your Reading Details:</div>', 
                unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📖 Total Words", result["total_words"])
    c2.metric("✅ Correct", result["correct_words"])
    c3.metric("⚠️ Different", result["substituted_words"])
    c4.metric("❌ Missed", result["missed_words"])
    
    if result.get("extra_words", 0) > 0:
        st.warning(f"➕ **Extra words you added:** {result['extra_words']}")
    
    st.markdown("")
    
    # Word-by-word comparison
    st.markdown('<div class="section-subtitle">🔍 Word-by-Word Check:</div>', 
                unsafe_allow_html=True)
    
    st.markdown(
        '<span class="legend-pill" style="background:#E8F5E9;color:#2e7d32; border: 2px solid #4CAF50;">✅ Correct</span>'
        '<span class="legend-pill" style="background:#FFF3E0;color:#e65100; border: 2px solid #FF9800;">⚠️ Different</span>'
        '<span class="legend-pill" style="background:#FFEBEE;color:#c62828; border: 2px solid #FF6B6B;">❌ Missed</span>'
        '<span class="legend-pill" style="background:#E3F2FD;color:#1565c0; border: 2px solid #1976D2;">➕ Extra</span>',
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
        message = "🌟 **READING SUPERSTAR!** You are an incredible reader! You read this perfectly! Keep up the excellent work!"
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
Result: {celebration}

📊 WORD BREAKDOWN
Total Words: {result["total_words"]}
✅ Correct: {result["correct_words"]}
⚠️ Different: {result["substituted_words"]}
❌ Missed: {result["missed_words"]}
➕ Extra: {result["extra_words"]}

--- ORIGINAL STORY ---
{PARA_FULL_STORY}
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
