"""Main voice command application with LLM-powered interpretation."""

import pvporcupine
import sounddevice as sd
import struct
import vosk
import json
import os
import time
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
# Map handler functions back to command names for logging
HANDLER_TO_COMMAND = {}
for command_key, phrases in COMMAND_ALIASES.items():
    func = COMMAND_FUNCTIONS[command_key]
    HANDLER_TO_COMMAND[func] = command_key
    for phrase in phrases:
        COMMAND_MAP[phrase.lower()] = func


def get_command_handler_fallback(spoken_text):
    """
    Fallback command handler using old mapping system.

    Returns:
        tuple: (handler_function, command_name) or (None, None) if no match
    """
    spoken_text = spoken_text.lower()
    handler = None
    matched_phrase = None

    if spoken_text in COMMAND_MAP:
        handler = COMMAND_MAP[spoken_text]
        matched_phrase = spoken_text
    else:
        close = get_close_matches(spoken_text, COMMAND_MAP.keys(), n=1, cutoff=0.8)
        if close:
            matched_phrase = close[0]
            handler = COMMAND_MAP[matched_phrase]

    if handler:
        command_name = HANDLER_TO_COMMAND.get(handler, "unknown")
        return (handler, command_name)
    return (None, None)


# Global audio queue (initialized in main)
audio_queue = None

# Global flag to prevent wake word detection during command processing
command_in_progress = False

# Global flag to prevent wake word detection during TTS output
tts_speaking = False


