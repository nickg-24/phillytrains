import datetime
from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

_WHITE = (255, 255, 255)
_GRAY = (120, 120, 120)
_DIVIDER = (60, 60, 80)

_LABELS = {
    "northbound": "NB Fern Rk",   # 10 chars x 6px = 60px
    "southbound": "SB AT&T",       # 7 chars x 6px = 42px
}


def _upcoming(times):
    now = datetime.datetime.now()
    cutoff = now.hour * 60 + now.minute - 1
    result = []
    for t in times:
        try:
            dt = datetime.datetime.strptime(t.strip(), "%I:%M %p")
            if dt.hour * 60 + dt.minute >= cutoff:
                result.append(t)
        except ValueError:
            result.append(t)
    return result[:3]


def render(data, direction, size=(64, 64)):
    """data: output of data.subway.fetch_subway(); direction: 'northbound' or 'southbound'"""
    img = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_hd, font_bd = _load_fonts()
    w, _ = size

    label = _LABELS.get(direction, direction.upper())
    label_w = draw.textbbox((0, 0), label, font=font_hd)[2]
    draw.text((max(2, (w - label_w) // 2), 1), label, font=font_hd, fill=_WHITE)
    draw.line([(0, 12), (w - 1, 12)], fill=_DIVIDER)

    times = _upcoming(data.get(direction, []))
    if not times:
        draw.text((2, 15), "No upcoming", font=font_bd, fill=_GRAY)
        draw.text((2, 25), "departures.", font=font_bd, fill=_GRAY)
        return img

    y = 15
    for t in times:
        draw.text((2, y), t, font=font_bd, fill=_WHITE)
        y += 13

    return img
