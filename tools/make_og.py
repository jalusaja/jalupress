#!/usr/bin/env python3
"""Compose a 1200x630 Open Graph JPEG for a Jalu Press product.

This is a starting point. Always open the output and check that the title is
readable, then replace it with a tighter crop or a designed mockup if needed.
"""
import argparse, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
TEAL, CREAM, RUST, PAPER = (22, 52, 58), (246, 241, 231), (185, 85, 42), (246, 241, 231)
SPLIT = 520

SERIF = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/SourceSerifPro-Semibold.ttf"
SANS = "/usr/share/fonts/truetype/sand-box/custom/Source Sans Pro/SourceSansPro-Regular.ttf"
SANS_SB = "/usr/share/fonts/truetype/sand-box/custom/Source Sans Pro/SourceSansPro-Semibold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or [text]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--eyebrow", default="Jalu Press")
    ap.add_argument("--cover", required=True, help="Cover or mockup image")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    canvas = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, SPLIT, H], fill=TEAL)

    cover = Image.open(a.cover).convert("RGB")
    box_w, box_h, box_x, box_y = W - SPLIT - 64, H - 80, SPLIT + 32, 40
    scale = min(box_w / cover.size[0], box_h / cover.size[1])
    nw, nh = int(cover.size[0] * scale), int(cover.size[1] * scale)
    cover = cover.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(cover, (box_x + (box_w - nw) // 2, box_y + (box_h - nh) // 2))

    pad, max_w = 48, SPLIT - 96
    y = 70
    eyebrow = font(SANS_SB, 18)
    draw.text((pad, y), a.eyebrow.upper(), font=eyebrow, fill=RUST)
    y += 40
    title_f = font(SERIF, 52)
    for line in wrap(draw, a.title, title_f, max_w):
        draw.text((pad, y), line, font=title_f, fill=PAPER)
        y += 62
    if a.subtitle:
        y += 10
        sub_f = font(SANS, 22)
        for line in wrap(draw, a.subtitle, sub_f, max_w):
            draw.text((pad, y), line, font=sub_f, fill=(207, 219, 216))
            y += 30

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "JPEG", quality=90, optimize=True, subsampling=0)
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("make_og:", e, file=sys.stderr)
        sys.exit(1)
