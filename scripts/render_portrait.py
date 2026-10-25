import glob
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from common import BAR_H, INK, STATIC, esc, panel, write

COLS, ROWS = 84, 54
CW, LH, FS = 4.0, 7.2, 6.8
PAD = 18
RAMP = " .'`:-~=+*icxsoS#%&@"


def load_photo():
    paths = [p for p in glob.glob("assets/photo.*") if p.lower().endswith((".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"))]
    if not paths:
        return None
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        pass
    return ImageOps.exif_transpose(Image.open(paths[0])).convert("RGB")


def from_photo(img):
    from rembg import new_session, remove

    rgba = np.array(remove(img, session=new_session("u2net_human_seg")))
    alpha = rgba[:, :, 3].astype(np.float32) / 255
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray).astype(np.float32) / 255

    fg = gray[alpha > 0.5]
    lo, hi = np.percentile(fg, 8), np.percentile(fg, 99.5)
    v = np.clip((gray - lo) / max(hi - lo, 1e-3), 0, 1) ** 0.75 * alpha

    mask = alpha > 0.5
    ys = np.where(mask.any(axis=1))[0]
    top, bottom = ys[0], ys[-1]
    upper = range(top, top + int((bottom - top) * 0.6) + 1)
    widths, centers = [], []
    for y in upper:
        xs = np.where(mask[y])[0]
        if len(xs):
            widths.append(xs[-1] - xs[0])
            centers.append((xs[0] + xs[-1]) / 2)
    head_w = float(np.median(widths))
    cx = float(np.median(centers[: max(1, len(centers) // 2)]))

    crop_w = head_w * 1.9
    crop_h = crop_w * (ROWS * LH) / (COLS * CW)
    x0, y0 = int(cx - crop_w / 2), int(top - head_w * 0.12)
    return crop(v, x0, y0, int(crop_w), int(crop_h))


def from_initials(text="SK"):
    img = Image.new("L", (900, 900), 0)
    try:
        font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 420)
    except OSError:
        font = ImageFont.load_default(size=420)
    d = ImageDraw.Draw(img)
    x = 20
    for ch in text:
        box = d.textbbox((0, 0), ch, font=font)
        d.text((x - box[0], 450 - (box[3] + box[1]) / 2), ch, fill=255, font=font)
        x += box[2] - box[0] + 60
    v = np.array(img, dtype=np.float32) / 255
    ys, xs = np.where(v > 0.5)
    bw = xs.max() - xs.min()
    crop_w = int(bw * 1.2)
    crop_h = int(crop_w * (ROWS * LH) / (COLS * CW))
    cx, cy = (xs.max() + xs.min()) // 2, (ys.max() + ys.min()) // 2
    return crop(v, cx - crop_w // 2, cy - crop_h // 2, crop_w, crop_h)


def crop(v, x0, y0, w, h):
    canvas = np.zeros((h, w), np.float32)
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + w, v.shape[1]), min(y0 + h, v.shape[0])
    canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = v[sy0:sy1, sx0:sx1]
    return cv2.resize(canvas, (COLS, ROWS), interpolation=cv2.INTER_AREA)


def to_svg(grid, title):
    W = int(PAD * 2 + COLS * CW)
    H = int(BAR_H + PAD + ROWS * LH + PAD)
    defs, rows = [], []
    for r in range(ROWS):
        line = "".join(RAMP[int(round(min(max(x, 0), 1) * (len(RAMP) - 1)))] for x in grid[r])
        y = BAR_H + PAD + (r + 1) * LH - 2
        runs, c = [], 0
        while c < COLS:
            if line[c] == " ":
                c += 1
                continue
            s = c
            while c < COLS and line[c] != " ":
                c += 1
            seg = line[s:c]
            runs.append(
                f'<text x="{PAD + s * CW:.1f}" y="{y:.1f}" textLength="{len(seg) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{esc(seg)}</text>'
            )
        if not runs:
            continue
        if STATIC:
            rows.append("".join(runs))
        else:
            begin = 0.2 + r * 0.045
            defs.append(
                f'<clipPath id="r{r}"><rect x="{PAD}" y="{y - LH + 1:.1f}" width="0" height="{LH + 1}">'
                f'<animate attributeName="width" from="0" to="{COLS * CW:.1f}" begin="{begin:.3f}s" dur="0.22s" fill="freeze"/></rect></clipPath>'
            )
            rows.append(f'<g clip-path="url(#r{r})">{"".join(runs)}</g>')
    body = f'<defs>{"".join(defs)}</defs><g font-size="{FS}" fill="{INK}">{"".join(rows)}</g>'
    return panel(W, H, title, body)


img = load_photo()
if img is None:
    print("no assets/photo.* found, rendering initials placeholder", file=sys.stderr)
    grid = from_initials()
else:
    grid = from_photo(img)
write("ascii-portrait.svg", to_svg(grid, "~/portrait.txt"))
