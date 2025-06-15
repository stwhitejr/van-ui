import pigpio
import time
import math


class LEDController:
    def __init__(self, num_leds=288, pin=18, brightness=1.0):
        self.num_leds = num_leds
        self.gpio_pin = pin
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Cannot connect to pigpio daemon")

        # Store colors as (r, g, b)
        self.leds = [(0, 0, 0)] * num_leds
        self.is_on = False
        self.color = (255, 255, 255)
        self.brightness = max(0.0, min(1.0, brightness))

    def _apply_brightness(self, color):
        return tuple(int(c * self.brightness) for c in color)

    def set_pixel(self, index, color):
        if 0 <= index < self.num_leds:
            leds_list = list(self.leds)
            leds_list[index] = color
            self.leds = tuple(leds_list)

    def show(self):
        # Prepare data in GRB order (WS2812 standard)
        data = []
        for r, g, b in self.leds:
            r, g, b = self._apply_brightness((r, g, b))
            data.extend([g, r, b])

        self.pi.wave_add_new()
        wf = []
        for byte in data:
            for i in range(8):
                if byte & (1 << (7 - i)):
                    # 1 bit
                    wf.append(pigpio.pulse(1 << self.gpio_pin, 0, 0.8))
                    wf.append(pigpio.pulse(0, 1 << self.gpio_pin, 0.45))
                else:
                    # 0 bit
                    wf.append(pigpio.pulse(1 << self.gpio_pin, 0, 0.4))
                    wf.append(pigpio.pulse(0, 1 << self.gpio_pin, 0.85))
        self.pi.wave_add_generic(wf)
        wid = self.pi.wave_create()
        self.pi.wave_send_once(wid)
        while self.pi.wave_tx_busy():
            time.sleep(0.001)
        self.pi.wave_delete(wid)

    def fill(self, color):
        self.leds = [color] * self.num_leds
        self.show()

    def turn_on(self):
        self.is_on = True
        self.fill(self.color)

    def turn_off(self):
        self.is_on = False
        self.clear()

    def clear(self):
        self.fill((0, 0, 0))

    def set_brightness(self, brightness_percent):
        self.brightness = max(0.0, min(1.0, brightness_percent / 100))
        if self.is_on:
            self.fill(self.color)

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        if self.is_on:
            self.fill(self.color)

    def status(self):
        return {
            "power": "on" if self.is_on else "off",
            "brightness": round(self.brightness * 100),
            "color": self.color,
        }

    def run_preset(self, name):
        if name == "rainbow":
            self._rainbow_cycle(0.001)
        elif name == "chase":
            self._color_chase((0, 255, 0), 0.05)
        elif name == "pulse":
            self._pulse((0, 0, 255))
        else:
            raise ValueError(f"Unknown preset: {name}")

    def _rainbow_cycle(self, wait):
        def wheel(pos):
            if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return (0, pos * 3, 255 - pos * 3)

        for j in range(256):
            for i in range(self.num_leds):
                self.leds = list(self.leds)
                self.leds[i] = wheel((i * 256 // self.num_leds + j) & 255)
            self.leds = tuple(self.leds)
            self.show()
            time.sleep(wait)

    def _color_chase(self, color, wait):
        for i in range(self.num_leds):
            leds_list = list(self.leds)
            leds_list[i] = color
            self.leds = tuple(leds_list)
            self.show()
            time.sleep(wait)
        self.clear()

    def _pulse(self, color, steps=50, delay=0.02):
        for i in range(steps):
            factor = math.sin(math.pi * i / steps)
            scaled_color = tuple(int(c * factor) for c in color)
            self.fill(scaled_color)
            time.sleep(delay)

    def cleanup(self):
        self.clear()
        self.pi.stop()
