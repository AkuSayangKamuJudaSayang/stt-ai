"""
stt.py
------
Handles all Speech-to-Text (STT) operations using the SpeechRecognition
library, which connects to Google's Web Speech API (no API key required).

AI Technique : Speech-to-Text via Google Web Speech API
Course       : ITE153 - Intro to AI and Expert Systems
"""

import io
import wave
import speech_recognition as sr
from pydub import AudioSegment


# ─────────────────────────────────────────────
#  Audio Preprocessing
# ─────────────────────────────────────────────

def preprocess_audio(audio_bytes: bytes) -> bytes:
    """
    Converts uploaded audio (WAV or MP3) to a 16kHz mono WAV file
    in memory — the format expected by SpeechRecognition.

    Parameters:
        audio_bytes : raw bytes from st.audio_input() or st.file_uploader()

    Returns:
        Processed WAV bytes ready for the STT engine.
    """
    try:
        # Load from bytes (pydub auto-detects WAV / MP3 / OGG)
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Normalize to 16kHz mono (optimal for Google Speech API)
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export back to bytes as WAV
        output_buffer = io.BytesIO()
        audio.export(output_buffer, format="wav")
        output_buffer.seek(0)
        return output_buffer.read()

    except Exception as e:
        raise ValueError(f"Audio preprocessing failed: {e}")


# ─────────────────────────────────────────────
#  Speech-to-Text Engine
# ─────────────────────────────────────────────

def transcribe(audio_bytes: bytes, language: str = "en-US") -> tuple[str | None, str | None]:
    """
    Sends preprocessed audio to Google Web Speech API and returns
    the transcribed text.

    Parameters:
        audio_bytes : WAV audio bytes (preprocessed)
        language    : BCP-47 language code (default: "en-US")

    Returns:
        (transcribed_text, error_message)
        On success : ("the transcribed words...", None)
        On failure : (None, "human-readable error message")
    """
    recognizer = sr.Recognizer()

    # Tune sensitivity — lower energy_threshold = picks up quieter speech
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        # Load the WAV bytes into SpeechRecognition's AudioData format
        processed = preprocess_audio(audio_bytes)
        audio_file = io.BytesIO(processed)

        with sr.AudioFile(audio_file) as source:
            # Adjust for ambient noise (first 0.5s of recording)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        # Call Google Web Speech API (free, no key needed)
        text = recognizer.recognize_google(audio_data, language=language)
        return text, None

    except sr.UnknownValueError:
        return None, (
            "Could not understand the audio. "
            "Please speak clearly and try again."
        )
    except sr.RequestError as e:
        return None, (
            f"Could not reach the speech recognition service. "
            f"Check your internet connection. (Detail: {e})"
        )
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Unexpected error during transcription: {e}"


# ─────────────────────────────────────────────
#  Utility: Word count from transcript
# ─────────────────────────────────────────────

def word_count(text: str) -> int:
    """Returns the number of words in a string."""
    if not text or not text.strip():
        return 0
    return len(text.strip().split())