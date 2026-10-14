# -*- coding: utf-8 -*-
"""Generate flat, vector-style art assets for the Xi'an deck (no stock photos)."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
os.makedirs(ASSETS, exist_ok=True)

# ---- palette (kept in sync with build_deck.py) ----
INK        = (23, 25, 34)
PAPER      = (247, 242, 233)
PAPER2     = (239, 230, 215)
PAPER_LINE = (214, 201, 180)
CLAY       = (192, 92, 60)
CLAY_DEEP  = (154, 69, 39)
GOLD       = (199, 154, 69)
JADE       = (62, 124, 105)
SLATE      = (92, 100, 112)
MUTED      = (122, 114, 102)
VERM       = (195, 58, 46)

FDIR = r"C:\Windows\Fonts"
def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

GEO   = lambda s: font("georgia.ttf", s)
GEOB  = lambda s: font("georgiab.ttf", s)
SEGOE = lambda s: font("segoeui.ttf", s)
SEGOEB= lambda s: font("segoeuib.ttf", s)
YH    = lambda s: font("msyh.ttc", s)
YHB   = lambda s: font("msyhbd.ttc", s)

def save(img, name):
    p = os.path.join(ASSETS, name)
    img.save(p)
    print("%-24s %s" % (name, img.size))

# =====================================================================
# 1. radial glow (clay) for the dark cover / closing slides
# =====================================================================
def make_glow():
    S = 1400
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    cx, cy = S * 0.5, S * 0.5
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (S * 0.5)
    a = np.clip(1.0 - r, 0, 1) ** 2.4
    img = np.zeros((S, S, 4), dtype=np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = CLAY
    img[..., 3] = (a * 255).astype(np.uint8)
    save(Image.fromarray(img, "RGBA"), "glow_clay.png")

    img2 = np.zeros((S, S, 4), dtype=np.uint8)
    img2[..., 0], img2[..., 1], img2[..., 2] = GOLD
    img2[..., 3] = (a * 255 * 0.8).astype(np.uint8)
    save(Image.fromarray(img2, "RGBA"), "glow_gold.png")

# =====================================================================
# 2. seamless tiles: film grain + brick bond
# =====================================================================
def make_tiles():
    rng = np.random.default_rng(20261009)
    T = 256
    n = rng.normal(0, 1, (T, T))
    n = np.clip(n, -2.1, 2.1) / 2.1
    alpha = (np.abs(n) * 26).astype(np.uint8)
    for col, name in (((46, 38, 30), "tex_grain_dark.png"), ((255, 250, 240), "tex_grain_light.png")):
        img = np.zeros((T, T, 4), dtype=np.uint8)
        img[..., 0], img[..., 1], img[..., 2] = col
        img[..., 3] = alpha
        save(Image.fromarray(img, "RGBA"), name)

    # running-bond brick, mortar lines drawn as hairlines
    for col, name in (((255, 245, 230), "tex_brick_light.png"), ((70, 58, 46), "tex_brick_dark.png")):
        img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        c = col + (26,)
        bh, bw = 32, 64
        for row in range(T // bh + 1):
            y = row * bh
            d.line([(0, y), (T, y)], fill=c, width=2)
            off = 0 if row % 2 == 0 else bw // 2
            for x in range(-bw, T + bw, bw):
                d.line([(x + off, y), (x + off, y + bh)], fill=c, width=2)
        save(img, name)

# =====================================================================
# 3. location art: graticule + Silk Road route with named stops
# =====================================================================
def _smooth(points, samples=18):
    """Catmull-Rom spline through the points, returned as a dense polyline."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(samples):
            t = j / float(samples)
            t2, t3 = t * t, t * t * t
            out.append((
                0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(pts[-2])
    return out


def _dashed(d, pts, fill, width, dash=20.0, gap=13.0):
    """Dashed line along a polyline, with even dash spacing across corners."""
    on, left, cur = True, dash, pts[0]
    for nxt in pts[1:]:
        while True:
            dx, dy = nxt[0] - cur[0], nxt[1] - cur[1]
            seg = math.hypot(dx, dy)
            if seg < 1e-9:
                break
            step = min(left, seg)
            t = step / seg
            end = (cur[0] + dx * t, cur[1] + dy * t)
            if on:
                d.line([cur, end], fill=fill, width=width)
            cur = end
            left -= step
            if left <= 1e-9:
                on = not on
                left = dash if on else gap
            if step >= seg - 1e-9:
                break


def make_map():
    """A real, if very simplified, map: every place sits at its true
    latitude and longitude on an equirectangular grid."""
    W, H = 1900, 1180
    LON0, LON1 = 62.0, 122.0
    LAT0, LAT1 = 20.0, 50.0
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(lon, lat):
        return ((lon - LON0) / (LON1 - LON0) * W,
                (LAT1 - lat) / (LAT1 - LAT0) * H)

    def poly(lonlats):
        return [P(a, b) for a, b in lonlats]

    def lab(text, x, y, font, fill, align="center"):
        w = d.textlength(text, font=font)
        if align == "center":
            d.text((x - w / 2.0, y), text, font=font, fill=fill)
        elif align == "right":
            d.text((x - w, y), text, font=font, fill=fill)
        else:
            d.text((x, y), text, font=font, fill=fill)

    def inside(pt, pg):
        x, y = pt
        c = False
        n = len(pg)
        for i in range(n):
            x1, y1 = pg[i]
            x2, y2 = pg[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
        return c

    def ridge(lonlats, size=8, gap=27, col=(198, 184, 161, 235)):
        pts = poly(lonlats)
        carry = 0.0
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            L = math.hypot(x2 - x1, y2 - y1)
            t = carry
            while L and t <= L:
                f = t / L
                x, y = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
                d.polygon([(x, y - size), (x - size * 0.85, y + size * 0.55),
                           (x + size * 0.85, y + size * 0.55)], fill=col)
                t += gap
            carry = t - L

    # ---- coordinate grid: a line every 5 degrees, a number every 10 ----
    GRID = PAPER_LINE + (70,)
    for lon in range(65, 125, 5):
        x = P(lon, 0)[0]
        d.line([(x, 0), (x, H)], fill=GRID, width=2)
    for lat in range(25, 50, 5):
        y = P(0, lat)[1]
        d.line([(0, y), (W, y)], fill=GRID, width=2)
    for lon in range(70, 125, 10):
        x = P(lon, 0)[0]
        lab("%d\u00b0E" % lon, x, 6, SEGOE(20), MUTED + (200,))
        lab("%d\u00b0E" % lon, x, H - 28, SEGOE(20), MUTED + (200,))
    for lat in (30, 40):
        y = P(0, lat)[1]
        lab("%d\u00b0N" % lat, 10, y - 26, SEGOE(20), MUTED + (200,), "left")
        lab("%d\u00b0N" % lat, W - 10, y - 26, SEGOE(20), MUTED + (200,), "right")

    # ---- land, drawn as terrain rather than borders ----
    TER = (203, 190, 169) + (255,)
    DUNE = (206, 193, 172) + (205,)
    for pg in (poly([(78.0, 41.2), (81.0, 41.6), (84.5, 41.3), (87.5, 40.6),
                     (88.5, 39.5), (87.5, 38.3), (85.0, 37.2), (82.0, 36.8),
                     (79.5, 37.3), (78.0, 38.5), (77.5, 40.0)]),
               poly([(97, 44.5), (103, 45.5), (109, 45.0), (112, 43.5),
                     (110, 42.0), (105, 41.5), (100, 42.0), (97, 43.0)])):
        xs = [p[0] for p in pg]
        ys = [p[1] for p in pg]
        for gx in range(int(min(xs)), int(max(xs)) + 1, 25):
            for gy in range(int(min(ys)), int(max(ys)) + 1, 25):
                px = gx + ((gx * 7 + gy * 13) % 13) - 6
                py = gy + ((gx * 11 + gy * 5) % 13) - 6
                if inside((px, py), pg):
                    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=DUNE)
    ridge([(69, 42.2), (74, 42.9), (79, 42.6), (84, 42.9), (89, 43.2)])       # Tian Shan
    ridge([(71.5, 38.6), (73.5, 38.0), (75.5, 38.4)], size=7, gap=22)          # Pamir
    ridge([(78, 36.0), (83, 35.8), (88, 36.2), (92, 36.6)], size=7, gap=24)    # Kunlun
    ridge([(80, 28.6), (85, 28.0), (90, 28.0), (95, 28.4)])                    # Himalaya

    lab("TAKLAMAKAN DESERT", *P(82.5, 39.4), font=SEGOEB(19), fill=TER)
    lab("GOBI DESERT", *P(104, 43.4), font=SEGOEB(19), fill=TER)
    lab("TIAN SHAN", *P(71.5, 43.6), font=SEGOEB(19), fill=TER)
    lab("HIMALAYAS", *P(87.5, 27.2), font=SEGOEB(19), fill=TER)
    for name, lon, lat, fs in (("CHINA", 100.0, 33.5, 30), ("MONGOLIA", 105.0, 46.6, 26),
                               ("KAZAKHSTAN", 70.0, 48.4, 26), ("INDIA", 78.0, 22.0, 28)):
        f = SEGOEB(fs)
        w = d.textlength(name, font=f) + (len(name) - 1) * fs * 0.18
        x, y = P(lon, lat)
        d.text((x - w / 2.0, y), " ".join(name), font=f, fill=(212, 199, 178, 255))

    # ---- the road: Chang'an west, splitting round the Tarim Basin ----
    xian      = P(108.94, 34.26)
    luoyang   = P(112.45, 34.62)
    lanzhou   = P(103.83, 36.06)
    dunhuang  = P(94.66, 40.14)
    turpan    = P(89.19, 42.95)
    hotan     = P(79.93, 37.11)
    kashgar   = P(75.99, 39.47)
    samarkand = P(66.96, 39.65)
    road_end  = P(63.8, 41.0)

    GOLDL = GOLD + (215,)
    # east of Chang'an the road ran on to Luoyang, through Hangu Pass
    _dashed(d, _smooth([luoyang, P(112.10, 34.72), P(110.30, 34.55), xian]), GOLDL, 6)
    _dashed(d, _smooth([xian, lanzhou, dunhuang]), GOLDL, 6)
    _dashed(d, _smooth([dunhuang, turpan, kashgar]), GOLDL, 6)
    _dashed(d, _smooth([dunhuang, hotan, kashgar]), GOLDL, 6)
    west = _smooth([kashgar, samarkand, road_end])
    _dashed(d, west, GOLDL, 6)

    (ax, ay), (bx, by) = west[-4], west[-1]
    vx, vy = bx - ax, by - ay
    leng = math.hypot(vx, vy) or 1.0
    ux, uy = vx / leng, vy / leng
    nx, ny = -uy, ux
    tip = (bx + ux * 8, by + uy * 8)
    d.polygon([tip,
               (tip[0] - ux * 36 + nx * 13, tip[1] - uy * 36 + ny * 13),
               (tip[0] - ux * 36 - nx * 13, tip[1] - uy * 36 - ny * 13)],
              fill=GOLD + (255,))

    # ---- stops: a paper disc breaks the dash, then the marker ----
    for (px, py), r, col in ((luoyang, 11, SLATE), (lanzhou, 11, SLATE), (dunhuang, 11, SLATE),
                             (kashgar, 12, SLATE), (samarkand, 12, SLATE),
                             (turpan, 8, MUTED), (hotan, 8, MUTED)):
        d.ellipse([px - r - 6, py - r - 6, px + r + 6, py + r + 6], fill=PAPER + (255,))
        d.ellipse([px - r, py - r, px + r, py + r], fill=col + (255,))

    lab("LANZHOU",  lanzhou[0] - 14, lanzhou[1] + 40, SEGOEB(26), SLATE + (255,))
    lab("DUNHUANG", dunhuang[0] + 20, dunhuang[1] - 38, SEGOEB(26), SLATE + (255,), "left")
    lab("TURPAN",   turpan[0], turpan[1] - 46, SEGOEB(24), MUTED + (255,))
    lab("HOTAN",    hotan[0] - 28, hotan[1] - 10, SEGOEB(24), MUTED + (255,), "right")
    lab("KASHGAR",  kashgar[0], kashgar[1] - 48, SEGOEB(28), SLATE + (255,))
    lab("SAMARKAND", samarkand[0], samarkand[1] - 48, SEGOEB(28), SLATE + (255,))
    lab("LUOYANG",  luoyang[0] - 28, luoyang[1] + 45, SEGOEB(26), SLATE + (255,), "left")

    # ---- route title ----
    d.line([(100, 158), (146, 158)], fill=GOLD + (255,), width=6)
    d.text((170, 134), "THE SILK ROAD", font=SEGOEB(34), fill=GOLD + (255,))
    d.text((100, 190), "Luoyang  \u00b7  Chang'an  \u2192  Persia  \u00b7  Rome", font=SEGOE(25),
           fill=MUTED + (255,))
    for i, line in enumerate(("The route split in two to avoid the desert,",
                              "and the two parts met again at Kashgar.",
                              "East of Xi'an it also reached Luoyang.")):
        d.text((70, 972 + i * 34), line, font=SEGOE(23), fill=MUTED + (230,))

    # ---- scale bar: 1,000 km at this latitude ----
    km = 1000.0 / (111.32 * math.cos(math.radians(35.0)))
    bar = km / (LON1 - LON0) * W
    sx, sy = W - 120 - bar, H - 96
    d.line([(sx, sy), (sx + bar, sy)], fill=SLATE + (230,), width=5)
    for i in (0, 0.5, 1.0):
        d.line([(sx + bar * i, sy - 11), (sx + bar * i, sy + 11)], fill=SLATE + (230,), width=4)
    lab("0", sx, sy + 20, SEGOE(20), MUTED + (230,))
    lab("1,000 km", sx + bar, sy + 20, SEGOE(20), MUTED + (230,))

    # ---- Xi'an: the anchor node ----
    for rr, al in ((74, 60), (52, 110), (32, 170)):
        d.ellipse([xian[0] - rr, xian[1] - rr, xian[0] + rr, xian[1] + rr],
                  outline=CLAY + (al,), width=4)
    d.ellipse([xian[0] - 21, xian[1] - 21, xian[0] + 21, xian[1] + 21], fill=CLAY + (255,))
    d.text((xian[0] + 118, xian[1] - 80), "XI'AN", font=GEOB(58), fill=INK + (255,))
    d.text((xian[0] + 138, xian[1] - 10), "34.26\u00b0N  108.94\u00b0E",
           font=SEGOE(28), fill=MUTED + (255,))

    # ---- other cities, for reference ----
    for (lon, lat, name, dist) in ((116.41, 39.90, "BEIJING", "1,200 km NE"),
                                   (121.47, 31.23, "SHANGHAI", "1,500 km E")):
        cx, cy = P(lon, lat)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=SLATE + (255,))
        lab(name, cx - 26, cy - 52, SEGOEB(28), SLATE + (255,), "right")
        lab(dist, cx - 26, cy - 8, SEGOE(25), MUTED + (255,), "right")
    for (lon, lat, name, dist) in ((104.07, 30.57, "CHENGDU", "700 km SW"),
                                   (91.14, 29.65, "LHASA", "2,600 km W"),
                                   (77.21, 28.61, "DELHI", "3,400 km SW")):
        cx, cy = P(lon, lat)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=SLATE + (170,))
        d.text((cx + 22, cy - 16), name, font=SEGOEB(26), fill=SLATE + (200,))
        d.text((cx + 22, cy + 18), dist, font=SEGOE(23), fill=MUTED + (200,))

    # ---- compass ----
    ox, oy = 1150, 1010
    d.line([(ox, oy - 56), (ox, oy + 56)], fill=SLATE + (230,), width=5)
    d.line([(ox - 56, oy), (ox + 56, oy)], fill=SLATE + (120,), width=3)
    d.polygon([(ox, oy - 74), (ox - 15, oy - 46), (ox + 15, oy - 46)], fill=CLAY + (255,))
    d.text((ox - 11, oy - 132), "N", font=GEOB(34), fill=INK + (255,))

    save(img, "art_map.png")

