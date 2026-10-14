# -*- coding: utf-8 -*-
"""Crop the food photos: four square thumbnails for the list rows, plus one
panorama for the 'Eat like a local' card."""
import os, json
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "build", "pool")
ASSETS = os.path.join(HERE, "assets")

SQUARES = [
    ("food_roujiamo.jpg", "roujiamo_00.jpg", 0.50, 0.50),
    ("food_paomo.jpg",    "paomo_07.jpg",    0.50, 0.50),
    ("food_yopo.jpg",     "yopo_01.jpg",     0.50, 0.50),
    ("food_liangpi.jpg",  "liangpi_00.jpg",  0.50, 0.50),
]
PANORAMA = ("food_market.jpg", "market_04.jpg", 1600, 580)

src = json.load(open(os.path.join(POOL, "sources.json"), encoding="utf-8"))
credits = {}

for name, f, xb, yb in SQUARES:
    im = Image.open(os.path.join(POOL, f)).convert("RGB")
    w, h = im.size
    s = min(w, h)
    x0 = int((w - s) * xb)
    y0 = int((h - s) * yb)
    im = im.crop((x0, y0, x0 + s, y0 + s)).resize((460, 460), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.05)
    im = ImageEnhance.Brightness(im).enhance(1.03)
    im.save(os.path.join(ASSETS, name), quality=88, optimize=True)
    credits[name] = src.get(f, {}).get("source", "")
    print("%-20s <- %-16s ok" % (name, f))

name, f, tw, th = PANORAMA
im = Image.open(os.path.join(POOL, f)).convert("RGB")
w, h = im.size
want = float(tw) / th
if w / float(h) > want:                    # too wide: trim the sides
    nw = int(h * want)
    x0 = (w - nw) // 2
    box = (x0, 0, x0 + nw, h)
else:                                      # too tall: trim top and bottom
    nh = int(w / want)
    y0 = int((h - nh) * 0.5)
    box = (0, y0, w, y0 + nh)
im = im.crop(box).resize((tw, th), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(1.06)
im = ImageEnhance.Brightness(im).enhance(1.05)
im.save(os.path.join(ASSETS, name), quality=88, optimize=True)
credits[name] = src.get(f, {}).get("source", "")
print("%-20s <- %-16s %s" % (name, f, box))

old = {}
p = os.path.join(ASSETS, "photo_sources.json")
if os.path.exists(p):
    old = json.load(open(p, encoding="utf-8"))
old.update(credits)
json.dump(old, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\ncredits updated")
