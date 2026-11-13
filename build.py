#!/usr/bin/env python3
"""Static site builder for Jalu Press. Writes HTML into ./docs.
All internal links are RELATIVE so the site works both at
https://jalusaja.github.io/jalupress/ and at https://jalupress.com/."""
import os, html
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
YEAR = "2026"

P = {
 "slug": "grab-and-go-household-binder",
 "title": "The Grab-and-Go Household Binder",
 "subtitle": "Emergency Plan, Important-Info Organizer & Expiry Tracker",
 "price": "12",
 "img": "binder",
}

LOGO = '''<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="12" fill="#16343a"/><path d="M18 14h22a6 6 0 0 1 6 6v30H24a6 6 0 0 1-6-6z" fill="#f6f1e7"/><path d="M18 44a6 6 0 0 1 6-6h22" fill="none" stroke="#16343a" stroke-width="3"/><path d="M36 14v14l-4-3-4 3V14" fill="#b9552a"/></svg>'''

NAV = [("Shop", "index.html#shop", "home"), ("How to buy", "how-to-buy/", "how"),
       ("About", "about/", "about"), ("Help & terms", "terms/", "terms")]

def page(path, title, desc, body, active="", depth=None, extra_head="", scripts=""):
    depth = path.count("/") if depth is None else depth
    r = "../" * depth or "./"
    nav = "".join(
        f'<a href="{r}{h}"{" aria-current=page" if k==active else ""}>{t}</a>' for t, h, k in NAV)
    full_title = f"{title} | Jalu Press" if title != "Jalu Press" else "Jalu Press: practical English ebooks and light tools"
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{extra_head}<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta property="og:site_name" content="Jalu Press">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#16343a">
<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="{r}">{LOGO}<span class="brand-name">Jalu Press</span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>
<main id="main">
{body.replace("{R}", r)}
</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div><a class="brand" href="{r}" style="margin-bottom:12px">{LOGO}<span class="brand-name">Jalu Press</span></a>
<p>Practical English ebooks and light tools, sold as instant digital downloads. Paid in USDC (Solana or Polygon) or USDT (TRC20 or Polygon) only. Nothing physical is shipped.</p></div>
<div><h3>Shop</h3><ul>
<li><a href="{r}products/{P["slug"]}/">Household Binder</a></li>
<li><a href="{r}how-to-buy/">How to buy</a></li>
<li><a href="{r}checkout/?p={P["slug"]}">Checkout</a></li></ul></div>
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
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(doc)

def img(name, alt, cls="shot", w=1600, h=1200, eager=False, sizes="(max-width: 900px) 100vw, 600px"):
    b = f'{{R}}assets/img/{P["img"]}-{name}'
    return (f'<img class="{cls}" src="{b}.webp" srcset="{b}-800.webp 800w, {b}.webp 1600w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{html.escape(alt)}"{"" if eager else " loading=lazy"} decoding="async">')

PAY_BADGES = '''<ul class="pay-badges" aria-label="Accepted payment">
<li class="badge"><span class="dot"></span>USDC on Solana</li>
<li class="badge"><span class="dot"></span>USDC on Polygon</li>
<li class="badge"><span class="dot"></span>USDT on TRC20 (Tron)</li>
<li class="badge"><span class="dot"></span>USDT on Polygon</li>
<li class="badge">Instant digital download</li></ul>'''

