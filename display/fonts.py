from pathlib import Path
from PIL import ImageFont

_FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def load():
    """Returns (header_font, body_font) as crisp PIL bitmap fonts."""
    return (
        ImageFont.load(str(_FONTS_DIR / "6x10.pil")),
        ImageFont.load(str(_FONTS_DIR / "5x8.pil")),
    )
