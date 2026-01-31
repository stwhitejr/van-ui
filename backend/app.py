from flask import Flask, jsonify, send_from_directory
from hardware import (
    LevelSensor,
    InverterToggle,
    getInverterRelayStatus,
    Smartshunt,
    FanToggle,
)
from dotenv import load_dotenv
import subprocess


load_dotenv()

app = Flask(__name__, static_folder="../dist")


# API
@app.route("/inverter/toggle", methods=["POST"])
def toggleInverter():
    data = InverterToggle()
    return jsonify(data)


@app.route("/fan/toggle", methods=["POST"])
def toggleFan():
    FanToggle()
    return jsonify(True)


@app.route("/app/kill", methods=["POST"])
def killFrontend():
    try:
        subprocess.run(["pkill", "chromium"], check=True)
    except subprocess.CalledProcessError:
        print("Chromium was not running.")

    return jsonify(True)


@app.route("/inverter", methods=["GET"])
def inverterRelayStatus():
    return jsonify({"on": getInverterRelayStatus()})


@app.route("/smartshunt/data", methods=["GET"])
def smartshunData():
    data = Smartshunt()
    json = jsonify(data)
    return json


@app.route("/level_sensor/data", methods=["GET"])
def levelsensorData():
    data = LevelSensor()
    return jsonify(data)


# Frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
