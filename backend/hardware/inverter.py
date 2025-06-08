def toggleInverter():
    from gpiozero import LED

    relay = LED(26)

    try:
        if relay.value == 1:
            relay.off()
            return {"on": False, "success": True}
        else:
            relay.on()
            return {"on": True, "success": True}
    except Exception as e:
        return {"on": bool(relay.value), "success": False, "error": str(e)}


def toggleInverterMock():
    mock = {"on": True, "success": True}
    return mock
