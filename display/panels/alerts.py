from PIL import Image, ImageDraw, ImageFont

_YELLOW = (240, 200, 0)
_WHITE = (255, 255, 255)
_DIVIDER = (60, 60, 80)
_MAX_LINES = 4


def _fonts():
    try:
        return ImageFont.load_default(size=9), ImageFont.load_default(size=8)
    except TypeError:
        f = ImageFont.load_default()
        return f, f


def _wrap(draw, text, font, max_px):
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font, anchor="lt")[2] <= max_px or not line:
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
    draw.text((2, 1), "ALERT", font=font_hd, fill=_YELLOW, anchor="lt")
    draw.line([(0, 12), (w - 1, 12)], fill=_DIVIDER)
    y = 15
    for line in lines[:_MAX_LINES]:
        draw.text((2, y), line, font=font_bd, fill=_WHITE, anchor="lt")
        y += 11
    return img


def render(alert_list, size=(64, 64)):
    """Returns a list of PIL Images, one per page across all alerts."""
    if not alert_list:
        return []

    font_hd, font_bd = _fonts()
    scratch = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    images = []

    for alert in alert_list:
        lines = _wrap(scratch, alert, font_bd, size[0] - 4)
        for i in range(0, max(len(lines), 1), _MAX_LINES):
            images.append(_page(lines[i:i + _MAX_LINES], font_hd, font_bd, size))

    return images
