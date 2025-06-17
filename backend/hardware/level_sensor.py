def getRating(degree):
    abs_degree = abs(degree)
    if abs_degree < 2:
        return "Good"
    elif abs_degree < 5:
        return "Okay"
    else:
        return "Bad"


def checkLevel():
    from mpu6050 import mpu6050
    import math

    # These should be readings you get when the van is actually level. This depends on how you mount the sensor.
    CALIBRATION_PITCH_OFFSET = -130
    CALIBRATION_ROLL_OFFSET = 0

    sensor = mpu6050(0x68)
    accel_data = sensor.get_accel_data()

    ax = accel_data["x"]
    ay = accel_data["y"]
    az = accel_data["z"]

    pitch = (
        math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))
        - CALIBRATION_PITCH_OFFSET
    )
    roll = (
        math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2))) - CALIBRATION_ROLL_OFFSET
    )

    # Assume 0° = 100% level, and ±10° = 0% level
    max_angle = 10

    # Compute total deviation
    deviation = math.sqrt(pitch**2 + roll**2)
    level_percent = max(0, 100 - (deviation / max_angle) * 100)
    level_percent = round(level_percent, 2)

    return {
        "pitch": abs(round(pitch, 2)),
        "roll": abs(round(roll, 2)),
        "level_percent": level_percent,
        "pitch_rating": getRating(pitch),
        "roll_rating": getRating(roll),
    }


def checkLevelMock():
    mock = {
        "pitch": 1,
        "roll": 3,
        "level_percent": "100%",
        "pitch_rating": "Good",
        "roll_rating": "Okay",
    }
    return mock
