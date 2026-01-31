"""Main voice command application."""

import pvporcupine
import sounddevice as sd
import struct
import vosk
import json
import os
from dotenv import load_dotenv
from time import sleep
from threading import Timer
from difflib import get_close_matches

from voice.config import (
    VOSK_MODEL_PATH,
    WAKE_WORD,
    RATE,
    CHANNELS,
)
from voice.audio_manager import AudioQueue
from voice.tts_service import TTSService
from voice.command_executor import execute_command
from voice.llm_service import LLMService

load_dotenv()

# Command mapping for voice commands
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
    "get_inverter_status": [
        "status",
        "inverter status",
        "check inverter",
        "is inverter on",
        "inverter on",
        "inverter off",
        "what's the inverter",
        "inverter state",
        "status inverter",
    ],
    "get_battery_data": [
        "battery",
        "battery status",
        "battery data",
        "check battery",
        "battery voltage",
        "battery charge",
        "state of charge",
        "how's the battery",
        "battery info",
        "battery level",
        "what's the battery",
    ],
    "disable_listening": [
        "off",
        "disable listening",
        "disable microphone",
        "privacy mode",
        "stop listening",
        "turn off microphone",
        "mute microphone",
        "disable wake word",
        "turn off wake word",
    ],
}

def disable_listening():
    """Disable wake word listening for 60 minutes."""
    global wake_word_disabled

    if wake_word_disabled:
        print("Wake word listening already disabled")
        return

    wake_word_disabled = True
    print("Wake word listening disabled for 60 minutes")

    # Re-enable after 60 minutes (3600 seconds)
    def re_enable_listening():
        global wake_word_disabled
        wake_word_disabled = False
        print("Wake word listening re-enabled after 60 minutes")

    timer = Timer(3600.0, re_enable_listening)
    timer.daemon = True
    timer.start()


COMMAND_FUNCTIONS = {
    "toggle_inverter": lambda: execute_command("toggle_inverter"),
    "toggle_fan": lambda: execute_command("toggle_fan"),
    "get_inverter_status": lambda: execute_command("get_inverter_status"),
    "get_battery_data": lambda: execute_command("get_battery_data"),
    "disable_listening": disable_listening,
}

COMMAND_MAP = {}
# Map handler functions back to command names for logging
HANDLER_TO_COMMAND = {}
for command_key, phrases in COMMAND_ALIASES.items():
    func = COMMAND_FUNCTIONS[command_key]
    HANDLER_TO_COMMAND[func] = command_key
    for phrase in phrases:
        COMMAND_MAP[phrase.lower()] = func


def get_command_handler(spoken_text):
    """
    Command handler using command mapping system.

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

# Global flag to disable wake word listening (for privacy mode)
wake_word_disabled = False


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


def conversational_mode(recognizer, audio_queue, llm_service, tts_service):
    """
    Conversational mode: pass user input directly to LLM and speak responses.
    Continues until 20 seconds of silence.
    """
    global command_in_progress

    if not llm_service.is_available():
        safe_speak(tts_service, "LLM service is not available. Cannot start conversation.", blocking=True, cooldown=0.5)
        return

    command_in_progress = True

    try:
        # Initial greeting (no LLM call)
        safe_speak(tts_service, "How can I help?", blocking=True, cooldown=0.5)

        # Conversation history for context
        conversation_history = []

        # Main conversation loop
        while True:
            print("Listening for user input in conversational mode...")

            # Listen for user input with 20 second timeout
            text = _listen_for_speech(recognizer, audio_queue, timeout=20)

            if not text:
                # 20 seconds of silence - end conversation
                print("No input for 20 seconds, ending conversation")
                safe_speak(tts_service, "Goodbye", blocking=True, cooldown=0.5)
                break

            print(f"User said: '{text}'")

            # Add user message to conversation history
            conversation_history.append({"role": "user", "content": text})

            # Call LLM with conversation history
            llm_response = llm_service.chat(conversation_history, timeout=60)

            if llm_response:
                print(f"LLM responded: '{llm_response}'")
                # Add assistant response to conversation history
                conversation_history.append({"role": "assistant", "content": llm_response})
                # Speak the response
                safe_speak(tts_service, llm_response, blocking=True, cooldown=0.5)
            else:
                print("LLM returned empty response or error")
                safe_speak(tts_service, "I didn't get a response. Please try again.", blocking=True, cooldown=0.5)

    finally:
        command_in_progress = False


def listen_for_command(recognizer, audio_queue, tts_service):
    """Listen for and process voice command using command mapping."""
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

        # Use command mapping
        handler, command_name = get_command_handler(text)
        if handler:
            print(f"Matched command: {command_name} (from text: '{text}')")

            # Special handling for specific commands
            if command_name == "disable_listening":
                safe_speak(tts_service, "Disabling wake word listening for 60 minutes", blocking=True, cooldown=0.5)
                handler()
                safe_speak(tts_service, "Listening disabled. Wake words will be ignored for 60 minutes.", blocking=False, cooldown=0.5)
            elif command_name == "get_inverter_status":
                safe_speak(tts_service, "Checking inverter status", blocking=True, cooldown=0.5)
                result = handler()
                if result and result.get("success"):
                    status_message = result.get("message", "Unknown status")
                    safe_speak(tts_service, status_message, blocking=False, cooldown=0.5)
                else:
                    safe_speak(tts_service, "Failed to get inverter status", blocking=False, cooldown=0.5)
            elif command_name == "get_battery_data":
                safe_speak(tts_service, "Checking battery status", blocking=True, cooldown=0.5)
                result = handler()
                if result and result.get("success"):
                    battery_message = result.get("message", "Unknown battery status")
                    safe_speak(tts_service, battery_message, blocking=False, cooldown=0.5)
                else:
                    safe_speak(tts_service, "Failed to get battery data", blocking=False, cooldown=0.5)
            else:
                safe_speak(tts_service, f"Executing command {command_name}", blocking=True, cooldown=0.5)
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

    print("Initializing TTS service...")
    tts_service = TTSService()

    # Initialize LLM service for conversational mode
    print("Initializing LLM service...")
    llm_service = LLMService()

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
            wake_word_index = porcupine.process(pcm_unpacked)

            if wake_word_index >= 0:
                # Check if wake word listening is disabled
                if wake_word_disabled:
                    print("Wake word detected but ignoring (listening disabled)")
                    continue

                # Only process wake word if no command is currently in progress and TTS is not speaking
                if not command_in_progress and not tts_speaking:
                    # wake_word_index: 0 = WAKE_WORD, 1 = "terminator", 2 = "computer"
                    if wake_word_index == 1:  # "terminator"
                        print("Terminator wake word detected - entering conversational mode!")
                        conversational_mode(recognizer, audio_queue, llm_service, tts_service)
                    else:
                        print("Wake word detected!")
                        listen_for_command(recognizer, audio_queue, tts_service)
                else:
                    if command_in_progress:
                        print("Wake word detected but ignoring (command in progress)")
                    if tts_speaking:
                        print("Wake word detected but ignoring (TTS speaking)")


if __name__ == "__main__":
    main()