# =====================================================================
# 4. flat glyphs, drawn in a 100x100 space then upscaled
# =====================================================================
def glyph(name, draw_fn, size=560, color=CLAY):
    S = 1000
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = S / 100.0
    def R(x0, y0, x1, y1, **kw):
        d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], **kw)
    def E(x0, y0, x1, y1, **kw):
        d.ellipse([x0 * k, y0 * k, x1 * k, y1 * k], **kw)
    def L(pts, **kw):
        d.line([(x * k, y * k) for x, y in pts], **kw)
    def P(pts, **kw):
        d.polygon([(x * k, y * k) for x, y in pts], **kw)
    draw_fn(R, E, L, P, d, k, color)
    img = img.resize((size, size), Image.LANCZOS)
    save(img, name)

def wall_glyph(R, E, L, P, d, k, C):
    R(6, 52, 94, 90, fill=C)
    for i in range(7):                       # merlons
        x = 6 + i * 12.6
        R(x, 42, x + 8, 52, fill=C)
    R(38, 66, 62, 90, fill=(0, 0, 0, 0))     # gate opening
    E(38, 54, 62, 78, fill=(0, 0, 0, 0))
    L([(0, 90), (100, 90)], fill=C, width=int(3 * k))

def pagoda_glyph(R, E, L, P, d, k, C):
    R(30, 88, 70, 94, fill=C)                # platform
    tiers = [(24, 40, 72, 82), (30, 33, 62, 68), (35, 26, 55, 54), (40, 19, 50, 41), (44, 12, 46, 29)]
    for (bw, y0, bw2, y1) in tiers:
        half0 = (bw2 - bw) / 2 + (50 - bw) / 1  # not used; build symmetric below
    widths = [26, 22, 18, 14, 10]
    ys = [(82, 66), (66, 52), (52, 38), (38, 25), (25, 13)]
    for w, (y1, y0) in zip(widths, ys):
        R(50 - w / 2, y0, 50 + w / 2, y1, fill=C)
        R(50 - w / 2 - 4, y0 - 3, 50 + w / 2 + 4, y0 + 1.5, fill=C)   # eave
    L([(50, 13), (50, 4)], fill=C, width=int(3 * k))
    E(46.5, 0.5, 53.5, 7.5, fill=C)

