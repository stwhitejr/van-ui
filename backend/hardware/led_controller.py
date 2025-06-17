import board
import neopixel
import time
import math
import threading


class LEDController:
    def __init__(self, num_leds=288, pin=board.D18, brightness=1.0):
        self.num_leds = num_leds
        self.pixels = neopixel.NeoPixel(
            pin, num_leds, brightness=brightness, auto_write=False
        )
        self.is_on = False
        self.color = (255, 255, 255)
        self.brightness = brightness
        self.preset = None
        self._preset_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def turn_on(self):
        self.is_on = True
        self.pixels.fill(self.color)
        self.pixels.show()

    def turn_off(self):
        with self._lock:
            self.is_on = False
            self.preset = None
            if self._preset_thread and self._preset_thread.is_alive():
                self._stop_event.set()
                self._preset_thread.join()
            self.pixels.fill((0, 0, 0))
            self.pixels.show()

    def set_brightness(self, brightness_percent):
        self.brightness = max(0.0, min(1.0, brightness_percent / 100))
        self.pixels.brightness = self.brightness
        if self.is_on:
            self.pixels.fill(self.color)
            self.pixels.show()

    def set_color(self, r, g, b):
        self.preset = None
        self.color = (r, g, b)
        if self.is_on:
            self.pixels.fill(self.color)
            self.pixels.show()

    def status(self):
        return {
            "on": self.is_on,
            "brightness": round(self.brightness * 100),
            "color": self.color,
            "preset": self.preset,
        }

    def run_preset(self, name):
        with self._lock:
            # If a preset is already running, stop it
            if self._preset_thread and self._preset_thread.is_alive():
                self._stop_event.set()
                self._preset_thread.join()

            # Reset stop event for new preset
            self._stop_event.clear()
            self.preset = name

            # Start new thread for the preset
            self._preset_thread = threading.Thread(
                target=self._run_preset_loop, args=(name,), daemon=True
            )
            self._preset_thread.start()

    def _run_preset_loop(self, name):
        if name == "rainbow":
            while not self._stop_event.is_set() and self.preset == "rainbow":
                self._rainbow_cycle(0.001)
        elif name == "chase":
            while not self._stop_event.is_set() and self.preset == "chase":
                self._color_chase(self.color, 0.05)
        elif name == "pulse":
            while not self._stop_event.is_set() and self.preset == "pulse":
                self._pulse(self.color)
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
            if self._stop_event.is_set() or self.preset != "rainbow":
                break
            for i in range(self.num_leds):
                self.pixels[i] = wheel((i * 256 // self.num_leds + j) & 255)
            self.pixels.show()
            time.sleep(wait)

    def _color_chase(self, color, wait):
        for i in range(self.num_leds):
            if self._stop_event.is_set() or self.preset != "chase":
                break
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(wait)
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def _pulse(self, color, steps=50, delay=0.02):
        for i in range(steps):
            if self._stop_event.is_set() or self.preset != "pulse":
                break
            factor = math.sin(math.pi * i / steps)
            scaled_color = tuple(int(c * factor) for c in color)
            self.pixels.fill(scaled_color)
            self.pixels.show()
            time.sleep(delay)
