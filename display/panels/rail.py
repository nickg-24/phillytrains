from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

_WHITE  = (255, 255, 255)
_GREEN  = (0, 200, 60)
_RED    = (220, 50, 50)
_GRAY   = (120, 120, 120)
_DIVIDER = (60, 60, 80)

# Scroll speed: 1 pixel per frame at ~30 fps
_FRAME_DELAY = 0.033


def _status_color(status):
    s = (status or "").strip().lower()
    if "on time" in s:
        return _GREEN
    if not s:
        return _GRAY
    return _RED


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


def _make_base(train, font_lg, font_sm, size):
    """Renders the static portion of the slide (everything below the header)."""
    w, h = size
    img = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.line([(0, 15), (w - 1, 15)], fill=_DIVIDER)

    if train is None:
        draw.text((2, 20), "No service", font=font_sm, fill=_GRAY)
        draw.text((2, 30), "scheduled.", font=font_sm, fill=_GRAY)
        return img

    depart = train.get("depart") or "—"
    status = train.get("status") or ""
    arrive = train.get("arrive") or ""

    draw.text((2, 19), depart, font=font_lg, fill=_WHITE)
    draw.text((2, 34), _fit(draw, status, font_lg, w - 4), font=font_lg,
              fill=_status_color(status))
    if arrive:
        draw.text((2, 51), "> " + arrive, font=font_sm, fill=_GRAY)

    return img


def render(line_name, train, size=(64, 64)):
    """Returns a list of PIL Images (animation frames) for one train.

    line_name: string (e.g. 'Norristown')
    train: dict with keys depart, arrive, status — or None for no-service slide
    """
    font_lg, font_md, font_sm = _load_fonts()
    w, h = size

    base = _make_base(train, font_lg, font_sm, size)
    header = line_name.upper()

    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    header_w = scratch.textbbox((0, 0), header, font=font_lg)[2]

    if header_w <= w:
        # Header fits — single static frame, centered
        frame = base.copy()
        x = max(2, (w - header_w) // 2)
        ImageDraw.Draw(frame).text((x, 1), header, font=font_lg, fill=_WHITE)
        return [frame]

    # Header wider than display — scroll left across the slide
    frames = []
    for pos in range(w + header_w):
        frame = base.copy()
        ImageDraw.Draw(frame).text((w - pos, 1), header, font=font_lg, fill=_WHITE)
        frames.append(frame)
    return frames
