class MockLEDController:
    def __init__(self):
        self.is_on = False
        self.brightness = 100  # 0-100
        self.color = (255, 255, 255)  # RGB

    def turn_on(self):
        self.is_on = True
        print("LEDs turned ON")

    def turn_off(self):
        self.is_on = False
        print("LEDs turned OFF")

    def set_brightness(self, value):
        self.brightness = max(0, min(100, value))
        print(f"Brightness set to {self.brightness}%")

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        print(f"Color set to RGB {self.color}")

    def status(self):
        return {
            "power": "on" if self.is_on else "off",
            "brightness": self.brightness,
            "color": self.color,
        }