def route_glyph(R, E, L, P, d, k, C):
    arc = []
    for i in range(121):
        t = i / 120.0
        x = 6 + 88 * t
        y = 66 - 34 * math.sin(math.pi * t) - 14 * t
        arc.append((x, y))
    step = 0
    while step < len(arc) - 9:
        L([arc[step], arc[step + 9]], fill=C, width=int(3.4 * k))
        step += 17
    for i in (0, 60, 120):
        x, y = arc[i]
        E(x - 5.5, y - 5.5, x + 5.5, y + 5.5, fill=C)
    E(85, 12, 97, 24, outline=C, width=int(3 * k))

def bowl_glyph(R, E, L, P, d, k, C):
    P([(16, 44), (84, 44), (74, 74), (26, 74)], fill=C)
    R(38, 74, 62, 79, fill=C)
    R(28, 79, 72, 84, fill=C)
    # steam
    for x0 in (33, 50, 67):
        pts = [(x0, 34), (x0 + 4, 27), (x0, 20), (x0 + 4, 13)]
        L(pts, fill=C, width=int(3 * k), joint="curve")

def crowdb_glyph(R, E, L, P, d, k, C):
    for i, (cx, sc) in enumerate(((22, 1.0), (50, 1.18), (78, 1.0))):
        E(cx - 7 * sc, 22 - 6 * sc, cx + 7 * sc, 36 + 2 * sc, fill=C)
        P([(cx - 13 * sc, 84), (cx - 10 * sc, 44), (cx + 10 * sc, 44), (cx + 13 * sc, 84)], fill=C)

