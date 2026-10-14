# -*- coding: utf-8 -*-
"""Crop the chosen photos to the card slot (3:4 portrait) and record their sources."""
import os, json
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "build", "photos")
ASSETS = os.path.join(HERE, "assets")

# asset name -> photo file, vertical bias, horizontal bias (0 = left, .5 = centre)
PICKS = [
    ("card_wall.jpg",    "wall_05.jpg",    0.50, 0.50),
    ("card_muslim.jpg",  "hmj_07.jpg",     0.50, 0.78),
    ("card_datang.jpg",  "huimin_02.jpg",  0.50, 0.50),
]

manifest = json.load(open(os.path.join(SRC, "sources.json"), encoding="utf-8"))
out = {}
for name, src, bias, xbias in PICKS:
    im = Image.open(os.path.join(SRC, src)).convert("RGB")
    w, h = im.size
    tw = int(round(h * 0.75))
    if tw <= w:
        x0 = int((w - tw) * xbias)
        box = (x0, 0, x0 + tw, h)
    else:                                  # portrait source: crop top/bottom
        th = int(round(w / 0.75))
        y0 = int((h - th) * bias)
        box = (0, y0, w, y0 + th)
    im = im.crop(box).resize((720, 960), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    im.save(os.path.join(ASSETS, name), quality=89, optimize=True)
    out[name] = manifest.get(src, {}).get("source", "")
    print("%-18s <- %-16s %s  %.0f KB" % (name, src, box,
          os.path.getsize(os.path.join(ASSETS, name)) / 1024))
    print("     source: %s" % out[name][:96])

with open(os.path.join(ASSETS, "photo_sources.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
