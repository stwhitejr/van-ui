from flask import Flask, jsonify, request, send_from_directory
from hardware import LevelSensor, InverterToggle, Smartshunt

app = Flask(__name__, static_folder="../dist")


# API
@app.route("/inverter/toggle", methods=["POST"])
def toggleInverter():
    data = InverterToggle()
    return jsonify(data)


@app.route("/smartshunt/data", methods=["GET"])
def smartshunData():
    data = Smartshunt()
    print("pre-API return", data)
    return jsonify(data)


@app.route("/level_sensor/data", methods=["GET"])
def levelsensorData():
    data = LevelSensor()
    return jsonify(data)


# @app.route("/api/data", methods=["POST"])
# def get_data():
#     data = request.json
#     return jsonify({"you_sent": data})


# Frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True)
