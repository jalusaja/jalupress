#!/usr/bin/env python3
"""Static site builder for Jalu Press. Writes HTML into ./docs.

Product data lives in catalog.json (the same file autodeliver reads).
All internal links are RELATIVE so the site works both at
https://jalusaja.github.io/jalupress/ and at https://jalupress.com/.

Every product page uses its own Open Graph image at
docs/assets/img/og-<slug>.jpg (1200x630 JPEG). If that file is missing,
the page falls back to assets/img/og-default.jpg. Home and other
non-product pages use the site default. See ADD_PRODUCT.md and the
README: every new product must ship an og-<slug>.jpg.
"""
import html, json, os, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "docs"
SITE = "https://jalupress.com"
PAYPAL_BUSINESS = "jalurahadi@gmail.com"
YEAR = "2026"
OG_DEFAULT = "assets/img/og-default.jpg"
OG_W, OG_H = 1200, 630

CATALOG = json.loads((HERE / "catalog.json").read_text(encoding="utf-8"))


def for_sale():
    products = [p for p in CATALOG["products"] if p.get("status", "for_sale") == "for_sale"]
    products.sort(key=lambda p: p.get("released") or "", reverse=True)
    return products


PRODUCTS = for_sale()


def usd(p):
    n = p["price_usd"]
    return str(int(n)) if float(n) == int(float(n)) else f"{float(n):.2f}"


SUPPORT = "hallo@jalupublishing.com"
FORM_ENDPOINT = "https://formsubmit.co/hallo@jalupublishing.com"


def kind(p):
    return p.get("kind") or "single"


def fmtn(n):
    return str(int(n)) if float(n) == int(float(n)) else f"{float(n):.2f}"


def list_usd(p):
    """Honest reference price: only for bundles, the sum of the separate prices."""
    v = p.get("list_price_usd")
    if kind(p) == "bundle" and v and float(v) > float(p["price_usd"]):
        return fmtn(v)
    return None


def save_usd(p):
    lp = list_usd(p)
    return fmtn(float(lp) - float(p["price_usd"])) if lp else None


def save_pct(p):
    lp = list_usd(p)
    return int(round((float(lp) - float(p["price_usd"])) / float(lp) * 100)) if lp else None


def money_line(p, lead="Paid as"):
    u = usd(p)
    lp = list_usd(p)
    was = f'<s class="was" aria-label="Regular price if bought separately">${lp}</s> ' if lp else ""
    return f"{was}${u} <small>{lead} PayPal, or {u} USDC (Solana or Polygon) or {u} USDT (TRC20 or Polygon)</small>"


# Honest delivery wording, from the real pipeline: payment notices are checked every 10 minutes
# (PayPal notice reaches our inbox in a minute or two; crypto is checked once final on-chain).
DELIVERY_NOTE = (
    '<p class="delivery-note"><strong>When you get it:</strong> your files are emailed to you, usually within '
    '15 minutes after payment. It is not instant: we check for new payments every 10 minutes. '
    'If nothing has arrived after 30 minutes, check your spam folder, then write to '
    f'<a href="mailto:{SUPPORT}">{SUPPORT}</a> with your order reference.</p>'
)
DELIVERY_NOTE_SMALL = (
    'Emailed after payment, usually within 15 minutes (not instant). '
    f'Nothing after 30 minutes? Check spam, then <a href="mailto:{SUPPORT}">email us</a>.'
)


def signup_form(source, uid):
    return f'''<form class="signup" action="{FORM_ENDPOINT}" method="post">
<input type="hidden" name="_subject" value="Jalu Press free sample signup">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="{SITE}/free/thanks/">
<input type="hidden" name="source" value="{source}">
<input type="hidden" name="ref" value="">
<input type="text" name="_honey" value="" tabindex="-1" autocomplete="off" style="display:none" aria-hidden="true">
<label for="em-{uid}">Your email</label>
<div class="signup-row"><input type="email" id="em-{uid}" name="email" required autocomplete="email" placeholder="you@example.com" maxlength="120">
<button class="btn rust" type="submit">Send me the free pack</button></div>
<p class="small">We use your email only to send the free pack and one short follow-up about the bundle. No spam, never shared or sold, and every email has an unsubscribe link. Form delivery is handled by FormSubmit and your address is kept on our own computer. See our <a href="{{R}}privacy/">privacy notice</a>.</p>
</form>'''


def paypal_form(p, cancel_path=None, button_label=None):
    """Standard PayPal Buy Now (_xclick) form. Invoice/custom are filled on submit by paypal-buy.js."""
    u = usd(p)
    slug = p["slug"]
    title = p["title"]
    cancel = cancel_path or f"products/{slug}/"
    label = button_label or f"Pay ${u} with PayPal"
    ret = f"{SITE}/thank-you/?p={html.escape(slug, quote=True)}"
    cancel_url = f"{SITE}/{cancel.lstrip('/')}"
    biz = html.escape(PAYPAL_BUSINESS, quote=True)
    return (
        f'<form class="paypal-buy" action="https://www.paypal.com/cgi-bin/webscr" method="post">'
        f'<input type="hidden" name="cmd" value="_xclick">'
        f'<input type="hidden" name="business" value="{biz}">'
        f'<input type="hidden" name="item_name" value="{html.escape(title, quote=True)}">'
        f'<input type="hidden" name="item_number" value="{html.escape(slug, quote=True)}">'
        f'<input type="hidden" name="amount" value="{html.escape(u, quote=True)}">'
        f'<input type="hidden" name="currency_code" value="USD">'
        f'<input type="hidden" name="no_shipping" value="1">'
        f'<input type="hidden" name="no_note" value="1">'
        f'<input type="hidden" name="charset" value="utf-8">'
        f'<input type="hidden" name="rm" value="1">'
        f'<input type="hidden" name="return" value="{html.escape(ret, quote=True)}">'
        f'<input type="hidden" name="cancel_return" value="{html.escape(cancel_url, quote=True)}">'
        f'<input type="hidden" name="invoice" value="">'
        f'<input type="hidden" name="custom" value="">'
        f'<button class="btn paypal" type="submit">{html.escape(label)}</button>'
        f'</form>'
    )


def og_abs(rel_or_default):
    rel = rel_or_default.lstrip("/")
    if (ROOT / rel).is_file():
        return f"{SITE}/{rel}"
    return f"{SITE}/{OG_DEFAULT}"


