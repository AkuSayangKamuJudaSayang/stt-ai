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
import time

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
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        font-family: 'Nunito', sans-serif;
    }
    
    /* Animated background with floating elements */
    .main {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #FFEBEE 100%);
        position: relative;
        overflow: hidden;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(255,107,107,0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(25,118,210,0.1) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(255,215,0,0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Floating bubbles */
    @keyframes float-up {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 0.8; }
        90% { opacity: 0.8; }
        100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
    }
    
    .bubble {
        position: fixed;
        bottom: -100px;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        animation: float-up 15s infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    .bubble:nth-child(1) { left: 10%; width: 40px; height: 40px; animation-delay: 0s; }
    .bubble:nth-child(2) { left: 30%; width: 60px; height: 60px; animation-delay: 3s; }
    .bubble:nth-child(3) { left: 50%; width: 30px; height: 30px; animation-delay: 6s; }
    .bubble:nth-child(4) { left: 70%; width: 50px; height: 50px; animation-delay: 9s; }
    .bubble:nth-child(5) { left: 90%; width: 45px; height: 45px; animation-delay: 12s; }

    /* Game title with bounce animation */
    @keyframes title-bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes sparkle {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    
    .game-title {
        font-family: 'Fredoka One', cursive;
        font-size: clamp(36px, 8vw, 64px);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #1976D2, #FF6B6B);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 20px 0;
        animation: gradient-shift 3s ease infinite, title-bounce 2s ease-in-out infinite;
        text-shadow: none;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.1));
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .game-subtitle {
        font-family: 'Nunito', sans-serif;
        font-size: clamp(18px, 5vw, 24px);
        text-align: center;
        color: #1976D2;
        font-weight: 800;
        margin-bottom: 30px;
        animation: sparkle 2s ease-in-out infinite;
    }
    
    /* Main menu container */
    .menu-container {
        background: rgba(255,255,255,0.9);
        border-radius: 30px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 0 20px 60px rgba(25, 118, 210, 0.2);
        border: 3px solid rgba(255, 107, 107, 0.3);
        backdrop-filter: blur(10px);
    }

    /* Story Cards - Sliding Container */
    .story-slider-container {
        position: relative;
        width: 100%;
        overflow: hidden;
        margin: 30px 0;
        padding: 20px 0;
    }
    
    .story-cards-wrapper {
        display: flex;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        gap: 25px;
    }
    
    .story-card {
        min-width: calc(100% - 50px);
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
        border-radius: 30px;
        padding: 35px 30px;
        border: 4px solid transparent;
        background-clip: padding-box;
        position: relative;
        box-shadow: 0 15px 35px rgba(25, 118, 210, 0.25);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    
    .story-card::before {
        content: '';
        position: absolute;
        top: -4px;
        left: -4px;
        right: -4px;
        bottom: -4px;
        background: linear-gradient(135deg, #FF6B6B, #1976D2, #FF6B6B);
        border-radius: 34px;
        z-index: -1;
        opacity: 0.5;
        transition: opacity 0.3s;
    }
    
    .story-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(25, 118, 210, 0.35);
    }
    
    .story-card:hover::before {
        opacity: 1;
    }
    
    .story-card.active {
        border-color: #FF6B6B;
        background: linear-gradient(135deg, #FFF5F5 0%, #F0F7FF 100%);
        transform: scale(1.02);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3);
    }
    
    .story-card.completed {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #F1F8E9 0%, #FFFFFF 100%);
        opacity: 0.9;
    }
    
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    
    .card-number-container {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .card-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #FF6B6B, #FF8E72);
        color: white;
        border-radius: 50%;
        width: 55px;
        height: 55px;
        font-weight: 900;
        font-size: 24px;
        font-family: 'Fredoka One', cursive;
        box-shadow: 0 8px 16px rgba(255, 107, 107, 0.3);
        animation: pulse-glow 2s ease-in-out infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 8px 16px rgba(255, 107, 107, 0.3); }
        50% { box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5); }
    }
    
    .card-emoji {
        font-size: 36px;
        animation: float-emoji 3s ease-in-out infinite;
    }
    
    @keyframes float-emoji {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .card-status {
        font-size: 28px;
    }
    
    .card-text {
        font-size: clamp(16px, 3vw, 20px);
        line-height: 2;
        color: #333;
        word-wrap: break-word;
        letter-spacing: 0.5px;
    }
    
    /* Word highlighting */
    .word {
        display: inline;
        padding: 3px 6px;
        margin: 0 1px;
        border-radius: 6px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
        position: relative;
    }
    
    .word.highlighted {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #333;
        font-weight: 800;
        box-shadow: 0 0 15px rgba(255, 165, 0, 0.6);
        animation: highlight-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        transform: scale(1.05);
    }
    
    @keyframes highlight-pop {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1.05); }
    }
    
    /* Progress indicator */
    .progress-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 30px 0;
    }
    
    .progress-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #E0E0E0;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .progress-dot.active {
        background: linear-gradient(135deg, #FF6B6B, #FF8E72);
        transform: scale(1.3);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
    }
    
    .progress-dot.completed {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
    }

    /* Recording indicator */
    .recording-indicator {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 15px 25px;
        background: linear-gradient(135deg, #FF6B6B, #FF4444);
        color: white;
        border-radius: 50px;
        font-weight: 800;
        font-size: 18px;
        animation: recording-pulse 1.5s ease-in-out infinite;
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
    }
    
    @keyframes recording-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .recording-dot {
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        animation: blink 1s ease-in-out infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Result card */
    .result-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(240,247,255,0.95));
        border-radius: 30px;
        padding: 30px;
        margin: 20px 0;
        border: 3px solid #1976D2;
        box-shadow: 0 15px 35px rgba(25, 118, 210, 0.2);
        backdrop-filter: blur(10px);
    }

    /* Score badge */
    .score-container {
        text-align: center;
        padding: 30px;
        position: relative;
    }
    
    .score-circle {
        width: 200px;
        height: 200px;
        margin: 0 auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        animation: score-appear 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes score-appear {
        0% { transform: scale(0) rotate(-180deg); opacity: 0; }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    
    .score-inner {
        font-family: 'Fredoka One', cursive;
        font-size: 64px;
        color: white;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }

    /* Legend pills */
    .legend-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }
    
    .legend-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 10px 20px;
        border-radius: 50px;
        font-size: clamp(12px, 3vw, 14px);
        font-weight: 700;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .legend-pill:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }

    /* Section titles */
    .section-title {
        font-family: 'Fredoka One', cursive;
        font-size: clamp(24px, 6vw, 36px);
        font-weight: 900;
        color: #FF6B6B;
        margin-top: 20px;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(255, 107, 107, 0.2);
        position: relative;
        display: inline-block;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF6B6B, #1976D2);
        border-radius: 2px;
    }
    
    .section-subtitle {
        font-family: 'Nunito', sans-serif;
        font-size: clamp(16px, 4vw, 20px);
        color: #1976D2;
        font-weight: 800;
        margin-bottom: 15px;
    }

    /* Custom button styles */
    .game-button {
        background: linear-gradient(135deg, #1976D2, #42A5F5);
        color: white;
        border: none;
        border-radius: 50px;
        font-family: 'Fredoka One', cursive;
        font-size: clamp(14px, 3vw, 18px);
        font-weight: 700;
        padding: clamp(12px, 2vw, 18px) clamp(24px, 4vw, 36px);
        box-shadow: 0 8px 20px rgba(25, 118, 210, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        letter-spacing: 0.5px;
    }
    
    .game-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(25, 118, 210, 0.4);
    }
    
    .game-button:active {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(25, 118, 210, 0.3);
    }
    
    .game-button.red {
        background: linear-gradient(135deg, #FF6B6B, #FF8E72);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
    }
    
    .game-button.red:hover {
        box-shadow: 0 12px 25px rgba(255, 107, 107, 0.4);
    }
    
    .game-button.green {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
    }

    /* Streamlit element customizations */
    [data-testid="stMetricContainer"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #E3F2FD 100%);
        border: 3px solid #1976D2;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(25, 118, 210, 0.15);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetricContainer"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(25, 118, 210, 0.25);
    }
    
    /* Info/Warning/Success/Error boxes */
    .stAlert {
        border-radius: 20px;
        border: none;
        font-family: 'Nunito', sans-serif;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 20px;
        border: 3px solid #1976D2;
        font-family: 'Nunito', sans-serif;
        font-size: 16px;
        font-weight: 600;
        background: rgba(255,255,255,0.9);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .game-title {
            font-size: 28px;
        }
        
        .section-title {
            font-size: 22px;
        }
        
        .story-card {
            padding: 25px 20px;
        }
        
        .card-text {
            font-size: 16px;
            line-height: 1.8;
        }
        
        .card-number {
            width: 45px;
            height: 45px;
            font-size: 20px;
        }
        
        .score-circle {
            width: 150px;
            height: 150px;
        }
        
        .score-inner {
            font-size: 48px;
        }
    }
</style>

<!-- Floating bubbles for fun background effect -->
<div class="bubble"></div>
<div class="bubble"></div>
<div class="bubble"></div>
<div class="bubble"></div>
<div class="bubble"></div>
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
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "completed_cards" not in st.session_state:
    st.session_state.completed_cards = set()
if "spoken_words_set" not in st.session_state:
    st.session_state.spoken_words_set = set()
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

# ─────────────────────────────────────────────
#  The Story - Para's Adventure (Split into 4 Cards)
# ─────────────────────────────────────────────

PARA_FULL_STORY = """Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home. It is getting dark. There are many cars on the road because it is the end of the work day. Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing! Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man."""

# Split story into 4 logical cards
STORY_CARDS = [
    {
        "number": 1,
        "emoji": "🏠",
        "title": "Para's Journey Begins",
        "text": "Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home.",
        "color": "#FF6B6B"
    },
    {
        "number": 2,
        "emoji": "🌆",
        "title": "Getting Dark",
        "text": "It is getting dark. There are many cars on the road because it is the end of the work day.",
        "color": "#FF9800"
    },
    {
        "number": 3,
        "emoji": "🚗",
        "title": "A Big Surprise!",
        "text": "Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing!",
        "color": "#1976D2"
    },
    {
        "number": 4,
        "emoji": "👮",
        "title": "The Dancing Officer",
        "text": "Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man.",
        "color": "#4CAF50"
    }
]

# ─────────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────────

def get_words_from_text(text):
    """Extract words from text."""
    import re
    return re.findall(r'\b\w+\b', text.lower())

def highlight_spoken_words(spoken_text):
    """
    Create HTML with real-time highlighting of spoken words.
    Compares spoken words with story words and highlights matches.
    """
    spoken_words = set(get_words_from_text(spoken_text))
    st.session_state.spoken_words_set = spoken_words
    
    html_parts = []
    for idx, card in enumerate(STORY_CARDS):
        story_words = get_words_from_text(card["text"])
        is_active = idx == st.session_state.current_card_index
        is_completed = idx in st.session_state.completed_cards
        
        card_class = "story-card"
        if is_active:
            card_class += " active"
        elif is_completed:
            card_class += " completed"
        
        status_icon = "✅" if is_completed else "📖" if is_active else "🔒"
        
        card_html = f'<div class="{card_class}">'
        card_html += f'<div class="card-header">'
        card_html += f'<div class="card-number-container">'
        card_html += f'<span class="card-number" style="background: linear-gradient(135deg, {card["color"]}, {card["color"]}dd);">{card["number"]}</span>'
        card_html += f'<span class="card-emoji">{card["emoji"]}</span>'
        card_html += f'</div>'
        card_html += f'<span class="card-status">{status_icon}</span>'
        card_html += f'</div>'
        
        card_html += f'<div class="card-text">'
        for word in story_words:
            clean_word = ''.join(c for c in word if c.isalnum())
            is_spoken = clean_word in spoken_words
            
            if is_spoken:
                card_html += f'<span class="word highlighted">{word}</span> '
            else:
                card_html += f'<span class="word">{word}</span> '
        
        card_html += '</div>'
        card_html += '</div>'
        html_parts.append(card_html)
    
    # Create the slider wrapper
    all_cards_html = f"""
    <div class="story-slider-container">
        <div class="story-cards-wrapper" style="transform: translateX(-{st.session_state.current_card_index * 100}%);">
            {''.join(html_parts)}
        </div>
    </div>
    """
    
    # Progress dots
    dots_html = '<div class="progress-container">'
    for i in range(4):
        dot_class = "progress-dot"
        if i == st.session_state.current_card_index:
            dot_class += " active"
        if i in st.session_state.completed_cards:
            dot_class += " completed"
        dots_html += f'<div class="{dot_class}"></div>'
    dots_html += '</div>'
    
    return all_cards_html + dots_html

def display_story_cards_with_slider(highlight_text=None):
    """Display the 4 story cards with slider and optional highlighting."""
    if highlight_text and highlight_text.strip():
        st.markdown(highlight_spoken_words(highlight_text), unsafe_allow_html=True)
    else:
        # Display without highlighting
        html_parts = []
        for idx, card in enumerate(STORY_CARDS):
            is_active = idx == st.session_state.current_card_index
            is_completed = idx in st.session_state.completed_cards
            
            card_class = "story-card"
            if is_active:
                card_class += " active"
            elif is_completed:
                card_class += " completed"
            
            status_icon = "✅" if is_completed else "📖" if is_active else "🔒"
            
            card_html = f'<div class="{card_class}">'
            card_html += f'<div class="card-header">'
            card_html += f'<div class="card-number-container">'
            card_html += f'<span class="card-number" style="background: linear-gradient(135deg, {card["color"]}, {card["color"]}dd);">{card["number"]}</span>'
            card_html += f'<span class="card-emoji">{card["emoji"]}</span>'
            card_html += f'</div>'
            card_html += f'<span class="card-status">{status_icon}</span>'
            card_html += f'</div>'
            card_html += f'<div class="card-text">{card["text"]}</div>'
            card_html += '</div>'
            html_parts.append(card_html)
        
        all_cards_html = f"""
        <div class="story-slider-container">
            <div class="story-cards-wrapper" style="transform: translateX(-{st.session_state.current_card_index * 100}%);">
                {''.join(html_parts)}
            </div>
        </div>
        """
        
        dots_html = '<div class="progress-container">'
        for i in range(4):
            dot_class = "progress-dot"
            if i == st.session_state.current_card_index:
                dot_class += " active"
            if i in st.session_state.completed_cards:
                dot_class += " completed"
            dots_html += f'<div class="{dot_class}"></div>'
        dots_html += '</div>'
        
        st.markdown(all_cards_html + dots_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Main Menu Page
# ─────────────────────────────────────────────

def show_menu():
    st.markdown("""
    <div class="game-title">🦜 Para's Reading Adventure 🦜</div>
    <div class="game-subtitle">🌟 Help Para practice reading! 📚</div>
    """, unsafe_allow_html=True)
    
    # Welcome container
    st.markdown("""
    <div class="menu-container">
        <div style="text-align: center;">
            <h2 style="color: #1976D2; font-family: 'Fredoka One', cursive; font-size: 28px;">
                🌟 Welcome, Young Reader! 🌟
            </h2>
            <p style="font-size: 18px; color: #555; margin: 20px 0; line-height: 1.6;">
                Get ready for an exciting adventure with Para the Parrot! 🦜
            </p>
            <p style="font-size: 16px; color: #777; margin: 15px 0; line-height: 1.5;">
                Read Para's amazing story about flying through the market 
                and meeting a <span style="color: #FF6B6B; font-weight: bold;">dancing police officer</span>!
            </p>
            <p style="font-size: 18px; color: #1976D2; font-weight: bold;">
                Can you read with 95% accuracy? Let's find out! 🎉
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Story preview
    st.markdown('<div class="section-title">📖 Story Preview</div>', unsafe_allow_html=True)
    
    # Reset card state for preview
    temp_current = st.session_state.current_card_index
    temp_completed = st.session_state.completed_cards.copy()
    st.session_state.current_card_index = 0
    st.session_state.completed_cards = set()
    display_story_cards_with_slider()
    st.session_state.current_card_index = temp_current
    st.session_state.completed_cards = temp_completed
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Menu buttons
    st.markdown('<div class="section-title">🎮 Choose Your Adventure</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <button onclick="document.getElementById('btn_start').click()" 
                    class="game-button green" 
                    style="width: 100%; font-size: 20px;">
                🎮 START GAME
            </button>
        </div>
        """, unsafe_allow_html=True)
        if st.button("START GAME", key="btn_start", use_container_width=True):
            st.session_state.page = "game"
            st.session_state.current_card_index = 0
            st.session_state.completed_cards = set()
            st.session_state.spoken_words_set = set()
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <button class="game-button" style="width: 100%; font-size: 20px;">
                📖 READ STORY
            </button>
        </div>
        """, unsafe_allow_html=True)
        if st.button("READ STORY", key="btn_read", use_container_width=True):
            st.session_state.page = "read_story"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <button class="game-button red" style="width: 100%; font-size: 20px;">
                ❓ HOW TO PLAY
            </button>
        </div>
        """, unsafe_allow_html=True)
        if st.button("HOW TO PLAY", key="btn_help", use_container_width=True):
            st.session_state.page = "instructions"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <p style="font-size: 20px; color: #1976D2; font-weight: bold;">
            ✨ Made with ❤️ for amazing young readers! ✨
        </p>
        <p style="font-size: 14px; color: #999;">
            🦜 Para believes in you! You can do it! 🌟
        </p>
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
    
    st.markdown('<div class="section-title">📖 Para\'s Adventure Story</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(25,118,210,0.1)); 
                border-radius: 20px; padding: 20px; margin: 20px 0; border-left: 6px solid #FF6B6B;">
    <p style="font-size: 16px; color: #333; margin: 0;">
    📚 Take your time reading through each part of Para's adventure! 
    Use the arrows to move between cards. 🦜
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation for reading
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("◀ Previous", use_container_width=True) and st.session_state.current_card_index > 0:
            st.session_state.current_card_index -= 1
            st.rerun()
    with col3:
        if st.button("Next ▶", use_container_width=True) and st.session_state.current_card_index < 3:
            st.session_state.current_card_index += 1
            st.rerun()
    
    display_story_cards_with_slider()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎮 Ready to Read? Let's Go!", use_container_width=True):
            st.session_state.page = "game"
            st.session_state.current_card_index = 0
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
    
    # Instructions with cards
    instructions = [
        {
            "step": "1",
            "icon": "👂",
            "title": "Listen & Read",
            "description": "Read Para's exciting story one card at a time. The story has 4 fun parts!",
            "color": "#FF6B6B"
        },
        {
            "step": "2",
            "icon": "🎤",
            "title": "Record Your Voice",
            "description": "Click the microphone and read each card aloud. Speak clearly!",
            "color": "#FF9800"
        },
        {
            "step": "3",
            "icon": "✨",
            "title": "Watch Real-Time Magic",
            "description": "As you speak, watch the words light up with golden sparkles!",
            "color": "#1976D2"
        },
        {
            "step": "4",
            "icon": "🌟",
            "title": "Get Your Score",
            "description": "See how well you did! Get 95% to become a Reading Superstar!",
            "color": "#4CAF50"
        }
    ]
    
    for inst in instructions:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, white, {inst['color']}15);
                    border-radius: 20px; 
                    padding: 25px; 
                    margin: 15px 0;
                    border-left: 6px solid {inst['color']};
                    box-shadow: 0 8px 20px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="background: linear-gradient(135deg, {inst['color']}, {inst['color']}dd);
                            color: white;
                            border-radius: 50%;
                            width: 50px;
                            height: 50px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: 900;
                            font-size: 20px;
                            font-family: 'Fredoka One', cursive;
                            box-shadow: 0 6px 15px {inst['color']}40;">
                    {inst['step']}
                </div>
                <div>
                    <h3 style="color: {inst['color']}; margin: 0; font-family: 'Fredoka One', cursive;">
                        {inst['icon']} {inst['title']}
                    </h3>
                    <p style="color: #555; margin: 5px 0 0 0; font-size: 16px;">
                        {inst['description']}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Color legend
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">🎨 Color Legend</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="legend-container">
        <span class="legend-pill" style="background:#E8F5E9;color:#2e7d32; border: 2px solid #4CAF50;">
            ✅ Correct Words
        </span>
        <span class="legend-pill" style="background:#FFF3E0;color:#e65100; border: 2px solid #FF9800;">
            ⚠️ Different Words
        </span>
        <span class="legend-pill" style="background:#FFEBEE;color:#c62828; border: 2px solid #FF6B6B;">
            ❌ Missed Words
        </span>
        <span class="legend-pill" style="background:#E3F2FD;color:#1565c0; border: 2px solid #1976D2;">
            ➕ Extra Words
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Tips
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E8F5E9, #FFFFFF); 
                border-radius: 25px; 
                padding: 25px; 
                border-left: 6px solid #4CAF50; 
                margin: 20px 0;
                box-shadow: 0 8px 20px rgba(76, 175, 80, 0.2);">
        <h3 style="color: #2e7d32; font-family: 'Fredoka One', cursive;">💡 Tips for Best Results</h3>
        <ul style="font-size: 16px; line-height: 2; color: #555;">
            <li>🔇 Find a quiet place to read without background noise</li>
            <li>🗣️ Speak clearly and at a comfortable speed</li>
            <li>🎯 Read with expression - it makes it more fun!</li>
            <li>⏸️ Take a breath between sentences</li>
            <li>🔄 You can try again as many times as you want</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Main Game Page
# ─────────────────────────────────────────────

def show_game():
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("◀ Menu", key="btn_back_game"):
            st.session_state.page = "menu"
            st.session_state.current_card_index = 0
            st.session_state.completed_cards = set()
            st.session_state.spoken_words_set = set()
            st.rerun()
    
    st.markdown('<div class="section-title">🎮 Let\'s Read!</div>', unsafe_allow_html=True)
    
    # Card navigation
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("◀ Prev Card", use_container_width=True) and st.session_state.current_card_index > 0:
            st.session_state.current_card_index -= 1
            st.rerun()
    with col4:
        if st.button("Next Card ▶", use_container_width=True) and st.session_state.current_card_index < 3:
            st.session_state.current_card_index += 1
            st.rerun()
    
    # Show current card info
    current_card = STORY_CARDS[st.session_state.current_card_index]
    st.markdown(f"""
    <div style="text-align: center; 
                background: linear-gradient(135deg, {current_card['color']}20, white);
                border-radius: 20px;
                padding: 15px;
                margin: 10px 0;">
        <span style="font-size: 40px;">{current_card['emoji']}</span>
        <span style="font-family: 'Fredoka One', cursive; 
                     font-size: 22px; 
                     color: {current_card['color']};
                     margin-left: 10px;">
            Card {current_card['number']}: {current_card['title']}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the story cards with slider
    display_story_cards_with_slider(
        highlight_text=st.session_state.transcribed_text if st.session_state.transcribed_text else None
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recording section
    st.markdown('<div class="section-subtitle">🎤 Record Your Reading</div>', unsafe_allow_html=True)
    
    # Recording indicator
    if st.session_state.is_recording:
        st.markdown("""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <div class="recording-indicator">
                <div class="recording-dot"></div>
                Recording... Speak now!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    audio_value = st.audio_input(
        label="Click the microphone to start recording",
        label_visibility="collapsed",
        key="mic_input",
    )
    
    if audio_value is not None:
        st.session_state.is_recording = False
        st.audio(audio_value, format="audio/wav")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 Check My Reading", use_container_width=True, key="btn_transcribe"):
                with st.spinner("🤖 Computer is listening carefully..."):
                    text, error = transcribe(audio_value.getvalue())
                if error:
                    st.error(f"❌ Oops! {error}")
                else:
                    st.session_state.transcribed_text = text
                    st.session_state.accuracy_result = None
                    # Mark current card as completed if they read something
                    if text.strip():
                        st.session_state.completed_cards.add(st.session_state.current_card_index)
                    st.success("✅ Got it! Now let me check your reading...")
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show transcribed text if available
    if st.session_state.transcribed_text:
        st.markdown('<div class="section-subtitle">🔍 What I Heard You Say:</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            transcribed_text = st.text_area(
                label="You can fix it if the computer made a mistake",
                value=st.session_state.transcribed_text,
                height=100,
                key="transcribed_display",
            )
            st.session_state.transcribed_text = transcribed_text
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🌟 Calculate My Score", use_container_width=True, key="btn_calculate"):
                result = calculate_accuracy(PARA_FULL_STORY, transcribed_text)
                st.session_state.accuracy_result = result
                st.rerun()
    
    # Show results if available
    if st.session_state.accuracy_result:
        show_game_results(st.session_state.accuracy_result)

# ─────────────────────────────────────────────
#  Game Results Display
# ─────────────────────────────────────────────

def show_game_results(result):
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<br>", unsafe_allow_html=True)
    
    pct = result["accuracy_pct"]
    label, color = get_accuracy_label(pct)
    
    # Determine score circle gradient
    if pct >= 95:
        gradient = "linear-gradient(135deg, #4CAF50, #66BB6A)"
        emoji = "🌟⭐🌟"
        celebration = "READING SUPERSTAR! 🚀"
    elif pct >= 85:
        gradient = "linear-gradient(135deg, #1976D2, #42A5F5)"
        emoji = "⭐👏🎉"
        celebration = "GREAT JOB! 👏"
    elif pct >= 70:
        gradient = "linear-gradient(135deg, #FF9800, #FFB74D)"
        emoji = "👍😊"
        celebration = "GOOD EFFORT! 💪"
    else:
        gradient = "linear-gradient(135deg, #FF6B6B, #FF8A80)"
        emoji = "💪📚✨"
        celebration = "KEEP GOING! 📚"
    
    # Animated score display
    st.markdown(f"""
    <div class="score-container">
        <div class="score-circle" style="background: {gradient}; 
                                          box-shadow: 0 15px 40px rgba(0,0,0,0.2);">
            <span class="score-inner">{pct}%</span>
        </div>
        <h2 style="color: #333; font-family: 'Fredoka One', cursive; font-size: 28px; margin-top: 20px;">
            {label}
        </h2>
        <div style="font-size: 54px; margin: 20px 0; animation: title-bounce 1s ease-in-out infinite;">
            {emoji}
        </div>
        <h3 style="color: {gradient.split('(')[1].split(',')[0]}; 
                   font-family: 'Fredoka One', cursive; 
                   font-size: 32px;">
            {celebration}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Word breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">📊 Your Reading Details</div>', 
                unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📖 Total Words", result["total_words"])
    with c2:
        st.metric("✅ Correct", result["correct_words"])
    with c3:
        st.metric("⚠️ Different", result["substituted_words"])
    with c4:
        st.metric("❌ Missed", result["missed_words"])
    
    if result.get("extra_words", 0) > 0:
        st.warning(f"➕ **Extra words you added:** {result['extra_words']}")
    
    # Word-by-word comparison
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">🔍 Word-by-Word Check</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div class="legend-container">
        <span class="legend-pill" style="background:#E8F5E9;color:#2e7d32; border: 2px solid #4CAF50;">
            ✅ Correct
        </span>
        <span class="legend-pill" style="background:#FFF3E0;color:#e65100; border: 2px solid #FF9800;">
            ⚠️ Different
        </span>
        <span class="legend-pill" style="background:#FFEBEE;color:#c62828; border: 2px solid #FF6B6B;">
            ❌ Missed
        </span>
        <span class="legend-pill" style="background:#E3F2FD;color:#1565c0; border: 2px solid #1976D2;">
            ➕ Extra
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    diff_html = build_diff_html(result["diff_tokens"])
    st.markdown(f'<div class="result-card">{diff_html}</div>', unsafe_allow_html=True)
    
    # Encouraging message
    st.markdown("<br>", unsafe_allow_html=True)
    
    if pct >= 95:
        message = "🌟 **READING SUPERSTAR!** You are an incredible reader! Para is so proud of you! You read this perfectly! Keep up the excellent work!"
    elif pct >= 85:
        message = "⭐ **GREAT JOB!** You did really well! Para thinks you're amazing! Keep practicing and you'll be a superstar soon!"
    elif pct >= 70:
        message = "👍 **GOOD EFFORT!** You're doing well! Practice the words that gave you trouble and you'll improve in no time!"
    else:
        message = "💪 **KEEP GOING!** This story was challenging, but that's okay! Para believes in you! Try it again and watch yourself improve!"
    
    st.success(message)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
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
Achievement: {celebration}

📊 WORD BREAKDOWN
Total Words: {result["total_words"]}
✅ Correct: {result["correct_words"]}
⚠️ Different: {result["substituted_words"]}
❌ Missed: {result["missed_words"]}
➕ Extra: {result["extra_words"]}

--- ORIGINAL STORY ---
{PARA_FULL_STORY}

--- WHAT YOU READ ---
{st.session_state.transcribed_text}
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
            st.session_state.current_card_index = 0
            st.session_state.completed_cards = set()
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
