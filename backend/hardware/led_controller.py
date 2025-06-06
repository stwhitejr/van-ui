import board
import neopixel


class LEDController:
    def __init__(self, num_leds=288, pin=board.D18, brightness=1.0):
        self.num_leds = num_leds
        self.pixels = neopixel.NeoPixel(
            pin, num_leds, brightness=brightness, auto_write=False
        )
        self.is_on = False
        self.color = (255, 255, 255)
        self.brightness = brightness

    def turn_on(self):
        self.is_on = True
        self.pixels.fill(self.color)
        self.pixels.show()

    def turn_off(self):
        self.is_on = False
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def set_brightness(self, brightness_percent):
        self.brightness = max(0.0, min(1.0, brightness_percent / 100))
        self.pixels.brightness = self.brightness
        if self.is_on:
            self.pixels.fill(self.color)
            self.pixels.show()

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        if self.is_on:
            self.pixels.fill(self.color)
            self.pixels.show()

    def status(self):
        return {
            "power": "on" if self.is_on else "off",
            "brightness": round(self.brightness * 100),
            "color": self.color,
        }
