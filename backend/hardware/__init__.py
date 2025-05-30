import platform
import os


def is_pi():
    return (
        os.uname().nodename.startswith("raspberrypi")
        or "arm" in platform.machine()
        and os.path.exists("/proc/device-tree/model")
    )


ON_PI = is_pi()


if ON_PI:
    from .level_sensor import checkLevel as LevelSensor
    from .inverter import toggleInverter as InverterToggle
    from .smartshunt import smartshunt as Smartshunt
else:
    from .level_sensor import checkLevelMock as LevelSensor
    from .inverter import toggleInverterMock as InverterToggle
    from .smartshunt import smartshuntMock as Smartshunt
