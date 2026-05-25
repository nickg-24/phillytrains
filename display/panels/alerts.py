from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

_YELLOW  = (240, 200, 0)
_WHITE   = (255, 255, 255)
_DIVIDER = (60, 60, 80)
_MAX_LINES = 4


def _text(draw, xy, text, font, fill):
    x, y = xy
    draw.text((x, y), text, font=font, fill=fill)


def _wrap(draw, text, font, max_px):
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_px or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _page(lines, font_sm, size):
    w, _ = size
    img  = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    _text(draw, (2, 2), "ALERT", font_sm, _YELLOW)
    draw.line([(0, 12), (w - 1, 12)], fill=_DIVIDER)
    y = 16
    for line in lines[:_MAX_LINES]:
        _text(draw, (2, y), line, font_sm, _WHITE)
        y += 10
    return img


def render(alert_list, size=(64, 64)):
    """Returns a list of PIL Images, one per page across all alerts."""
    if not alert_list:
        return []

    _, _, font_sm = _load_fonts()
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    images  = []

    for alert in alert_list:
        lines = _wrap(scratch, alert, font_sm, size[0] - 4)
        for i in range(0, max(len(lines), 1), _MAX_LINES):
            images.append(_page(lines[i:i + _MAX_LINES], font_sm, size))

    return images