def warrior_glyph(R, E, L, P, d, k, C):
    """A single robed terracotta soldier, front on."""
    E(47, 2, 53, 8.5, fill=C)                       # topknot
    R(43, 8, 57, 23, fill=C)                        # head
    P([(34, 25), (66, 25), (68, 32), (32, 32)], fill=C)     # shoulders
    R(30, 31, 37, 60, fill=C)                       # arms
    R(63, 31, 70, 60, fill=C)
    P([(37, 30), (63, 30), (62, 58), (38, 58)], fill=C)     # torso
    P([(38, 56), (62, 56), (69, 88), (31, 88)], fill=C)     # robe
    R(26, 88, 74, 93, fill=C)                       # base

# =====================================================================
# 4b. Pen: draw a Xi'an landmark in a 0-100 design box mapped onto any
#     rect, so the same drawing serves a small card glyph and the big
#     cover skyline.
# =====================================================================
CLEAR = (0, 0, 0, 0)


class Pen(object):
    def __init__(self, d, box, color):
        self.d = d
        self.x, self.y, self.w, self.h = box
        self.c = color

    def _pt(self, px, py):
        return (self.x + px / 100.0 * self.w, self.y + py / 100.0 * self.h)

    def rect(self, x0, y0, x1, y1, fill=None):
        self.d.rectangle([self._pt(x0, y0), self._pt(x1, y1)],
                         fill=self.c if fill is None else fill)

    def ell(self, x0, y0, x1, y1, fill=None):
        self.d.ellipse([self._pt(x0, y0), self._pt(x1, y1)],
                       fill=self.c if fill is None else fill)

    def poly(self, pts, fill=None):
        self.d.polygon([self._pt(a, b) for a, b in pts],
                       fill=self.c if fill is None else fill)

    def line(self, pts, width):
        self.d.line([self._pt(a, b) for a, b in pts], fill=self.c,
                    width=max(1, int(width)))


