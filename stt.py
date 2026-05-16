"""
stt.py
------
Handles all Speech-to-Text (STT) operations using the AssemblyAI SDK.
AssemblyAI's Universal-3 Pro model is used for high-accuracy transcription.

AI Technique : Speech-to-Text via AssemblyAI (Universal-3 Pro model)
Course       : ITE153 - Intro to AI and Expert Systems
"""

import os
import tempfile
import assemblyai as aai


# ─────────────────────────────────────────────
#  Core Transcription Function
# ─────────────────────────────────────────────

def transcribe(audio_bytes: bytes, api_key: str) -> tuple[str | None, str | None]:
    """
    Sends audio bytes to AssemblyAI for transcription.

    Parameters:
        audio_bytes : raw audio bytes (WAV, MP3, OGG, M4A, etc.)
        api_key     : AssemblyAI API key

    Returns:
        (transcribed_text, error_message)
        On success : ("the transcribed words...", None)
        On failure : (None, "human-readable error message")

    AI Technique:
        Uses AssemblyAI Universal-3 Pro model (primary) with Universal-2
        as a fallback. The speech_models list is an ordered priority list —
        the first available model is used.
    """

    if not api_key or not api_key.strip():
        return None, "No API key provided. Please enter your AssemblyAI API key in the sidebar."

    # Set the API key for this request
    aai.settings.api_key = api_key.strip()

    # Configure transcription — speech_models is REQUIRED by AssemblyAI
    config = aai.TranscriptionConfig(
        speech_models=["universal-3-pro", "universal-2"],
        # universal-3-pro = highest accuracy (primary)
        # universal-2     = fallback if universal-3-pro is unavailable
    )

    # Save audio bytes to a temporary file (AssemblyAI SDK needs a file path or URL)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # Transcribe — SDK handles upload, polling, and result fetching automatically
        transcript = aai.Transcriber().transcribe(tmp_path, config)

        if transcript.status == aai.TranscriptStatus.error:
            return None, f"AssemblyAI error: {transcript.error}"

        if not transcript.text or not transcript.text.strip():
            return None, "No speech detected in the audio. Please try again."

        return transcript.text, None

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return None, "Invalid API key. Please check your AssemblyAI API key in the sidebar."
        if "connection" in error_msg.lower() or "network" in error_msg.lower():
            return None, "No internet connection. AssemblyAI requires an active connection."
        return None, f"Transcription failed: {error_msg}"

    finally:
        # Always clean up the temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ─────────────────────────────────────────────
#  Utility
# ─────────────────────────────────────────────

def word_count(text: str) -> int:
    """Returns the number of words in a string."""
    if not text or not text.strip():
        return 0
    return len(text.strip().split())