def og_for(p=None):
    if p:
        rel = p.get("og_image") or f"assets/img/og-{p['slug']}.jpg"
        return og_abs(rel)
    return og_abs(OG_DEFAULT)


def page_url(path):
    if path == "index.html":
        return f"{SITE}/"
    if path.endswith("/index.html"):
        return f"{SITE}/{path[:-len('index.html')]}"
    return f"{SITE}/{path}"


LOGO = '''<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="12" fill="#16343a"/><path d="M18 14h22a6 6 0 0 1 6 6v30H24a6 6 0 0 1-6-6z" fill="#f6f1e7"/><path d="M18 44a6 6 0 0 1 6-6h22" fill="none" stroke="#16343a" stroke-width="3"/><path d="M36 14v14l-4-3-4 3V14" fill="#b9552a"/></svg>'''

def page(path, title, desc, body, active="", depth=None, extra_head="", scripts="",
         og_image=None, og_alt=None):
    depth = path.count("/") if depth is None else depth
    r = "../" * depth or "./"
    full_title = f"{title} | Jalu Press" if title != "Jalu Press" else "Jalu Press: practical English ebooks and light tools"
    url = page_url(path)
    image = og_image or og_for()
    alt = og_alt or "Jalu Press: practical English ebooks and light tools"
    shop_links = "".join(
        f'<li><a href="{r}products/{html.escape(p["slug"], quote=True)}/">{html.escape(p.get("nav_label") or p["title"])}</a></li>'
        for p in PRODUCTS)
    esc = html.escape
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta name="p:domain_verify" content="a39d20201d1c6e6ccf937fa8591ae1ad"/>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{extra_head}<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="canonical" href="{esc(url, quote=True)}">
<meta property="og:site_name" content="Jalu Press">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(url, quote=True)}">
<meta property="og:image" content="{esc(image, quote=True)}">
<meta property="og:image:width" content="{OG_W}">
<meta property="og:image:height" content="{OG_H}">
<meta property="og:image:alt" content="{esc(alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(full_title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(image, quote=True)}">
<meta name="theme-color" content="#16343a">
<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="{r}" aria-label="Jalu Press home">{LOGO}<span class="brand-name">Jalu Press</span></a>
</div></header>
<main id="main">
{body.replace("{R}", r)}
</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div><a class="brand" href="{r}" style="margin-bottom:12px">{LOGO}<span class="brand-name">Jalu Press</span></a>
<p>Practical English ebooks and light tools, sold as digital downloads that are emailed after payment. Paid with PayPal, or USDC (Solana or Polygon) or USDT (TRC20 or Polygon). Nothing physical is shipped.</p></div>
<div><h3>Shop</h3><ul>
{shop_links}
<li><a href="{r}free/">Free sample pack</a></li>
<li><a href="{r}how-to-buy/">How to buy</a></li>
<li><a href="{r}checkout/">Checkout</a></li></ul></div>
<div><h3>Info</h3><ul>
<li><a href="{r}about/">About Jalu Press</a></li>
<li><a href="{r}terms/">Help, license &amp; refunds</a></li>
<li><a href="{r}privacy/">Privacy</a></li></ul></div>
</div>
<div class="foot-legal">&copy; {YEAR} Jalu Press. All products are original works. Jalu Press products are organizing tools, not legal, medical, financial or emergency-services advice.</div>
</div></footer>
{scripts.replace("{R}", r)}
</body>
</html>
'''
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def img(stem, alt, cls="shot", w=1600, h=1200, eager=False, sizes="(max-width: 900px) 100vw, 600px"):
    b = f'{{R}}assets/img/{stem}'
    return (f'<img class="{cls}" src="{b}.webp" srcset="{b}-800.webp 800w, {b}.webp 1600w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{html.escape(alt)}"{"" if eager else " loading=lazy"} decoding="async">')


PAY_BADGES = '''<ul class="pay-badges" aria-label="Accepted payment">
<li class="badge"><span class="dot"></span>PayPal</li>
<li class="badge"><span class="dot"></span>USDC on Solana</li>
<li class="badge"><span class="dot"></span>USDC on Polygon</li>
<li class="badge"><span class="dot"></span>USDT on TRC20 (Tron)</li>
<li class="badge"><span class="dot"></span>USDT on Polygon</li>
<li class="badge">Emailed within about 15 minutes</li></ul>'''

# ---------- HOME ----------
if not PRODUCTS:
    raise SystemExit("catalog.json has no for_sale products")

SINGLES = [p for p in PRODUCTS if kind(p) == "single"]
MINIS = [p for p in PRODUCTS if kind(p) == "mini"]
BUNDLES = [p for p in PRODUCTS if kind(p) == "bundle"]
PM = {p["slug"]: p for p in CATALOG["products"]}

featured = SINGLES[0]
hero_cta = '<a class="btn" href="{R}index.html#bundles">See the bundles</a>'


def teaser(p, label="View details"):
    cover = p["images"][0]
    ticks = "".join(f'<li>{html.escape(t)}</li>' for t in (p.get("shop_ticks") or [])[:3])
    return (
        f'''<article class="product-teaser">
<a href="{{R}}products/{p["slug"]}/">{img(cover["file"], cover["alt"], sizes="(max-width: 900px) 100vw, 400px")}</a>
<div class="teaser-body">
<h3>{html.escape(p["title"])}</h3>
<p class="meta">{html.escape(p.get("subtitle") or "")}</p>
<p>{html.escape(p.get("short") or p.get("description") or "")}</p>
<ul class="ticks">{ticks}</ul>
<p class="price">{money_line(p)}</p>
<div class="btn-row" style="margin-top:16px"><a class="btn" href="{{R}}products/{p["slug"]}/">{label}</a></div>
</div></article>''')


def bundle_card(p):
    cover = p["images"][0]
    items = "".join(
        f'<li>{html.escape(PM[s]["title"])} <span class="small">(${usd(PM[s])})</span></li>' for s in p.get("includes") or [])
    return f'''<article class="bundle-card">
