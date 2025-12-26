"""Configuration management for voice command system."""

import os
from dotenv import load_dotenv

load_dotenv()

# Wake word and speech recognition
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis")
VOSK_MODEL_PATH = os.getenv(
    "VOSK_MODEL_PATH", "/home/steve/models/vosk/vosk-model-small-en-us-0.15"
)

# Audio settings
RATE = 16000
CHANNELS = 1

# API configuration
API_HOST = os.getenv("API_HOST", "http://localhost:5000")

# Ollama LLM configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# TTS configuration
TTS_VOICE_ID = os.getenv("TTS_VOICE_ID", None) or None  # None = system default
TTS_RATE = int(os.getenv("TTS_RATE", "150"))  # Words per minute
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "0.9"))  # 0.0 to 1.0
