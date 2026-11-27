#!/usr/bin/env python3
"""Build Jalu Press bundle products: the delivery zip, a Start-Here PDF, cover and
OG images, and the catalog.json entries. Safe to re-run (replaces by slug).

The zips go to /workspace/ebook-store/products/<slug>/ (gitignored). Images go to
docs/assets/img/. Autodeliver reads catalog.json and mails the zip.
"""
import json, os, shutil, sys, tempfile, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = Path(__file__).resolve().parent.parent
IMG = HERE / "docs" / "assets" / "img"
PRODUCTS = Path("/workspace/ebook-store/products")
CATALOG = HERE / "catalog.json"
FD = "/usr/share/fonts/truetype/sand-box/custom/"
SERIF = FD + "Source Serif Pro/SourceSerifPro-Semibold.ttf"
SANS = FD + "Source Sans Pro/SourceSansPro-Regular.ttf"
SANS_SB = FD + "Source Sans Pro/SourceSansPro-Semibold.ttf"
TEAL, CREAM, RUST, PAPER = (22, 52, 58), (246, 241, 231), (185, 85, 42), (246, 241, 231)

BLURBS = {
    "grab-and-go-household-binder": "Emergency plan, important papers, medical details and an expiry tracker, all in one place.",
    "home-maintenance-planner-car-service-log": "Monthly and seasonal checklists, appliance and repair records, and a car service log.",
    "moving-day-relocation-planner": "A week-by-week timeline, moving budget, box inventory and address-change tracker.",
    "plan-ahead-meal-grocery-planner": "Weekly meal plans with grocery lists, a pantry inventory and a spreadsheet that writes the shopping list.",
    "pet-care-record-book": "Vet visits, vaccines, medicine, daily care and pet-sitter pages for any pet.",
    "holiday-gift-budget-planner": "Gift lists per person, spending against your own budget, a card list and a week-by-week countdown.",
    "holiday-hosting-dinner-planner": "Guest list and RSVPs, dietary needs, menu, grocery list, prep countdown and seating plan.",
    "new-year-goal-habit-planner": "A year review, goal action plans, habit trackers and weekly, monthly and quarterly check-ins.",
}

