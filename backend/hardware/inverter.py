def toggleInverter():
    from gpiozero import LED

    print("here")

    relay = LED(26)
    print(relay)

    try:
        if relay.is_active:
            relay.off()
            return {"on": False, "success": True}
        else:
            relay.on()
            return {"on": True, "success": True}
    except Exception as e:
        return {"on": relay.is_active, "success": False, "error": str(e)}


def toggleInverterMock():
    print("mock")
    mock = {"on": True, "success": True}
    return mock
