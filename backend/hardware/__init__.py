import platform
import os
import argparse

# Set GPIO pin factory BEFORE importing any GPIO modules
# This prevents auto-detection issues and GPIO busy errors
# Wrap in try/except to ensure module can still load even if pin factory setup fails
try:
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    from gpiozero import Device
    Device.pin_factory = RPiGPIOFactory()
    print("Using RPi.GPIO pin factory")
except Exception as e2:
    print(f"Could not use RPi.GPIO pin factory: {e2}")
    print("Will use default pin factory (may cause issues)")

parser = argparse.ArgumentParser(description="Use API stubs.")
parser.add_argument("-m", "--mock", help="API Stub")
args = parser.parse_args()


def is_pi():
    return (
        os.uname().nodename.startswith("raspberrypi")
        or "arm" in platform.machine()
        and os.path.exists("/proc/device-tree/model")
    )


ON_PI = not args.mock and is_pi()


if ON_PI:
    from .level_sensor import checkLevel as LevelSensor
    from .inverter import toggleInverter as InverterToggle, getInverterRelayStatus
    from .fan import toggleFan as FanToggle
    from .smartshunt import smartshunt as Smartshunt
else:
    from .level_sensor import checkLevelMock as LevelSensor
    from .inverter import toggleInverterMock as InverterToggle, getInverterRelayStatus
    # FanToggle mock - create simple no-op function if no mock exists
    try:
        from .fan import toggleFanMock as FanToggle
    except ImportError:
        def FanToggle():
            pass
    from .smartshunt import smartshuntMock as Smartshunt
