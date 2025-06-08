from gpiozero import LED
from time import sleep

relay = LED(26)


def toggleInverter():
    print("relay", relay)

    try:
        if relay.is_active:
            relay.off()
            sleep(2)
            return {"on": False, "success": True}
        else:
            relay.on()
            sleep(2)
            return {"on": True, "success": True}
    except Exception as e:
        return {"on": relay.is_active, "success": False, "error": str(e)}


def toggleInverterMock():
    mock = {"on": True, "success": True}
    return mock