def _quad(p0, p1, p2, n=9):
    """quadratic bezier sample points"""
    out = []
    for i in range(n + 1):
        t = i / float(n)
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]))
    return out


def _cn_roof(p, xl, xr, ytop, ybot, flare=0.15):
    """Chinese roof silhouette: narrow ridge, wide eave whose corners sweep up."""
    w = xr - xl
    inset = w * 0.18
    rise = w * flare
    r_tip = (xr, ybot - rise)
    l_tip = (xl, ybot - rise)
    pts = [(xl + inset, ytop), (xr - inset, ytop), r_tip]
    pts += _quad(r_tip, (xr - w * 0.20, ybot), (xr - w * 0.30, ybot))
    pts.append((xl + w * 0.30, ybot))
    pts += _quad((xl + w * 0.30, ybot), (xl + w * 0.20, ybot), l_tip)
    p.poly(pts)


def _gate(p, x0, x1, ytop, ybot):
    """arched opening cut out of a brick podium"""
    p.rect(x0, (ytop + ybot) / 2.0, x1, ybot, fill=CLEAR)
    p.ell(x0, ytop, x1, ytop + (x1 - x0))


def draw_belltower(p):
    """Xi'an Bell Tower - slender square tower, two roofs, arched podium."""
    p.ell(47.0, 0.0, 53.0, 5.0)
    p.rect(49.0, 4.0, 51.0, 13.0)
    _cn_roof(p, 33, 67, 12, 25)
    p.rect(42, 24, 58, 40)
    p.rect(35, 36, 65, 40)
    _cn_roof(p, 24, 76, 38, 53)
    p.rect(29, 52, 71, 95)
    _gate(p, 42, 58, 63, 95)
    p.line([(20, 96), (80, 96)], 4)


