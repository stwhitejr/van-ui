"""Text-to-speech service using pyttsx3."""

import pyttsx3
from threading import Thread
from .config import TTS_VOICE_ID, TTS_RATE, TTS_VOLUME


class TTSService:
    """Text-to-speech service wrapper."""

    def __init__(self):
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the TTS engine with configuration."""
        try:
            self.engine = pyttsx3.init()

            # Set voice if specified
            if TTS_VOICE_ID is not None and TTS_VOICE_ID != "":
                try:
                    voice_id = int(TTS_VOICE_ID)
                    voices = self.engine.getProperty("voices")
                    if voices and voice_id < len(voices):
                        self.engine.setProperty("voice", voices[voice_id].id)
                    else:
                        print(f"Warning: Voice ID {voice_id} not found, using default")
                except (ValueError, TypeError):
                    print(
                        f"Warning: Invalid TTS_VOICE_ID '{TTS_VOICE_ID}', using default"
                    )

            # Set rate (words per minute)
            self.engine.setProperty("rate", TTS_RATE)

            # Set volume (0.0 to 1.0)
            self.engine.setProperty("volume", TTS_VOLUME)
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.engine = None

    def speak(self, text, blocking=False):
        """
        Speak text using TTS.

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete. If False, speak in background thread.
        """
        if not self.engine:
            print(f"TTS not available, would say: {text}")
            return

        if not text or not text.strip():
            return

        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error speaking text: {e}")

        if blocking:
            _speak()
        else:
            thread = Thread(target=_speak, daemon=True)
            thread.start()

    def stop(self):
        """Stop any ongoing speech."""
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass

    def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
            self.engine = None