# ---------- HOME ----------
home = f'''
<section class="hero"><div class="wrap hero-grid">
<div>
<p class="eyebrow">Jalu Press</p>
<h1>Practical English ebooks and light tools for real life.</h1>
<p class="lead">Clear, well-made printables, workbooks and trackers that help you get one thing in order, then keep it that way. Original work, delivered as digital files.</p>
{PAY_BADGES}
<div class="btn-row"><a class="btn" href="{{R}}products/{P["slug"]}/">See the Household Binder</a><a class="btn alt" href="{{R}}how-to-buy/">How buying works</a></div>
</div>
<div>{img("cover","Cover of The Grab-and-Go Household Binder with the companion expiry tracker", eager=True)}</div>
</div></section>

<section class="paper2" id="shop"><div class="wrap">
<p class="eyebrow">First release</p>
<h2>Shop</h2>
<div class="product-card">
<a href="{{R}}products/{P["slug"]}/">{img("preview-1-whats-inside","Preview of pages inside the binder")}</a>
<div>
<h3 style="font-size:1.6rem">{P["title"]}</h3>
<p class="meta">{P["subtitle"]}</p>
<p>One organized place for what your household needs in an emergency: who to call, where to meet, where the important papers are, medical details for each person, and what to keep ready for three days.</p>
<ul class="ticks">
<li>44-page fillable PDF, in US Letter and A4</li>
<li>Expiry and review tracker for Excel or Google Sheets</li>
<li>Country-neutral, metric and imperial units</li></ul>
<p class="price">$12 <small>Paid as 12 USDC (Solana or Polygon) or 12 USDT (TRC20 or Polygon)</small></p>
<div class="btn-row" style="margin-top:16px"><a class="btn" href="{{R}}products/{P["slug"]}/">View details</a></div>
</div></div>
</div></section>

<section><div class="wrap">
<h2>Why Jalu Press</h2>
<div class="grid3" style="margin-top:22px">
<div class="card"><h3>Made to be used</h3><p>Every product is built around a job you actually need to do, with clear fields, sensible order and pages that print cleanly at home.</p></div>
<div class="card"><h3>Written for anywhere</h3><p>Plain English for readers worldwide. No single-country defaults where they would get in your way, and both metric and imperial where it matters.</p></div>
<div class="card"><h3>Simple crypto checkout</h3><p>Pay with a stablecoin you already hold: USDC on Solana or Polygon, or USDT on TRC20 or Polygon. No cards, no accounts, no subscription.</p></div>
</div></div></section>

<section class="band"><div class="wrap">
<p class="eyebrow">How it works</p>
<h2>Buying takes three steps</h2>
<div class="grid3" style="margin-top:22px">
<div class="card"><div class="step-n">1</div><h3>Choose a product</h3><p>Read the details and preview pages, and check it suits you before you pay.</p></div>
<div class="card"><div class="step-n">2</div><h3>Pay in USDC or USDT</h3><p>Checkout shows the exact amount for your order, the network and the receive address.</p></div>
<div class="card"><div class="step-n">3</div><h3>Get your files</h3><p>Once the payment is confirmed on-chain, your files are emailed to you automatically.</p></div>
</div>
<p style="margin-top:22px"><a href="{{R}}how-to-buy/">Read the full buying guide &rarr;</a></p>
</div></section>
'''
page("index.html", "Jalu Press", "Jalu Press makes practical English ebooks and light tools, sold as digital downloads and paid in USDC or USDT on Solana, TRC20 or Polygon.", home, "home", depth=0,
     extra_head='<meta property="og:image" content="https://jalupress.com/assets/img/og-binder.jpg">\n')

# ---------- PRODUCT ----------
imgs = [("cover","Cover and companion tracker"),("preview-1-whats-inside","What's inside: 44 pages in six parts"),
        ("preview-2-fill-or-print","Fill it in on screen or print and write"),("preview-3-tracker","The expiry and review tracker"),
        ("preview-4-any-country","Written to work in any country")]
thumbs = "".join(
  f'<button type="button" aria-pressed="{"true" if i==0 else "false"}" data-src="{{R}}assets/img/{P["img"]}-{n}.webp" data-alt="{html.escape(a)}" aria-label="Show preview: {html.escape(a)}">'
  f'<img src="{{R}}assets/img/{P["img"]}-{n}-800.webp" width="800" height="600" alt="" loading="lazy"></button>' for i,(n,a) in enumerate(imgs))