<a href="{{R}}products/{p["slug"]}/">{img(cover["file"], cover["alt"], sizes="(max-width: 900px) 100vw, 520px")}</a>
<div>
<p class="eyebrow">Bundle &middot; save ${save_usd(p)} ({save_pct(p)}% off)</p>
<h3 style="font-size:1.6rem">{html.escape(p["title"])}</h3>
<p class="price">{money_line(p, lead="Pay")}</p>
<p class="small" style="margin:6px 0 12px">Regular price if bought separately: ${list_usd(p)}. Lifetime access: pay once, keep the files for good.</p>
<ul class="ticks">{items}</ul>
<div class="btn-row"><a class="btn rust" href="{{R}}products/{p["slug"]}/">See what's inside</a>{paypal_form(p, cancel_path="index.html")}</div>
<p class="small" style="margin-top:12px">{DELIVERY_NOTE_SMALL}</p>
</div></article>'''


bundle_block = "".join(bundle_card(p) for p in BUNDLES)
mini_block = '<div class="product-grid">' + "".join(teaser(p) for p in MINIS) + "</div>"
shop_block = '<div class="product-grid">' + "".join(teaser(p) for p in SINGLES) + "</div>"

cover0 = featured["images"][0]
home = f'''
<section class="hero"><div class="wrap hero-grid">
<div>
<p class="eyebrow">Jalu Press</p>
<h1>Practical English ebooks and light tools for real life.</h1>
<p class="lead">Clear, well-made printables, workbooks and trackers that help you get one thing in order, then keep it that way. Original work, delivered as digital files.</p>
{PAY_BADGES}
<div class="btn-row">{hero_cta}<a class="btn alt" href="{{R}}free/">Get a free sample pack</a></div>
</div>
<div>{img(cover0["file"], cover0["alt"], eager=True)}</div>
</div></section>

<section class="paper2" id="bundles"><div class="wrap">
<p class="eyebrow">Best value</p>
<h2>Bundles</h2>
<p class="lead" style="margin-bottom:22px">Several planners in one download, for far less than buying them one by one. Pay once, keep the files for good.</p>
{bundle_block}
</div></section>

<section class="band" id="free"><div class="wrap grid2" style="align-items:center">
<div>
<p class="eyebrow">Free</p>
<h2>Try before you buy: the Home Starter Pack</h2>
<p>Seven free, fillable pages from our planners: a household-at-a-glance sheet, a water and food planner, a 3-day supplies checklist, a winter home checklist, a moving timeline and a weekly meal plan with grocery list. Enter your email and we send it to you.</p>
<p class="small" style="color:#cfdbd8"><a href="{{R}}free/">See what is inside &rarr;</a></p>
</div>
<div class="card signup-card" style="color:var(--text)">
{signup_form("home", "home")}
</div></div></section>

<section><div class="wrap">
<p class="eyebrow">Quick printables</p>
<h2>Just need one thing done? $3 to $4</h2>
<p class="lead">Single-purpose printable PDFs, excerpted from our full planners.</p>
{mini_block}
</div></section>

<section class="paper2" id="shop"><div class="wrap">
<p class="eyebrow">Shop</p>
<h2>Full planners</h2>
{shop_block}
</div></section>

<section><div class="wrap">
<h2>Why Jalu Press</h2>
<div class="grid3" style="margin-top:22px">
<div class="card"><h3>Made to be used</h3><p>Every product is built around a job you actually need to do, with clear fields, sensible order and pages that print cleanly at home.</p></div>
<div class="card"><h3>Written for anywhere</h3><p>Plain English for readers worldwide. No single-country defaults where they would get in your way, and both metric and imperial where it matters.</p></div>
<div class="card"><h3>Simple checkout</h3><p>Pay with PayPal, or with a stablecoin you already hold: USDC on Solana or Polygon, or USDT on TRC20 or Polygon. No subscription.</p></div>
</div></div></section>

<section class="band"><div class="wrap">
<p class="eyebrow">How it works</p>
<h2>Buying takes three steps</h2>
<div class="grid3" style="margin-top:22px">
<div class="card"><div class="step-n">1</div><h3>Choose a product</h3><p>Read the details and preview pages, and check it suits you before you pay.</p></div>
<div class="card"><div class="step-n">2</div><h3>Pay with PayPal or crypto</h3><p>Pay with PayPal in USD, or send USDC or USDT from checkout. Checkout shows the exact amount and, for crypto, the network and receive address.</p></div>
<div class="card"><div class="step-n">3</div><h3>Get your files by email</h3><p>Usually within 15 minutes after payment. It is not instant: we check for new payments every 10 minutes. If nothing has arrived after 30 minutes, check your spam folder, then email us.</p></div>
</div>
<p style="margin-top:22px"><a href="{{R}}how-to-buy/">Read the full buying guide &rarr;</a></p>
</div></section>
'''
page("index.html", "Jalu Press",
     "Jalu Press makes practical English ebooks and light tools, sold as digital downloads and paid with PayPal, or USDC or USDT on Solana, TRC20 or Polygon.",
     home, "home", depth=0, og_image=og_for(), og_alt="Jalu Press: practical English ebooks and light tools",
     scripts='<script src="{R}assets/paypal-buy.js" defer></script><script src="{R}assets/signup.js" defer></script>')


# ---------- PRODUCT PAGES ----------
gallery_js = '''<script>
(function(){var m=document.getElementById('mainimg'),t=document.getElementById('thumbs');if(!m||!t)return;
t.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
m.removeAttribute('srcset');m.src=b.dataset.src;m.alt=b.dataset.alt;
t.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});});})();
</script>'''


BLURB = {
    "grab-and-go-household-binder": "Emergency plan, important papers, medical details and an expiry tracker.",
    "home-maintenance-planner-car-service-log": "Monthly and seasonal checklists, appliance and repair records, car service log.",
    "moving-day-relocation-planner": "Timeline, moving budget, box inventory and address-change tracker.",
    "plan-ahead-meal-grocery-planner": "Weekly meal plans, grocery lists, pantry inventory and a spreadsheet.",
    "pet-care-record-book": "Vet visits, vaccines, medicine, daily care and pet-sitter pages.",
    "holiday-gift-budget-planner": "Gift lists, spending against your budget, card list and countdown.",
    "holiday-hosting-dinner-planner": "Guest list, menu, grocery list, prep countdown and seating plan.",
    "new-year-goal-habit-planner": "Year review, goal plans, habit trackers and check-ins.",
}


def product_page(p):
    esc = html.escape
    u = usd(p)
    imgs = p["images"]
    thumbs = "".join(
        f'<button type="button" aria-pressed="{"true" if i==0 else "false"}" data-src="{{R}}assets/img/{im["file"]}.webp" data-alt="{esc(im["alt"])}" aria-label="Show preview: {esc(im["alt"])}">'
        f'<img src="{{R}}assets/img/{im["file"]}-800.webp" width="800" height="600" alt="" loading="lazy"></button>'
        for i, im in enumerate(imgs))
    buy_ticks = "".join(f'<li>{esc(t)}</li>' for t in p.get("buy_ticks") or [])
    story_cols = []
    for block in p.get("story") or []:
        paras = "".join(f'<p>{esc(para)}</p>' for para in block.get("paragraphs") or [])
        note = f'<div class="note">{block["note_html"]}</div>' if block.get("note_html") else ""
        story_cols.append(f'<div class="prose"><h2>{esc(block["heading"])}</h2>{paras}{note}</div>')
    story = '<section class="paper2"><div class="wrap grid2">' + "".join(story_cols) + "</div></section>" if story_cols else ""
    files = "".join(
        f'<li><span class="ftype{" " + esc(f["badge"], quote=True) if f.get("badge") else ""}">{esc(f["type"])}</span>'
        f'<div><strong>{esc(f["name"])}</strong>{esc(f.get("detail") or "")}</div></li>'
        for f in p.get("included") or [])
    included_note = f'<p class="small" style="margin-top:12px">{esc(p["included_note"])}</p>' if p.get("included_note") else ""
    toc = "".join(
        f'<li><strong>{esc(item["strong"])}</strong> {esc(item.get("rest") or "")}</li>'
        for item in p.get("inside") or [])
    inside = f'''<div>
