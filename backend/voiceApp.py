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
    CONFIDENCE_THRESHOLD,
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

# Global flag to prevent wake word detection during command processing
command_in_progress = False


def audio_callback(indata, frames, time, status):
    """Audio callback for sounddevice."""
    if audio_queue:
        audio_queue.put(bytes(indata))


def _listen_for_speech(recognizer, audio_queue, timeout=4):
    """
    Helper function to listen for speech and return transcribed text.

    Args:
        recognizer: Vosk recognizer
        audio_queue: Audio queue
        timeout: Timeout in seconds

    Returns:
        Transcribed text string, or empty string if nothing heard
    """
    audio_queue.flush()
    text = ""

    # Listen for specified duration
    iterations = int((RATE / 1024) * timeout)
    for _ in range(iterations):
        try:
            data = audio_queue.get(timeout=1)
        except:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            print(f"Partial result: {text}")
            if text:
                break

    if not text:
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "").strip()

    return text


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

    text = _listen_for_speech(recognizer, audio_queue, timeout)
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
    global command_in_progress

    # Set flag to prevent wake word interruption
    command_in_progress = True

    try:
        print("Listening for command...")

        # Greet user
        tts_service.speak("Yes?", blocking=True)

        # Listen for command (with retry mechanism)
        text = _listen_for_speech(recognizer, audio_queue, timeout=4)
        print(f"Heard: '{text}'", flush=True)

        # Retry once if nothing was heard
        if not text:
            tts_service.speak("I didn't catch that. Please try again.", blocking=True)
            sleep(0.3)
            text = _listen_for_speech(recognizer, audio_queue, timeout=4)
            print(f"Retry heard: '{text}'", flush=True)

        if not text:
            tts_service.speak("Still didn't catch that. Please say the wake word again.", blocking=False)
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

            # Log confidence for debugging
            print(f"LLM interpretation - Command: {command}, Confidence: {confidence:.2f}, Needs confirmation: {needs_confirmation}")

            if clarification:
                # LLM needs clarification
                tts_service.speak(clarification, blocking=True)
                # Could implement conversational follow-up here
                return

            # Use confidence directly to determine if confirmation is needed
            # This provides a safety check in case needs_confirmation wasn't set correctly
            should_confirm = needs_confirmation or confidence < CONFIDENCE_THRESHOLD

            if command and not should_confirm:
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

            elif command and should_confirm:
                # Low confidence - ask for confirmation
                cleaned_command = command.replace('_', ' ')
                confirmation_message = (
                    user_message
                    or f"Did you want to {cleaned_command}? Say yes or no."
                )
                print(f"Confirming command: {cleaned_command} (confidence: {confidence:.2f})")
                tts_service.speak(confirmation_message, blocking=True)
                sleep(0.1)

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
                print(f"Could not understand (confidence: {confidence:.2f})")
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
            sleep(0.1)
    finally:
        # Always clear the flag when done processing
        command_in_progress = False


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
                # Only process wake word if no command is currently in progress
                if not command_in_progress:
                    print("Wake word detected!")
                    listen_for_command(recognizer, audio_queue, llm_service, tts_service)
                else:
                    print("Wake word detected but ignoring (command in progress)")


if __name__ == "__main__":
    main()
