# -*- coding: utf-8 -*-
"""Prepare 3:4 photos for the three 'who made it' cards on page 6."""
import os, json
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "build", "pool")
PHOTOS = os.path.join(HERE, "build", "photos")
ASSETS = os.path.join(HERE, "assets")

PICKS = [
    ("bld_pit.jpg",    POOL,   "pit_07.jpg",     0.50, 0.50),   # Terracotta pit
    ("bld_wall.jpg",   PHOTOS, "huimin_05.jpg",  0.50, 0.50),   # Ming city wall
    ("bld_pagoda.jpg", PHOTOS, "pagoda_00.jpg",  0.34, 0.50),   # Big Wild Goose Pagoda
]

credits = {}
old = {}
p = os.path.join(ASSETS, "photo_sources.json")
if os.path.exists(p):
    old = json.load(open(p, encoding="utf-8"))
src = {}
for d in (POOL, PHOTOS):
    f = os.path.join(d, "sources.json")
    if os.path.exists(f):
        src.update(json.load(open(f, encoding="utf-8")))

for name, folder, f, yb, xb in PICKS:
    im = Image.open(os.path.join(folder, f)).convert("RGB")
    w, h = im.size
    want = 0.75
    if w / float(h) > want:                 # landscape: trim the sides
        nw = int(h * want)
        x0 = int((w - nw) * xb)
        box = (x0, 0, x0 + nw, h)
    else:                                   # portrait: trim top and bottom
        nh = int(w / want)
        y0 = int((h - nh) * yb)
        box = (0, y0, w, y0 + nh)
    im = im.crop(box).resize((580, 773), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.05)
    im = ImageEnhance.Brightness(im).enhance(1.04)
    im.save(os.path.join(ASSETS, name), quality=88, optimize=True)
    credits[name] = src.get(f, {}).get("source", "")
    print("%-18s <- %-16s %s  %.0f KB" % (name, f, box,
          os.path.getsize(os.path.join(ASSETS, name)) / 1024))

old.update(credits)
json.dump(old, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("credits updated")
