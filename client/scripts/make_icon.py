"""Generate Server Monitor app icon (PNG + multi-size ICO)."""
import os
import math

from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "resources")


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def make_icon(size):
    # rounded-square base
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    radius = int(size * 0.22)
    pad = int(size * 0.045)

    # gradient background: #0a84ff (top) -> #00307a (bottom)
    top = (10, 132, 255)
    bottom = (0, 48, 122)
    grad = Image.new("RGBA", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / max(size - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        gd.line([(0, y), (size, y)], fill=c)

    mask = rounded_mask(size, radius)
    img.paste(grad, (0, 0), mask)

    # subtle inner ring highlight
    d = ImageDraw.Draw(img)
    ring = ImageDraw.Draw(img)
    ring_width = max(2, int(size * 0.02))
    ring.rounded_rectangle(
        [pad, pad, size - 1 - pad, size - 1 - pad],
        radius=radius - int(pad),
        outline=(255, 255, 255, 40),
        width=ring_width,
    )

    # center monitor / server panel
    panel_w = int(size * 0.58)
    panel_h = int(size * 0.42)
    px = (size - panel_w) // 2
    py = int(size * 0.20)
    panel_radius = int(panel_w * 0.10)
    panel = ImageDraw.Draw(img)
    panel.rounded_rectangle(
        [px, py, px + panel_w, py + panel_h],
        radius=panel_radius,
        fill=(255, 255, 255, 235),
    )

    # status bars inside panel (server rack)
    n_bars = 4
    bar_w = max(2, int(panel_w * 0.07))
    gap = int(panel_w * 0.09)
    start_x = px + int(panel_w * 0.16)
    bar_y = py + int(panel_h * 0.28)
    bar_h = max(3, int(panel_h * 0.14))
    bar_colors = [(0, 122, 255, 255), (52, 199, 89, 255), (0, 122, 255, 255), (52, 199, 89, 255)]
    for i in range(n_bars):
        bx = start_x + i * (bar_w + gap)
        panel.rounded_rectangle(
            [bx, bar_y, bx + bar_w, bar_y + bar_h],
            radius=bar_w // 2,
            fill=bar_colors[i],
        )

    # waveform line (CPU/mem trend) on lower half of panel
    wave_y = bar_y + int(panel_h * 0.42)
    wave_pts = []
    for i in range(41):
        t = i / 40
        x = px + int(panel_w * 0.16) + t * (panel_w - int(panel_w * 0.32))
        base = wave_y
        amp = int(panel_h * 0.20)
        y = base - int(amp * (0.5 + 0.5 * math.sin(t * math.tau * 1.5 + math.pi * 0.4)))
        wave_pts.append((x, y))
    line_w = max(2, int(size * 0.035))
    if len(wave_pts) > 1:
        panel.line(wave_pts, fill=(0, 48, 122, 255), width=line_w, joint="curve")

    # online dot top-right of panel
    dot_r = max(4, int(size * 0.045))
    dot_x = px + panel_w - int(panel_w * 0.18)
    dot_y = py + int(panel_h * 0.22)
    panel.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=(52, 199, 89, 255),
        outline=(255, 255, 255, 255),
        width=max(1, int(size * 0.01)),
    )

    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    png_path = os.path.join(OUT_DIR, "icon.png")
    make_icon(256).save(png_path)
    print("PNG:", png_path)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_path = os.path.join(OUT_DIR, "icon.ico")
    make_icon(256).save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
    )
    print("ICO:", ico_path)


if __name__ == "__main__":
    main()
