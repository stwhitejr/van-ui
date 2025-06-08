def toggleInverter():
    from gpiozero import LED
    from time import sleep

    relay = LED(26)
    relay.on()
    print("Relay ON (should click)")
    sleep(10)
    relay.off()
    print("Relay OFF (should click again)")

    # try:
    #     if relay.is_active:
    #         relay.off()
    #         return {"on": False, "success": True}
    #     else:
    #         relay.on()
    #         return {"on": True, "success": True}
    # except Exception as e:
    #     return {"on": relay.is_active, "success": False, "error": str(e)}


def toggleInverterMock():
    mock = {"on": True, "success": True}
    return mock
