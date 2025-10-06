from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import json, time, os, yaml

# ---------- Load config ----------
def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
config = load_config()

# ---------- Matrix setup ----------
mconf = config.get("matrix", {})
opts = RGBMatrixOptions()
opts.rows = mconf.get("rows", 64)
opts.cols = mconf.get("cols", 64)
opts.chain_length = mconf.get("chain_length", 1)
opts.parallel = mconf.get("parallel", 1)
opts.hardware_mapping = mconf.get("hardware_mapping", "adafruit-hat")
matrix = RGBMatrix(options=opts)
canvas = matrix.CreateFrameCanvas()

# ---------- Fonts / colors ----------
font_large = graphics.Font(); font_large.LoadFont("./fonts/7x13.bdf")
font_small = graphics.Font(); font_small.LoadFont("./fonts/5x8.bdf")
white = graphics.Color(255,255,255)
blue  = graphics.Color(0,102,204)

# ---------- Scroll header ----------
def update_header(canvas, header_state):
    header_state["pos"] -= 1
    if header_state["pos"] + header_state["width"] < 0:
        header_state["pos"] = canvas.width
    graphics.DrawText(canvas, header_state["font"], header_state["pos"],
                      header_state["y"], header_state["color"], header_state["text"])

# ---------- Slides ----------
def draw_logo(canvas):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 10, 30, blue, "SEPTA")

def draw_train_info(canvas, train):
    status_text = train.get('status', '').strip().lower()

    # Color logic
    if status_text == "on time":
        status_color = graphics.Color(0, 255, 0)   # green
    else:
        status_color = graphics.Color(255, 0, 0)   # red

    graphics.DrawText(canvas, font_small, 2, 28, white, f"Train {train.get('train_no','')}")
    graphics.DrawText(canvas, font_small, 2, 40, white, f"Dep: {train.get('depart','')}")
    graphics.DrawText(canvas, font_small, 2, 52, white, f"Arr: {train.get('arrive','')}")
    graphics.DrawText(canvas, font_small, 2, 62, status_color, train.get('status', ''))


def draw_alert(canvas, alert_text):
    canvas.Clear()
    graphics.DrawText(canvas, font_large, 2, 12, blue, "ALERT")
    graphics.DrawText(canvas, font_small, 2, 32, white, alert_text[:40])

# ---------- Load data ----------
DATA_PATH = "./mock_data.json"
with open(DATA_PATH) as f:
    data = json.load(f)
trains  = data.get("trains", [])
alerts  = data.get("alerts", [])
route   = f"{data['origin']} → {data['destination']}"

# ---------- Timing ----------
tconf = config.get("display", {})
T_LOGO  = tconf.get("logo",5)
T_TRAIN = tconf.get("train",10)
T_ALERT = tconf.get("alert",10)

# ---------- Header state ----------
header_w = graphics.DrawText(canvas, font_small, 0, 10, blue, route)
header = {"text":route, "font":font_small, "color":blue, "width":header_w,
          "pos":canvas.width if header_w>canvas.width else 0, "y":10}

# ---------- Main slideshow ----------
try:
    while True:
        # --- 1. SEPTA logo ---
        draw_logo(canvas)
        matrix.SwapOnVSync(canvas)
        time.sleep(T_LOGO)

        # --- 2. Train slides ---
        for train in trains:
            start = time.time()
            while time.time() - start < T_TRAIN:
                canvas.Clear()
                # header (scrolls)
                if header["width"] > canvas.width:
                    update_header(canvas, header)
                else:
                    x = (canvas.width - header["width"]) // 2
                    graphics.DrawText(canvas, font_small, x, header["y"], blue, route)
                # train info
                draw_train_info(canvas, train)
                canvas = matrix.SwapOnVSync(canvas)
                time.sleep(0.03)

        # --- 3. Alert slides ---
        for alert in alerts:
            canvas.Clear()
            draw_alert(canvas, alert)
            canvas = matrix.SwapOnVSync(canvas)
            time.sleep(T_ALERT)

        # Loop back to step 1 automatically

except KeyboardInterrupt:
    print("Exiting...")
