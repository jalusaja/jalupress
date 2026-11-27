#!/usr/bin/env python3
"""Build the low-price entry products (excerpt PDFs of existing Jalu Press planners):
Letter + A4 PDFs, zip, cover/preview/OG images and catalog.json entries. Re-runnable.
Zips go to /workspace/ebook-store/products/<slug>/ (gitignored)."""
import glob, json, subprocess, tempfile, zipfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
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

ENTRIES = [
    {
        "slug": "printable-car-maintenance-log",
        "title": "Printable Car Maintenance Log: Vehicle Service Record PDF",
        "nav_label": "Car Maintenance Log",
        "subtitle": "Fillable vehicle profile, service log and tire & fluid check sheet, in US Letter and A4",
        "price_usd": 3,
        "source": "home-maintenance-planner-car-service-log",
        "src_name": "The-Home-Maintenance-Planner-and-Car-Service-Log",
        "pages": [20, 21, 22, 23, 24],
        "file": "Printable-Car-Maintenance-Log",
        "page_names": ["vehicle profile", "service log", "service log", "service log", "tire and fluid check sheet"],
        "tint": "car",
        "short": "A printable, fillable car maintenance log: a vehicle profile page, three pages of service log for services, repairs and tire jobs, and a tire and fluid check sheet. US Letter and A4.",
        "howto": [
            "Fill in the vehicle profile once: year, make and model, tire size and pressure, fluid types and warranty date. Copy them from the owner's manual and the labels on the vehicle.",
            "After every service, repair, test or tire job, add one line to the service log: date, odometer, work done, who did it, and the cost.",
            "Use the tire and fluid check sheet once a month or before a long trip, and note anything that needs attention.",
            "Write the next-due date or odometer from your owner's manual or your garage. This log does not contain service schedules for any vehicle.",
            "Type into the fields on screen (Adobe Acrobat Reader is free), or print as many copies as you need and write by hand.",
        ],
        "good_for": [
            "Keeping every service and repair for one or more cars in one place",
            "Having a record to show a mechanic, a buyer or an insurer",
            "New drivers and anyone who keeps forgetting when the last service was",
            "A glove-box log you can print again whenever the pages fill up",
        ],
        "related": [
            {"slug": "home-household-starter-bundle", "blurb": "Want the whole home covered? This log is a small part of the Home & Household Starter Bundle: 5 planners, including a full home maintenance planner and car service log, for one price."},
            {"slug": "home-maintenance-planner-car-service-log", "blurb": "Want more? The full planner adds home checklists, appliance records, repair log and a spreadsheet that works out what is due next."},
        ],
        "note": "This is a record-keeping tool, not a substitute for the manufacturer's manual or a qualified mechanic.",
    },
    {
        "slug": "job-application-tracker-pdf",
        "title": "Job Application Tracker PDF: Printable Job Search Log",
        "nav_label": "Job Application Tracker",
        "subtitle": "Fillable application log, pipeline board, interview log and follow-up checklist, in US Letter and A4",
        "price_usd": 4,
        "source": "job-search-tracker-career-planner",
        "src_name": "The-Job-Search-Tracker-and-Career-Planner",
        "pages": [6, 7, 8, 9, 18, 24],
        "file": "Job-Application-Tracker",
        "page_names": ["application log", "application log", "application log", "pipeline board", "interview log", "follow-up checklist"],
        "tint": "job",
        "short": "A printable, fillable job application tracker: three pages of application log with follow-up dates, a one-page pipeline board, an interview log and a follow-up checklist. US Letter and A4.",
        "howto": [
            "Log every application the day you send it: date, company, role, where you found it, status and a follow-up date.",
            "Use the same status words every time (Saved, Applied, Screening, Interview, Offer, Rejected, Withdrawn) so the pipeline board stays clear.",
            "Move each application across the pipeline board as its status changes, so you can see the whole search at a glance.",
            "Write down each interview soon after it happens: who you met, the questions you remember, and what to do better next time.",
            "Work through the follow-up checklist when you apply, after an interview, when there is no reply and when you get an offer.",
        ],
        "good_for": [
            "Anyone applying to more than a handful of jobs at once",
            "Career changers and new graduates who want a simple, printable system",
            "People who think better on paper than in a spreadsheet",
            "Keeping follow-up dates so no application goes quiet by accident",
        ],
        "related": [
            {"slug": "job-search-tracker-career-planner", "blurb": "Want more? The full Job Search Tracker & Career Planner adds goals, weekly planning, company research, interview story prep, a networking log, an offer comparison and a spreadsheet."},
        ],
        "note": "This is an organizing tool, not legal, immigration, tax or salary advice.",
    },
    {
        "slug": "weekly-meal-plan-grocery-list-printable",
        "title": "Weekly Meal Plan & Grocery List Printable PDF",
        "nav_label": "Weekly Meal Plan Printable",
        "subtitle": "Fillable weekly meal plans with matching grocery lists, a pantry checklist and a go-to meals list, in US Letter and A4",
        "price_usd": 3,
        "source": "plan-ahead-meal-grocery-planner",
        "src_name": "The-Plan-Ahead-Meal-and-Grocery-Planner",
        "pages": [5, 6, 8, 9, 10, 11],
        "file": "Weekly-Meal-Plan-and-Grocery-List",
        "page_names": ["go-to meals list", "pantry staples checklist", "weekly meal plan", "grocery list", "weekly meal plan", "grocery list"],
        "tint": "meal",
        "short": "A printable, fillable weekly meal plan with a matching grocery list sorted by store section, plus a pantry staples checklist and a go-to meals list. US Letter and A4.",
        "howto": [
            "Start with the go-to meals list: write down the dinners your household already likes, so planning is choosing, not inventing.",
            "Tick the pantry staples page, then plan the week: one meal plan page covers seven days of breakfast, lunch, dinner and snacks.",
            "Copy what you need onto the grocery list on the facing page. It is sorted by store section, so you shop in one pass.",
            "Print as many copies of the weekly pages as you need, or type into the fields on screen in Adobe Acrobat Reader (free).",
            "Plan in about 20 minutes on the same day each week, and shop once.",
        ],
        "good_for": [
            "Households that want to stop asking \"what's for dinner?\" every day",
            "Cutting food waste and last-minute takeout",
            "Anyone who likes a paper plan on the fridge",
            "Shopping once a week with a list sorted by store section",
        ],
        "related": [
            {"slug": "home-household-starter-bundle", "blurb": "Want the whole home covered? The meal planner is part of the Home & Household Starter Bundle: 5 planners for one price."},
            {"slug": "plan-ahead-meal-grocery-planner", "blurb": "Want more? The full Plan-Ahead Meal & Grocery Planner adds four weeks, a fridge and freezer inventory, prep sessions, recipe cards, a spend log and a spreadsheet that writes your grocery list."},
        ],
        "note": "This is a planning tool, not nutrition or dietary advice.",
    },
]


