from PIL import Image


def render(size=(64, 64)):
    """Returns a 64x64 PIL Image of the SEPTA logo."""
    try:
        img = Image.open("septa_logo.png").convert("RGBA")
        bg = Image.new("RGBA", size, (0, 0, 0, 255))
        img = img.resize(size, Image.LANCZOS)
        bg.paste(img, (0, 0), img)
        return bg.convert("RGB")
    except FileNotFoundError:
        return Image.new("RGB", size, (0, 0, 0))
