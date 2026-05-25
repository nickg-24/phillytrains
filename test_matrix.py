#!/usr/bin/env python3
"""
Hardware smoke test — displays a solid blue screen for 5 seconds.
Run with: sudo .venv/bin/python3 test_matrix.py

If the matrix lights up blue, the library and wiring are good.
"""
import time
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

opts = RGBMatrixOptions()
opts.rows = 64
opts.cols = 64
opts.hardware_mapping = "adafruit-hat"
opts.brightness = 50

matrix = RGBMatrix(options=opts)
canvas = matrix.CreateFrameCanvas()

img = Image.new("RGB", (64, 64), (0, 80, 200))
canvas.SetImage(img, 0, 0)
canvas = matrix.SwapOnVSync(canvas)

print("Matrix should show solid blue. Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