def draw_drumtower(p):
    """Xi'an Drum Tower - wider and lower, with an open gallery."""
    p.rect(45, 3, 55, 12)
    _cn_roof(p, 26, 74, 11, 26)
    p.rect(31, 25, 69, 44)
    for cx in (38, 50, 62):
        p.rect(cx - 3.6, 33, cx + 3.6, 41, fill=CLEAR)
        p.ell(cx - 3.6, 29, cx + 3.6, 36, fill=CLEAR)
    _cn_roof(p, 13, 87, 42, 59)
    p.rect(17, 58, 83, 95)
    _gate(p, 41, 59, 62, 95)
    p.line([(6, 96), (94, 96)], 4)


def draw_pagoda(p):
    """Big Wild Goose Pagoda - seven storeys and a finial."""
    p.rect(29, 92, 71, 97)
    y1 = 92.0
    for w in (30, 27, 24, 21, 18, 15, 12):
        y0 = y1 - 10.0
        p.rect(50 - w / 2.0, y0, 50 + w / 2.0, y1)
        p.rect(50 - w / 2.0 - 4, y0 - 2.2, 50 + w / 2.0 + 4, y0 + 0.9)
        y1 = y0 - 0.8
    p.line([(50, y1), (50, y1 - 6)], 4)
    p.ell(46.5, y1 - 13, 53.5, y1 - 6)


def draw_wall(p):
    """Crenellated Ming city wall with a gate."""
    p.rect(0, 46, 100, 94)
    for i in range(9):
        p.rect(i * 11.5, 33, i * 11.5 + 7, 46)
    p.rect(38, 74, 62, 94, fill=CLEAR)
    p.ell(38, 58, 62, 82, fill=CLEAR)
    p.line([(0, 95), (100, 95)], 4)


