from gpiozero import LED
from time import sleep

relay = LED(22)


def toggleLights():
    try:
        if relay.is_active:
            relay.off()
            sleep(0.05)
            return {"on": False, "success": True}
        else:
            relay.on()
            sleep(0.05)
            return {"on": True, "success": True}
    except Exception as e:
        return {"on": relay.is_active, "success": False, "error": str(e)}


def getLightsRelayStatus():
    return relay.is_active