prod = f'''
<div class="wrap"><p class="crumbs"><a href="{{R}}">Home</a> / <a href="{{R}}index.html#shop">Shop</a> / Household Binder</p></div>
<div class="wrap pp">
<div>
<div class="gallery-main">{img("cover", imgs[0][1], eager=True, sizes="(max-width: 900px) 100vw, 640px").replace('class="shot"','class="shot" id="mainimg"')}</div>
<div class="thumbs" id="thumbs">{thumbs}</div>
</div>
<aside class="buybox"><div class="card">
<p class="eyebrow">Digital download</p>
<h1 style="font-size:clamp(1.7rem,3.2vw,2.3rem)">{P["title"]}</h1>
<p class="meta">{P["subtitle"]}</p>
<p class="price">$12 <small>Pay 12 USDC (Solana or Polygon) or 12 USDT (TRC20 or Polygon). No cards.</small></p>
<ul class="ticks" style="margin-top:16px">
<li>Fillable PDF, 44 pages, US Letter + A4</li>
<li>Expiry &amp; review tracker (.xlsx, works in Google Sheets)</li>
<li>Instructions for filling in, printing and keeping it current</li>
<li>Personal and household license</li></ul>
<div class="btn-row"><a class="btn rust" href="{{R}}checkout/?p={P["slug"]}">Buy for $12</a><a class="btn alt" href="#included">What's included</a></div>
<p class="small" style="margin-top:14px">Files are delivered by email after your payment is confirmed. Nothing physical is shipped.</p>
</div></aside>
</div>

<section class="paper2"><div class="wrap grid2">
<div class="prose">
<h2>Everything in one place, before you need it</h2>
<p>When something goes wrong, such as a power cut, a storm, a sudden hospital visit or a quick evacuation, the information you need is often scattered across phones, drawers and memories. This binder gathers it into one place, so you, or anyone helping you, can find it in seconds.</p>
<p>Fill it in on screen and save it, or print the blank pages and write by hand. Every field is a clear box or line, margins are safe for home printers, and the pages read well in black and white.</p>
<p>It is written for households in any country. You add your own local emergency number, water amounts appear in both liters and US gallons, and there is a cross-border section for families with papers, property or relatives in more than one country.</p>
</div>
<div class="prose">
<h2>A tracker that keeps it current</h2>
<p>A binder is only useful if it is up to date. The companion spreadsheet lists your stored supplies and your documents (passports, ID cards, residence permits, insurance policies, vehicle papers) with their expiry dates. Each row shows the days left and a clear status: OK, Expires soon, Expired or No date.</p>
<p>A dashboard counts what needs attention, a calculator works out water and food targets for your household, and a review tab tells you when your next six-month check is due.</p>
<div class="note"><strong>Private by design.</strong> The binder records <em>where</em> things are and <em>who</em> to call. It never asks for passwords, PINs, full account or card numbers, document numbers or crypto seed phrases.</div>
</div>
</div></section>

<section id="included"><div class="wrap grid2">
<div>
<h2>What's included</h2>
<ul class="files">
<li><span class="ftype">PDF</span><div><strong>Household Binder, US Letter</strong>44 fillable pages, 8.5 &times; 11 in</div></li>
<li><span class="ftype">PDF</span><div><strong>Household Binder, A4</strong>44 fillable pages, 210 &times; 297 mm, same content</div></li>
<li><span class="ftype x">XLSX</span><div><strong>Expiry &amp; review tracker</strong>For Microsoft Excel or Google Sheets (import steps included)</div></li>
<li><span class="ftype i">PDF</span><div><strong>Instructions</strong>How to fill in, print, assemble and keep everything up to date</div></li>
</ul>
<p class="small" style="margin-top:12px">Delivered together as one ZIP download.</p>
</div>
<div>
<h2>Inside the binder</h2>
<ul class="toc">
<li><strong>Start here:</strong> how to use it, plus a privacy and safety page</li>
<li><strong>People &amp; contacts:</strong> household at a glance, pets, emergency and out-of-area contacts, neighbors, school and work, pocket contact cards</li>
<li><strong>Our plan &amp; home:</strong> meeting points and routes, quick actions, staying in touch without phone or internet, utility shut-offs, providers</li>
<li><strong>Health:</strong> five medical profile pages</li>
<li><strong>Papers &amp; money:</strong> document locators, cross-border add-on, emergency cash, insurance and digital-accounts locators</li>
<li><strong>Supplies &amp; kits:</strong> water and food planner, 3-day checklists, grab bag and car kit lists</li>
<li><strong>Care &amp; review:</strong> caring for a dependent, a backup person plan, "where the papers are", six-month review log, at-a-glance sheet</li>
</ul>
</div>
</div></section>

<section class="paper2"><div class="wrap grid2">
<div>
<h2>Good for</h2>
<ul class="ticks">
<li>Parents and anyone running a busy household</li>
<li>People caring for an older relative or another dependent</li>
<li>Expats, digital nomads and families with documents in more than one country</li>
<li>Renters and homeowners who want a plan without buying a pre-made kit</li></ul>
</div>
<div>
<h2>Details</h2>
<table class="spec">
<tr><th>Format</th><td>Fillable PDF (2 sizes), XLSX spreadsheet, instructions PDF</td></tr>
<tr><th>Pages</th><td>44 per PDF, 1,300+ fillable fields, 200+ check boxes</td></tr>
<tr><th>Works in</th><td>Adobe Acrobat Reader (free), Apple Preview and other form-capable PDF readers; Excel or Google Sheets</td></tr>
<tr><th>Printing</th><td>Color or black and white, home-printer margins</td></tr>
<tr><th>Language</th><td>English</td></tr>
<tr><th>Price</th><td>$12, paid as 12 USDC (Solana or Polygon) or 12 USDT (TRC20 or Polygon)</td></tr>
<tr><th>License</th><td>Personal and household use. Print as many copies as your household needs. Please do not resell or share the files.</td></tr>
</table>
</div>
</div></section>

<section><div class="wrap prose">
<h2>Please note</h2>
<ul>
<li>This binder is an organizing tool. It is not legal, medical, financial or emergency-services advice, and it does not replace instructions from your local authorities or emergency services.</li>
<li>The "where the papers are" page is not a will, power of attorney, advance directive or any other legal document. No legal templates are included.</li>
<li>Emergency numbers, rules and recommended supplies vary by country and change over time. Check them locally.</li>
<li>Jalu Press is independent and is not affiliated with or endorsed by any government agency or public body. Sources and credits for the public guidance the binder draws on are listed inside the product.</li>
</ul>
<div class="btn-row" style="margin-top:20px"><a class="btn rust" href="{{R}}checkout/?p={P["slug"]}">Buy for $12</a><a class="btn alt" href="{{R}}how-to-buy/">How buying works</a></div>
</div></section>
'''
gallery_js = '''<script>
(function(){var m=document.getElementById('mainimg'),t=document.getElementById('thumbs');if(!m||!t)return;
t.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
m.removeAttribute('srcset');m.src=b.dataset.src;m.alt=b.dataset.alt;
t.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});});})();
</script>'''
page(f"products/{P['slug']}/index.html", P["title"], "A 44-page fillable emergency binder (US Letter and A4) with an expiry and review tracker for Excel or Google Sheets. $12, paid in USDC or USDT.", prod, "home",
     extra_head='<meta property="og:image" content="https://jalupress.com/assets/img/og-binder.jpg">\n', scripts=gallery_js)

