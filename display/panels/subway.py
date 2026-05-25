import datetime
from PIL import Image, ImageDraw, ImageFont

_WHITE = (255, 255, 255)
_GRAY = (120, 120, 120)
_DIVIDER = (60, 60, 80)

_LABELS = {
    "northbound": "↑ Fern Rock",
    "southbound": "↓ AT&T Stn",
}
_FALLBACK_LABELS = {
    "northbound": "BSL NB",
    "southbound": "BSL SB",
}


def _fonts():
    try:
        return ImageFont.load_default(size=9), ImageFont.load_default(size=8)
    except TypeError:
        f = ImageFont.load_default()
        return f, f


def _upcoming(times):
    """Filter to next 3 departures from now."""
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
    font_hd, font_bd = _fonts()
    w, _ = size

    label = _LABELS.get(direction, direction.upper())
    bbox = draw.textbbox((0, 0), label, font=font_hd, anchor="lt")
    if bbox[2] - bbox[0] > w - 4:
        label = _FALLBACK_LABELS.get(direction, direction.upper())
        bbox = draw.textbbox((0, 0), label, font=font_hd, anchor="lt")
    x = max(2, (w - (bbox[2] - bbox[0])) // 2)
    draw.text((x, 1), label, font=font_hd, fill=_WHITE, anchor="lt")
    draw.line([(0, 12), (w - 1, 12)], fill=_DIVIDER)

    times = _upcoming(data.get(direction, []))
    if not times:
        draw.text((2, 16), "No upcoming", font=font_bd, fill=_GRAY, anchor="lt")
        draw.text((2, 28), "departures.", font=font_bd, fill=_GRAY, anchor="lt")
        return img

    y = 16
    for t in times:
        draw.text((2, y), t, font=font_bd, fill=_WHITE, anchor="lt")
        y += 13

    return img
