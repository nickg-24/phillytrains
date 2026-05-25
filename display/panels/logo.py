from pathlib import Path
from PIL import Image, UnidentifiedImageError

_LOGO = Path(__file__).resolve().parents[2] / "images" / "septa_logo.png"


def render(size=(64, 64)):
    """Returns a 64x64 PIL Image of the SEPTA logo."""
    try:
        img = Image.open(_LOGO).convert("RGBA")
        bg = Image.new("RGBA", size, (0, 0, 0, 255))
        img = img.resize(size, Image.LANCZOS)
        bg.paste(img, (0, 0), img)
        return bg.convert("RGB")
    except (FileNotFoundError, UnidentifiedImageError):
        return Image.new("RGB", size, (0, 0, 0))