<h2>{esc(p.get("inside_heading") or "Inside the product")}</h2>
<ul class="toc">
{toc}
</ul>
</div>''' if toc else ""
    included = f'''<section id="included"><div class="wrap grid2">
<div>
<h2>What's included</h2>
<ul class="files">
{files}
</ul>
{included_note}
</div>
{inside}
</div></section>''' if files or toc else ""
    good = "".join(f'<li>{esc(t)}</li>' for t in p.get("good_for") or [])
    # Keep catalog specs, but always derive the Price row from price_usd so it cannot drift.
    specs = []
    seen_price = False
    for row in p.get("specs") or []:
        if row[0] == "Price":
            specs.append(("Price", f"${u}, paid with PayPal, or as {u} USDC (Solana or Polygon) or {u} USDT (TRC20 or Polygon)"))
            seen_price = True
        else:
            specs.append((row[0], row[1]))
    if not seen_price:
        specs.append(("Price", f"${u}, paid with PayPal, or as {u} USDC (Solana or Polygon) or {u} USDT (TRC20 or Polygon)"))
    spec_rows = "".join(f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in specs)
    notes = "".join(f'<li>{esc(n)}</li>' for n in p.get("please_note") or [])
    crumbs_label = esc(p.get("nav_label") or p["title"])
    lp = list_usd(p)
    savebox = (f'<p class="savebox">Regular price if bought separately: <s>${lp}</s><br>'
               f'<strong>You save ${save_usd(p)} ({save_pct(p)}% off)</strong> &middot; lifetime access, pay once</p>') if lp else ""
    bundle_items = ""
    if kind(p) == "bundle":
        cards = "".join(
            f'''<a class="inc-card" href="{{R}}products/{s_}/">{img(PM[s_]["images"][0]["file"], PM[s_]["images"][0]["alt"], sizes="(max-width: 700px) 100vw, 260px")}
<span><strong>{esc(PM[s_]["title"])}</strong><span class="small">{esc(BLURB.get(s_, ""))}</span><span class="small">Sold separately for ${usd(PM[s_])}</span></span></a>'''
            for s_ in p.get("includes") or [])
        bundle_items = f'''<section id="in-the-bundle"><div class="wrap">
<h2>What's in the bundle</h2>
<p class="lead" style="margin-bottom:18px">{len(p.get("includes") or [])} complete planners, worth ${lp} if bought one by one. You pay ${u}.</p>
<div class="inc-grid">{cards}</div>
</div></section>'''
    related = ""
    if p.get("related"):
        rc = "".join(
            f'''<a class="inc-card" href="{{R}}products/{r_["slug"]}/">{img(PM[r_["slug"]]["images"][0]["file"], PM[r_["slug"]]["images"][0]["alt"], sizes="(max-width: 700px) 100vw, 260px")}
<span><strong>{esc(PM[r_["slug"]]["title"])}</strong><span class="small">{esc(r_["blurb"])}</span><span class="small">{"<s class=\'was\'>$" + list_usd(PM[r_["slug"]]) + "</s> " if list_usd(PM[r_["slug"]]) else ""}${usd(PM[r_["slug"]])}</span></span></a>'''
            for r_ in p["related"])
        related = f'''<section class="paper2"><div class="wrap">
<h2>You might also like</h2>
<div class="inc-grid" style="margin-top:18px">{rc}</div>
</div></section>'''
    body = f'''
<div class="wrap"><p class="crumbs"><a href="{{R}}">Home</a> / <a href="{{R}}index.html#shop">Shop</a> / {crumbs_label}</p></div>
<div class="wrap pp">
<div>
<div class="gallery-main">{img(imgs[0]["file"], imgs[0]["alt"], eager=True, sizes="(max-width: 900px) 100vw, 640px").replace('class="shot"','class="shot" id="mainimg"')}</div>
<div class="thumbs" id="thumbs">{thumbs}</div>
</div>
<aside class="buybox"><div class="card">
<p class="eyebrow">Digital download</p>
<h1 style="font-size:clamp(1.7rem,3.2vw,2.3rem)">{esc(p["title"])}</h1>
<p class="meta">{esc(p.get("subtitle") or "")}</p>
<p class="price">{money_line(p, lead="Pay")}</p>
{savebox}
<ul class="ticks" style="margin-top:16px">
{buy_ticks}</ul>
<div class="btn-row"><a class="btn rust" href="{{R}}checkout/?p={esc(p["slug"], quote=True)}">Buy for ${u}</a>{paypal_form(p, cancel_path="products/" + p["slug"] + "/")}<a class="btn alt" href="#included">What's included</a></div>
<p class="small" style="margin-top:14px">Pay with PayPal, or continue to checkout to pay with USDC or USDT. Files are delivered by email. Nothing physical is shipped.</p>
{DELIVERY_NOTE}
</div></aside>
</div>
{story}
{bundle_items}
{included}
<section class="paper2"><div class="wrap grid2">
<div>
<h2>Good for</h2>
<ul class="ticks">
{good}</ul>
</div>
<div>
<h2>Details</h2>
<table class="spec">
{spec_rows}
</table>
</div>
</div></section>
<section><div class="wrap prose">
<h2>Please note</h2>
<ul>
{notes}
</ul>
<div class="btn-row" style="margin-top:20px"><a class="btn rust" href="{{R}}checkout/?p={esc(p["slug"], quote=True)}">Buy for ${u}</a>{paypal_form(p, cancel_path="products/" + p["slug"] + "/")}<a class="btn alt" href="{{R}}how-to-buy/">How buying works</a></div>
<p class="small" style="margin-top:12px">{DELIVERY_NOTE_SMALL}</p>
</div></section>
{related}
'''
    page(f"products/{p['slug']}/index.html", p["title"], p.get("description") or p.get("short") or p["title"],
         body, "home", og_image=og_for(p), og_alt=p.get("og_alt") or p["title"],
         scripts=gallery_js + '<script src="{R}assets/paypal-buy.js" defer></script>')


for prod in PRODUCTS:
    product_page(prod)

# ---------- HOW TO BUY ----------
how = f'''
<section><div class="wrap prose">
<p class="eyebrow">Buying guide</p>
<h1>How to buy</h1>
<p class="lead">Jalu Press accepts <strong>PayPal</strong> (in US dollars) and two stablecoins: <strong>USDC</strong> and <strong>USDT</strong>. USDC can be sent on Solana or Polygon, and USDT on TRC20 (Tron) or Polygon. Prices are in US dollars.</p>

