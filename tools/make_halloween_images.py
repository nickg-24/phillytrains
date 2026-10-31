#!/usr/bin/env python3
"""
Generates a few 64x64 Halloween pixel-art images into images/halloween/.
Run from anywhere: python3 tools/make_halloween_images.py
Drop your own 64x64 PNGs into images/halloween/ to use those instead (or as well).
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "images" / "halloween"
OUT.mkdir(parents=True, exist_ok=True)

ORANGE = (255, 120, 0)
DARK_ORANGE = (190, 70, 0)
GREEN = (60, 150, 40)
BLACK = (0, 0, 0)
WHITE = (235, 235, 255)
PURPLE_BG = (30, 0, 40)
BAT = (20, 20, 20)
RED = (255, 60, 60)


def pumpkin():
    img = Image.new("RGB", (64, 64), BLACK)
    d = ImageDraw.Draw(img)
    # Body built from overlapping ellipses with darker ribs
    d.ellipse((12, 20, 52, 54), fill=ORANGE)
    d.ellipse((20, 20, 44, 54), outline=DARK_ORANGE)
    d.ellipse((28, 20, 36, 54), outline=DARK_ORANGE)
    # Stem
    d.rectangle((30, 10, 34, 20), fill=GREEN)
    # Eyes
    d.polygon([(20, 30), (28, 30), (24, 38)], fill=BLACK)
    d.polygon([(36, 30), (44, 30), (40, 38)], fill=BLACK)
    # Jagged grin
    d.polygon([(18, 44), (46, 44), (42, 50), (38, 44), (32, 51), (26, 44), (22, 50)], fill=BLACK)
    return img


def ghost():
    img = Image.new("RGB", (64, 64), BLACK)
    d = ImageDraw.Draw(img)
    d.ellipse((14, 8, 50, 40), fill=WHITE)
    d.rectangle((14, 24, 50, 48), fill=WHITE)
    # Wavy hem
    d.polygon([(14, 48), (50, 48), (50, 54), (46, 58), (42, 52),
               (37, 58), (32, 52), (28, 58), (23, 52), (18, 58), (14, 54)], fill=WHITE)
    # Eyes and mouth
    d.ellipse((23, 22, 29, 30), fill=BLACK)
    d.ellipse((35, 22, 41, 30), fill=BLACK)
    d.ellipse((29, 34, 35, 40), fill=BLACK)
    return img


def bat():
    img = Image.new("RGB", (64, 64), PURPLE_BG)
    d = ImageDraw.Draw(img)
    # Wings
    d.polygon([(28, 30), (4, 18), (10, 34), (2, 40), (14, 44), (22, 40), (28, 40)], fill=BAT)
    d.polygon([(36, 30), (60, 18), (54, 34), (62, 40), (50, 44), (42, 40), (36, 40)], fill=BAT)
    # Body and ears
    d.ellipse((28, 26, 36, 42), fill=BAT)
    d.polygon([(28, 28), (29, 21), (32, 27)], fill=BAT)
    d.polygon([(36, 28), (35, 21), (32, 27)], fill=BAT)
    # Glowing eyes
    d.ellipse((29, 32, 31, 34), fill=RED)
    d.ellipse((33, 32, 35, 34), fill=RED)
    return img


if __name__ == "__main__":
    for name, fn in [("pumpkin", pumpkin), ("ghost", ghost), ("bat", bat)]:
        path = OUT / f"{name}.png"
        fn().save(path)
        print(f"wrote {path}")
