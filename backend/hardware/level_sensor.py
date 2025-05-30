def checkLevel():
    from mpu6050 import mpu6050

    sensor = mpu6050(0x68)
    accel = sensor.get_accel_data()
    # gyro = sensor.get_gyro_data()
    return accel


def checkLevelMock():
    mock = {"x": 22, "y": 3}
    return mock