def safe_speak(tts_service, text, blocking=False, cooldown=0.5):
    """
    Speak text and prevent wake word detection during/after TTS.

    Args:
        tts_service: TTSService instance
        text: Text to speak
        blocking: If True, wait for speech to complete
        cooldown: Seconds to wait after TTS before allowing wake words again
    """
    global tts_speaking, audio_queue

    if not text or not text.strip():
        return

    # Flush audio queue before speaking to clear any residual audio
    if audio_queue:
        audio_queue.flush()

    # Set flag to prevent wake word detection
    tts_speaking = True

    if blocking:
        # For blocking calls, speak and wait for completion
        try:
            tts_service.speak(text, blocking=True)
            # Add cooldown after TTS finishes
            sleep(cooldown)
        finally:
            # Clear flag after blocking TTS + cooldown
            tts_speaking = False
            # Flush audio queue again after TTS to clear any echo
            if audio_queue:
                audio_queue.flush()
    else:
        # For non-blocking, estimate speech duration and add cooldown
        # Rough estimate: ~150 words per minute = ~2.5 words per second
        # Average 5 letters per word, so ~12.5 chars per second
        estimated_duration = len(text) / 12.5
        total_duration = estimated_duration + cooldown

        # Speak in background
        tts_service.speak(text, blocking=False)

        # Use a thread to clear the flag after estimated duration + cooldown
        def clear_flag_after_delay():
            sleep(total_duration)
            global tts_speaking
            tts_speaking = False
            # Flush audio queue after TTS to clear any echo
            if audio_queue:
                audio_queue.flush()

        from threading import Thread
        Thread(target=clear_flag_after_delay, daemon=True).start()


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

        # Greet user (using safe_speak to prevent echo)
        safe_speak(tts_service, "Yes?", blocking=True, cooldown=0.5)

        # Listen for command (with retry mechanism)
        text = _listen_for_speech(recognizer, audio_queue, timeout=4)
        print(f"Heard: '{text}'", flush=True)

        # Retry once if nothing was heard
        if not text:
            safe_speak(tts_service, "I didn't catch that. Please try again.", blocking=True, cooldown=0.5)
            sleep(0.3)
            text = _listen_for_speech(recognizer, audio_queue, timeout=4)
            print(f"Retry heard: '{text}'", flush=True)

        if not text:
            safe_speak(tts_service, "Still didn't catch that. Please say the wake word again.", blocking=False, cooldown=0.5)
            return

        # Try LLM interpretation first
        interpretation = None
        llm_available = llm_service.is_available()
        print(f"LLM service availability check: {llm_available}")

        if llm_available:
            print(f"Calling LLM to interpret: '{text}'")
            start_time = time.time()
            try:
                interpretation = llm_service.interpret_command(text)
                elapsed = time.time() - start_time
                print(f"LLM call completed in {elapsed:.2f}s, result: {interpretation is not None}")
                if interpretation is None:
                    print("Warning: LLM service returned None (may have timed out or encountered an error)")
                else:
                    print(f"LLM returned interpretation: {interpretation}")
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"LLM call failed after {elapsed:.2f}s with exception: {e}")
                interpretation = None
        else:
            print("LLM service marked as unavailable (failed initial check)")

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
                safe_speak(tts_service, clarification, blocking=True, cooldown=0.5)
                # Could implement conversational follow-up here
                return

            # Use confidence directly to determine if confirmation is needed
            # This provides a safety check in case needs_confirmation wasn't set correctly
            should_confirm = needs_confirmation or confidence < CONFIDENCE_THRESHOLD

            if command and not should_confirm:
                # High confidence - execute directly
                safe_speak(tts_service, user_message or f"Executing {command}", blocking=True, cooldown=0.5)
                sleep(0.1)

                result = execute_command(command)
                if result.get("success"):
                    safe_speak(tts_service, "Done", blocking=False, cooldown=0.5)
                else:
                    safe_speak(tts_service, f"Error: {result.get('message', 'Command failed')}", blocking=False, cooldown=0.5)
                return

            elif command and should_confirm:
                # Low confidence - ask for confirmation
                cleaned_command = command.replace('_', ' ')
                confirmation_message = (
                    user_message
                    or f"Did you want to {cleaned_command}? Say yes or no."
                )
                print(f"Confirming command: {cleaned_command} (confidence: {confidence:.2f})")
                safe_speak(tts_service, confirmation_message, blocking=True, cooldown=0.5)
                sleep(0.1)

                response = listen_for_yes_no(recognizer, audio_queue, timeout=3)

                if response is True:
                    # User confirmed
                    result = execute_command(command)
                    if result.get("success"):
                        safe_speak(tts_service, "Done", blocking=False, cooldown=0.5)
                    else:
                        safe_speak(tts_service, f"Error: {result.get('message', 'Command failed')}", blocking=False, cooldown=0.5)
                elif response is False:
                    # User denied
                    safe_speak(tts_service, "Cancelled", blocking=False, cooldown=0.5)
                else:
                    # Timeout or unclear
                    safe_speak(tts_service, "I didn't understand. Cancelling.", blocking=False, cooldown=0.5)
                return

            else:
                # LLM couldn't determine command
                safe_speak(tts_service, "I'm not sure what you want. Please try again.", blocking=False, cooldown=0.5)
                print(f"Could not understand (confidence: {confidence:.2f})")
                return

        else:
            # LLM unavailable or returned None - use fallback
            if llm_available:
                print("LLM service is available but returned None - using fallback (may have timed out, errored, or couldn't parse response)")
            else:
                print("LLM service unavailable - using fallback command mapping")
            handler, command_name = get_command_handler_fallback(text)
            if handler:
                print(f"Fallback matched command: {command_name} (from text: '{text}')")
                safe_speak(tts_service, "Executing command", blocking=True, cooldown=0.5)
                sleep(0.5)
                handler()
                safe_speak(tts_service, "Done", blocking=False, cooldown=0.5)
                return

            # No command found
            print("No matching command found.")
            safe_speak(tts_service, "I didn't understand that command. Please try again.", blocking=False, cooldown=0.5)
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
                # Only process wake word if no command is currently in progress and TTS is not speaking
                if not command_in_progress and not tts_speaking:
                    print("Wake word detected!")
                    listen_for_command(recognizer, audio_queue, llm_service, tts_service)
                else:
                    if command_in_progress:
                        print("Wake word detected but ignoring (command in progress)")
                    if tts_speaking:
                        print("Wake word detected but ignoring (TTS speaking)")


if __name__ == "__main__":
    main()
