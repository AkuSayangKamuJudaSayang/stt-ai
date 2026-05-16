"""
accuracy.py
-----------
Compares the original reading passage against the STT-transcribed text
and computes a Reading Accuracy percentage using difflib.SequenceMatcher.

AI Technique: NLP text comparison (SequenceMatcher + optional Levenshtein)
Course      : ITE153 - Intro to AI and Expert Systems
"""

import re
from difflib import SequenceMatcher

# Optional enhanced metric — install with: pip install python-Levenshtein
try:
    from Levenshtein import distance as lev_distance
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False


# ─────────────────────────────────────────────
#  Text Preprocessing
# ─────────────────────────────────────────────

def normalize(text: str) -> list[str]:
    """
    Converts text to lowercase and removes punctuation,
    then splits into a list of individual words.

    Example:
        "The cat sat." → ["the", "cat", "sat"]
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)   # strip punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text.split()


# ─────────────────────────────────────────────
#  Core Accuracy Calculation
# ─────────────────────────────────────────────

def calculate_accuracy(original: str, transcribed: str) -> dict:
    """
    Compares the original passage with the student's transcribed reading.

    Returns a dictionary containing:
        - accuracy_pct        : overall reading accuracy (0–100%)
        - total_words         : word count in the original passage
        - correct_words       : number of words read correctly
        - substituted_words   : words read but differently from original
        - missed_words        : words in original that were skipped
        - extra_words         : words the student added (not in original)
        - diff_tokens         : list of (word, tag) pairs for UI highlighting
        - levenshtein_distance: character-level edit distance (if available)
    """

    orig_words  = normalize(original)
    trans_words = normalize(transcribed)

    if not orig_words:
        return _empty_result()

    matcher  = SequenceMatcher(None, orig_words, trans_words, autojunk=False)
    ratio    = matcher.ratio()
    accuracy = round(ratio * 100, 2)

    # ── Word-level diff ──────────────────────────────────────────────────
    diff_tokens  = []   # list of {"word": str, "tag": str} for UI rendering
    correct      = []
    substituted  = []
    missed       = []
    extra        = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for w in orig_words[i1:i2]:
                correct.append(w)
                diff_tokens.append({"word": w, "tag": "correct"})

        elif tag == "replace":
            for w in orig_words[i1:i2]:
                substituted.append(w)
                diff_tokens.append({"word": w, "tag": "substituted"})

        elif tag == "delete":
            for w in orig_words[i1:i2]:
                missed.append(w)
                diff_tokens.append({"word": w, "tag": "missed"})

        elif tag == "insert":
            for w in trans_words[j1:j2]:
                extra.append(w)
                diff_tokens.append({"word": w, "tag": "extra"})

    result = {
        "accuracy_pct"      : accuracy,
        "total_words"       : len(orig_words),
        "correct_words"     : len(correct),
        "substituted_words" : len(substituted),
        "missed_words"      : len(missed),
        "extra_words"       : len(extra),
        "diff_tokens"       : diff_tokens,
    }

    # ── Optional: Levenshtein distance ──────────────────────────────────
    if LEVENSHTEIN_AVAILABLE:
        result["levenshtein_distance"] = lev_distance(
            " ".join(orig_words), " ".join(trans_words)
        )

    return result


# ─────────────────────────────────────────────
#  Helper: Performance Label
# ─────────────────────────────────────────────

def get_accuracy_label(pct: float) -> tuple[str, str]:
    """
    Maps an accuracy percentage to a (performance label, Streamlit color).

    Thresholds based on standard oral reading fluency benchmarks:
        95–100% → Independent reading level
        85–94%  → Instructional level
        70–84%  → Developing
        <70%    → Needs support
    """
    if pct >= 95:
        return "Excellent (Independent)", "green"
    elif pct >= 85:
        return "Proficient (Instructional)", "blue"
    elif pct >= 70:
        return "Developing", "orange"
    else:
        return "Needs Support", "red"


# ─────────────────────────────────────────────
#  Helper: Build HTML diff string for Streamlit
# ─────────────────────────────────────────────

def build_diff_html(diff_tokens: list[dict]) -> str:
    """
    Converts diff_tokens into an HTML string with color-coded spans
    suitable for st.markdown(..., unsafe_allow_html=True).

    Color key:
        ✅ green  = correct
        🟠 orange = substituted (read differently)
        🔴 red    = missed (skipped entirely)
        🔵 blue   = extra (added by student)
    """
    COLOR_MAP = {
        "correct"    : "#2e7d32",   # dark green
        "substituted": "#e65100",   # dark orange
        "missed"     : "#c62828",   # dark red
        "extra"      : "#1565c0",   # dark blue
    }
    STYLE_MAP = {
        "correct"    : "",
        "substituted": "text-decoration: line-through;",
        "missed"     : "text-decoration: underline; font-weight: bold;",
        "extra"      : "font-style: italic;",
    }

    parts = []
    for token in diff_tokens:
        word  = token["word"]
        tag   = token["tag"]
        color = COLOR_MAP.get(tag, "#000")
        style = STYLE_MAP.get(tag, "")
        parts.append(
            f'<span style="color:{color}; {style} padding:1px 3px;">{word}</span>'
        )

    return "<p style='font-size:16px; line-height:2;'>" + " ".join(parts) + "</p>"


# ─────────────────────────────────────────────
#  Private helper
# ─────────────────────────────────────────────

def _empty_result() -> dict:
    return {
        "accuracy_pct"      : 0.0,
        "total_words"       : 0,
        "correct_words"     : 0,
        "substituted_words" : 0,
        "missed_words"      : 0,
        "extra_words"       : 0,
        "diff_tokens"       : [],
    }
