"""Main voice command application with LLM-powered interpretation."""

import pvporcupine
import sounddevice as sd
import struct
import vosk
import json
import os
from dotenv import load_dotenv
from time import sleep
from difflib import get_close_matches

from voice.config import (
    VOSK_MODEL_PATH,
    WAKE_WORD,
    RATE,
    CHANNELS,
)
from voice.audio_manager import AudioQueue
from voice.llm_service import LLMService
from voice.tts_service import TTSService
from voice.command_executor import execute_command

load_dotenv()

# Fallback command mapping (used if LLM unavailable)
COMMAND_ALIASES = {
    "toggle_inverter": [
        "toggle inverter",
        "toggle her",
        "toggling her",
        "try and murder",
        "time to cook",
        "time to cut",
        "let's cook",
        "let's go",
        "what's cook",
        "what cook",
        "done cooking",
        "it's correct",
        "what",
        "let's go",
        "that's good",
        "i'm hungry",
        "who",
        "food",
        "i'm done",
        "done",
        "don't okay",
        "reverse",
        "reverse the polarity",
        "the polarity",
        "turn on lights",
        "turn off lights",
        "my",
        "right",
        "online",
        "my",
        "turn off boy",
        "like",
        "right",
        "lights",
        "the way",
        "good night",
        "the morning",
    ],
    "toggle_fan": ["fan", "ben", "then", "bench", "van", "the fan", "there", "when"],
}

COMMAND_FUNCTIONS = {
    "toggle_inverter": lambda: execute_command("toggle_inverter"),
    "toggle_fan": lambda: execute_command("toggle_fan"),
}

COMMAND_MAP = {}
for command_key, phrases in COMMAND_ALIASES.items():
    func = COMMAND_FUNCTIONS[command_key]
    for phrase in phrases:
        COMMAND_MAP[phrase.lower()] = func


def get_command_handler_fallback(spoken_text):
    """Fallback command handler using old mapping system."""
    spoken_text = spoken_text.lower()
    if spoken_text in COMMAND_MAP:
        return COMMAND_MAP[spoken_text]
    close = get_close_matches(spoken_text, COMMAND_MAP.keys(), n=1, cutoff=0.8)
    if close:
        return COMMAND_MAP[close[0]]
    return None


# Global audio queue (initialized in main)
audio_queue = None


def audio_callback(indata, frames, time, status):
    """Audio callback for sounddevice."""
    if audio_queue:
        audio_queue.put(bytes(indata))


def listen_for_yes_no(recognizer, audio_queue, timeout=3):
    """
    Listen for yes/no response.

    Args:
        recognizer: Vosk recognizer
        audio_queue: Audio queue
        timeout: Timeout in seconds

    Returns:
        True for yes, False for no, None for timeout/no response
    """
    yes_words = ["yes", "yeah", "yep", "yup", "sure", "okay", "ok"]
    no_words = ["no", "nope", "nah", "cancel", "stop"]

    audio_queue.flush()
    text = ""

    # Listen for a few seconds
    iterations = int((RATE / 1024) * timeout)
    for _ in range(iterations):
        try:
            data = audio_queue.get(timeout=1)
        except:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip().lower()
            if text:
                break

    if not text:
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "").strip().lower()

    print(f"Heard response: '{text}'", flush=True)

    text_lower = text.lower()
    for yes_word in yes_words:
        if yes_word in text_lower:
            return True
    for no_word in no_words:
        if no_word in text_lower:
            return False

    return None  # Timeout or unclear