# ---------- HOW TO BUY ----------
how = f'''
<section><div class="wrap prose">
<p class="eyebrow">Buying guide</p>
<h1>How to buy</h1>
<p class="lead">Jalu Press accepts two stablecoins only: <strong>USDC</strong> and <strong>USDT</strong>. USDC can be sent on Solana or Polygon, and USDT on TRC20 (Tron) or Polygon. Prices are in US dollars and you pay the same number of tokens, plus a few unique hundredths of a cent that identify your order (for example, $12 = 12.0347 USDC).</p>

<h2>Step by step</h2>
<ol>
<li><strong>Pick your product</strong> and open its checkout.</li>
<li><strong>Enter your email</strong> so we know where to send your files. A name is optional.</li>
<li><strong>Choose a network:</strong> USDC on Solana or Polygon, or USDT on TRC20 or Polygon.</li>
<li><strong>Email us your order</strong> with the button on the checkout page. This step is required: it tells us which payment is yours.</li>
<li><strong>Send the exact amount</strong> shown (for example 12.0347 USDC), to the address shown, on the network shown. The last digits are unique to your order. Network fees are paid by the sender and are on top of the price.</li>
<li><strong>Receive your files.</strong> Our system checks the blockchain every few minutes. Once your payment is final, your files are emailed to you automatically as an attachment, usually within 30 minutes.</li>
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
<p>Credit or debit cards, PayPal, bank transfers and other coins or networks are not accepted.</p>

<h2>Questions</h2>
<p>See <a href="{{R}}terms/">Help, license &amp; refunds</a> for delivery, license and refund details.</p>
<div class="btn-row" style="margin-top:20px"><a class="btn" href="{{R}}index.html#shop">Browse the shop</a></div>
</div></section>
'''
page("how-to-buy/index.html", "How to buy", "How to buy from Jalu Press with USDC or USDT on Solana, TRC20 or Polygon.", how, "how")

