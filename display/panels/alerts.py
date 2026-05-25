from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

_YELLOW = (240, 200, 0)
_WHITE = (255, 255, 255)
_DIVIDER = (60, 60, 80)
_MAX_LINES = 4


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


def _page(lines, font_hd, font_bd, size):
    w, _ = size
    img = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((2, 1), "ALERT", font=font_hd, fill=_YELLOW)
    draw.line([(0, 12), (w - 1, 12)], fill=_DIVIDER)
    y = 14
    for line in lines[:_MAX_LINES]:
        draw.text((2, y), line, font=font_bd, fill=_WHITE)
        y += 10
    return img


def render(alert_list, size=(64, 64)):
    """Returns a list of PIL Images, one per page across all alerts."""
    if not alert_list:
        return []

    font_hd, font_bd = _load_fonts()
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    images = []

    for alert in alert_list:
        lines = _wrap(scratch, alert, font_bd, size[0] - 4)
        for i in range(0, max(len(lines), 1), _MAX_LINES):
            images.append(_page(lines[i:i + _MAX_LINES], font_hd, font_bd, size))

    return images
