from pathlib import Path
from PIL import Image, UnidentifiedImageError

_ROOT = Path(__file__).resolve().parents[2]
_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}


def load_images(folder="images/halloween", size=(64, 64)):
    """Returns a list of 64x64 RGB PIL Images from `folder`, sorted by filename.

    Missing folder or unreadable files are skipped, so this is always safe to call.
    """
    path = Path(folder)
    if not path.is_absolute():
        path = _ROOT / path
    if not path.is_dir():
        return []

    images = []
    for f in sorted(path.iterdir()):
        if f.suffix.lower() not in _EXTS:
            continue
        try:
            img = Image.open(f).convert("RGBA")
        except (UnidentifiedImageError, OSError):
            continue
        img = img.resize(size, Image.LANCZOS)
        bg = Image.new("RGBA", size, (0, 0, 0, 255))
        bg.paste(img, (0, 0), img)
        images.append(bg.convert("RGB"))
    return images
