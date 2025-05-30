readable = {
    "V": "voltage",
    "I": "current",
    "P": "power",
    "SOC": "state_of_charge_percent",
    "CE": "consumed_ah",
    "TTG": "time_to_go_min",
}


def smartshunt(port="/dev/ttyUSB0"):
    import serial

    ser = serial.Serial(port, 19200, timeout=1)
    frame = {}

    try:
        while True:
            line = ser.readline().decode("ascii", errors="ignore").strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) == 2:
                key, value = parts
                frame[readable[key] or key] = value
            elif line == "Checksum":
                break
    except Exception as e:
        print("Error reading VE.Direct:", e)
    finally:
        ser.close()

    return frame


def smartshuntMock():
    mock = {
        "voltage": "12920",
        "current": "-590",
        "power": "763",
        "consumed_ah": "-1156",
        "state_of_charge_percent": "92",
        "time_to_go_min": "45",
    }
    return mock
