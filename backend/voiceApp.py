import pvporcupine
import sounddevice as sd
import queue
import struct
import vosk
import json
import requests
import os

# === Config ===
VOSK_MODEL_PATH = "/home/steve/models/vosk/vosk-model-small-en-us-0.15"
WAKE_WORD = "jarvis"
RATE = 16000
CHANNELS = 1

togglerInverter = lambda: requests.post(
    "https://172.20.10.6:5000/inverter/toggle", verify=False
)

# === Command Map ===
COMMAND_MAP = {
    "toggle inverter": togglerInverter,
    "toggle her": togglerInverter,
    "toggling her": togglerInverter,
    "try and murder": togglerInverter,
    "time to cook": togglerInverter,
    "time to cut": togglerInverter,
    "let's cook": togglerInverter,
    "let's go": togglerInverter,
    "what's cook": togglerInverter,
    "what cook": togglerInverter,
    "done cooking": togglerInverter,
}

# === Audio Queue ===
q = queue.Queue()


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
    print("Listening for command...")
    collected_audio = b""

    # Listen for a few seconds
    for _ in range(50):
        try:
            data = q.get(timeout=1)
        except queue.Empty:
            break
        collected_audio += data
        if recognizer.AcceptWaveform(data):
            break

    result = recognizer.FinalResult()
    text = json.loads(result).get("text", "").lower()
    print(f"Heard: '{text}'")

    for phrase, action in COMMAND_MAP.items():
        if phrase in text:
            print(f"Executing command: {phrase}")
            action()
            return

    print("No matching command found.")


if __name__ == "__main__":
    main()
