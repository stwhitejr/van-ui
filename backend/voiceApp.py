import pvporcupine
import sounddevice as sd
import queue
import struct
import vosk
import json
import requests
import os
from dotenv import load_dotenv
from time import sleep
from difflib import get_close_matches
import pygame
from threading import Thread
import random

load_dotenv()

# === Config ===
VOSK_MODEL_PATH = "/home/steve/models/vosk/vosk-model-small-en-us-0.15"
WAKE_WORD = "jarvis"
RATE = 16000
CHANNELS = 1

API_HOST = "http://localhost:5000"

AUDIO_PATH = "/home/steve/Desktop/van-ui/audio"
AUDIO_CONFIRM_PATH = AUDIO_PATH + "/confirm"
AUDIO_GREET_PATH = AUDIO_PATH + "/greet"


def play_audio(file_path, shouldThread):
    def _play():
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            sleep(0.1)

    if shouldThread:
        Thread(target=_play, daemon=True).start()
    else:
        _play()


def play_random_from_folder(folder_path, shouldThread):
    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".mp3", ".wav"))]
    if not files:
        print(f"No audio files found in {folder_path}")
        return
    selected = random.choice(files)
    play_audio(os.path.join(folder_path, selected), shouldThread)


def greet():
    play_random_from_folder(AUDIO_GREET_PATH, False)


def confirm():
    play_random_from_folder(AUDIO_CONFIRM_PATH, True)


def led_status():
    return requests.get(f"{API_HOST}/leds", verify=False)


def led_configure(payload):
    return requests.post(
        f"{API_HOST}/leds/configure",
        verify=False,
        json=payload,
    )


def toggle_inverter():
    confirm()
    return requests.post(f"{API_HOST}/inverter/toggle", verify=False)


def turn_off_leds():
    confirm()
    return requests.post(f"{API_HOST}/leds/configure", verify=False, json={"on": False})


def turn_on_leds():
    confirm()
    return requests.post(
        f"{API_HOST}/leds/configure",
        verify=False,
        json={"on": True, "color": "252, 255, 92", "preset": None},
    )


def rainbow_leds():
    confirm()
    return requests.post(
        f"{API_HOST}/leds/configure",
        verify=False,
        json={"on": True, "color": "252, 255, 92", "preset": "rainbow"},
    )


def blue_leds():
    confirm()
    return requests.post(
        f"{API_HOST}/leds/configure",
        verify=False,
        json={"on": True, "color": "7, 28, 255", "preset": None},
    )


def toggle_lights():
    confirm()
    return requests.post(f"{API_HOST}/lights/toggle", verify=False)


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
        # Move these to toggle_lights if i ever add another relay for the main lights in the van
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
    "turn_off_leds": ["turn off leds", "leds off", "strip off", "reset"],
    "turn_on_leds": ["turn on leds", "leds on", "strip on"],
    "rainbow_leds": ["i'm happy", "happy", "let's dance", "dance"],
    "blue_leds": ["i'm sad", "sad", "i'm blue", "i'm feeling blue"],
    "toggle_lights": [],
}

COMMAND_FUNCTIONS = {
    "toggle_inverter": toggle_inverter,
    "turn_off_leds": turn_off_leds,
    "turn_on_leds": turn_on_leds,
    "blue_leds": blue_leds,
    "rainbow_leds": rainbow_leds,
    "toggle_lights": toggle_lights,
}

COMMAND_MAP = {}
for command_key, phrases in COMMAND_ALIASES.items():
    func = COMMAND_FUNCTIONS[command_key]
    for phrase in phrases:
        COMMAND_MAP[phrase.lower()] = func


def get_command_handler(spoken_text):
    spoken_text = spoken_text.lower()
    if spoken_text in COMMAND_MAP:
        return COMMAND_MAP[spoken_text]
    close = get_close_matches(spoken_text, COMMAND_MAP.keys(), n=1, cutoff=0.8)
    if close:
        return COMMAND_MAP[close[0]]
    return None


# === Audio Queue ===
q = queue.Queue()


def flush_audio_queue():
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break


def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))


# === Main Loop ===
def main():
    print("Loading Porcupine...")
    porcupine = pvporcupine.create(
        access_key=os.getenv("PICOVOICE_ACCESS_KEY"),
        keywords=[WAKE_WORD],
    )
    print("Loading Vosk...")
    model = vosk.Model(VOSK_MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, RATE)

    print("Ready and listening...")

    with sd.RawInputStream(
        samplerate=RATE,
        blocksize=512,
        dtype="int16",
        channels=CHANNELS,
        callback=audio_callback,
    ):

        while True:
            pcm = q.get()
            pcm_unpacked = struct.unpack_from("h" * (len(pcm) // 2), pcm)
            if porcupine.process(pcm_unpacked) >= 0:
                print("Wake word detected!")
                listen_for_command(recognizer)


def listen_for_command(recognizer):
    originalLedState = led_status().json()
    led_configure({"on": True, "color": "255, 255, 255", "preset": "pulse"})
    print("Listening for command...")
    collected_audio = b""

    greet()
    flush_audio_queue()
    text = ""

    # Listen for a few seconds
    for _ in range(int((RATE / 1024) * 4)):
        try:
            data = q.get(timeout=1)
        except queue.Empty:
            break
        collected_audio += data
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            print(f"Partial result: {text}")
            if text:  # Only break if it's not empty
                break

    if not text:
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "").strip().lower()
    print(f"Heard: '{text}'", flush=True)

    handler = get_command_handler(text)
    if handler:
        led_configure({"on": True, "color": "14, 218, 62", "preset": None})
        print(f"Executing command: {text}")
        sleep(0.5)
        handler()
        return

    print("No matching command found.")
    led_configure({"on": True, "color": "216, 8, 8", "preset": None})
    sleep(0.5)
    led_configure(originalLedState)


if __name__ == "__main__":
    main()
