from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# --- Matrix setup ---
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = "adafruit-hat"
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

def slide_train(canvas, train_no, depart, arrive, status):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 2, 12, blue, "SEPTA")
    graphics.DrawText(canvas, font_small, 2, 28, white, f"Train {train_no}")
    graphics.DrawText(canvas, font_small, 2, 40, white, f"Dep: {depart}")
    graphics.DrawText(canvas, font_small, 2, 52, white, f"Arr: {arrive}")
    graphics.DrawText(canvas, font_small, 2, 62, white, f"{status}")
    return canvas

def slide_no_trains(canvas):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 2, 30, white, "No more trains")
    return canvas

# --- Display timing (seconds) ---
DISPLAY_TIMINGS = {
    "logo": 5,
    "train": 10,
    "no_trains": 8,
}

# --- Example placeholder data ---
train_data = [
    {"train_no": "214", "depart": "07:32 AM", "arrive": "07:58 AM", "status": "On time"},
    {"train_no": "220", "depart": "07:59 AM", "arrive": "08:25 AM", "status": "5m late"},
]
no_trains = False  # set True to test no-trains slide

# --- Slideshow loop ---
try:
    while True:
        # Logo always first
        canvas = matrix.CreateFrameCanvas()
        slide_logo(canvas)
        matrix.SwapOnVSync(canvas)
        time.sleep(DISPLAY_TIMINGS["logo"])

        if no_trains or not train_data:
            canvas = matrix.CreateFrameCanvas()
            slide_no_trains(canvas)
            matrix.SwapOnVSync(canvas)
            time.sleep(DISPLAY_TIMINGS["no_trains"])
        else:
            for t in train_data:
                canvas = matrix.CreateFrameCanvas()
                slide_train(canvas, t["train_no"], t["depart"], t["arrive"], t["status"])
                matrix.SwapOnVSync(canvas)
                time.sleep(DISPLAY_TIMINGS["train"])

except KeyboardInterrupt:
    print("Exiting...")