def names_of(e):
    u = []
    for n in e["page_names"]:
        if n not in u:
            u.append(n)
    return ", ".join(u[:-1]) + " and " + u[-1] if len(u) > 1 else u[0]


def font(p, s):
    return ImageFont.truetype(p, s)


def load():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def howto_page(path, size, e, source_title, source_price):
    pdfmetrics.registerFont(TTFont("Serif", SERIF))
    pdfmetrics.registerFont(TTFont("Sans", SANS))
    pdfmetrics.registerFont(TTFont("SansSB", SANS_SB))
    W, H = size
    c = canvas.Canvas(str(path), pagesize=size)
    teal, rust, ink, muted = HexColor("#16343a"), HexColor("#b9552a"), HexColor("#1f2a2c"), HexColor("#5b6668")
    c.setFillColor(teal); c.rect(0, H - 140, W, 140, fill=1, stroke=0)
    c.setFillColor(HexColor("#f0a77f")); c.setFont("SansSB", 11)
    c.drawString(54, H - 54, "JALU PRESS  ·  PRINTABLE")
    c.setFillColor(HexColor("#ffffff"))
    y = H - 88
    for ln in simpleSplit(e["title"], "Serif", 22, W - 108):
        c.setFont("Serif", 22); c.drawString(54, y, ln); y -= 28
    y = H - 185
    c.setFillColor(teal); c.setFont("SansSB", 14); c.drawString(54, y, "How to use this"); y -= 24
    for i, t in enumerate(e["howto"], 1):
        c.setFillColor(rust); c.setFont("SansSB", 12); c.drawString(54, y, str(i))
        c.setFillColor(ink); c.setFont("Sans", 11.5)
        for ln in simpleSplit(t, "Sans", 11.5, W - 140):
            c.drawString(74, y, ln); y -= 16
        y -= 8
    y -= 8
    c.setFillColor(teal); c.setFont("SansSB", 12); c.drawString(54, y, "What is in this file"); y -= 17
    c.setFillColor(ink); c.setFont("Sans", 11)
    names = names_of(e)
    for ln in simpleSplit("The pages that follow: %s. They are fillable: type into them on screen or print and write by hand." % names, "Sans", 11, W - 108):
        c.drawString(54, y, ln); y -= 14
    y -= 14
    c.setFillColor(teal); c.setFont("SansSB", 12); c.drawString(54, y, "Want more?"); y -= 17
    c.setFillColor(ink); c.setFont("Sans", 11)
    for ln in simpleSplit("These pages are taken from %s ($%s) at jalupress.com, which has many more pages and a spreadsheet." % (source_title, source_price), "Sans", 11, W - 108):
        c.drawString(54, y, ln); y -= 14
    y -= 14
    c.setFillColor(muted); c.setFont("Sans", 9.5)
    for ln in simpleSplit("Personal and household license: print as many copies as you need for yourself and your household. Please do not share, upload or resell the file. %s Questions: hallo@jalupublishing.com" % e["note"], "Sans", 9.5, W - 108):
        c.drawString(54, y, ln); y -= 12.5
    c.setFont("Sans", 9); c.drawString(54, 40, "Jalu Press  ·  jalupress.com")
    c.showPage(); c.save()


