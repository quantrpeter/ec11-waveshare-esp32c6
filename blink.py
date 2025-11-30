# ws2812_3colors.py
from machine import Pin
from neopixel import NeoPixel
from time import sleep

# WS2812 LED on GPIO 8, 1 pixel
pin = Pin(8, Pin.OUT)
np = NeoPixel(pin, 1)

# Color values in GRB order: (Green, Red, Blue)
RED    = (0, 50, 0)   # Full red
GREEN  = (50, 0, 0)   # Full green
BLUE   = (0, 0, 50)   # Full blue
OFF    = (0, 0, 0)    # LED off

colors = [RED, GREEN, BLUE]

print("Blinking WS2812: Red → Green → Blue")

while True:
    for color in colors:
        np[0] = color
        np.write()
        sleep(0.7)      # Hold each color
        np[0] = OFF
        np.write()
        sleep(0.3)      # Short pause between colors
