# -*- coding: utf-8 -*-
"""Find the horizontal hairlines in a rendered page and compare with design intent."""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1]
dpi = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0

im = Image.open(path).convert("L")
a = np.asarray(im, dtype=np.float32)
H, W = a.shape
print("image %dx%d px, assumed %.0f dpi -> %.3f x %.3f in"
      % (W, H, dpi, W / dpi, H / dpi))

# a hairline row = a row that is clearly darker than its neighbours, across most of the width
rowmean = a[:, int(W * 0.10):int(W * 0.90)].mean(axis=1)
bg = np.median(rowmean)
dips = []
for y in range(2, H - 2):
    if rowmean[y] < bg - 6 and rowmean[y] <= rowmean[y - 1] and rowmean[y] <= rowmean[y + 1]:
        dips.append((y, round(bg - rowmean[y], 1)))

# merge consecutive
merged = []
for y, d in dips:
    if merged and y - merged[-1][0] <= 3:
        if d > merged[-1][1]:
            merged[-1] = (y, d)
    else:
        merged.append((y, d))

print("detected dark rows (y_px, depth, y_in):")
for y, d in merged:
    if d > 7:
        print("   y=%4d  depth=%5.1f   y_in=%.3f" % (y, d, y / dpi))
