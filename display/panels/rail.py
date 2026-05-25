from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

_BLUE  = (0, 102, 204)
_WHITE = (255, 255, 255)
_GREEN = (0, 255, 0)
_RED   = (255, 0, 0)
_GRAY  = (120, 120, 120)


def _text(draw, xy, text, font, fill):
    """Draw text twice with 1px horizontal offset for a bolder stroke."""
    x, y = xy
    draw.text((x, y), text, font=font, fill=fill)
    draw.text((x + 1, y), text, font=font, fill=fill)


def _status_color(status):
    s = (status or "").strip().lower()
    if "on time" in s:
        return _GREEN
    if not s:
        return _GRAY
    return _RED


def _fmt_time(t):
    """Strip leading zero from hour: '08:15 AM' -> '8:15 AM'."""
    return (t or "-").lstrip("0") or "0"


def _fit(draw, text, font, max_px):
    if not text:
        return ""
    if draw.textbbox((0, 0), text, font=font)[2] <= max_px:
        return text
    while len(text) > 1:
        text = text[:-1]
        if draw.textbbox((0, 0), text + "...", font=font)[2] <= max_px:
            return text + "..."
    return text


def _make_base(train, font, size):
    w, h = size
    img = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)

    if train is None:
        _text(draw, (2, 20), "No service", font, _GRAY)
        _text(draw, (2, 32), "scheduled.", font, _GRAY)
        return img

    train_no = train.get("train_no")
    depart   = _fmt_time(train.get("depart"))
    arrive   = _fmt_time(train.get("arrive"))
    status   = train.get("status") or ""

    if train_no:
        _text(draw, (2, 12), f"Train {train_no}", font, _WHITE)
        _text(draw, (2, 24), f"Dep: {depart}",   font, _WHITE)
        _text(draw, (2, 36), f"Arr: {arrive}",   font, _WHITE)
        _text(draw, (2, 48), _fit(draw, status, font, w - 4),
              font, _status_color(status))
    else:
        _text(draw, (2, 12), f"Dep: {depart}", font, _WHITE)
        _text(draw, (2, 24), f"Arr: {arrive}", font, _WHITE)
        _text(draw, (2, 36), _fit(draw, status, font, w - 4),
              font, _status_color(status))

    return img


def render(header, train, size=(64, 64)):
    """Returns a list of PIL Images (animation frames) for one train.

    header : string displayed as the scrolling header (e.g. "ORIGIN > DEST")
    train  : dict with keys train_no, depart, arrive, status -- or None
    """
    _, _, font_sm = _load_fonts()
    w, h = size

    base     = _make_base(train, font_sm, size)
    hdr      = header.upper()
    scratch  = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    hdr_w    = scratch.textbbox((0, 0), hdr, font=font_sm)[2]

    if hdr_w <= w:
        frame = base.copy()
        x = max(2, (w - hdr_w) // 2)
        _text(ImageDraw.Draw(frame), (x, 2), hdr, font_sm, _BLUE)
        return [frame]

    frames = []
    for pos in range(w + hdr_w):
        frame = base.copy()
        _text(ImageDraw.Draw(frame), (w - pos, 2), hdr, font_sm, _BLUE)
        frames.append(frame)
    return frames