def build_pdf(e, label, size, src_title, price, out):
    src = PRODUCTS / e["source"] / ("%s-%s.pdf" % (e["src_name"], label))
    tmp = Path(tempfile.mkdtemp()) / "howto.pdf"
    howto_page(tmp, size, e, src_title, price)
    w = PdfWriter()
    w.append(PdfReader(str(tmp)))
    r = PdfReader(str(src))
    for n in e["pages"]:
        w.append(r, pages=(n - 1, n))
    w.add_metadata({"/Title": e["title"], "/Author": "Jalu Press"})
    with open(out, "wb") as f:
        w.write(f)


def tile(img, ang, shadow=True):
    img = img.convert("RGBA")
    pad = 30
    base = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(base).rectangle([pad + 8, pad + 12, pad + img.width + 8, pad + img.height + 12], fill=(22, 52, 58, 80))
    base.paste(img, (pad, pad))
    return base.rotate(ang, expand=True, resample=Image.Resampling.BICUBIC)


def make_images(e, pngs):
    W, H = 1600, 1200
    pages = [Image.open(p).convert("RGB") for p in pngs]
    price = e["price_usd"]
    def comp(W, H, text_w, scale_title):
        cv = Image.new("RGB", (W, H), TEAL)
        d = ImageDraw.Draw(cv)
        d.rectangle([text_w, 0, W, H], fill=CREAM)
        return cv, d
    # cover
    cv, d = comp(W, H, 760, 1)
    ph = 760
    for i, (ang, dx, dy) in enumerate([(-7, 0, 120), (5, 190, 220), (-2, 340, 60)]):
        pg = pages[i % len(pages)]
        t = pg.resize((int(pg.width * ph / pg.height * 0.9), int(ph * 0.9)), Image.Resampling.LANCZOS)
        tl = tile(t, ang)
        cv.paste(tl, (790 + dx - 60, dy), tl)
    d.text((70, 150), "JALU PRESS · PRINTABLE", font=font(SANS_SB, 30), fill=RUST)
    y = 230
    for line in e["cover_lines"]:
        d.text((70, y), line, font=font(SERIF, 70), fill=PAPER); y += 86
    y += 14
    for line in e["cover_sub"]:
        d.text((70, y), line, font=font(SANS, 40), fill=(207, 219, 216)); y += 54
    y += 50
    d.rounded_rectangle([70, y, 330, y + 130], radius=22, fill=RUST)
    d.text((100, y + 8), "$%d" % price, font=font(SERIF, 100), fill=(255, 255, 255))
    d.text((70, y + 160), "Fillable PDF · Letter + A4", font=font(SANS_SB, 34), fill=(207, 219, 216))
    cv.save(IMG / (e["slug"] + "-cover.webp"), "WEBP", quality=88)
    cv.resize((800, 600), Image.Resampling.LANCZOS).save(IMG / (e["slug"] + "-cover-800.webp"), "WEBP", quality=88)
    # previews: one page each on cream
    for i, (pg, nm) in enumerate(zip(pages[:3], e["preview_names"]), 1):
        pv = Image.new("RGB", (W, H), CREAM)
        h = 1080
        t = pg.resize((int(pg.width * h / pg.height), h), Image.Resampling.LANCZOS)
        tl = tile(t, 0)
        pv.paste(tl, ((W - tl.width) // 2, (H - tl.height) // 2), tl)
        stem = "%s-preview-%d-%s" % (e["slug"], i, nm)
        pv.save(IMG / (stem + ".webp"), "WEBP", quality=86)
        pv.resize((800, 600), Image.Resampling.LANCZOS).save(IMG / (stem + "-800.webp"), "WEBP", quality=86)
    # og
    og = Image.new("RGB", (1200, 630), CREAM)
    d = ImageDraw.Draw(og)
    d.rectangle([0, 0, 560, 630], fill=TEAL)
    for ang, dx, dy in [(-7, 0, 70), (5, 150, 120), (-2, 250, 30)][::1]:
        pass
    for i, (ang, dx, dy) in enumerate([(-7, 0, 80), (5, 140, 130), (-2, 250, 40)]):
        pg = pages[i % len(pages)]
        t = pg.resize((int(pg.width * 440 / pg.height), 440), Image.Resampling.LANCZOS)
        tl = tile(t, ang)
        og.paste(tl, (590 + dx - 30, dy), tl)
    d.rectangle([0, 0, 560, 630], fill=TEAL)
    d.text((48, 70), "JALU PRESS · PRINTABLE", font=font(SANS_SB, 18), fill=RUST)
    y = 114
    for line in e["cover_lines"]:
        d.text((48, y), line, font=font(SERIF, 40), fill=PAPER); y += 50
    y += 6
    for line in e["cover_sub"]:
        d.text((48, y), line, font=font(SANS, 22), fill=(207, 219, 216)); y += 30
    d.rounded_rectangle([48, 440, 190, 510], radius=14, fill=RUST)
    d.text((66, 444), "$%d" % price, font=font(SERIF, 54), fill=(255, 255, 255))
    d.text((48, 530), "Fillable PDF · Letter + A4", font=font(SANS_SB, 20), fill=(207, 219, 216))
    og.save(IMG / ("og-" + e["slug"] + ".jpg"), "JPEG", quality=90, optimize=True, subsampling=0)


COVER = {
    "printable-car-maintenance-log": (["Car Maintenance", "Log"], ["Vehicle service record", "+ tire & fluid checks"], ["vehicle-profile", "service-log", "tire-and-fluid-check"]),
    "job-application-tracker-pdf": (["Job Application", "Tracker"], ["Application log, pipeline", "board & interview log"], ["application-log", "pipeline-board", "interview-log"]),
    "weekly-meal-plan-grocery-list-printable": (["Weekly Meal Plan", "& Grocery List"], ["Plan the week, shop once", "+ pantry checklist"], ["weekly-meal-plan", "grocery-list", "go-to-meals"]),
}
# which rendered pages (index into e["pages"] after the how-to page) to use for images
IMG_PAGES = {
    "printable-car-maintenance-log": [1, 2, 5],
    "job-application-tracker-pdf": [1, 4, 5],
    "weekly-meal-plan-grocery-list-printable": [3, 4, 1],
}


def entry(e, cat):
    m = {p["slug"]: p for p in cat["products"]}
    src = m[e["source"]]
    price = e["price_usd"]
    n = len(e["pages"])
    imgs = [{"file": e["slug"] + "-cover", "alt": "Cover of %s: a printable PDF, $%d" % (e["title"], price)}]
    for i, nm in enumerate(e["preview_names"], 1):
        imgs.append({"file": "%s-preview-%d-%s" % (e["slug"], i, nm), "alt": "Preview page: %s" % nm.replace("-", " ")})
    names = names_of(e)
    return {
        "slug": e["slug"], "kind": "mini", "related": e["related"],
        "title": e["title"], "subtitle": e["subtitle"], "nav_label": e["nav_label"],
        "price_usd": price, "status": "for_sale", "released": "2026-11-27",
        "short": e["short"],
        "description": "%s $%d, paid with PayPal, or USDC or USDT. Delivered by email." % (e["short"], price),
        "format_blurb": "Digital download (fillable PDF, Letter + A4)",
        "og_image": "assets/img/og-%s.jpg" % e["slug"],
        "og_alt": "%s: a printable fillable PDF for $%d" % (e["title"], price),
        "images": imgs,
        "shop_ticks": ["%d fillable pages plus a one-page guide, in US Letter and A4" % n,
                       "Type on screen or print as many copies as you need",
                       "Excerpted from a $%s planner, for a fraction of the price" % fmt(src["price_usd"])],
        "buy_ticks": ["Fillable PDF: %s" % names, "Both US Letter and A4 sizes in one ZIP",
                      "One-page how-to-use guide", "Personal and household license"],
        "story": [
            {"heading": "What you get",
             "paragraphs": ["A short, practical printable: %s. Every page has clear boxes and lines you can type into on screen or fill in by hand, and the pages print cleanly on a home printer, in color or black and white." % names,
                            "The pages come from %s, our full planner, so they are the same carefully laid-out sheets, without the extras. If you only need this one job done, this is the quick and inexpensive way to do it." % src["title"]]},
            {"heading": "How it works",
             "paragraphs": ["Open the PDF in Adobe Acrobat Reader (free) or another form-capable PDF reader and type straight into the fields, or print it. Print more copies whenever a page fills up.",
                            "Pay once and keep the file for good: no subscription, no login, nothing that expires."]},
        ],
        "included": [{"type": "PDF", "name": "%s, US Letter" % e["nav_label"], "detail": "%d pages including a one-page guide, 8.5 × 11 in" % (n + 1)},
                     {"type": "PDF", "name": "%s, A4" % e["nav_label"], "detail": "%d pages including a one-page guide, 210 × 297 mm, same content" % (n + 1)}],
        "included_note": "Delivered together as one ZIP download.",
        "inside": [],
        "good_for": e["good_for"],
        "specs": [["Format", "Fillable PDF in two paper sizes, delivered as one ZIP"],
                  ["Pages", "%d fillable pages plus a one-page guide, per paper size" % n],
                  ["Works in", "Adobe Acrobat Reader (free), Apple Preview and other form-capable PDF readers"],
                  ["Printing", "Color or black and white, home-printer margins"],
                  ["Language", "English"], ["Price", "$%d" % price],
                  ["License", "Personal and household use, not for resale or sharing"]],
        "please_note": [e["note"],
                        "These pages are excerpted from %s. If you already own it, you do not need this file." % src["title"],
                        "Files are delivered by email as a ZIP, usually within 15 minutes of payment. Save the attachment and unzip it (double-click on most computers).",
                        "Personal and household license: print as many copies as you need, but do not share, upload or resell the file."],
        "zip": e["file"] + ".zip",
        "whats_inside": ["%s, US Letter size (fillable PDF)" % e["nav_label"], "%s, A4 size (fillable PDF)" % e["nav_label"]],
        "delivery_note": "To open it, save the attachment and unzip it (double-click on most computers). Open the Letter or A4 PDF, whichever matches your paper: the first page explains how to use it, and the rest are fillable.",
    }


def fmt(n):
    return str(int(n)) if float(n) == int(float(n)) else "%.2f" % n


def main():
    cat = load()
    m = {p["slug"]: p for p in cat["products"]}
    for e in ENTRIES:
        e["cover_lines"], e["cover_sub"], e["preview_names"] = COVER[e["slug"]]
        src = m[e["source"]]
        out = PRODUCTS / e["slug"]
        out.mkdir(parents=True, exist_ok=True)
        tmp = Path(tempfile.mkdtemp())
        root = e["file"]
        (tmp / root).mkdir()
        build_pdf(e, "Letter", letter, src["title"], fmt(src["price_usd"]), tmp / root / ("%s-Letter.pdf" % root))
        build_pdf(e, "A4", A4, src["title"], fmt(src["price_usd"]), tmp / root / ("%s-A4.pdf" % root))
        shutil.copy(tmp / root / ("%s-Letter.pdf" % root), out / ("%s-Letter.pdf" % root))
        zp = out / (root + ".zip")
        if zp.exists():
            zp.unlink()
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for f in sorted((tmp / root).iterdir()):
                z.write(f, "%s/%s" % (root, f.name))
        # images from the Letter PDF
        pngs = []
        for idx in IMG_PAGES[e["slug"]]:
            base = str(tmp / ("pg%d" % idx))
            subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", str(idx + 1), "-l", str(idx + 1), "-singlefile",
                            str(tmp / root / ("%s-Letter.pdf" % root)), base], check=True)
            pngs.append(base + ".png")
        make_images(e, pngs)
        ent = entry(e, cat)
        cat["products"] = [p for p in cat["products"] if p["slug"] != e["slug"]] + [ent]
        print("built", e["slug"], zp.stat().st_size)
    # cross-link bundle -> minis
    for p in cat["products"]:
        if p["slug"] == "home-household-starter-bundle":
            p["related"] = [
                {"slug": "printable-car-maintenance-log", "blurb": "Only need one piece? The car maintenance log is available on its own."},
                {"slug": "weekly-meal-plan-grocery-list-printable", "blurb": "Only need one piece? The weekly meal plan and grocery list is available on its own."}]
    CATALOG.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
