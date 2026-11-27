#!/usr/bin/env python3
"""Build the free email sample: 'The Home Starter Pack' (7 pages excerpted from five Jalu Press
planners + a one-page guide). Output: /workspace/ebook-store/products/_free-sample/Home-Starter-Pack.pdf
Also writes the three preview/cover images used on the /free/ page."""
import tempfile, subprocess
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

P = Path("/workspace/ebook-store/products")
HERE = Path(__file__).resolve().parent.parent
IMG = HERE / "docs" / "assets" / "img"
OUT = P / "_free-sample" / "Home-Starter-Pack.pdf"
FD = "/usr/share/fonts/truetype/sand-box/custom/"
SERIF = FD + "Source Serif Pro/SourceSerifPro-Semibold.ttf"
SANS = FD + "Source Sans Pro/SourceSansPro-Regular.ttf"
SANS_SB = FD + "Source Sans Pro/SourceSansPro-Semibold.ttf"
TEAL, CREAM, RUST = (22, 52, 58), (246, 241, 231), (185, 85, 42)

SRC = [
    ("grab-and-go-household-binder", "The-Grab-and-Go-Household-Binder-Letter.pdf", 6, "Household at a glance", "The Grab-and-Go Household Binder"),
    ("grab-and-go-household-binder", "The-Grab-and-Go-Household-Binder-Letter.pdf", 31, "Water and food planner (metric + imperial)", "The Grab-and-Go Household Binder"),
    ("grab-and-go-household-binder", "The-Grab-and-Go-Household-Binder-Letter.pdf", 32, "3-day home supplies checklist", "The Grab-and-Go Household Binder"),
    ("home-maintenance-planner-car-service-log", "The-Home-Maintenance-Planner-and-Car-Service-Log-Letter.pdf", 8, "Winter home checklist", "The Home Maintenance Planner & Car Service Log"),
    ("moving-day-relocation-planner", "The-Moving-Day-Planner-Letter.pdf", 3, "Moving timeline: 8 to 5 weeks before", "The Moving Day Planner & Relocation Checklist"),
    ("plan-ahead-meal-grocery-planner", "The-Plan-Ahead-Meal-and-Grocery-Planner-Letter.pdf", 8, "Weekly meal plan", "The Plan-Ahead Meal & Grocery Planner"),
    ("plan-ahead-meal-grocery-planner", "The-Plan-Ahead-Meal-and-Grocery-Planner-Letter.pdf", 9, "Grocery list sorted by store section", "The Plan-Ahead Meal & Grocery Planner"),
]


def guide(path):
    pdfmetrics.registerFont(TTFont("Serif", SERIF)); pdfmetrics.registerFont(TTFont("Sans", SANS)); pdfmetrics.registerFont(TTFont("SansSB", SANS_SB))
    W, H = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    teal, rust, ink, muted = HexColor("#16343a"), HexColor("#b9552a"), HexColor("#1f2a2c"), HexColor("#5b6668")
    c.setFillColor(teal); c.rect(0, H - 150, W, 150, fill=1, stroke=0)
    c.setFillColor(HexColor("#f0a77f")); c.setFont("SansSB", 11); c.drawString(54, H - 56, "JALU PRESS  ·  FREE SAMPLE")
    c.setFillColor(HexColor("#ffffff")); c.setFont("Serif", 30); c.drawString(54, H - 98, "The Home Starter Pack")
    c.setFillColor(HexColor("#cfdbd8")); c.setFont("Sans", 14); c.drawString(54, H - 124, "7 free, fillable pages to get your household in order")
    y = H - 190
    c.setFillColor(ink); c.setFont("Sans", 12)
    for ln in simpleSplit("Thanks for signing up. These pages are taken from five Jalu Press planners. Type into them on screen (Adobe Acrobat Reader is free) or print them and write by hand. Start with the one that matches the job in front of you this week.", "Sans", 12, W - 108):
        c.drawString(54, y, ln); y -= 17
    y -= 12
    c.setFillColor(teal); c.setFont("SansSB", 13); c.drawString(54, y, "What is in this pack"); y -= 22
    for i, (_, _, pg, name, src) in enumerate(SRC, 1):
        c.setFillColor(rust); c.setFont("SansSB", 11.5); c.drawString(54, y, "Page %d" % (i + 1))
        c.setFillColor(ink); c.setFont("SansSB", 11.5); c.drawString(112, y, name)
        c.setFillColor(muted); c.setFont("Sans", 10); c.drawString(112, y - 13, "from " + src)
        y -= 34
    y -= 6
    c.setFillColor(teal); c.setFont("SansSB", 13); c.drawString(54, y, "Want the full set?"); y -= 20
    c.setFillColor(ink); c.setFont("Sans", 11.5)
    for ln in simpleSplit("The Home & Household Starter Bundle has all five complete planners (142 fillable pages per paper size, plus spreadsheets) for $24 instead of $48. Pay once, keep the files for good, no subscription: jalupress.com/products/home-household-starter-bundle/", "Sans", 11.5, W - 108):
        c.drawString(54, y, ln); y -= 16
    c.setFillColor(muted); c.setFont("Sans", 9.5)
    for ln in simpleSplit("Personal and household license: print as many copies as your household needs. Please do not share, upload or resell the file. These pages are organizing tools, not legal, medical or emergency-services advice.", "Sans", 9.5, W - 108):
        pass
    yy = 78
    for ln in simpleSplit("Personal and household license: print as many copies as your household needs. Please do not share, upload or resell the file. These pages are organizing tools, not legal, medical or emergency-services advice.", "Sans", 9.5, W - 108):
        c.drawString(54, yy, ln); yy -= 12.5
    c.setFont("Sans", 9); c.drawString(54, 40, "Jalu Press  ·  jalupress.com")
    c.showPage(); c.save()