<h2>Pay with PayPal</h2>
<ol>
<li><strong>Pick your product</strong> and click <strong>Pay with PayPal</strong> on the product page, or choose PayPal at checkout.</li>
<li><strong>Pay on PayPal's site</strong> in USD, using your PayPal balance or the payment methods PayPal offers you there.</li>
<li><strong>Receive your files.</strong> After you pay, you will see a thank-you page. Your files are emailed to the email address on your PayPal account (or the delivery email you entered at checkout), usually within 15 minutes after payment. It is not instant: we check for new payments every 10 minutes. Please check your spam folder if you don't see them.</li>
</ol>
<p>You do not need to email us first for a PayPal order. If the files have not arrived after 30 minutes, check your spam folder, then write to <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a> with your PayPal transaction details or order reference. (If PayPal holds a payment as pending, for example an eCheck, delivery waits until it clears.)</p>

<h2>Pay with USDC or USDT</h2>
<p>For crypto, you pay the same number of tokens as the dollar price, plus a few unique hundredths of a cent that identify your order (for example, $12 = 12.0347 USDC).</p>
<ol>
<li><strong>Pick your product</strong> and open its checkout.</li>
<li><strong>Enter your email</strong> so we know where to send your files. A name is optional.</li>
<li><strong>Choose a network:</strong> USDC on Solana or Polygon, or USDT on TRC20 or Polygon.</li>
<li><strong>Email us your order</strong> with the button on the checkout page. This step is required: it tells us which payment is yours.</li>
<li><strong>Send the exact amount</strong> shown (for example 12.0347 USDC), to the address shown, on the network shown. The last digits are unique to your order. Network fees are paid by the sender and are on top of the price.</li>
<li><strong>Receive your files.</strong> Our system checks the blockchain every few minutes. Once your payment is final, your files are emailed to you automatically as an attachment, usually within 20 minutes after your payment is final on the blockchain and your order email has reached us. If nothing has arrived after 40 minutes, check spam, then write to us.</li>
</ol>

<div class="note"><strong>Check the network before you send.</strong> Send only the token and network shown at checkout: USDC on <strong>Solana</strong> or <strong>Polygon</strong>, or USDT on <strong>Tron (TRC20)</strong> or <strong>Polygon</strong>. Tokens sent on another network (such as Ethereum or BNB Chain) or a different coin cannot be recovered. On Polygon, send native USDC, not the older bridged USDC.e. If you pay from an exchange, choose the matching network in its withdrawal screen.</div>

<h2>Token details</h2>
<table class="spec">
<tr><th>USDC on Solana</th><td>Official USDC mint: <span class="mono">EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v</span></td></tr>
<tr><th>USDT on TRC20</th><td>Official USDT contract on Tron: <span class="mono">TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t</span></td></tr>
<tr><th>USDC on Polygon</th><td>Native USDC (not USDC.e): <span class="mono">0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359</span></td></tr>
<tr><th>USDT on Polygon</th><td>Official USDT contract: <span class="mono">0xc2132D05D31c914a87C6611C10748AEb04B58e8F</span></td></tr>
</table>
<p class="small">Our receive addresses are shown only on the checkout page of this website. Jalu Press will never message you first with a payment address, and never asks for a seed phrase, private key or password.</p>

<h2>What we do not accept</h2>
<p>We do not accept credit or debit cards or bank transfers directly on this site (you can pay by card through PayPal). Other coins or networks are not accepted.</p>

