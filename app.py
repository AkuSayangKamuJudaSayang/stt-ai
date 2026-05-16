"""
app.py
------
🎮 Para's Reading Adventure - Duolingo-Style Speech-to-Text Reading Game
A gamified Streamlit application designed for children with an engaging,
game-like interface inspired by Duolingo's design language.

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
    page_title="Para's Reading Adventure",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  Duolingo-Style Game UI Styling
# ─────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
    
    /* Reset & Base */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        font-family: 'Nunito', sans-serif;
        background: #FFFFFF;
    }
    
    /* Main container */
    .main {
        background: #FFFFFF;
    }
    
    /* ── Header Bar ── */
    .game-header {
        background: #58CC02;
        padding: 12px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 3px solid #46A302;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .game-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .game-header-logo {
        font-size: 28px;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    .game-header-xp {
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 6px 16px;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 15px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .game-header-hearts {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .heart-icon {
        font-size: 22px;
        filter: drop-shadow(0 2px 2px rgba(0,0,0,0.1));
    }
    
    /* ── Progress Bar ── */
    .progress-bar-container {
        background: #E5E5E5;
        height: 16px;
        border-radius: 10px;
        margin: 16px 24px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #58CC02, #7CD636);
        border-radius: 10px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .progress-bar-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, transparent 50%);
        border-radius: 10px;
    }
    
    /* ── Card Container ── */
    .cards-viewport {
        position: relative;
        width: 100%;
        max-width: 700px;
        margin: 0 auto;
        height: auto;
        min-height: 300px;
        overflow: hidden;
        padding: 20px 0;
    }
    
    .cards-track {
        display: flex;
        transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        gap: 0;
    }
    
    /* ── Story Card ── */
    .story-card {
        min-width: 100%;
        padding: 32px 28px;
        background: #FFFFFF;
        border-radius: 20px;
        border: 2.5px solid #E5E5E5;
        box-shadow: 0 4px 0 #E5E5E5, 0 8px 24px rgba(0,0,0,0.06);
        position: relative;
        transition: all 0.3s ease;
    }
    
    .story-card.active-card {
        border-color: #1CB0F6;
        box-shadow: 0 4px 0 #1899D6, 0 12px 32px rgba(28, 176, 246, 0.2);
    }
    
    .story-card.completed-card {
        border-color: #58CC02;
        box-shadow: 0 4px 0 #46A302, 0 8px 24px rgba(88, 204, 2, 0.15);
        background: #F7FFF0;
    }
    
    .story-card.locked-card {
        opacity: 0.5;
        pointer-events: none;
    }
    
    /* Card header */
    .card-top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    
    .card-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #F0F0F0;
        border-radius: 14px;
        padding: 8px 16px;
        font-weight: 800;
        font-size: 15px;
        color: #4B4B4B;
    }
    
    .card-badge.active-badge {
        background: #E5F5FF;
        color: #1CB0F6;
    }
    
    .card-badge.completed-badge {
        background: #E5FFD9;
        color: #58CC02;
    }
    
    .card-status-icon {
        font-size: 28px;
    }
    
    /* Card text area */
    .card-reading-area {
        position: relative;
        padding: 16px 0;
    }
    
    .card-sentence {
        font-size: 22px;
        line-height: 2;
        color: #3C3C3C;
        font-weight: 700;
        letter-spacing: 0.3px;
    }
    
    /* Word tokens */
    .word-token {
        display: inline;
        padding: 4px 8px;
        margin: 0 2px;
        border-radius: 8px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        cursor: default;
        line-height: 2.2;
    }
    
    .word-token.unread {
        color: #AFAFAF;
        background: transparent;
    }
    
    .word-token.current {
        color: #1CB0F6;
        background: #E5F5FF;
        font-weight: 800;
        box-shadow: 0 0 0 3px rgba(28, 176, 246, 0.3);
        border-radius: 8px;
        animation: currentPulse 1.5s ease-in-out infinite;
    }
    
    @keyframes currentPulse {
        0%, 100% { box-shadow: 0 0 0 3px rgba(28, 176, 246, 0.3); }
        50% { box-shadow: 0 0 0 6px rgba(28, 176, 246, 0.15); }
    }
    
    .word-token.read {
        color: #58CC02;
        background: #E5FFD9;
        font-weight: 700;
        border-radius: 8px;
    }
    
    .word-token.missed {
        color: #FF4B4B;
        background: #FFE5E5;
        font-weight: 700;
        border-radius: 8px;
        text-decoration: line-through;
        text-decoration-color: #FF4B4B;
        text-decoration-thickness: 2px;
    }
    
    /* ── Card Navigation Dots ── */
    .dots-row {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }
    
    .nav-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #E5E5E5;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .nav-dot.active-dot {
        background: #1CB0F6;
        width: 32px;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(28, 176, 246, 0.4);
    }
    
    .nav-dot.completed-dot {
        background: #58CC02;
        box-shadow: 0 2px 8px rgba(88, 204, 2, 0.3);
    }
    
    /* ── Buttons ── */
    .duo-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 14px 28px;
        border-radius: 16px;
        font-family: 'Nunito', sans-serif;
        font-weight: 800;
        font-size: 17px;
        letter-spacing: 0.3px;
        border: none;
        cursor: pointer;
        transition: all 0.15s ease;
        position: relative;
        text-transform: uppercase;
        box-shadow: 0 4px 0 rgba(0,0,0,0.15);
        width: 100%;
    }
    
    .duo-button:active {
        transform: translateY(2px);
        box-shadow: 0 2px 0 rgba(0,0,0,0.15);
    }
    
    .duo-button.primary {
        background: #58CC02;
        color: #FFFFFF;
        border-bottom: 3px solid #46A302;
    }
    
    .duo-button.primary:hover {
        background: #62D80B;
    }
    
    .duo-button.secondary {
        background: #1CB0F6;
        color: #FFFFFF;
        border-bottom: 3px solid #1899D6;
    }
    
    .duo-button.secondary:hover {
        background: #2DB9F7;
    }
    
    .duo-button.outline {
        background: #FFFFFF;
        color: #1CB0F6;
        border: 2.5px solid #E5E5E5;
        border-bottom: 4px solid #E5E5E5;
        box-shadow: none;
    }
    
    .duo-button.outline:hover {
        background: #F7F7F7;
    }
    
    .duo-button.danger {
        background: #FF4B4B;
        color: #FFFFFF;
        border-bottom: 3px solid #D94040;
    }
    
    .duo-button.small {
        padding: 10px 20px;
        font-size: 14px;
        border-radius: 12px;
    }
    
    /* ── Bottom Sheet / Result Panel ── */
    .result-panel {
        background: #FFFFFF;
        border-radius: 24px 24px 0 0;
        padding: 32px 28px;
        box-shadow: 0 -8px 40px rgba(0,0,0,0.12);
        margin-top: 24px;
    }
    
    .result-score-ring {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px;
        position: relative;
    }
    
    .result-score-ring::before {
        content: '';
        position: absolute;
        inset: -8px;
        border-radius: 50%;
        background: inherit;
        opacity: 0.2;
    }
    
    .result-score-text {
        font-size: 48px;
        font-weight: 900;
        color: #FFFFFF;
        text-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    /* ── Stat Cards ── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: #F7F7F7;
        border-radius: 16px;
        padding: 16px 12px;
        text-align: center;
        border: 2px solid #E5E5E5;
    }
    
    .stat-card.correct-stat {
        border-color: #58CC02;
        background: #F7FFF0;
    }
    
    .stat-card.wrong-stat {
        border-color: #FF4B4B;
        background: #FFF5F5;
    }
    
    .stat-card.neutral-stat {
        border-color: #FF9600;
        background: #FFF8F0;
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: 900;
        color: #3C3C3C;
    }
    
    .stat-label {
        font-size: 13px;
        font-weight: 700;
        color: #AFAFAF;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ── Word result chips ── */
    .word-result-chip {
        display: inline-block;
        padding: 6px 12px;
        margin: 3px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 15px;
        border: 2px solid transparent;
    }
    
    .word-result-chip.correct {
        background: #E5FFD9;
        color: #58CC02;
        border-color: #58CC02;
    }
    
    .word-result-chip.substituted {
        background: #FFF8F0;
        color: #FF9600;
        border-color: #FF9600;
    }
    
    .word-result-chip.missed {
        background: #FFE5E5;
        color: #FF4B4B;
        border-color: #FF4B4B;
    }
    
    .word-result-chip.extra {
        background: #E5F5FF;
        color: #1CB0F6;
        border-color: #1CB0F6;
    }
    
    /* ── Typing indicator ── */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: #FF4B4B;
        color: #FFFFFF;
        border-radius: 20px;
        font-weight: 800;
        font-size: 15px;
    }
    
    .typing-dot {
        width: 10px;
        height: 10px;
        background: #FFFFFF;
        border-radius: 50%;
        animation: typingBlink 0.8s ease-in-out infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingBlink {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    /* ── Misc ── */
    .section-label {
        font-size: 13px;
        font-weight: 800;
        color: #AFAFAF;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .encouragement-banner {
        background: linear-gradient(135deg, #E5FFD9, #F7FFF0);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 2px solid #58CC02;
        margin: 16px 0;
    }
    
    .encouragement-text {
        font-size: 20px;
        font-weight: 800;
        color: #58CC02;
    }
    
    /* ── Mobile Optimization ── */
    @media (max-width: 768px) {
        .card-sentence {
            font-size: 18px;
            line-height: 1.8;
        }
        
        .story-card {
            padding: 20px 16px;
        }
        
        .stat-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .duo-button {
            font-size: 15px;
            padding: 12px 20px;
        }
        
        .result-score-ring {
            width: 110px;
            height: 110px;
        }
        
        .result-score-text {
            font-size: 38px;
        }
    }
    
    /* Hide Streamlit elements we don't need */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
    [data-testid="stToolbar"] {
        display: none;
    }
    
    /* Streamlit button override */
    .stButton > button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 800 !important;
        border-radius: 16px !important;
        border: none !important;
        transition: all 0.15s ease !important;
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
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "completed_cards" not in st.session_state:
    st.session_state.completed_cards = set()
if "spoken_words_set" not in st.session_state:
    st.session_state.spoken_words_set = set()
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "xp_points" not in st.session_state:
    st.session_state.xp_points = 0
if "hearts" not in st.session_state:
    st.session_state.hearts = 5
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# ─────────────────────────────────────────────
#  The Story - Para's Adventure
# ─────────────────────────────────────────────

PARA_FULL_STORY = """Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home. It is getting dark. There are many cars on the road because it is the end of the work day. Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing! Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man."""

# Split story into 4 cards
STORY_CARDS = [
    {
        "number": 1,
        "emoji": "🏠",
        "title": "Off to the Market",
        "text": "Para flies away from the houses and into the market. She must look for some fruits and food she can eat. She is having fun, but wants to go home.",
        "words": ["Para", "flies", "away", "from", "the", "houses", "and", "into", "the", "market", "She", "must", "look", "for", "some", "fruits", "and", "food", "she", "can", "eat", "She", "is", "having", "fun", "but", "wants", "to", "go", "home"]
    },
    {
        "number": 2,
        "emoji": "🌆",
        "title": "The Sun Sets",
        "text": "It is getting dark. There are many cars on the road because it is the end of the work day.",
        "words": ["It", "is", "getting", "dark", "There", "are", "many", "cars", "on", "the", "road", "because", "it", "is", "the", "end", "of", "the", "work", "day"]
    },
    {
        "number": 3,
        "emoji": "🚗",
        "title": "A Surprise!",
        "text": "Then, she sees something! Para stops flying and lands on top of a parked car. She sees a police officer and he is directing traffic. He is also dancing!",
        "words": ["Then", "she", "sees", "something", "Para", "stops", "flying", "and", "lands", "on", "top", "of", "a", "parked", "car", "She", "sees", "a", "police", "officer", "and", "he", "is", "directing", "traffic", "He", "is", "also", "dancing"]
    },
    {
        "number": 4,
        "emoji": "👮",
        "title": "The Dancing Officer",
        "text": "Para has never seen a police officer dance. The police officer is smiling. Para wants to learn more about this man.",
        "words": ["Para", "has", "never", "seen", "a", "police", "officer", "dance", "The", "police", "officer", "is", "smiling", "Para", "wants", "to", "learn", "more", "about", "this", "man"]
    }
]

# Total words across all cards for progress calculation
ALL_STORY_WORDS = []
for card in STORY_CARDS:
    ALL_STORY_WORDS.extend(card["words"])
TOTAL_WORDS = len(ALL_STORY_WORDS)


# ─────────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────────

def get_words_from_text(text):
    """Extract clean words from text."""
    import re
    return re.findall(r'\b\w+\b', text.lower())

def get_current_word_index():
    """Get the index of the current word being read based on completed cards."""
    idx = 0
    for i, card in enumerate(STORY_CARDS):
        if i < st.session_state.current_card_index:
            idx += len(card["words"])
        elif i == st.session_state.current_card_index:
            return idx, card["words"]
    return idx, []

def build_card_html(card_index, spoken_words_set, is_active, is_completed):
    """Build HTML for a single story card with word highlighting."""
    card = STORY_CARDS[card_index]
    words = card["words"]
    
    # Determine card classes
    card_class = "story-card"
    badge_class = "card-badge"
    
    if is_completed:
        card_class += " completed-card"
        badge_class += " completed-badge"
        status_icon = "✅"
    elif is_active:
        card_class += " active-card"
        badge_class += " active-badge"
        status_icon = "📖"
    else:
        card_class += " locked-card"
        status_icon = "🔒"
    
    # Build word tokens
    word_html_parts = []
    for word in words:
        clean_word = word.lower().strip('.,!?;:')
        word_class = "word-token unread"
        
        if clean_word in spoken_words_set:
            word_class = "word-token read"
        elif is_active:
            # Check if this is the next unread word
            word_idx_in_card = words.index(word)
            previous_words = words[:word_idx_in_card]
            all_previous_read = all(
                w.lower().strip('.,!?;:') in spoken_words_set 
                for w in previous_words
            )
            if all_previous_read and clean_word not in spoken_words_set:
                word_class = "word-token current"
        
        word_html_parts.append(f'<span class="{word_class}">{word}</span>')
    
    card_html = f"""
    <div class="{card_class}">
        <div class="card-top-bar">
            <div class="{badge_class}">
                <span style="font-size: 20px;">{card['emoji']}</span>
                <span>Part {card['number']}</span>
            </div>
            <div class="card-status-icon">{status_icon}</div>
        </div>
        <div class="card-reading-area">
            <div class="card-sentence">
                {' '.join(word_html_parts)}
            </div>
        </div>
    </div>
    """
    
    return card_html

def render_story_cards(spoken_text=""):
    """Render all story cards in a sliding track."""
    spoken_words_set = set(get_words_from_text(spoken_text)) if spoken_text else set()
    st.session_state.spoken_words_set = spoken_words_set
    
    current_idx = st.session_state.current_card_index
    completed = st.session_state.completed_cards
    
    # Build all cards
    cards_html = []
    for i in range(4):
        is_active = (i == current_idx)
        is_completed = (i in completed)
        cards_html.append(build_card_html(i, spoken_words_set, is_active, is_completed))
    
    # Calculate translation
    translate_x = current_idx * 100
    
    all_html = f"""
    <div class="cards-viewport">
        <div class="cards-track" style="transform: translateX(-{translate_x}%);">
            {''.join(cards_html)}
        </div>
    </div>
    """
    
    # Navigation dots
    dots_html = '<div class="dots-row">'
    for i in range(4):
        dot_class = "nav-dot"
        if i == current_idx:
            dot_class += " active-dot"
        if i in completed:
            dot_class += " completed-dot"
        dots_html += f'<div class="{dot_class}"></div>'
    dots_html += '</div>'
    
    st.markdown(all_html + dots_html, unsafe_allow_html=True)

def get_progress_percentage():
    """Calculate overall reading progress."""
    total_read = 0
    for i in st.session_state.completed_cards:
        total_read += len(STORY_CARDS[i]["words"])
    # Add current card progress
    current_words = STORY_CARDS[st.session_state.current_card_index]["words"]
    current_read = sum(
        1 for w in current_words 
        if w.lower().strip('.,!?;:') in st.session_state.spoken_words_set
    )
    total_read += current_read
    return int((total_read / TOTAL_WORDS) * 100) if TOTAL_WORDS > 0 else 0


# ─────────────────────────────────────────────
#  Page: Main Menu
# ─────────────────────────────────────────────

def show_menu():
    # Header
    st.markdown(f"""
    <div class="game-header">
        <div class="game-header-left">
            <span style="font-size: 32px;">🦜</span>
            <span class="game-header-logo">Para's Reading</span>
        </div>
        <div class="game-header-xp">
            <span>⭐</span>
            <span>{st.session_state.xp_points} XP</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px 20px;">
        <div style="font-size: 72px; margin-bottom: 10px;">🦜</div>
        <h1 style="font-size: 36px; font-weight: 900; color: #3C3C3C; margin: 0 0 8px;">
            Reading Adventure
        </h1>
        <p style="font-size: 18px; color: #AFAFAF; font-weight: 600; margin: 0;">
            Help Para read her exciting story!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Story preview - show all cards without highlight
    st.markdown('<div style="max-width: 650px; margin: 0 auto; padding: 0 16px;">', unsafe_allow_html=True)
    
    # Temporarily set current to 0 for preview
    temp_idx = st.session_state.current_card_index
    temp_completed = st.session_state.completed_cards.copy()
    st.session_state.current_card_index = 0
    st.session_state.completed_cards = set()
    render_story_cards()
    st.session_state.current_card_index = temp_idx
    st.session_state.completed_cards = temp_completed
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    st.markdown('<div style="max-width: 500px; margin: 30px auto; padding: 0 16px;">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎮 START", key="btn_start_menu", use_container_width=True):
            st.session_state.page = "game"
            st.session_state.current_card_index = 0
            st.session_state.completed_cards = set()
            st.session_state.spoken_words_set = set()
            st.session_state.game_started = True
            st.rerun()
    with col2:
        if st.button("📖 READ STORY", key="btn_read_menu", use_container_width=True):
            st.session_state.page = "read_story"
            st.rerun()
    
    if st.button("❓ HOW TO PLAY", key="btn_help_menu", use_container_width=True):
        st.session_state.page = "instructions"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 30px 20px; color: #AFAFAF; font-weight: 700; font-size: 14px;">
        Press START to begin your reading journey!
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Page: Read Story (Preview Mode)
# ─────────────────────────────────────────────

def show_read_story():
    # Header
    st.markdown(f"""
    <div class="game-header">
        <div class="game-header-left">
            <span style="font-size: 32px;">🦜</span>
            <span class="game-header-logo">Story Preview</span>
        </div>
        <div style="display: flex; gap: 8px;">
    """, unsafe_allow_html=True)
    
    if st.button("✕", key="btn_close_read"):
        st.session_state.page = "menu"
        st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <p style="font-size: 16px; color: #AFAFAF; font-weight: 700;">
            Swipe through Para's story below
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀", key="btn_prev_read", use_container_width=True):
            if st.session_state.current_card_index > 0:
                st.session_state.current_card_index -= 1
                st.rerun()
    with col3:
        if st.button("▶", key="btn_next_read", use_container_width=True):
            if st.session_state.current_card_index < 3:
                st.session_state.current_card_index += 1
                st.rerun()
    
    render_story_cards()
    
    # Start button
    st.markdown('<div style="max-width: 400px; margin: 30px auto; padding: 0 16px;">', unsafe_allow_html=True)
    if st.button("🎮 Ready? Start Reading!", key="btn_start_from_read", use_container_width=True):
        st.session_state.page = "game"
        st.session_state.current_card_index = 0
        st.session_state.completed_cards = set()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Page: How to Play
# ─────────────────────────────────────────────

def show_instructions():
    # Header
    st.markdown(f"""
    <div class="game-header">
        <div class="game-header-left">
            <span style="font-size: 32px;">📚</span>
            <span class="game-header-logo">How to Play</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("✕ Close", key="btn_close_help"):
        st.session_state.page = "menu"
        st.rerun()
    
    steps = [
        {"num": "1", "icon": "👂", "title": "Read the Story", "desc": "Each card shows part of Para's adventure. Read each word clearly!", "color": "#1CB0F6"},
        {"num": "2", "icon": "🎤", "title": "Record Your Voice", "desc": "Tap the microphone and read aloud. Words will light up as you speak!", "color": "#58CC02"},
        {"num": "3", "icon": "✨", "title": "Complete Each Card", "desc": "Finish reading a card to unlock the next one. Watch your progress!", "color": "#FF9600"},
        {"num": "4", "icon": "🌟", "title": "Earn Your Score", "desc": "Get 95% or higher to become a Reading Champion!", "color": "#FF4B4B"},
    ]
    
    for step in steps:
        st.markdown(f"""
        <div style="background: #FFFFFF; border-radius: 16px; padding: 20px; margin: 12px 0;
                    border: 2px solid #E5E5E5; box-shadow: 0 2px 0 #E5E5E5;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="background: {step['color']}; color: #FFFFFF; width: 44px; height: 44px;
                            border-radius: 14px; display: flex; align-items: center; justify-content: center;
                            font-weight: 900; font-size: 20px; flex-shrink: 0;">
                    {step['num']}
                </div>
                <div>
                    <div style="font-weight: 800; font-size: 17px; color: #3C3C3C;">
                        {step['icon']} {step['title']}
                    </div>
                    <div style="font-size: 14px; color: #AFAFAF; font-weight: 600; margin-top: 2px;">
                        {step['desc']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Color legend
    st.markdown('<div class="section-label" style="margin-top: 24px;">Word Colors</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 20px;">
        <span class="word-result-chip correct">✅ Correct</span>
        <span class="word-result-chip substituted">⚠️ Different</span>
        <span class="word-result-chip missed">❌ Missed</span>
        <span class="word-result-chip extra">➕ Extra</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎮 Got it! Let's Play!", key="btn_start_from_help", use_container_width=True):
        st.session_state.page = "game"
        st.session_state.current_card_index = 0
        st.session_state.completed_cards = set()
        st.rerun()


# ─────────────────────────────────────────────
#  Page: Game (Main Reading Interface)
# ─────────────────────────────────────────────

def show_game():
    current_card = STORY_CARDS[st.session_state.current_card_index]
    progress_pct = get_progress_percentage()
    
    # Build hearts display
    hearts_html = ''.join([
        '<span class="heart-icon">❤️</span>' if i < st.session_state.hearts 
        else '<span class="heart-icon">🖤</span>' 
        for i in range(5)
    ])
    
    # Header
    st.markdown(f"""
    <div class="game-header">
        <div class="game-header-left">
            <span style="font-size: 32px;">🦜</span>
            <span class="game-header-logo">Reading</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="game-header-hearts">{hearts_html}</div>
            <div class="game-header-xp">
                <span>⭐</span>
                <span>{st.session_state.xp_points} XP</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    st.markdown(f"""
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: {progress_pct}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Card title
    st.markdown(f"""
    <div style="text-align: center; padding: 10px 0 0;">
        <span style="font-size: 32px;">{current_card['emoji']}</span>
        <h2 style="font-size: 20px; font-weight: 800; color: #3C3C3C; margin: 4px 0 0;">
            {current_card['title']}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Story cards with slider
    render_story_cards(st.session_state.transcribed_text)
    
    # Card navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀", key="btn_game_prev", use_container_width=True):
            if st.session_state.current_card_index > 0:
                st.session_state.current_card_index -= 1
                st.rerun()
    with col3:
        if st.button("▶", key="btn_game_next", use_container_width=True):
            if st.session_state.current_card_index < 3:
                st.session_state.current_card_index += 1
                st.rerun()
    
    st.markdown('<div style="max-width: 500px; margin: 16px auto; padding: 0 16px;">', unsafe_allow_html=True)
    
    # Recording section
    audio_value = st.audio_input(
        label="🎤 Tap the mic and read aloud!",
        label_visibility="collapsed",
        key="mic_game_input",
    )
    
    if audio_value is not None:
        st.audio(audio_value, format="audio/wav")
        
        if st.button("📊 Check My Reading", key="btn_check_reading", use_container_width=True):
            with st.spinner("Listening carefully..."):
                text, error = transcribe(audio_value.getvalue())
            
            if error:
                st.error(f"❌ Hmm, I couldn't hear that clearly. {error}")
            else:
                st.session_state.transcribed_text = text
                st.session_state.accuracy_result = None
                
                # Mark current card complete if they spoke enough words
                if text.strip():
                    words_spoken = set(get_words_from_text(text))
                    card_words = set(w.lower().strip('.,!?;:') for w in current_card["words"])
                    overlap = words_spoken & card_words
                    if len(overlap) >= len(card_words) * 0.5:  # At least 50% read
                        st.session_state.completed_cards.add(st.session_state.current_card_index)
                        # Auto-advance
                        if st.session_state.current_card_index < 3:
                            st.session_state.current_card_index += 1
                
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transcribed text editor
    if st.session_state.transcribed_text:
        st.markdown('<div style="max-width: 500px; margin: 20px auto; padding: 0 16px;">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">What I heard you say</div>', unsafe_allow_html=True)
        
        edited_text = st.text_area(
            "Edit if needed",
            value=st.session_state.transcribed_text,
            height=80,
            key="edit_transcribed",
            label_visibility="collapsed",
        )
        st.session_state.transcribed_text = edited_text
        
        if st.button("🌟 See My Score!", key="btn_see_score", use_container_width=True):
            result = calculate_accuracy(PARA_FULL_STORY, st.session_state.transcribed_text)
            st.session_state.accuracy_result = result
            # Award XP
            pct = result["accuracy_pct"]
            if pct >= 95:
                st.session_state.xp_points += 50
            elif pct >= 85:
                st.session_state.xp_points += 30
            elif pct >= 70:
                st.session_state.xp_points += 15
            else:
                st.session_state.xp_points += 5
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results panel
    if st.session_state.accuracy_result:
        show_game_results(st.session_state.accuracy_result)


# ─────────────────────────────────────────────
#  Game Results Display
# ─────────────────────────────────────────────

def show_game_results(result):
    pct = result["accuracy_pct"]
    label, color_name = get_accuracy_label(pct)
    
    # Determine colors
    if pct >= 95:
        ring_bg = "#58CC02"
        emoji = "🌟"
        title = "LEGENDARY!"
        subtitle = "Perfect reading!"
    elif pct >= 85:
        ring_bg = "#1CB0F6"
        emoji = "⭐"
        title = "AMAZING!"
        subtitle = "Great work!"
    elif pct >= 70:
        ring_bg = "#FF9600"
        emoji = "👍"
        title = "GOOD JOB!"
        subtitle = "Keep practicing!"
    else:
        ring_bg = "#FF4B4B"
        emoji = "💪"
        title = "NICE TRY!"
        subtitle = "You'll get better!"
    
    st.markdown(f"""
    <div class="result-panel">
        <div style="text-align: center;">
            <div class="result-score-ring" style="background: {ring_bg};">
                <span class="result-score-text">{pct}%</span>
            </div>
            <div style="font-size: 48px; margin: 8px 0;">{emoji}</div>
            <h2 style="font-size: 28px; font-weight: 900; color: #3C3C3C; margin: 0;">{title}</h2>
            <p style="font-size: 17px; color: #AFAFAF; font-weight: 700; margin: 4px 0 20px;">{subtitle}</p>
        </div>
        
        <div class="stat-grid">
            <div class="stat-card correct-stat">
                <div class="stat-value">{result["correct_words"]}</div>
                <div class="stat-label">✅ Correct</div>
            </div>
            <div class="stat-card neutral-stat">
                <div class="stat-value">{result["substituted_words"]}</div>
                <div class="stat-label">⚠️ Different</div>
            </div>
            <div class="stat-card wrong-stat">
                <div class="stat-value">{result["missed_words"]}</div>
                <div class="stat-label">❌ Missed</div>
            </div>
            <div class="stat-card" style="border-color: #1CB0F6; background: #F0FAFF;">
                <div class="stat-value">{result.get("extra_words", 0)}</div>
                <div class="stat-label">➕ Extra</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Word-by-word display
    st.markdown('<div class="section-label" style="margin-top: 20px;">Word-by-Word Check</div>', unsafe_allow_html=True)
    
    diff_html = build_diff_html(result["diff_tokens"])
    # Convert diff HTML to use our custom chip styling
    diff_html = diff_html.replace('style="color: green;"', 'class="word-result-chip correct"')
    diff_html = diff_html.replace('style="color: orange;"', 'class="word-result-chip substituted"')
    diff_html = diff_html.replace('style="color: red;"', 'class="word-result-chip missed"')
    diff_html = diff_html.replace('style="color: blue;"', 'class="word-result-chip extra"')
    diff_html = diff_html.replace('<span ', '<span style="display: inline-block; margin: 3px;" ')
    
    st.markdown(f'<div style="padding: 0 16px; line-height: 2.5;">{diff_html}</div>', unsafe_allow_html=True)
    
    # Encouragement
    if pct >= 95:
        enc_text = "🏆 You're a reading superstar! Para is so proud of you!"
    elif pct >= 85:
        enc_text = "🎉 Fantastic effort! You're becoming a great reader!"
    elif pct >= 70:
        enc_text = "💪 Good work! Practice makes perfect - try again!"
    else:
        enc_text = "📚 Don't give up! Every great reader started right where you are!"
    
    st.markdown(f"""
    <div class="encouragement-banner">
        <div class="encouragement-text">{enc_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Retry", key="btn_retry_result", use_container_width=True):
            st.session_state.transcribed_text = ""
            st.session_state.accuracy_result = None
            st.session_state.current_card_index = 0
            st.session_state.completed_cards = set()
            st.session_state.spoken_words_set = set()
            st.rerun()
    with col2:
        export_data = f"Score: {pct}% | {title}\nCorrect: {result['correct_words']} | Different: {result['substituted_words']} | Missed: {result['missed_words']}"
        st.download_button(
            "📥 Save",
            export_data,
            "para_reading_score.txt",
            key="btn_download",
            use_container_width=True,
        )
    with col3:
        if st.button("🏠 Home", key="btn_home_result", use_container_width=True):
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
