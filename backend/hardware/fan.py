from gpiozero import LED
from time import sleep

relay = LED(6)


def toggleFan():
    relay.on()
    sleep(0.05)
    relay.off()