def draw_warrior(p):
    """A single robed terracotta soldier."""
    p.ell(47, 0, 53, 7)
    p.rect(43, 6, 57, 22)
    p.poly([(34, 24), (66, 24), (68, 31), (32, 31)])
    p.rect(30, 30, 37, 60)
    p.rect(63, 30, 70, 60)
    p.poly([(37, 29), (63, 29), (62, 58), (38, 58)])
    p.poly([(38, 56), (62, 56), (69, 90), (31, 90)])
    p.rect(26, 90, 74, 95)
    p.line([(22, 96), (78, 96)], 4)


def pen_glyph(name, drawer, size=560, color=CLAY, crop=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    drawer(Pen(d, (0, 0, size, size), color))
    if crop:
        bb = img.getbbox()
        if bb:
            pad = int(size * 0.012)
            img = img.crop((max(0, bb[0] - pad), max(0, bb[1] - pad),
                            min(size, bb[2] + pad), min(size, bb[3] + pad)))
    save(img, name)


def warriors_glyph(name, W=1400, H=760, color=CLAY):
    """A rank of three soldiers, the middle one closest."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for cx, s in ((250, 0.80), (700, 0.95), (1150, 0.80)):
        hd = H * s / 0.96
        yb = H - 0.96 * hd
        draw_warrior(Pen(d, (cx - hd / 2.0, yb, hd, hd), color))
    bb = img.getbbox()
    if bb:
        pad = 10
        img = img.crop((max(0, bb[0] - pad), max(0, bb[1] - pad),
                        min(W, bb[2] + pad), min(H, bb[3] + pad)))
    save(img, name)


def make_skyline(name="skyline.png", W=4200, H=530, base=508,
                 color=(255, 246, 232)):
    """One row of Xi'an landmarks standing on a shared ground line."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    C = color + (255,)
    d.rectangle([0, base, W, base + 8], fill=C)
    items = [
        (draw_wall,       300, 420),
        (draw_belltower,  980, 400),
        (draw_pagoda,    1720, 430),
        (draw_drumtower, 2480, 440),
        (draw_warrior,   3180, 400),
        (draw_wall,      3860, 400),
    ]
    for drawer, cx, h in items:
        drawer(Pen(d, (cx - h / 2.0, base - 0.96 * h, h, h), C))
    save(img, name)


# =====================================================================
# 5. full-bleed backgrounds: flat colour + fine grain + low-freq mottle
#    (baked as one image so PowerPoint and LibreOffice render it alike)
# =====================================================================
def _mottle(W, H, seed):
    rng = np.random.default_rng(seed)
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    fine = np.asarray(Image.fromarray(((fine * 42) + 128).clip(0, 255).astype(np.uint8), "L")
                      .filter(ImageFilter.GaussianBlur(0.7)), dtype=np.float32)
    fine = (fine - 128.0) / 42.0
    mott = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    mott = np.asarray(Image.fromarray(((mott * 40) + 128).clip(0, 255).astype(np.uint8), "L")
                      .resize((W, H), Image.BICUBIC)
                      .filter(ImageFilter.GaussianBlur(48)), dtype=np.float32)
    mott = (mott - 128.0) / 40.0
    return fine, mott

def _vignette(W, H, strength):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    r = np.sqrt(dx * dx + dy * dy) / math.sqrt(2.0)
    return (1.0 - np.clip(r, 0, 1) ** 2.2) * strength

def _glow_field(W, H, cx, cy, radius, strength):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - cx * W) ** 2 + (yy - cy * H) ** 2) / radius
    return (np.clip(1.0 - r, 0, 1) ** 2.6) * strength

