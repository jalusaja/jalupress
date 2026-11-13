# Jalu Press storefront

Static storefront for **Jalu Press** (practical English ebooks and light tools), hosted on
GitHub Pages from the `main` branch, `/docs` folder.

- `catalog.json` is the product catalog (slug, title, price, copy, images, zip name).
  `build.py` reads it to generate the home grid, footer, and one page per product.
  Autodeliver reads the same file. A copy is written to `docs/assets/catalog.json`
  so checkout (`checkout/?p=<slug>`) can load the product and price in the browser.
- `docs/` is the published website. All internal links are relative, so it works at
  `https://jalusaja.github.io/jalupress/` and at `https://jalupress.com/`.
- `build.py` regenerates the HTML pages in `docs/` (`python3 build.py`).
- `CNAME` (repo root) holds `jalupress.com`. GitHub Pages is set to this custom
  domain, with HTTPS enforced. `docs/CNAME` is written by the Pages setting.

To add a product, follow **[ADD_PRODUCT.md](ADD_PRODUCT.md)** exactly (one new
product a day). The short version: product files under
`/workspace/ebook-store/products/<slug>/`, cover and preview images, a required
`docs/assets/img/og-<slug>.jpg` (1200×630), a new entry in `catalog.json`, then
`python3 build.py`, commit and push.

## Social share images (Open Graph / Twitter)

Every page has `og:url`, `og:image` (plus width, height and alt), and
`twitter:card=summary_large_image` with matching title, description and image.

- **Product pages** use `docs/assets/img/og-<slug>.jpg`. If that file is missing,
  the page falls back to the site default. Title text on the image must stay
  readable at 1200×630 (the size Facebook, X and messaging apps expect).
- **Home and other pages** use `docs/assets/img/og-default.jpg`.
- **Every new product must ship `og-<slug>.jpg` at exactly 1200×630, JPEG.**
  Do not reuse another product's image and do not upload a 4:3 cover as the OG
  file. A helper lives at `tools/make_og.py` if you need a starting composition;
  always open the result and check the title is legible.

## Payments (USDC / USDT)

Checkout reads `docs/assets/payment-config.json`. It stays closed (and shows no
address) until that file exists with at least one valid receive address and an
order email. Accepted networks: USDC on Solana or Polygon, and USDT on TRC20
(Tron) or Polygon. See `payment-config.example.json` for the key names.

The unique per-order amount and automatic delivery both need the product slug
and price from `catalog.json`. New order emails use the subject
`Jalu Press order JP-XXXXXX <slug>`. Older binder orders that omit the slug
are still accepted and mapped to `grab-and-go-household-binder`.

## Product files

Full product files (PDF, XLSX, ZIP) are never committed or published (`.gitignore`).
Only cover, preview and OG images live in `docs/assets/img/`.