# ---------- ABOUT ----------
about = f'''
<section><div class="wrap prose">
<p class="eyebrow">About</p>
<h1>About Jalu Press</h1>
<p class="lead">Jalu Press publishes practical English ebooks and light tools: printables, workbooks and trackers that help people organize one important part of life.</p>
<p>Each product is original, written and designed in-house, and tested to print well and work in the free tools most people already have. Where a product draws on public guidance, the sources are credited inside it.</p>
<h2>How we work</h2>
<ul>
<li><strong>Digital only.</strong> Every product is a download. Nothing physical is shipped.</li>
<li><strong>Crypto checkout.</strong> We accept USDC on Solana or Polygon, and USDT on TRC20 or Polygon only.</li>
<li><strong>Light on data.</strong> No accounts, no tracking scripts, no advertising cookies. See <a href="{{R}}privacy/">Privacy</a>.</li>
<li><strong>For readers worldwide.</strong> Products are written in plain English and avoid single-country assumptions wherever they can.</li>
</ul>
<h2>Contact</h2>
<p>Questions and order support: <a href="mailto:hallo@jalupublishing.com">hallo@jalupublishing.com</a>.</p>
</div></section>
'''
page("about/index.html", "About", "About Jalu Press: practical English ebooks and light tools, sold as digital downloads.", about, "about")

