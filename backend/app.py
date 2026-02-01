from flask import Flask, jsonify, send_from_directory, request, send_file, session
from hardware import (
    LevelSensor,
    InverterToggle,
    getInverterRelayStatus,
    Smartshunt,
    FanToggle,
)
from dotenv import load_dotenv
import subprocess
import os
import shutil
from datetime import datetime
from files import (
    UPLOAD_DIR,
    MAX_FILE_SIZE,
    get_full_path,
    sanitize_path,
    is_safe_filename,
    ensure_upload_dir,
    is_folder_locked,
    lock_folder,
    unlock_folder,
)


load_dotenv()

app = Flask(__name__, static_folder="../dist")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")


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


# File Management API
@app.route("/files/upload", methods=["POST"])
def uploadFile():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not is_safe_filename(file.filename):
            return jsonify({"error": "Invalid filename"}), 400

        # Get folder path from form data
        folder_path = request.form.get("folder", "")
        sanitized_folder = sanitize_path(folder_path)
        if sanitized_folder is None:
            return jsonify({"error": "Invalid folder path"}), 400

        # Get full path for the folder
        folder_full_path = get_full_path(sanitized_folder)
        if folder_full_path is None:
            return jsonify({"error": "Invalid folder path"}), 400

        # Ensure folder exists
        os.makedirs(folder_full_path, exist_ok=True)

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return (
                jsonify(
                    {
                        "error": f"File size exceeds {MAX_FILE_SIZE / (1024*1024)}MB limit"
                    }
                ),
                400,
            )

        # Save file
        file_path = os.path.join(folder_full_path, file.filename)
        file.save(file_path)

        return jsonify(
            {"success": True, "filename": file.filename, "path": sanitized_folder}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/list", methods=["GET"])
def listFiles():
    try:
        path = request.args.get("path", "")
        sanitized_path = sanitize_path(path)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        # Check if current folder is locked and user is not authenticated
        if sanitized_path and is_folder_locked(sanitized_path):
            authenticated_folders = set(session.get("authenticated_folders", []))
            if sanitized_path not in authenticated_folders:
                return jsonify({"error": "Folder is locked", "locked": True}), 403

        full_path = get_full_path(sanitized_path)
        if full_path is None:
            return jsonify({"error": "Invalid path"}), 400

        if not os.path.exists(full_path):
            return jsonify([])

        items = []
        for item in os.listdir(full_path):
            # Filter out the locked folders configuration file
            if item == ".locked_folders.json":
                continue

            item_path = os.path.join(full_path, item)
            relative_path = (
                os.path.join(sanitized_path, item) if sanitized_path else item
            )

            if os.path.isdir(item_path):
                folder_locked = is_folder_locked(relative_path)
                items.append(
                    {
                        "name": item,
                        "type": "folder",
                        "path": relative_path,
                        "locked": folder_locked,
                    }
                )
            else:
                stat = os.stat(item_path)
                items.append(
                    {
                        "name": item,
                        "type": "file",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "path": relative_path,
                    }
                )

        # Sort: folders first, then files, both alphabetically
        items.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))

        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/view/<path:filepath>", methods=["GET"])
def viewFile(filepath):
    try:
        sanitized_path = sanitize_path(filepath)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        full_path = get_full_path(sanitized_path)
        if full_path is None:
            return jsonify({"error": "Invalid path"}), 400

        if not os.path.exists(full_path):
            return jsonify({"error": "File not found"}), 404

        if os.path.isdir(full_path):
            return jsonify({"error": "Path is a directory"}), 400

        return send_file(full_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/folder", methods=["POST"])
def createFolder():
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Folder name required"}), 400

        folder_name = data["name"]
        if not is_safe_filename(folder_name):
            return jsonify({"error": "Invalid folder name"}), 400

        current_path = data.get("path", "")
        sanitized_path = sanitize_path(current_path)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        # Create full path for new folder
        if sanitized_path:
            new_folder_path = sanitized_path + "/" + folder_name
        else:
            new_folder_path = folder_name

        sanitized_new_path = sanitize_path(new_folder_path)
        if sanitized_new_path is None:
            return jsonify({"error": "Invalid folder path"}), 400

        full_path = get_full_path(sanitized_new_path)
        if full_path is None:
            return jsonify({"error": "Invalid folder path"}), 400

        # Create folder
        os.makedirs(full_path, exist_ok=True)

        return jsonify({"success": True, "path": sanitized_new_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/delete", methods=["DELETE"])
def deleteFile():
    try:
        data = request.get_json()
        if not data or "path" not in data:
            return jsonify({"error": "Path required"}), 400

        path = data["path"]
        sanitized_path = sanitize_path(path)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        # Check if folder is locked
        if is_folder_locked(sanitized_path):
            authenticated_folders = set(session.get("authenticated_folders", []))
            if sanitized_path not in authenticated_folders:
                return jsonify({"error": "Folder is locked"}), 403

        full_path = get_full_path(sanitized_path)
        if full_path is None:
            return jsonify({"error": "Invalid path"}), 400

        if not os.path.exists(full_path):
            return jsonify({"error": "Path not found"}), 404

        # Delete file or folder
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            # Also unlock if it was locked
            unlock_folder(sanitized_path)
        else:
            os.remove(full_path)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/authenticate", methods=["POST"])
def authenticateFolder():
    try:
        data = request.get_json()
        if not data or "password" not in data or "path" not in data:
            return jsonify({"error": "Password and path required"}), 400

        password = data["password"]
        path = data["path"]
        sanitized_path = sanitize_path(path)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        # Check if folder is locked
        if not is_folder_locked(sanitized_path):
            return jsonify({"error": "Folder is not locked"}), 400

        # Validate password
        correct_password = os.getenv("FOLDER_PASSWORD")
        if not correct_password:
            return jsonify({"error": "Password not configured"}), 500

        if password != correct_password:
            return jsonify({"error": "Incorrect password"}), 401

        # Add to authenticated folders in session
        authenticated_folders = set(session.get("authenticated_folders", []))
        authenticated_folders.add(sanitized_path)
        session["authenticated_folders"] = list(authenticated_folders)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/lock", methods=["POST"])
def lockFolder():
    try:
        data = request.get_json()
        if not data or "path" not in data:
            return jsonify({"error": "Path required"}), 400

        path = data["path"]
        sanitized_path = sanitize_path(path)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        # Verify it's a folder
        full_path = get_full_path(sanitized_path)
        if full_path is None or not os.path.isdir(full_path):
            return jsonify({"error": "Path is not a folder"}), 400

        lock_folder(sanitized_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/unlock", methods=["POST"])
def unlockFolder():
    try:
        data = request.get_json()
        if not data or "path" not in data:
            return jsonify({"error": "Path required"}), 400

        path = data["path"]
        sanitized_path = sanitize_path(path)
        if sanitized_path is None:
            return jsonify({"error": "Invalid path"}), 400

        # Check authentication
        authenticated_folders = set(session.get("authenticated_folders", []))
        if sanitized_path not in authenticated_folders:
            return jsonify({"error": "Not authenticated"}), 403

        unlock_folder(sanitized_path)
        # Remove from authenticated folders
        authenticated_folders.discard(sanitized_path)
        session["authenticated_folders"] = list(authenticated_folders)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