<h2>Questions</h2>
<p>See <a href="{{R}}terms/">Help, license &amp; refunds</a> for delivery, license and refund details.</p>
<div class="btn-row" style="margin-top:20px"><a class="btn" href="{{R}}index.html#shop">Browse the shop</a></div>
</div></section>
'''
page("how-to-buy/index.html", "How to buy", "How to buy from Jalu Press with PayPal, or USDC or USDT on Solana, TRC20 or Polygon.", how, "how")

# ---------- ABOUT ----------
about = '''
<section><div class="wrap prose">
<p class="eyebrow">About</p>
<h1>About Jalu Press</h1>
<p class="lead">Jalu Press publishes practical English ebooks and light tools: printables, workbooks and trackers that help people organize one important part of life.</p>
<p>Each product is original, written and designed in-house, and tested to print well and work in the free tools most people already have. Where a product draws on public guidance, the sources are credited inside it.</p>
<h2>How we work</h2>
<ul>
<li><strong>Digital only.</strong> Every product is a download. Nothing physical is shipped.</li>
<li><strong>Simple checkout.</strong> We accept PayPal, plus USDC on Solana or Polygon and USDT on TRC20 or Polygon.</li>
<li><strong>Light on data.</strong> No accounts, no tracking scripts, no advertising cookies. See <a href="{R}privacy/">Privacy</a>.</li>
<li><strong>For readers worldwide.</strong> Products are written in plain English and avoid single-country assumptions wherever they can.</li>
</ul>
<h2>Contact</h2>
<p>Questions and order support: <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a>.</p>
</div></section>
'''
page("about/index.html", "About", "About Jalu Press: practical English ebooks and light tools, sold as digital downloads.", about, "about")

# ---------- TERMS ----------
terms = '''
<section><div class="wrap prose">
<p class="eyebrow">Help</p>
<h1>Help, license &amp; refunds</h1>
<h2>Delivery</h2>
<p>All Jalu Press products are digital files. Nothing physical is shipped. Please check your spam folder if your email has not arrived.</p>
<ul>
<li><strong>PayPal.</strong> After you pay, your files are emailed to the email address on your PayPal account, or the delivery email you entered at checkout, usually within 15 minutes. It is not instant: we check for new payments every 10 minutes. If nothing has arrived after 30 minutes, check your spam folder, then write to us.</li>
<li><strong>USDC or USDT.</strong> After your payment is confirmed on-chain and we have your order email, your files are emailed automatically, as an attachment, to the address you gave at checkout, usually within 20 minutes after the payment is final on the blockchain.</li>
</ul>
<h2>Payment</h2>
<p>We accept PayPal in US dollars, plus USDC on Solana or Polygon and USDT on TRC20 (Tron) or Polygon. Crypto prices are paid as the same number of tokens; network fees are paid by the sender. Blockchain payments cannot be reversed by us or by you, so please check the amount, network and address before sending. PayPal payments are processed by PayPal. See <a href="{R}how-to-buy/">How to buy</a>.</p>
<h2>Refunds and problems</h2>
<ul>
<li>If a file is faulty or will not open, tell us and we will fix it or send a replacement.</li>
<li>If we cannot deliver your order, we refund a PayPal payment through PayPal, or a crypto payment in the same token to a wallet address on the same network that you give us.</li>
<li>Because files can be kept once downloaded, completed orders are otherwise not refundable. Please read the product page and previews before you buy.</li>
<li>Crypto payments sent on the wrong network, in the wrong token or to an address not shown on our checkout page cannot be recovered by us.</li>
</ul>
<h2>License</h2>
<p>Your purchase gives you a personal, non-transferable license to use the files for yourself and your household. You may print as many copies as your household needs. You may not resell, share, upload or redistribute the files, or include them in other products.</p>
<h2>Not professional advice</h2>
<p>Jalu Press products are organizing and planning tools. They are not legal, medical, financial or emergency-services advice and do not replace guidance from qualified professionals or your local authorities.</p>
<h2>Contact</h2>
<p>Questions and order support: <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a>.</p>
</div></section>
'''
page("terms/index.html", "Help, license & refunds", "Delivery, payment, refund and license information for Jalu Press digital products.", terms, "terms")

# ---------- PRIVACY ----------
priv = '''
<section><div class="wrap prose">
<p class="eyebrow">Privacy</p>
<h1>Privacy</h1>
<p class="lead">Short version: we collect as little as possible.</p>
<ul>
<li><strong>No tracking.</strong> This site uses no analytics, advertising or social tracking scripts and sets no cookies.</li>
<li><strong>Hosting.</strong> The site is a static website hosted on GitHub Pages. GitHub may log basic technical data such as IP addresses for security, under its own privacy statement.</li>
<li><strong>Checkout.</strong> The details you type on the checkout page stay in your browser. For a crypto order they are only sent to us if you choose to email us your order. For a PayPal order, the product, amount and (if you entered one) delivery email are sent to PayPal to complete payment. We use this information only to deliver your files and answer you.</li>
<li><strong>PayPal.</strong> If you pay with PayPal you are taken to PayPal's website. PayPal processes your payment under its own privacy policy. We receive a payment notice with your PayPal name, email, amount and item, and use it only to deliver your files and for order support.</li>
<li><strong>Crypto payments.</strong> Blockchain transactions are public by nature. We see the sending address, amount and time of your payment, as anyone can.</li>
<li><strong>Never shared or sold.</strong> We do not sell or share your details, and we do not send marketing email unless you ask for it.</li>
<li><strong>Free sample pack.</strong> If you enter your email to get the free pack, the form is delivered to us by FormSubmit (formsubmit.co), a free form service. We keep your address, the date and the page you signed up on in a private file on our own computer, send you the pack and one short follow-up about our bundle, and nothing else. Every email has an unsubscribe link (reply with \"Unsubscribe\" in the subject) and we remove you on request. We never share or sell the list.</li>
<li><strong>What we never ask for on this site:</strong> passwords, card numbers, private keys or seed phrases. If you pay by card, you enter those details on PayPal's site, not on ours.</li>
</ul>
<p>You can ask us to delete your order emails at any time using the support address shown on the checkout page.</p>
</div></section>
'''
page("privacy/index.html", "Privacy", "Jalu Press privacy notice: no trackers, minimal data.", priv, "")

# ---------- CHECKOUT (product filled in by checkout.js from catalog.json + ?p=<slug>) ----------
co = '''
<div class="wrap"><p class="crumbs"><a href="{R}">Home</a> / Checkout</p></div>
<div class="wrap co" id="checkout" data-config="{R}assets/payment-config.json" data-catalog="{R}assets/catalog.json">
<div>
<h1 style="font-size:2rem">Checkout</h1>
<div class="card" id="co-summary">
<div class="summary-row">
<img id="co-cover" src="" width="800" height="600" alt="">
<div><strong style="color:var(--ink)" id="co-title">Choose a product</strong><div class="small" id="co-format">Digital download</div>
<div class="price" style="font-size:1.5rem;margin-top:8px" id="co-price" data-price=""></div></div>
</div>
<hr style="border:0;border-top:1px solid var(--line);margin:18px 0">
<p class="small" style="margin:0">Pay with PayPal in USD, or with USDC (Solana or Polygon) or USDT (TRC20 or Polygon). For crypto, the price is paid as the same number of tokens, plus a few unique hundredths of a cent that identify your order. Network fees are paid by the sender.</p>
<p class="delivery-note" style="margin-top:14px"><strong>When you get it:</strong> by email, usually within 15 minutes after a PayPal payment, or about 20 minutes after a crypto payment is final on the blockchain. It is not instant. Nothing after 30 minutes (40 for crypto)? Check spam, then write to <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a>.</p>
</div>
<p class="small" style="margin-top:14px"><a href="{R}how-to-buy/">How buying works</a> &middot; <a href="{R}terms/">Refunds &amp; license</a></p>
</div>

<div>
<div class="card hidden" id="co-pick">
<p class="eyebrow">Shop</p>
<h2 style="font-size:1.6rem">Choose a product to buy</h2>
<p>Open checkout from a product page, or pick one below.</p>
<div class="product-pick" id="co-pick-list"></div>
</div>

<div class="card hidden" id="co-unknown">
<p class="eyebrow">Not found</p>
<h2 style="font-size:1.6rem">We could not find that product</h2>
<p>It may have been renamed or is no longer for sale. <a href="{R}index.html#shop">Browse the shop</a>.</p>
</div>

<div class="card status-closed" id="co-closed">
<p class="eyebrow">Opening soon</p>
<h2 style="font-size:1.6rem">Checkout is not open yet</h2>
<p>Our receive addresses have not been published yet, so orders cannot be paid today. Please check back soon.</p>
<div class="note">Please do not send crypto for a Jalu Press order to any address you received elsewhere. Our payment addresses will appear only on this page.</div>
</div>

<form class="card hidden" id="co-form" novalidate>
<h2 style="font-size:1.4rem">Your details</h2>
<div class="field"><label for="email">Email for delivery</label><input type="email" id="email" name="email" autocomplete="email" required placeholder="you@example.com"></div>
<div class="field"><label for="name">Name <span class="small">(optional)</span></label><input type="text" id="name" name="name" autocomplete="name"></div>
<fieldset class="field" style="border:0;padding:0;margin:0 0 16px"><legend style="font-weight:600;color:var(--ink);margin-bottom:8px">Pay with</legend>
<div class="radio-cards" id="methods"></div></fieldset>
<p class="small" id="co-err" role="alert" style="color:#a23b16"></p>
<button class="btn" type="submit" id="co-submit">Show payment details</button>
<p class="small" style="margin-top:12px" id="co-submit-hint">Nothing is charged or sent from this page. We never ask for passwords, card numbers, private keys or seed phrases.</p>
</form>
<form class="hidden" id="paypal-form" action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="jalurahadi@gmail.com">
<input type="hidden" name="item_name" value="">
<input type="hidden" name="item_number" value="">
<input type="hidden" name="amount" value="">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="no_note" value="1">
<input type="hidden" name="charset" value="utf-8">
<input type="hidden" name="rm" value="1">
<input type="hidden" name="return" value="">
<input type="hidden" name="cancel_return" value="">
<input type="hidden" name="invoice" value="">
<input type="hidden" name="custom" value="">
<input type="hidden" name="on0" value="Delivery email">
<input type="hidden" name="os0" value="">
</form>

<div class="card hidden" id="co-resume">
<p class="eyebrow">Order in progress</p>
<h2 style="font-size:1.3rem">Order <span id="r-ref"></span></h2>
<p>You started this order on this device: <strong id="r-amount"></strong>. If you already emailed it or paid, open it again instead of starting a new one, so the amounts match.</p>
<div class="btn-row"><button class="btn" type="button" id="r-open">Open this order</button><button class="btn alt" type="button" id="r-new">Start a new order</button></div>
</div>

<div class="card hidden" id="co-pay" aria-live="polite">
<p class="eyebrow">Order <span id="o-ref"></span></p>
<h2 style="font-size:1.4rem">Send exactly <span id="o-amount"></span></h2>
<p class="small">The last digits are unique to your order. They are how we match your payment automatically, so please send this exact amount (if your exchange takes a withdrawal fee, make sure the amount that arrives is exactly this).</p>

<h3 style="margin-top:20px">Step 1 &middot; Email your order <span style="color:#a23b16">(required)</span></h3>
<p><strong>Your files are sent automatically once we receive this email and your payment.</strong> Without this email we cannot match your payment to you. It goes to <span id="o-support"></span> and your files are sent to <strong id="o-email"></strong>.</p>
<div class="btn-row"><a class="btn rust" id="o-mail" href="#">Email my order details</a></div>
<details style="margin:10px 0 4px"><summary class="small">Email button not working? Copy the text instead</summary>
<textarea id="o-mailtext" readonly rows="9" style="width:100%;font-family:monospace;font-size:.85rem;margin-top:8px"></textarea>
<div class="btn-row"><button class="btn alt" type="button" id="o-copymail">Copy email text</button><span class="small" id="o-copiedmail"></span></div>
<p class="small">Send it from any email account with the subject exactly as shown, including order <span id="o-ref2"></span>.</p>
</details>

<h3 style="margin-top:20px">Step 2 &middot; Send <span id="o-amount2"></span></h3>
<p>Network: <strong id="o-net"></strong></p>
<label>Receive address</label>
<div class="addr mono" id="o-addr"></div>
<div class="btn-row"><button class="btn alt" type="button" id="o-copy">Copy address</button><span class="small" id="o-copied"></span></div>
<div class="qr-wrap hidden" id="o-qr"><img id="o-qr-img" alt="QR code for the receive address" width="180" height="180"></div>
<p class="small" style="margin-top:12px" id="o-token"></p>
<div class="note" style="margin:16px 0">Send only <strong id="o-tok2"></strong> on <strong id="o-net2"></strong>. Other tokens or networks cannot be recovered.</div>
<div class="field"><label for="txid">Transaction ID <span class="small">(optional, add it before emailing if you already paid)</span></label><input type="text" id="txid" autocomplete="off" spellcheck="false"></div>

<h3 style="margin-top:20px">Then</h3>
<p>We check the blockchain every 10 minutes. Once your payment is final and your order email is in, your files arrive by email, usually within 20 minutes (not instant). If nothing has arrived after 40 minutes, check your spam folder, then write to us. Keep your order reference; it is valid for 72 hours.</p>
</div>
</div>
</div>
'''
co_js = '<script src="{R}assets/checkout.js" defer></script>'
page("checkout/index.html", "Checkout", "Jalu Press checkout: pay with PayPal, or USDC or USDT on Solana, TRC20 or Polygon.", co, "", extra_head='<meta name="robots" content="noindex">\n', scripts=co_js)

# ---------- THANK YOU (PayPal return) ----------
thanks = """
<section><div class="wrap prose">
<p class="eyebrow">Thank you</p>
<h1>Thank you for your order</h1>
<p class="lead">If you paid with PayPal, your files will be emailed to you, usually within 15 minutes. It is not instant.</p>
<ol><li><strong>Now:</strong> PayPal confirms your payment and sends us a notice, usually within a minute or two.</li><li><strong>Every 10 minutes:</strong> our system checks for new payments and emails your files as a ZIP attachment.</li><li><strong>If nothing has arrived after 30 minutes:</strong> check your spam or junk folder, then write to <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a> with your order reference.</li></ol>
<p>We send the files to the email address on your PayPal account, and to the delivery email you entered at checkout if you used that option. Please check your spam or junk folder if you do not see the email.</p>
<p class="hidden" id="ty-ref"></p>
<div class="note">You do not need to email us first. If the files have not arrived after 30 minutes and they are not in your spam folder, write to <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a> with your PayPal transaction details or order reference, and we will help. (If PayPal marks your payment as pending, for example an eCheck, delivery waits until it clears.)</div>
<div class="btn-row" style="margin-top:20px"><a class="btn" href="{R}index.html#shop">Back to the shop</a><a class="btn alt" href="{R}terms/">Help &amp; refunds</a></div>
</div></section>
"""
thanks_js = """<script>
(function(){
  var q = new URLSearchParams(location.search);
  var ref = (q.get("ref") || q.get("cm") || q.get("invoice") || "").trim();
  var el = document.getElementById("ty-ref");
  if (el && ref) {
    el.textContent = "Your order reference is " + ref + ". Please keep it in case you need to contact us.";
    el.classList.remove("hidden");
  }
})();
</script>"""
page("thank-you/index.html", "Thank you", "Thank you for your Jalu Press order. Your files will be emailed to you, usually within 15 minutes.", thanks, "", extra_head='<meta name="robots" content="noindex">\n', scripts=thanks_js)

# ---------- FREE SAMPLE ----------
free_body = f"""
<div class="wrap"><p class="crumbs"><a href="{{R}}">Home</a> / Free sample pack</p></div>
<div class="wrap pp">
<div><div class="gallery-main"><img class="shot" src="{{R}}assets/img/free-home-starter-pack-cover.webp" srcset="{{R}}assets/img/free-home-starter-pack-cover-800.webp 800w, {{R}}assets/img/free-home-starter-pack-cover.webp 1600w" sizes="(max-width: 900px) 100vw, 640px" width="1600" height="1200" alt="The Home Starter Pack: seven free fillable pages from Jalu Press planners" decoding="async"></div></div>
<aside class="buybox"><div class="card">
<p class="eyebrow">Free download</p>
<h1 style="font-size:clamp(1.7rem,3.2vw,2.3rem)">The Home Starter Pack</h1>
<p class="meta">7 fillable pages to get your household in order</p>
<p>Enter your email and we send you the pack as a PDF. Print it, or type into it on screen.</p>
{signup_form("free-page", "free")}
<p class="delivery-note"><strong>When you get it:</strong> by email, usually within 15 minutes (not instant). If it has not arrived after 30 minutes, check your spam folder, then write to <a href="mailto:{SUPPORT}">{SUPPORT}</a>.</p>
</div></aside>
</div>
<section class="paper2"><div class="wrap grid2">
<div class="prose">
<h2>What is inside</h2>
<ul class="ticks">
<li><strong>Household at a glance</strong>: who lives here, pets, and the key details someone would need in a hurry.</li>
<li><strong>Water and food planner</strong>: how much to store for your household, in liters and US gallons.</li>
<li><strong>3-day home supplies checklist</strong>: the essentials to have ready if the power or water goes out.</li>
<li><strong>Winter home checklist</strong>: the jobs worth doing before the cold sets in.</li>
<li><strong>Moving timeline, 8 to 5 weeks before</strong>: what to do early when a move is coming.</li>
<li><strong>Weekly meal plan and grocery list</strong>: plan the week once and shop in one pass.</li>
</ul>
<p>Plus a one-page guide. Every page is a real page from one of our paid planners, so you can see exactly what you would get.</p>
</div>
<div class="prose">
<h2>How it works</h2>
<ol>
<li><strong>Enter your email</strong> above and press the button.</li>
<li><strong>We email you the PDF</strong>, usually within 15 minutes, as an attachment.</li>
<li><strong>Fill it in</strong> on screen (Adobe Acrobat Reader is free) or print it.</li>
</ol>
<p>A few days later we send one short email about the Home &amp; Household Starter Bundle, which has all five complete planners for $24 instead of $48. That is the only follow-up, and you can unsubscribe at any time.</p>
<div class="note"><strong>Your privacy.</strong> We use your email only to send the pack and that one follow-up. We never share or sell it, and every email has an unsubscribe link. See the <a href="{{R}}privacy/">privacy notice</a>.</div>
</div>
</div></section>
"""
page("free/index.html", "Free Home Starter Pack: 7 printable pages",
     "Get The Home Starter Pack free: seven fillable pages from Jalu Press planners (household info, water and food, 3-day supplies, winter checklist, moving timeline, meal plan). Sent by email.",
     free_body, "", og_image=og_abs("assets/img/og-free.jpg"),
     og_alt="The Home Starter Pack: seven free fillable pages from Jalu Press planners",
     scripts='<script src="{R}assets/signup.js" defer></script>')

free_thanks = """
<section><div class="wrap prose">
<p class="eyebrow">Almost there</p>
<h1>Check your email</h1>
<p class="lead">Your free Home Starter Pack is on its way. It usually arrives within 15 minutes. It is not instant.</p>
<p>If it has not arrived after 30 minutes, check your spam or junk folder, then write to <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a>.</p>
<p>While you wait, see the <a href="{R}products/home-household-starter-bundle/">Home &amp; Household Starter Bundle</a>: five complete planners for $24 instead of $48.</p>
<div class="btn-row" style="margin-top:20px"><a class="btn" href="{R}index.html#bundles">See the bundles</a><a class="btn alt" href="{R}">Back to the shop</a></div>
</div></section>
"""
page("free/thanks/index.html", "Check your email", "Your free Home Starter Pack is on its way.", free_thanks, "",
     extra_head='<meta name="robots" content="noindex">\n')

# ---------- 404 (served at any depth, so it computes its own base) ----------
nf_body = '''
<section><div class="wrap prose">
<h1>Page not found</h1>
<p class="lead">That page does not exist. It may have moved.</p>
<div class="btn-row"><a class="btn" href="{R}">Go to the homepage</a></div>
</div></section>'''
page("404.html", "Page not found", "Page not found.", nf_body, "", depth=0,
     extra_head='<script>(function(){var b=location.hostname.endsWith("github.io")?"/jalupress/":"/";document.write(\'<base href="\'+b+\'">\');})();</script>\n')

shutil.copy(HERE / "catalog.json", ROOT / "assets" / "catalog.json")
print("built %d product(s)" % len(PRODUCTS))
