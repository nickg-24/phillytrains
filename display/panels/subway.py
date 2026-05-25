import datetime
from PIL import Image, ImageDraw
from display.fonts import load as _load_fonts

_WHITE   = (255, 255, 255)
_GRAY    = (120, 120, 120)
_DIVIDER = (60, 60, 80)

# 6x10 font: 6px/char — these labels stay within 64px
_LABELS = {
    "northbound": "NB Fern Rk",   # 10 x 6 = 60px
    "southbound": "SB AT&T",       #  7 x 6 = 42px
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
    font_lg, font_md, font_sm = _load_fonts()
    w, _ = size

    label = _LABELS.get(direction, direction.upper())
    label_w = draw.textbbox((0, 0), label, font=font_md)[2]
    draw.text((max(2, (w - label_w) // 2), 2), label, font=font_md, fill=_WHITE)
    draw.line([(0, 14), (w - 1, 14)], fill=_DIVIDER)

    times = _upcoming(data.get(direction, []))
    if not times:
        draw.text((2, 20), "No upcoming", font=font_sm, fill=_GRAY)
        draw.text((2, 30), "departures.", font=font_sm, fill=_GRAY)
        return img

    y = 18
    for t in times:
        draw.text((2, y), t, font=font_lg, fill=_WHITE)
        y += 16

    return img
