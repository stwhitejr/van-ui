"""Command execution interface for voice commands."""

import requests
from .config import API_HOST


def _make_request(method, endpoint, json_data=None):
    """Make HTTP request to API."""
    url = f"{API_HOST}{endpoint}"
    if method == "GET":
        return requests.get(url, verify=False)
    elif method == "POST":
        return requests.post(url, verify=False, json=json_data)
    else:
        raise ValueError(f"Unsupported method: {method}")


def led_status():
    """Get current LED status."""
    return _make_request("GET", "/leds")


def led_configure(payload):
    """Configure LEDs with given payload."""
    return _make_request("POST", "/leds/configure", payload)


def toggle_inverter():
    """Toggle the inverter on/off."""
    response = _make_request("POST", "/inverter/toggle")
    return {
        "success": response.status_code == 200,
        "message": "Inverter toggled",
        "data": response.json() if response.status_code == 200 else None,
    }


def toggle_fan():
    """Toggle the fan on/off."""
    response = _make_request("POST", "/fan/toggle")
    return {
        "success": response.status_code == 200,
        "message": "Fan toggled",
        "data": response.json() if response.status_code == 200 else None,
    }


def toggle_lights():
    """Toggle the main lights on/off."""
    response = _make_request("POST", "/lights/toggle")
    return {
        "success": response.status_code == 200,
        "message": "Lights toggled",
        "data": response.json() if response.status_code == 200 else None,
    }


def turn_off_leds():
    """Turn off LED strip."""
    response = led_configure({"on": False})
    return {
        "success": response.status_code == 200,
        "message": "LEDs turned off",
        "data": response.json() if response.status_code == 200 else None,
    }


def turn_on_leds():
    """Turn on LED strip with default color."""
    response = led_configure({"on": True, "color": "252, 255, 92", "preset": None})
    return {
        "success": response.status_code == 200,
        "message": "LEDs turned on",
        "data": response.json() if response.status_code == 200 else None,
    }


def rainbow_leds():
    """Set LED strip to rainbow preset."""
    response = led_configure({"on": True, "color": "252, 255, 92", "preset": "rainbow"})
    return {
        "success": response.status_code == 200,
        "message": "LEDs set to rainbow",
        "data": response.json() if response.status_code == 200 else None,
    }


def blue_leds():
    """Set LED strip to blue color."""
    response = led_configure({"on": True, "color": "7, 28, 255", "preset": None})
    return {
        "success": response.status_code == 200,
        "message": "LEDs set to blue",
        "data": response.json() if response.status_code == 200 else None,
    }


# Command registry for LLM
AVAILABLE_COMMANDS = {
    "toggle_inverter": {
        "function": toggle_inverter,
        "description": "Toggle the inverter on or off to convert DC to AC power so we can power up our 120v appliances such as the hot plate for cooking",
    },
    "toggle_fan": {
        "function": toggle_fan,
        "description": "Toggle the roof fan on or off to circulate air inside the van",
    },
    "toggle_lights": {
        "function": toggle_lights,
        "description": "Toggle the main lights on or off",
    },
    "turn_on_leds": {
        "function": turn_on_leds,
        "description": "Turn on LED strip with default color",
    },
    "turn_off_leds": {
        "function": turn_off_leds,
        "description": "Turn off LED strip",
    },
    "rainbow_leds": {
        "function": rainbow_leds,
        "description": "Set LED strip to rainbow preset",
    },
    "blue_leds": {
        "function": blue_leds,
        "description": "Set LED strip to blue color",
    },
}


def execute_command(command_name, params=None):
    """
    Execute a command by name.

    Args:
        command_name: Name of the command to execute
        params: Optional parameters (not currently used, but reserved for future)

    Returns:
        dict with success, message, and data fields
    """
    if command_name not in AVAILABLE_COMMANDS:
        return {
            "success": False,
            "message": f"Unknown command: {command_name}",
            "data": None,
        }

    try:
        command_func = AVAILABLE_COMMANDS[command_name]["function"]
        result = command_func()
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing {command_name}: {str(e)}",
            "data": None,
        }