def main():
    tmp = Path(tempfile.mkdtemp())
    g = tmp / "guide.pdf"; guide(g)
    w = PdfWriter(); w.append(PdfReader(str(g)))
    total_fields = 0
    for slug, fn, pg, _, _ in SRC:
        r = PdfReader(str(P / slug / fn))
        w.append(r, pages=(pg - 1, pg))
    w.add_metadata({"/Title": "The Home Starter Pack (free sample)", "/Author": "Jalu Press"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "wb") as f:
        w.write(f)
    r = PdfReader(str(OUT))
    print("pages", len(r.pages), "fields", len(r.get_fields() or {}), OUT.stat().st_size)
    # images: cover composite from pages 3,4,6 (index)
    pngs = []
    for idx in (2, 4, 6):
        base = str(tmp / ("p%d" % idx))
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", str(idx), "-l", str(idx), "-singlefile", str(OUT), base], check=True)
        pngs.append(base + ".png")
    pages = [Image.open(p).convert("RGB") for p in pngs]
    def f(p, s): return ImageFont.truetype(p, s)
    def tile(img, ang):
        img = img.convert("RGBA"); pad = 30
        b = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(b).rectangle([pad + 8, pad + 12, pad + img.width + 8, pad + img.height + 12], fill=(22, 52, 58, 80))
        b.paste(img, (pad, pad)); return b.rotate(ang, expand=True, resample=Image.Resampling.BICUBIC)
    # cover 1600x1200 (used on /free/) and og
    cv = Image.new("RGB", (1600, 1200), TEAL); d = ImageDraw.Draw(cv); d.rectangle([760, 0, 1600, 1200], fill=CREAM)
    for i, (ang, dx, dy) in enumerate([(-7, 0, 120), (5, 190, 220), (-2, 340, 60)]):
        t = pages[i].resize((int(pages[i].width * 680 / pages[i].height), 680), Image.Resampling.LANCZOS)
        tl = tile(t, ang); cv.paste(tl, (730 + dx, dy), tl)
    d.text((70, 150), "JALU PRESS · FREE SAMPLE", font=f(SANS_SB, 30), fill=RUST)
    y = 230
    for ln in ["The Home", "Starter Pack"]:
        d.text((70, y), ln, font=f(SERIF, 78), fill=CREAM); y += 94
    y += 14
    for ln in ["7 free fillable pages:", "emergency, home, moving", "and meal planning"]:
        d.text((70, y), ln, font=f(SANS, 40), fill=(207, 219, 216)); y += 54
    d.rounded_rectangle([70, y + 50, 330, y + 180], radius=22, fill=RUST)
    d.text((104, y + 66), "FREE", font=f(SERIF, 84), fill=(255, 255, 255))
    cv.save(IMG / "free-home-starter-pack-cover.webp", "WEBP", quality=88)
    cv.resize((800, 600), Image.Resampling.LANCZOS).save(IMG / "free-home-starter-pack-cover-800.webp", "WEBP", quality=88)
    og = Image.new("RGB", (1200, 630), CREAM); d = ImageDraw.Draw(og)
    for i, (ang, dx, dy) in enumerate([(-7, 0, 80), (5, 140, 130), (-2, 250, 40)]):
        t = pages[i].resize((int(pages[i].width * 440 / pages[i].height), 440), Image.Resampling.LANCZOS)
        tl = tile(t, ang); og.paste(tl, (590 + dx - 30, dy), tl)
    d.rectangle([0, 0, 560, 630], fill=TEAL)
    d.text((48, 70), "JALU PRESS · FREE SAMPLE", font=f(SANS_SB, 18), fill=RUST)
    y = 114
    for ln in ["The Home", "Starter Pack"]:
        d.text((48, y), ln, font=f(SERIF, 46), fill=CREAM); y += 56
    y += 8
    for ln in ["7 free fillable pages:", "emergency, home, moving", "and meal planning"]:
        d.text((48, y), ln, font=f(SANS, 24), fill=(207, 219, 216)); y += 32
    d.rounded_rectangle([48, 450, 230, 530], radius=14, fill=RUST)
    d.text((70, 452), "FREE", font=f(SERIF, 60), fill=(255, 255, 255))
    og.save(IMG / "og-free.jpg", "JPEG", quality=90, optimize=True, subsampling=0)


if __name__ == "__main__":
    main()