def make_backgrounds(W=2200, H=1238):
    fine, mott = _mottle(W, H, 4242)

    def build(name, base, grain_amp, mottle_amp, glows=(), vig=0.0):
        base = np.array(base, dtype=np.float32)
        img = np.empty((H, W, 3), dtype=np.float32)
        for c in range(3):
            layer = np.full((H, W), base[c], dtype=np.float32)
            layer += fine * grain_amp + mott * mottle_amp
            for (gx, gy, gr, gs, gc) in glows:
                f = _glow_field(W, H, gx, gy, gr, gs)
                layer += f * (np.array(gc, dtype=np.float32)[c] - base[c])
            if vig:
                layer -= (1.0 - _vignette(W, H, 1.0)) * vig * 255.0 * 0.42
            img[..., c] = layer
        out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
        out.save(os.path.join(ASSETS, name), quality=84, optimize=True, subsampling=1)
        print("%-24s %s  %d KB" % (name, out.size, os.path.getsize(os.path.join(ASSETS, name)) // 1024))

    build("bg_paper.jpg", PAPER, 2.0, 3.4, vig=0.35)
    build("bg_paper_brick.jpg", PAPER2, 1.8, 3.0, vig=0.30)
    build("bg_ink.jpg", INK, 2.6, 4.2,
          glows=((0.16, 1.02, H * 0.95, 0.85, CLAY), (0.92, -0.05, H * 0.8, 0.30, GOLD)), vig=0.55)
    build("bg_ink_gold.jpg", INK, 2.6, 4.2,
          glows=((0.86, 0.10, H * 0.9, 0.55, GOLD), (0.10, 1.05, H * 0.8, 0.40, CLAY)), vig=0.55)
    build("bg_clay.jpg", CLAY_DEEP, 2.4, 4.0,
          glows=((0.80, 0.86, H * 1.0, 0.45, CLAY), (0.08, 0.05, H * 0.7, 0.25, GOLD)), vig=0.45)
    build("bg_slate.jpg", (43, 47, 58), 2.4, 4.0,
          glows=((0.90, 0.95, H * 0.9, 0.35, CLAY),), vig=0.50)

# =====================================================================
# 6. contact sheet for review
# =====================================================================
def contact_sheet(names):
    pad, cols = 26, 4
    thumbs = []
    for n in names:
        im = Image.open(os.path.join(ASSETS, n)).convert("RGBA")
        im.thumbnail((420, 420), Image.LANCZOS)
        thumbs.append((n, im))
    cw, ch = 460, 480
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + pad, rows * ch + pad), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x, y = pad + c * cw, pad + r * ch
        # checkerboard backdrop so transparency is visible
        for by in range(0, 400, 20):
            for bx in range(0, 400, 20):
                if (bx // 20 + by // 20) % 2 == 0:
                    d.rectangle([x + bx, y + by, x + bx + 20, y + by + 20], fill=(232, 228, 220))
        sheet.paste(im, (x + (400 - im.width) // 2, y + (400 - im.height) // 2), im)
        d.text((x, y + 412), n, font=SEGOE(22), fill=(40, 40, 40))
    save(sheet, "_contact_sheet.png")

if __name__ == "__main__":
    import sys as _sys
    only = _sys.argv[1] if len(_sys.argv) > 1 else "all"
    if only in ("all", "glow"):
        make_glow()
        make_tiles()
        make_map()
    if only in ("all", "bg"):
        make_backgrounds()
    if only in ("all", "glyphs"):
        glyph("glyph_wall.png",    wall_glyph)
        glyph("glyph_pagoda.png",  pagoda_glyph, color=CLAY_DEEP)
        glyph("glyph_route.png",   route_glyph,  color=GOLD)
        glyph("glyph_bowl.png",    bowl_glyph,   color=PAPER)
        glyph("glyph_bowl_dark.png", bowl_glyph, color=CLAY_DEEP)
        glyph("glyph_crowd.png",   crowdb_glyph, color=(196, 148, 120))
        glyph("glyph_warrior.png", warrior_glyph, color=CLAY)
        # --- Xi'an landmarks (Pen based, same flat style) ---
        pen_glyph("glyph_belltower.png",  draw_belltower,  color=CLAY)
        pen_glyph("glyph_belltower_gold.png", draw_belltower, color=GOLD)
        pen_glyph("glyph_drumtower.png",  draw_drumtower,  color=CLAY)
        pen_glyph("glyph_towerpage.png",  draw_pagoda,     color=CLAY_DEEP)
        pen_glyph("glyph_wallpen.png",    draw_wall,       color=CLAY)
        warriors_glyph("glyph_warriors.png")
        make_skyline()
    if only == "all":
        contact_sheet(["bg_paper.jpg", "bg_ink.jpg", "skyline.png",
                       "glyph_belltower.png", "glyph_drumtower.png",
                       "glyph_warriors.png", "glyph_wallpen.png",
                       "glyph_towerpage.png", "art_map.png",
                       "glyph_bowl_dark.png", "glyph_route.png"])
    print("assets written to", ASSETS)
