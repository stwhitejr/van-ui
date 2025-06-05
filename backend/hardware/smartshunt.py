from util import (
    convert_to_float,
    convert_to_percentage,
    convert_minutes_to_duration,
)

readable = {
    "V": "voltage",
    "I": "current",
    "P": "power",
    "SOC": "state_of_charge_percent",
    "CE": "consumed_ah",
    "TTG": "time_to_go_min",
}

converter_map = {
    "V": convert_to_float,
    "I": convert_to_float,
    "CE": convert_to_float,
    "SOC": convert_to_percentage,
    "TTG": convert_minutes_to_duration,
}


def smartshunt(port="/dev/ttyUSB0"):
    import serial

    port = serial.Serial(port, baudrate=19200, timeout=1)
    data = {}

    while True:
        try:
            line = port.readline().decode("utf-8", errors="ignore").strip()
            if not line or "\t" not in line:
                continue
            key, value = line.split("\t", 1)

            converter = converter_map.get(key)
            if converter:
                value = converter(value)

            data[readable[key] or key] = value

            # End of a frame is usually marked by 'Checksum'
            if key == "Checksum":
                break
        except Exception as e:
            print(f"Error reading line: {e}")
            continue

    return data


def smartshuntMock():
    mock = {
        "voltage": convert_to_float(12920),
        "current": convert_to_float(-590),
        "power": convert_to_float(763),
        "consumed_ah": convert_to_float(-1156),
        "state_of_charge_percent": convert_to_percentage(92),
        "time_to_go_min": convert_minutes_to_duration(4540),
    }
    return mock