# ---------- TERMS ----------
terms = f'''
<section><div class="wrap prose">
<p class="eyebrow">Help</p>
<h1>Help, license &amp; refunds</h1>
<h2>Delivery</h2>
<p>All Jalu Press products are digital files. After your payment is confirmed on-chain and we have your order email, your files are emailed automatically, as an attachment, to the address you gave at checkout. Please check your spam folder if it has not arrived. Nothing physical is shipped.</p>
<h2>Payment</h2>
<p>We accept USDC on Solana or Polygon, and USDT on TRC20 (Tron) or Polygon only. Prices are in US dollars, paid as the same number of tokens. Network fees are paid by the sender. Blockchain payments cannot be reversed by us or by you, so please check the amount, network and address before sending. See <a href="{{R}}how-to-buy/">How to buy</a>.</p>
<h2>Refunds and problems</h2>
<ul>
<li>If a file is faulty or will not open, tell us and we will fix it or send a replacement.</li>
<li>If we cannot deliver your order, we refund the amount you paid in the same token, to a wallet address on the same network that you give us.</li>
<li>Because files can be kept once downloaded, completed orders are otherwise not refundable. Please read the product page and previews before you buy.</li>
<li>Payments sent on the wrong network, in the wrong token or to an address not shown on our checkout page cannot be recovered by us.</li>
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
priv = f'''
<section><div class="wrap prose">
<p class="eyebrow">Privacy</p>
<h1>Privacy</h1>
<p class="lead">Short version: we collect as little as possible.</p>
<ul>
<li><strong>No tracking.</strong> This site uses no analytics, advertising or social tracking scripts and sets no cookies.</li>
<li><strong>Hosting.</strong> The site is a static website hosted on GitHub Pages. GitHub may log basic technical data such as IP addresses for security, under its own privacy statement.</li>
<li><strong>Checkout.</strong> The details you type on the checkout page stay in your browser. They are only sent to us if you choose to email us your order, and we use them only to deliver your files and answer you.</li>
<li><strong>Payments.</strong> Blockchain transactions are public by nature. We see the sending address, amount and time of your payment, as anyone can.</li>
<li><strong>Never shared or sold.</strong> We do not sell or share your details, and we do not send marketing email unless you ask for it.</li>
<li><strong>What we never ask for:</strong> passwords, card numbers, private keys or seed phrases.</li>
</ul>
<p>You can ask us to delete your order emails at any time using the support address shown on the checkout page.</p>
</div></section>
'''
page("privacy/index.html", "Privacy", "Jalu Press privacy notice: no trackers, minimal data.", priv, "")

# ---------- CHECKOUT ----------
co = f'''
<div class="wrap"><p class="crumbs"><a href="{{R}}">Home</a> / Checkout</p></div>
<div class="wrap co" id="checkout" data-config="{{R}}assets/payment-config.json">
<div>
<h1 style="font-size:2rem">Checkout</h1>
<div class="card">
<div class="summary-row">
<img src="{{R}}assets/img/{P["img"]}-cover-800.webp" width="800" height="600" alt="">
<div><strong style="color:var(--ink)">{P["title"]}</strong><div class="small">Digital download (PDF + XLSX)</div>
<div class="price" style="font-size:1.5rem;margin-top:8px" id="co-price" data-price="{P["price"]}">$12</div></div>
</div>
<hr style="border:0;border-top:1px solid var(--line);margin:18px 0">
<p class="small" style="margin:0">Pay with USDC (Solana or Polygon) or USDT (TRC20 or Polygon). The price is paid as the same number of tokens, plus a few unique hundredths of a cent that identify your order. Network fees are paid by the sender.</p>
</div>
<p class="small" style="margin-top:14px"><a href="{{R}}how-to-buy/">How buying works</a> &middot; <a href="{{R}}terms/">Refunds &amp; license</a></p>
</div>

<div>
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
<button class="btn" type="submit">Show payment details</button>
<p class="small" style="margin-top:12px">Nothing is charged or sent from this page. We never ask for passwords, card numbers, private keys or seed phrases.</p>
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
<p>We check the blockchain every few minutes. Once your payment is final and your order email is in, your files arrive by email, usually within 30 minutes. Check your spam folder if you don't see it. Keep your order reference; it is valid for 72 hours.</p>
</div>
</div>
</div>
'''
co_js = '<script src="{R}assets/checkout.js" defer></script>'
page("checkout/index.html", "Checkout", "Jalu Press checkout: pay with USDC or USDT on Solana, TRC20 or Polygon.", co, "", extra_head='<meta name="robots" content="noindex">\n', scripts=co_js)

# ---------- 404 (served at any depth, so it computes its own base) ----------
nf_body = '''
<section><div class="wrap prose">
<h1>Page not found</h1>
<p class="lead">That page does not exist. It may have moved.</p>
<div class="btn-row"><a class="btn" href="{R}">Go to the homepage</a></div>
</div></section>'''
page("404.html", "Page not found", "Page not found.", nf_body, "", depth=0,
     extra_head='<script>(function(){var b=location.hostname.endsWith("github.io")?"/jalupress/":"/";document.write(\'<base href="\'+b+\'">\');})();</script>\n')
print("built")
