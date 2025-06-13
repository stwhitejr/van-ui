from flask import Flask, jsonify, request, send_from_directory
from hardware import (
    LevelSensor,
    InverterToggle,
    Smartshunt,
    LEDController,
    VoiceRecognition,
)
import time

from dotenv import load_dotenv
from threading import Thread

load_dotenv()

leds = LEDController()

app = Flask(__name__, static_folder="../dist")

INVERTER_ON_COLOR = "248, 232, 58"


# API
@app.route("/inverter/toggle", methods=["POST"])
def toggleInverter():
    data = InverterToggle()
    print(data)
    if data.on:
        leds.turn_on()
        leds.set_color(INVERTER_ON_COLOR)
    else:
        leds.turn_off()

    return jsonify(data)


@app.route("/smartshunt/data", methods=["GET"])
def smartshunData():
    return ""
    data = Smartshunt()
    return jsonify(data)


@app.route("/level_sensor/data", methods=["GET"])
def levelsensorData():
    data = LevelSensor()
    return jsonify(data)


@app.route("/leds/configure", methods=["POST"])
def configureLeds():
    """
    Expected request payload:
    {
      "on": true,
      "brightness": 70,
      "color": "#ffcc00",
      "sleep": 5,
      "preset": "rainbow"
    }
    """
    data = request.json

    print("leds class instance log:", leds)
    print("leds request log:", data)

    if data is None:
        return jsonify({"error": "Invalid request"}), 400

    on = data.get("on")
    brightness = data.get("brightness")
    color = data.get("color")
    sleep_duration = data.get("sleep", 0)

    if brightness is not None:
        leds.set_brightness(brightness)

    if color:
        try:
            leds.set_color(color)
        except ValueError:
            return jsonify({"error": "Invalid color format"}), 400

    if data.preset:
        try:
            leds.run_preset(data.preset)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if on is True:
        leds.turn_on()
    elif on is False:
        leds.turn_off()

    if sleep_duration:
        time.sleep(sleep_duration)
        leds.turn_off()

    return jsonify(leds.status())


# Frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    if VoiceRecognition:
        Thread(target=VoiceRecognition, daemon=True).start()

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=("cert.pem", "key.pem"))
