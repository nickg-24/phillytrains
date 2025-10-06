from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import json
import time
import os
import yaml

# --- Load Config ---
def load_config(path="config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

# --- Matrix setup ---
mconf = config.get("matrix", {})
options = RGBMatrixOptions()
options.rows = mconf.get("rows", 64)
options.cols = mconf.get("cols", 64)
options.chain_length = mconf.get("chain_length", 1)
options.parallel = mconf.get("parallel", 1)
options.hardware_mapping = mconf.get("hardware_mapping", "adafruit-hat")
matrix = RGBMatrix(options=options)

# --- Fonts ---
font_large = graphics.Font()
font_large.LoadFont("./fonts/7x13.bdf")

font_small = graphics.Font()
font_small.LoadFont("./fonts/5x8.bdf")

white = graphics.Color(255, 255, 255)
blue = graphics.Color(0, 102, 204)

# --- Slide functions ---
def slide_logo(canvas):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 10, 30, blue, "SEPTA")
    return canvas

def slide_train(canvas, train):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 2, 12, blue, f"{data['origin']} → {data['destination']}")
    graphics.DrawText(canvas, font_small, 2, 28, white, f"Train {train.get('train_no', '')}")
    graphics.DrawText(canvas, font_small, 2, 40, white, f"Dep: {train.get('depart', '')}")
    graphics.DrawText(canvas, font_small, 2, 52, white, f"Arr: {train.get('arrive', '')}")
    graphics.DrawText(canvas, font_small, 2, 62, white, f"Status: {train.get('status', '')}")

    return canvas

def slide_alert(canvas, alert_text):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 2, 12, blue, "ALERT")
    graphics.DrawText(canvas, font_small, 2, 32, white, alert_text[:40])  # truncate for now
    return canvas

# --- Display timing (from YAML) ---
DISPLAY_TIMINGS = config.get("display", {
    "logo": 5,
    "train": 10,
    "alert": 10,
})

# --- Load data (mock or live) ---
DATA_PATH = "./mock_data.json"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Mock data file not found: {DATA_PATH}")

with open(DATA_PATH, "r") as f:
    data = json.load(f)

trains = data.get("trains", [])
alerts = data.get("alerts", [])

# --- Slideshow loop ---
try:
    while True:
        # Logo slide
        canvas = matrix.CreateFrameCanvas()
        slide_logo(canvas)
        matrix.SwapOnVSync(canvas)
        time.sleep(DISPLAY_TIMINGS.get("logo", 5))

        # Train slides
        for train in trains:
            canvas = matrix.CreateFrameCanvas()
            slide_train(canvas, train)
            matrix.SwapOnVSync(canvas)
            time.sleep(DISPLAY_TIMINGS.get("train", 10))

        # Alert slides
        for alert in alerts:
            canvas = matrix.CreateFrameCanvas()
            slide_alert(canvas, alert)
            matrix.SwapOnVSync(canvas)
            time.sleep(DISPLAY_TIMINGS.get("alert", 10))

except KeyboardInterrupt:
    print("Exiting...")
