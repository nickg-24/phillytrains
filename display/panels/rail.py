from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

# Original colors from matrix_control.py
_BLUE  = (0, 102, 204)
_WHITE = (255, 255, 255)
_GREEN = (0, 255, 0)
_RED   = (255, 0, 0)
_GRAY  = (120, 120, 120)


def _status_color(status):
    s = (status or "").strip().lower()
    if "on time" in s:
        return _GREEN
    if not s:
        return _GRAY
    return _RED


def _fmt_time(t):
    """Strip leading zero from hour: '08:15 AM' → '8:15 AM'."""
    return (t or "—").lstrip("0") or "0"


def _fit(draw, text, font, max_px):
    if not text:
        return ""
    if draw.textbbox((0, 0), text, font=font)[2] <= max_px:
        return text
    while len(text) > 1:
        text = text[:-1]
        if draw.textbbox((0, 0), text + "…", font=font)[2] <= max_px:
            return text + "…"
    return text


def _make_base(train, font, size):
    """Static portion: everything except the scrolling header."""
    w, h = size
    img = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)

    if train is None:
        draw.text((2, 20), "No service", font=font, fill=_GRAY)
        draw.text((2, 32), "scheduled.", font=font, fill=_GRAY)
        return img

    train_no = train.get("train_no")
    depart   = _fmt_time(train.get("depart"))
    arrive   = _fmt_time(train.get("arrive"))
    status   = train.get("status") or ""

    # 4-line layout matching original: train#, depart, arrive, status
    # y=12, 24, 36, 48 → 12px spacing → 5x8 font with 4px leading
    if train_no:
        draw.text((2, 12), f"Train {train_no}", font=font, fill=_WHITE)
        draw.text((2, 24), f"Dep: {depart}",   font=font, fill=_WHITE)
        draw.text((2, 36), f"Arr: {arrive}",   font=font, fill=_WHITE)
        draw.text((2, 48), _fit(draw, status, font, w - 4),
                  font=font, fill=_status_color(status))
    else:
        # GTFS fallback: no train number, status is descriptive
        draw.text((2, 12), f"Dep: {depart}", font=font, fill=_WHITE)
        draw.text((2, 24), f"Arr: {arrive}", font=font, fill=_WHITE)
        draw.text((2, 36), _fit(draw, status, font, w - 4),
                  font=font, fill=_status_color(status))

    return img


def render(line_name, train, size=(64, 64)):
    """Returns a list of PIL Images (animation frames) for one train.

    line_name : string displayed as the scrolling header
    train     : dict with keys train_no, depart, arrive, status — or None
    """
    _, _, font_sm = _load_fonts()   # 5x8 — same font for header and body
    w, h = size

    base   = _make_base(train, font_sm, size)
    header = line_name.upper()

    scratch  = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    header_w = scratch.textbbox((0, 0), header, font=font_sm)[2]

    if header_w <= w:
        # Fits — static, centered in blue
        frame = base.copy()
        x = max(2, (w - header_w) // 2)
        ImageDraw.Draw(frame).text((x, 2), header, font=font_sm, fill=_BLUE)
        return [frame]

    # Wider than display — scroll left
    frames = []
    for pos in range(w + header_w):
        frame = base.copy()
        ImageDraw.Draw(frame).text((w - pos, 2), header, font=font_sm, fill=_BLUE)
        frames.append(frame)
    return frames