BUNDLES = [
    {
        "slug": "home-household-starter-bundle",
        "title": "The Home & Household Starter Bundle",
        "subtitle": "5 planners for emergencies, home upkeep, moving, meals and pets",
        "nav_label": "Home & Household Bundle",
        "price_usd": 24,
        "released": "2026-11-27",
        "zip": "The-Home-and-Household-Starter-Bundle.zip",
        "includes": ["grab-and-go-household-binder", "home-maintenance-planner-car-service-log",
                     "moving-day-relocation-planner", "plan-ahead-meal-grocery-planner", "pet-care-record-book"],
        "cover_title": "Home & Household\nStarter Bundle",
        "cover_sub": "5 planners, one download",
        "og_alt": "The Home & Household Starter Bundle: five Jalu Press planners for $24 instead of $48",
        "pitch": "the five planners most households reach for: the emergency binder, home maintenance and car service log, moving-day planner, meal and grocery planner, and the pet care record book",
        "story": [
            {"heading": "Everything a home runs on, in one download",
             "paragraphs": [
                 "A household is a lot of small jobs: knowing who to call in an emergency, remembering when the smoke alarms were last tested, planning dinners, keeping vet records straight, and, now and then, moving the whole lot to a new address. These five planners cover those jobs, with the same clear layout in each.",
                 "Every planner is a fillable PDF you can type into on screen or print and write on, in US Letter and A4, with a spreadsheet that does the adding up and the date-checking for you. Use one this week and the others as the need comes up."]},
            {"heading": "One price, yours for good",
             "paragraphs": [
                 "Bought one by one, these five planners cost $48. As a bundle they cost $24, which is half price. You pay once and there is no subscription, no login and nothing that expires.",
                 "Keep the files on your computer, print as many copies as your household needs, and start fresh each year. That is lifetime access to the files, for less than a healthy lunch and a coffee."]},
        ],
        "good_for": [
            "New homeowners and first-time renters setting up their household systems",
            "Anyone about to move who also wants a home that stays organized afterwards",
            "Families with pets who like to keep every vet record in one place",
            "A housewarming or new-home gift that is useful all year",
        ],
        "slug_extra_images": ["binder-cover", "home-maintenance-planner-car-service-log-cover",
                              "moving-day-relocation-planner-cover", "plan-ahead-meal-grocery-planner-cover",
                              "pet-care-record-book-cover"],
    },
    {
        "slug": "holiday-and-fresh-start-bundle",
        "title": "The Holiday & Fresh-Start Bundle",
        "subtitle": "3 planners: gifts and budget, hosting, and your new-year goals",
        "nav_label": "Holiday & Fresh-Start Bundle",
        "price_usd": 19,
        "released": "2026-11-27",
        "zip": "The-Holiday-and-Fresh-Start-Bundle.zip",
        "includes": ["holiday-gift-budget-planner", "holiday-hosting-dinner-planner", "new-year-goal-habit-planner"],
        "cover_title": "Holiday &\nFresh-Start Bundle",
        "cover_sub": "3 planners, one download",
        "og_alt": "The Holiday & Fresh-Start Bundle: three Jalu Press planners for $19 instead of $27",
        "pitch": "everything for the holiday season and the new year: gifts and budget, hosting dinner, and goals and habits",
        "story": [
            {"heading": "From the first gift to the first of January",
             "paragraphs": [
                 "The holiday season has a lot of moving parts: who you are buying for and what you can spend, who is coming to dinner and what they can eat, and then, once it is over, a fresh start. These three planners walk you through all of it in order.",
                 "Each planner is a fillable PDF you can type into on screen or print and write on, in US Letter and A4, with a spreadsheet that adds up the money and the progress for you."]},
            {"heading": "One price, yours for good",
             "paragraphs": [
                 "Bought one by one, the three planners cost $27. As a bundle they cost $19. You pay once and there is no subscription, no login and nothing that expires.",
                 "Keep the files, print as many copies as your household needs, and use them again next season. That is lifetime access to the files for less than a nice lunch."]},
        ],
        "good_for": [
            "Anyone who wants the holiday season to feel calmer and less expensive",
            "Hosts of Thanksgiving, Christmas or New Year dinners",
            "People who like to start January with a plan and a way to track it",
            "A thoughtful gift for a friend who is always organizing everyone else",
        ],
        "slug_extra_images": ["holiday-gift-budget-planner-cover", "holiday-hosting-dinner-planner-cover",
                              "new-year-goal-habit-planner-cover"],
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def by_slug(cat):
    return {p["slug"]: p for p in cat["products"]}


def list_price(b, cat):
    m = by_slug(cat)
    return sum(float(m[s]["price_usd"]) for s in b["includes"])


def fmt(n):
    return str(int(n)) if float(n) == int(float(n)) else "%.2f" % n


# ------------------------------------------------------------------ images
def cover_collage(b, cat, size=(1600, 1200)):
    W, H = size
    s = W / 1600.0
    cv = Image.new("RGB", size, TEAL)
    d = ImageDraw.Draw(cv)
    # soft paper panel on the right
    d.rectangle([int(760 * s), 0, W, H], fill=CREAM)
    m = by_slug(cat)
    covers = []
    for sl in b["includes"]:
        stem = {"grab-and-go-household-binder": "binder"}.get(sl, sl)
        covers.append(Image.open(IMG / (stem + "-cover.webp")).convert("RGB"))
    n = len(covers)
    tw, th = int(640 * s), int(480 * s)
    # fan the covers down the right side
    y0, y1 = 70, 1200 - 480 - 70
    for i, im in enumerate(covers):
        t = i / max(1, n - 1)
        x = int((800 + (i % 2) * 130 + 10) * s)
        y = int((y0 + (y1 - y0) * t) * s)
        tile = im.resize((tw, th), Image.Resampling.LANCZOS)
        shadow = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle([20, 24, tw + 20, th + 24], fill=(22, 52, 58, 70))
        cv.paste(shadow, (x - 20, y - 20), shadow)
        d.rectangle([x - 3, y - 3, x + tw + 3, y + th + 3], fill=(255, 255, 255))
        cv.paste(tile, (x, y))
    # left text
    pad = int(70 * s)
    y = int(150 * s)
    d.text((pad, y), "JALU PRESS · BUNDLE", font=font(SANS_SB, int(30 * s)), fill=RUST)
    y += int(80 * s)
    tf = font(SERIF, int(72 * s))
    for line in b["cover_title"].split("\n"):
        d.text((pad, y), line, font=tf, fill=PAPER)
        y += int(88 * s)
    y += int(20 * s)
    d.text((pad, y), b["cover_sub"], font=font(SANS, int(44 * s)), fill=(207, 219, 216))
    y += int(150 * s)
    lp = list_price(b, cat)
    save = lp - float(b["price_usd"])
    # price badge
    bw, bh = int(560 * s), int(210 * s)
    d.rounded_rectangle([pad, y, pad + bw, y + bh], radius=int(24 * s), fill=RUST)
    d.text((pad + int(36 * s), y + int(22 * s)), "$%s" % fmt(b["price_usd"]), font=font(SERIF, int(112 * s)), fill=(255, 255, 255))
    d.text((pad + int(36 * s), y + int(150 * s)), "instead of $%s · save $%s" % (fmt(lp), fmt(save)),
           font=font(SANS_SB, int(34 * s)), fill=(255, 255, 255))
    y += bh + int(40 * s)
    d.text((pad, y), "Fillable PDFs + spreadsheets", font=font(SANS, int(34 * s)), fill=(207, 219, 216))
    d.text((pad, y + int(48 * s)), "Lifetime access, no subscription", font=font(SANS, int(34 * s)), fill=(207, 219, 216))
    return cv


def make_images(b, cat):
    cv = cover_collage(b, cat)
    cv.save(IMG / (b["slug"] + "-cover.webp"), "WEBP", quality=88)
    cv.resize((800, 600), Image.Resampling.LANCZOS).save(IMG / (b["slug"] + "-cover-800.webp"), "WEBP", quality=88)
    # OG 1200x630: text panel left, fanned covers right
    W, H = 1200, 630
    og = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(og)
    d.rectangle([0, 0, 540, H], fill=TEAL)
    m = by_slug(cat)
    n = len(b["includes"])
    tw, th = 340, 255
    step = (H - 60 - th) / max(1, n - 1)
    for i, sl in enumerate(b["includes"]):
        stem = {"grab-and-go-household-binder": "binder"}.get(sl, sl)
        im = Image.open(IMG / (stem + "-cover.webp")).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x = 600 + (i % 2) * 215
        y = int(30 + step * i)
        shadow = Image.new("RGBA", (tw + 30, th + 30), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rectangle([15, 18, tw + 15, th + 18], fill=(22, 52, 58, 70))
        og.paste(shadow, (x - 15, y - 15), shadow)
        d.rectangle([x - 2, y - 2, x + tw + 2, y + th + 2], fill=(255, 255, 255))
        og.paste(im, (x, y))
    d.text((48, 64), "JALU PRESS · BUNDLE", font=font(SANS_SB, 18), fill=RUST)
    y = 112
    for line in b["cover_title"].split("\n"):
        d.text((48, y), line, font=font(SERIF, 42), fill=PAPER)
        y += 56
    d.text((48, y + 10), b["cover_sub"], font=font(SANS, 24), fill=(207, 219, 216))
    lp = list_price(b, cat)
    d.rounded_rectangle([48, 400, 400, 520], radius=16, fill=RUST)
    d.text((72, 404), "$%s" % fmt(b["price_usd"]), font=font(SERIF, 68), fill=(255, 255, 255))
    d.text((72, 480), "instead of $%s · save $%s" % (fmt(lp), fmt(lp - float(b["price_usd"]))), font=font(SANS_SB, 20), fill=(255, 255, 255))
    og.save(IMG / ("og-" + b["slug"] + ".jpg"), "JPEG", quality=90, optimize=True, subsampling=0)


# ------------------------------------------------------------------ start-here pdf + zip
def start_here_pdf(path, b, cat, folders):
    from reportlab.lib.utils import simpleSplit
    pdfmetrics.registerFont(TTFont("Serif", SERIF))
    pdfmetrics.registerFont(TTFont("Sans", SANS))
    pdfmetrics.registerFont(TTFont("SansSB", SANS_SB))
    c = canvas.Canvas(str(path), pagesize=letter)
    W, H = letter
    teal, rust, ink, muted = HexColor("#16343a"), HexColor("#b9552a"), HexColor("#1f2a2c"), HexColor("#5b6668")
    c.setFillColor(teal)
    c.rect(0, H - 150, W, 150, fill=1, stroke=0)
    c.setFillColor(HexColor("#f0a77f")); c.setFont("SansSB", 11)
    c.drawString(54, H - 60, "JALU PRESS  ·  BUNDLE")
    c.setFillColor(HexColor("#ffffff")); c.setFont("Serif", 26)
    c.drawString(54, H - 96, b["title"])
    c.setFillColor(HexColor("#cfdbd8")); c.setFont("Sans", 13)
    c.drawString(54, H - 122, "Start here: what is in this download")
    y = H - 188
    c.setFillColor(ink); c.setFont("Sans", 12)
    intro = ("Thank you for your order. This zip has one folder for each planner. Open a folder, read its "
             "Read-Me-First.pdf (or Instructions.pdf), then fill in the Letter or A4 PDF, whichever matches your paper. "
             "Each folder also has a spreadsheet that works in Excel or Google Sheets.")
    for ln in simpleSplit(intro, "Sans", 12, W - 108):
        c.drawString(54, y, ln); y -= 17
    y -= 16
    m = by_slug(cat)
    for sl, folder in zip(b["includes"], folders):
        p = m[sl]
        c.setFillColor(rust); c.rect(54, y - 36, 4, 52, fill=1, stroke=0)
        c.setFillColor(teal); c.setFont("SansSB", 13)
        c.drawString(68, y, p["title"])
        c.setFont("Sans", 10); c.setFillColor(muted)
        c.drawString(68, y - 14, "Folder: " + folder)
        c.setFont("Sans", 11); c.setFillColor(ink)
        yy = y - 29
        for ln in simpleSplit(BLURBS[sl], "Sans", 11, W - 130):
            c.drawString(68, yy, ln); yy -= 14
        y = yy - 22
    y -= 4
    c.setFillColor(teal); c.setFont("SansSB", 12)
    c.drawString(54, y, "Your license"); y -= 17
    c.setFillColor(ink); c.setFont("Sans", 11)
    lic = ("Lifetime access: these files are yours to keep and reuse. Your purchase gives you a personal license for you "
           "and your household, with as many printed copies as your household needs. Please don't share, upload or resell the files.")
    for ln in simpleSplit(lic, "Sans", 11, W - 108):
        c.drawString(54, y, ln); y -= 14
    y -= 12
    c.setFillColor(teal); c.setFont("SansSB", 12)
    c.drawString(54, y, "Need help?"); y -= 17
    c.setFillColor(ink); c.setFont("Sans", 11)
    for ln in simpleSplit("If a file is missing or will not open, write to hallo@jalupublishing.com with your order reference and we will sort it out.", "Sans", 11, W - 108):
        c.drawString(54, y, ln); y -= 14
    c.setFont("Sans", 9); c.setFillColor(muted)
    c.drawString(54, 40, "Jalu Press  ·  jalupress.com")
    c.showPage(); c.save()


def build_zip(b, cat):
    m = by_slug(cat)
    outdir = PRODUCTS / b["slug"]
    outdir.mkdir(parents=True, exist_ok=True)
    root = b["zip"][:-4]
    tmp = Path(tempfile.mkdtemp())
    folders = []
    for sl in b["includes"]:
        p = m[sl]
        src_zip = PRODUCTS / sl / p["zip"]
        with zipfile.ZipFile(src_zip) as z:
            top = sorted({n.split("/")[0] for n in z.namelist() if n.strip("/")})
            assert len(top) == 1, (sl, top)
            z.extractall(tmp)
        folders.append(top[0])
    start = tmp / "00-Start-Here.pdf"
    start_here_pdf(start, b, cat, folders)
    out = outdir / b["zip"]
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(start, "%s/00-Start-Here.pdf" % root)
        for f in folders:
            for fp in sorted((tmp / f).rglob("*")):
                if fp.is_file():
                    z.write(fp, "%s/%s" % (root, fp.relative_to(tmp)))
    shutil.rmtree(tmp)
    return out, folders


# ------------------------------------------------------------------ catalog entry
def pages_total(slugs):
    import subprocess, glob
    n = 0
    for sl in slugs:
        f = glob.glob(str(PRODUCTS / sl / "*-Letter.pdf"))[0]
        n += int([l for l in subprocess.run(["pdfinfo", f], capture_output=True, text=True).stdout.splitlines()
                  if l.startswith("Pages")][0].split()[1])
    return n


def entry(b, cat, zip_path, folders):
    m = by_slug(cat)
    lp = list_price(b, cat)
    price = float(b["price_usd"])
    save = lp - price
    pct = int(round(save / lp * 100))
    n = len(b["includes"])
    pages = pages_total(b["includes"])
    titles = [m[s]["title"] for s in b["includes"]]
    imgs = [{"file": b["slug"] + "-cover", "alt": "Cover of %s: %d Jalu Press planners in one download, $%s instead of $%s" % (b["title"], n, fmt(price), fmt(lp))}]
    for s, stem in zip(b["includes"], b["slug_extra_images"]):
        imgs.append({"file": stem, "alt": "Cover of %s, included in the bundle" % m[s]["title"]})
    whats = ["%s (Letter and A4 fillable PDFs, spreadsheet, read-me)" % m[s]["title"] for s in b["includes"]]
    whats.append("00-Start-Here.pdf: a one-page guide to what is in each folder")
    return {
        "slug": b["slug"],
        "kind": "bundle",
        "includes": b["includes"],
        "list_price_usd": lp,
        "title": b["title"],
        "subtitle": b["subtitle"],
        "nav_label": b["nav_label"],
        "price_usd": b["price_usd"],
        "status": "for_sale",
        "released": b["released"],
        "short": "%s Together: $%s instead of $%s, so you save $%s. Lifetime access, no subscription." % (
            (b["pitch"][0].upper() + b["pitch"][1:] + "."), fmt(price), fmt(lp), fmt(save)),
        "description": "%d Jalu Press planners in one download for $%s instead of $%s (save $%s, %d%% off): %s. Fillable PDFs in US Letter and A4, plus spreadsheets. Lifetime access, no subscription. Paid with PayPal, or USDC or USDT." % (
            n, fmt(price), fmt(lp), fmt(save), pct, "; ".join(titles)),
        "format_blurb": "Digital download (%d planners: PDFs + XLSX)" % n,
        "og_image": "assets/img/og-%s.jpg" % b["slug"],
        "og_alt": b["og_alt"],
        "images": imgs,
        "shop_ticks": [
            "%d planners, %d fillable pages per paper size, Letter and A4" % (n, pages),
            "Save $%s (%d%% off) compared with buying them one by one" % (fmt(save), pct),
            "Lifetime access: pay once, keep the files for good",
        ],
        "buy_ticks": [
            "%d planners in one ZIP, each with Letter + A4 fillable PDFs, a spreadsheet and a read-me" % n,
            "Save $%s compared with buying them separately ($%s)" % (fmt(save), fmt(lp)),
            "Lifetime access: pay once, keep the files forever, no subscription",
            "Personal and household license",
        ],
        "story": b["story"],
        "included": [{"type": "ZIP", "name": "%d planners, one folder each" % n,
                      "detail": "Letter and A4 fillable PDFs, a spreadsheet for Excel or Google Sheets, and a read-me for every planner"},
                     {"type": "PDF", "badge": "i", "name": "00-Start-Here.pdf",
                      "detail": "A one-page guide to what is in each folder"}],
        "included_note": "Delivered together as one ZIP download.",
        "inside": [],
        "good_for": b["good_for"],
        "specs": [
            ["Format", "One ZIP with %d folders: fillable PDFs (Letter and A4), XLSX spreadsheets and read-me PDFs" % n],
            ["Planners", "; ".join(titles)],
            ["Pages", "%d fillable pages per paper size across the %d planners" % (pages, n)],
            ["Works in", "Adobe Acrobat Reader (free), Apple Preview and other form-capable PDF readers; Excel or Google Sheets"],
            ["Regular price if bought separately", "$%s" % fmt(lp)],
            ["You save", "$%s (%d%%)" % (fmt(save), pct)],
            ["Price", "$%s" % fmt(price)],
            ["Access", "Lifetime: pay once, keep the files forever. No subscription, no login, nothing expires."],
            ["License", "Personal and household use, not for resale or sharing"],
        ],
        "please_note": [
            "This is a bundle of the products listed above; the files are identical to the individual products, so you do not need to buy any of them separately.",
            "The planners are organizing and record-keeping tools, not legal, medical, financial, veterinary or emergency-services advice.",
            "Files are delivered by email as a ZIP, usually within 15 minutes of payment. Save the attachment and unzip it (double-click on most computers).",
            "Personal and household license: print as many copies as your household needs, but do not share, upload or resell the files.",
        ],
        "zip": b["zip"],
        "whats_inside": whats,
        "delivery_note": "To open it, save the attachment and unzip it (double-click on most computers). Start with 00-Start-Here.pdf: it lists what is in each folder. These files are yours to keep for good.",
    }


def main():
    cat = load_catalog()
    for b in BUNDLES:
        make_images(b, cat)
        zp, folders = build_zip(b, cat)
        e = entry(b, cat, zp, folders)
        cat["products"] = [p for p in cat["products"] if p["slug"] != b["slug"]] + [e]
        print("built", b["slug"], zp.stat().st_size, "bytes; list $%s, price $%s" % (fmt(e["list_price_usd"]), fmt(e["price_usd"])))
    CATALOG.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