def listen_for_command(recognizer, audio_queue, llm_service, tts_service):
    """Listen for and process voice command."""
    print("Listening for command...")

    # Greet user
    tts_service.speak("Yes?", blocking=True)

    audio_queue.flush()
    text = ""

    # Listen for a few seconds
    for _ in range(int((RATE / 1024) * 4)):
        try:
            data = audio_queue.get(timeout=1)
        except:
            break
        collected_audio = data
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            print(f"Partial result: {text}")
            if text:
                break

    if not text:
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "").strip()

    print(f"Heard: '{text}'", flush=True)

    if not text:
        tts_service.speak("I didn't catch that. Please try again.")
        return

    # Try LLM interpretation first
    interpretation = None
    if llm_service.is_available():
        interpretation = llm_service.interpret_command(text)

    if interpretation:
        # LLM interpretation successful
        command = interpretation.get("command")
        confidence = interpretation.get("confidence", 0.0)
        user_message = interpretation.get("user_message", "")
        needs_confirmation = interpretation.get("needs_confirmation", False)
        clarification = interpretation.get("clarification")

        if clarification:
            # LLM needs clarification
            tts_service.speak(clarification, blocking=True)
            # Could implement conversational follow-up here
            return

        if command and not needs_confirmation:
            # High confidence - execute directly
            tts_service.speak(user_message or f"Executing {command}", blocking=True)
            sleep(0.1)

            result = execute_command(command)
            if result.get("success"):
                tts_service.speak("Done", blocking=False)
            else:
                tts_service.speak(
                    f"Error: {result.get('message', 'Command failed')}", blocking=False
                )
            return

        elif command and needs_confirmation:
            # Low confidence - ask for confirmation
            confirmation_message = (
                user_message
                or f"Did you want to {command.replace('_', ' ')}? Say yes or no."
            )
            tts_service.speak(confirmation_message, blocking=True)
            sleep(0.3)

            response = listen_for_yes_no(recognizer, audio_queue, timeout=3)

            if response is True:
                # User confirmed
                result = execute_command(command)
                if result.get("success"):
                    tts_service.speak("Done", blocking=False)
                else:
                    tts_service.speak(
                        f"Error: {result.get('message', 'Command failed')}",
                        blocking=False,
                    )
            elif response is False:
                # User denied
                tts_service.speak("Cancelled", blocking=False)
            else:
                # Timeout or unclear
                tts_service.speak("I didn't understand. Cancelling.", blocking=False)
            return

        else:
            # LLM couldn't determine command
            tts_service.speak(
                "I'm not sure what you want. Please try again.", blocking=False
            )
            return

    else:
        # LLM unavailable - use fallback
        print("LLM unavailable, using fallback command mapping")
        handler = get_command_handler_fallback(text)
        if handler:
            tts_service.speak("Executing command", blocking=True)
            sleep(0.5)
            handler()
            tts_service.speak("Done", blocking=False)
            return

        # No command found
        print("No matching command found.")
        tts_service.speak("I didn't understand that command. Please try again.")
        sleep(0.5)


def main():
    """Main application loop."""
    print("Loading Porcupine...")
    porcupine = pvporcupine.create(
        access_key=os.getenv("PICOVOICE_ACCESS_KEY"),
        keywords=[WAKE_WORD, "terminator", "computer"],
    )
    print("Loading Vosk...")
    model = vosk.Model(VOSK_MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, RATE)

    print("Initializing LLM service...")
    llm_service = LLMService()
    if not llm_service.is_available():
        print("Warning: LLM service unavailable, will use fallback command mapping")

    print("Initializing TTS service...")
    tts_service = TTSService()

    global audio_queue
    audio_queue = AudioQueue()

    print("Ready and listening...")

    with sd.RawInputStream(
        samplerate=RATE,
        blocksize=512,
        dtype="int16",
        channels=CHANNELS,
        callback=audio_callback,
    ):
        while True:
            pcm = audio_queue.get()
            pcm_unpacked = struct.unpack_from("h" * (len(pcm) // 2), pcm)
            if porcupine.process(pcm_unpacked) >= 0:
                print("Wake word detected!")
                listen_for_command(recognizer, audio_queue, llm_service, tts_service)


if __name__ == "__main__":
    main()
