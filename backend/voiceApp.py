try:
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

    load_dotenv()

    # === Config ===
    VOSK_MODEL_PATH = "/home/steve/models/vosk/vosk-model-small-en-us-0.15"
    WAKE_WORD = "jarvis"
    RATE = 16000
    CHANNELS = 1

    API_HOST = "http://172.20.10.6:5000"

    def led_status():
        return requests.get(f"{API_HOST}/leds", verify=False)

    def led_configure(payload):
        return requests.post(
            f"{API_HOST}/leds/configure",
            verify=False,
            json=payload,
        )

    def toggle_inverter():
        return requests.post(f"{API_HOST}/inverter/toggle", verify=False)

    def turn_off_leds():
        return requests.post(
            f"{API_HOST}/leds/configure", verify=False, json={"on": False}
        )

    def turn_on_leds():
        return requests.post(
            f"{API_HOST}/leds/configure",
            verify=False,
            json={"on": True, "color": "252, 255, 92", "preset": None},
        )

    def rainbow_leds():
        return requests.post(
            f"{API_HOST}/leds/configure",
            verify=False,
            json={"on": True, "color": "252, 255, 92", "preset": "rainbow"},
        )

    def blue_leds():
        return requests.post(
            f"{API_HOST}/leds/configure",
            verify=False,
            json={"on": True, "color": "7, 28, 255", "preset": None},
        )

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
        ],
        "turn_off_leds": ["turn off lights", "good night"],
        "turn_on_leds": ["turn on lights", "good morning"],
        "rainbow_leds": ["i'm happy", "happy", "let's dance", "dance"],
        "blue_leds": ["i'm sad", "sad", "i'm blue", "i'm feeling blue"],
    }

    COMMAND_FUNCTIONS = {
        "toggle_inverter": toggle_inverter,
        "turn_off_leds": turn_off_leds,
        "turn_on_leds": turn_on_leds,
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

        handler = get_command_handler(text)
        if handler:
            led_configure({"on": True, "color": "14, 218, 62", "preset": None})
            print(f"Executing command: {text}")
            sleep(2)
            handler()
            return

        print("No matching command found.")
        led_configure({"on": True, "color": "216, 8, 8", "preset": None})
        sleep(2)
        led_configure(originalLedState)

    if __name__ == "__main__":
        main()
except Exception as e:
    with open("/tmp/voiceapp_debug.log", "a") as f:
        f.write(f"Exception during imports: {e}\n")
    raise
