from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
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
opts.brightness = mconf.get("brightness", 60)
matrix = RGBMatrix(options=opts)
canvas = matrix.CreateFrameCanvas()

# ---------- Fonts / colors ----------
font_large = graphics.Font(); font_large.LoadFont("./fonts/7x13.bdf")
font_small = graphics.Font(); font_small.LoadFont("./fonts/5x8.bdf")
white = graphics.Color(255, 255, 255)
blue = graphics.Color(0, 102, 204)

# ---------- Header scroll ----------
def update_header(canvas, header_state):
    header_state["pos"] -= 1
    if header_state["pos"] + header_state["width"] < 0:
        header_state["pos"] = canvas.width
    graphics.DrawText(canvas, header_state["font"], header_state["pos"],
                      header_state["y"], header_state["color"], header_state["text"])

# ---------- Slides ----------
def draw_logo(canvas):
    """Display SEPTA logo image centered."""
    canvas.Clear()
    try:
        image = Image.open("./septa_logo.png").convert("RGBA")
        bg = Image.new("RGBA", image.size, (0, 0, 0, 255))
        image = Image.alpha_composite(bg, image)
        image = image.convert("RGB")
        image = image.resize((canvas.width, canvas.height), resample=Image.NEAREST)
        w, h = image.size
        x = (canvas.width - w) // 2
        y = (canvas.height - h) // 2
        canvas.SetImage(image, x, y)
        matrix.SwapOnVSync(canvas)
    except Exception as e:
        print(f"[ERROR] Could not load logo: {e}")
        graphics.DrawText(canvas, font_large, 10, 30, blue, "SEPTA")

def draw_train_info(canvas, train):
    """Display a single train’s info below the scrolling header."""
    status_text = train.get('status', '').strip().lower()
    if "on time" in status_text:
        status_color = graphics.Color(0, 255, 0)
    else:
        status_color = graphics.Color(255, 0, 0)

    graphics.DrawText(canvas, font_small, 2, 28, white, f"Train {train.get('train_no','')}")
    graphics.DrawText(canvas, font_small, 2, 40, white, f"Dep: {train.get('depart','')}")
    graphics.DrawText(canvas, font_small, 2, 52, white, f"Arr: {train.get('arrive','')}")
    graphics.DrawText(canvas, font_small, 2, 62, status_color, train.get('status',''))

# ---------- Alert: Pagination style ----------
def paginate_alert(canvas, alert_text):
    """Show long alerts one 'page' at a time with 4 lines per page."""
    words = alert_text.split()
    max_chars = 13  # roughly fits width for 5x8 font
    lines, line = [], ""

    # Wrap text into lines
    for w in words:
        if len(line + " " + w) < max_chars:
            line += (" " if line else "") + w
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)

    chunk_size = 4  # lines per page now
    hold_time = 2   # seconds per page

    for i in range(0, len(lines), chunk_size):
        canvas.Clear()
        graphics.DrawText(canvas, font_small, 2, 12, graphics.Color(255, 255, 0), "ALERT")
        y = 24
        for l in lines[i:i+chunk_size]:
            graphics.DrawText(canvas, font_small, 2, y, white, l)
            y += 10
        matrix.SwapOnVSync(canvas)
        time.sleep(hold_time)


# ---------- Short alerts ----------
def draw_wrapped_alert(canvas, alert_text):
    """Show short alerts as one static message."""
    canvas.Clear()
    header_color = graphics.Color(255, 255, 0)
    text_color = white
    words = alert_text.split()
    lines, line = [], ""
    for w in words:
        if len(line + " " + w) < 13:
            line += (" " if line else "") + w
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)

    y = 12
    graphics.DrawText(canvas, font_small, 2, y, header_color, "ALERT")
    for l in lines[:5]:
        y += 10
        graphics.DrawText(canvas, font_small, 2, y, text_color, l)

    matrix.SwapOnVSync(canvas)
    time.sleep(T_ALERT)

def display_alert(canvas, alert_text):
    """Choose between short (static) and long (paginated) alerts."""
    if len(alert_text) > 60:
        paginate_alert(canvas, alert_text)
    else:
        draw_wrapped_alert(canvas, alert_text)

# ---------- Load data ----------
DATA_PATH = "./mock_data.json"
with open(DATA_PATH) as f:
    data = json.load(f)
trains  = data.get("trains", [])
alerts  = data.get("alerts", [])
route   = f"{data['origin']} → {data['destination']}"

# ---------- Timing ----------
tconf = config.get("display", {})
T_LOGO  = tconf.get("logo", 5)
T_TRAIN = tconf.get("train", 10)
T_ALERT = tconf.get("alert", 10)

# ---------- Header scroll setup ----------
header_w = graphics.DrawText(canvas, font_small, 0, 10, blue, route)
header = {"text": route, "font": font_small, "color": blue, "width": header_w,
          "pos": canvas.width if header_w > canvas.width else 0, "y": 10}

# ---------- Main slideshow ----------
try:
    while True:
        # 1. SEPTA logo
        draw_logo(canvas)
        time.sleep(T_LOGO)

        # 2. Train slides
        for train in trains:
            start = time.time()
            while time.time() - start < T_TRAIN:
                canvas.Clear()
                if header["width"] > canvas.width:
                    update_header(canvas, header)
                else:
                    x = (canvas.width - header["width"]) // 2
                    graphics.DrawText(canvas, font_small, x, header["y"], blue, route)
                draw_train_info(canvas, train)
                canvas = matrix.SwapOnVSync(canvas)
                time.sleep(0.03)

        # 3. Alerts
        for alert in alerts:
            display_alert(canvas, alert)

        # 4. Loop back to logo

except KeyboardInterrupt:
    print("Exiting...")
