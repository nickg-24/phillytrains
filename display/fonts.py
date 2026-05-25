from pathlib import Path
from PIL import ImageFont

_FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def load():
    """Returns (large, medium, small) PIL bitmap fonts.

    large  = 7x13  — body text on rail/subway slides
    medium = 6x10  — headers, alert title
    small  = 5x8   — secondary info, alert body text
    """
    return (
        ImageFont.load(str(_FONTS_DIR / "7x13.pil")),
        ImageFont.load(str(_FONTS_DIR / "6x10.pil")),
        ImageFont.load(str(_FONTS_DIR / "5x8.pil")),
    )
