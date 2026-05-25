from PIL import Image, ImageDraw, ImageFont

_WHITE = (255, 255, 255)
_GREEN = (0, 200, 60)
_RED = (220, 50, 50)
_GRAY = (120, 120, 120)
_DIVIDER = (60, 60, 80)


def _fonts():
    try:
        return ImageFont.load_default(size=9), ImageFont.load_default(size=8)
    except TypeError:
        f = ImageFont.load_default()
        return f, f


def _status_color(status):
    s = (status or "").strip().lower()
    if "on time" in s or s == "on time":
        return _GREEN
    if not s:
        return _GRAY
    return _RED


def _fit(draw, text, font, max_px):
    """Truncate text with ellipsis to fit within max_px wide."""
    if not text:
        return ""
    if draw.textbbox((0, 0), text, font=font, anchor="lt")[2] <= max_px:
        return text
    while len(text) > 1:
        text = text[:-1]
        candidate = text + "…"
        if draw.textbbox((0, 0), candidate, font=font, anchor="lt")[2] <= max_px:
            return candidate
    return text


def render(data, size=(64, 64)):
    """data: output of data.rail.fetch_rail()"""
    img = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_hd, font_bd = _fonts()
    w, _ = size

    name = data.get("name", "").upper()
    bbox = draw.textbbox((0, 0), name, font=font_hd, anchor="lt")
    x = max(2, (w - (bbox[2] - bbox[0])) // 2)
    draw.text((x, 1), name, font=font_hd, fill=_WHITE, anchor="lt")
    draw.line([(0, 12), (w - 1, 12)], fill=_DIVIDER)

    trains = data.get("trains", [])
    if not trains:
        draw.text((2, 16), "No service", font=font_bd, fill=_GRAY, anchor="lt")
        draw.text((2, 28), "scheduled.", font=font_bd, fill=_GRAY, anchor="lt")
        return img

    y = 15
    for train in trains[:2]:
        depart = train.get("depart") or "—"
        status = train.get("status") or ""
        draw.text((2, y), depart, font=font_bd, fill=_WHITE, anchor="lt")
        y += 11
        draw.text((2, y), _fit(draw, status, font_bd, w - 4), font=font_bd,
                  fill=_status_color(status), anchor="lt")
        y += 13

    return img
