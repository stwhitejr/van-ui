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

    ser = serial.Serial(port, baudrate=19200, timeout=1)
    data = {}
    max_retries = 100  # Maximum number of lines to read before giving up
    retry_count = 0

    try:
        while retry_count < max_retries:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line or "\t" not in line:
                    retry_count += 1
                    continue
                key, value = line.split("\t", 1)

                converter = converter_map.get(key)
                if converter:
                    value = converter(value)

                data[readable.get(key) or key] = value

                # End of a frame is usually marked by 'Checksum'
                if key == "Checksum":
                    break
                retry_count += 1
            except serial.SerialException as e:
                print(f"Serial error reading line: {e}")
                break  # Break on serial errors (device disconnected, etc.)
            except Exception as e:
                print(f"Error reading line: {e}")
                retry_count += 1
                continue

        if retry_count >= max_retries:
            print(f"Warning: Reached maximum retries ({max_retries}) without receiving Checksum")
    finally:
        ser.close()  # Always close the serial port

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
