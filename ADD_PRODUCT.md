# Adding a Jalu Press product

Do this once per new product, in this order. The store sells one new product a
day; do not skip the OG image or the catalog entry, and do not put wallet
addresses in the catalog, the commit message, or chat.

The live site is built from this repo (`jalusaja/jalupress`, `main`, `/docs`)
and served at https://jalupress.com. Autodeliver on the box reads
`/workspace/ebook-store/site/catalog.json` and emails the zip from
`/workspace/ebook-store/products/<slug>/`.

## 1. Choose a slug

Lowercase letters, numbers and hyphens only, for example
`grab-and-go-household-binder`. This slug is the folder name, the page URL
(`/products/<slug>/`), the checkout query (`/checkout/?p=<slug>`), the OG
filename, and the suffix on the buyer's order-email subject
(`Jalu Press order JP-XXXXXX <slug>`).

## 2. Product files (not committed)

Create `/workspace/ebook-store/products/<slug>/` and put the downloadable zip
there, named exactly as the `zip` field you will add to the catalog (for
example `The-Grab-and-Go-Household-Binder.zip`). Keep source files, PDFs and
spreadsheets in that folder too. They are gitignored and must never be pushed.

## 3. Cover, previews and OG image

Copy the storefront images into `docs/assets/img/`:

| File | Size | Notes |
| --- | --- | --- |
| `<slug>-cover.webp` and `<slug>-cover-800.webp` | 1600×1200 and 800×600 | Product cover / mockup |
| `<slug>-preview-N-<name>.webp` and `-800.webp` | same | At least one preview; four is typical |
| **`og-<slug>.jpg`** | **exactly 1200×630, JPEG** | **Required.** Social share thumbnail. Title text must be readable. |

A starting composition can be made with:

```bash
python3 tools/make_og.py \
  --title "Product Title" \
  --subtitle "Short subtitle" \
  --cover docs/assets/img/<slug>-cover.webp \
  --out docs/assets/img/og-<slug>.jpg
```

Always open the JPEG and check it before you commit. Do not ship a 4:3 cover
(for example 1200×900) as the OG image — feeds will crop it badly.

In `catalog.json`, set `images[].file` to the stem without `.webp`
(for example `my-product-cover`) and set:

```json
"og_image": "assets/img/og-<slug>.jpg",
"og_alt": "A short description of the share image"
```

If `og-<slug>.jpg` is missing at build time, the product page falls back to
`assets/img/og-default.jpg`. That is only a safety net; every new product
must still ship its own image.

## 4. Catalog entry

Add one object to the `products` array in `catalog.json` (repo root). Required
fields:

- `slug`, `title`, `subtitle`, `nav_label`, `price_usd` (number), `status`
  (`for_sale`), `released` (YYYY-MM-DD; newest appears first)
- `short` (home card), `description` (meta / social description)
- `format_blurb` (checkout, for example `Digital download (PDF)`)
- `images`, `og_image`, `og_alt`
- `shop_ticks`, `buy_ticks`
- `story` (sections with `heading`, `paragraphs`, optional `note_html`)
- `included` (files listed on the page: `type`, `name`, `detail`, optional
  `badge` `x` or `i`), `included_note`, `inside` (table of contents),
  optional `inside_heading`
- `good_for`, `specs`, `please_note`
- `zip` (filename only, sitting in `products/<slug>/`)
- `whats_inside` (bullet lines used in the delivery email)
- `delivery_note` (one short paragraph after the file list in that email)

`build.py` and autodeliver both read this file. Keep copy original (or public
domain / licensed). Do not paste another publisher's text. Price in `specs` is
rewritten from `price_usd` at build time, so you only need to set `price_usd`.

## 5. Build, check, commit, push

From this repo root:

```bash
python3 build.py
```

Then open locally:

- `docs/index.html` — the new card is in the shop grid
- `docs/products/<slug>/index.html` — gallery, price, Buy link
- the product HTML `<head>` contains `og:image` pointing at
  `https://jalupress.com/assets/img/og-<slug>.jpg`, plus `og:url`,
  `og:image:width` / `height` / `alt`, and `twitter:card=summary_large_image`
- `docs/checkout/index.html` and `docs/assets/catalog.json` — checkout should
  load this slug

Commit with the existing repo identity (do not change `user.name` / `user.email`)
and include: `catalog.json`, `build.py` only if you had to change it, the new
images, the regenerated `docs/` HTML, and `docs/assets/catalog.json`. Never
commit zips, PDFs, XLSX, or edits to `docs/assets/payment-config.json`.

```bash
git add catalog.json docs/assets/catalog.json docs/assets/img/og-<slug>.jpg \
  docs/assets/img/<slug>-*.webp docs/index.html docs/products/<slug>/ \
  docs/checkout/index.html docs/404.html docs/about docs/how-to-buy docs/privacy docs/terms
git status   # confirm payment-config.json is not staged
git commit -m "Add product: <title>"
git push origin main
```

## 6. Verify live

Wait for GitHub Pages to publish (usually one or two minutes), then:

```bash
curl -sS https://jalupress.com/products/<slug>/ | rg "og:image|twitter:card|og:url"
curl -sSI https://jalupress.com/assets/img/og-<slug>.jpg
# expect HTTP 200 and content-type image/jpeg. CDN cache may lag up to ~10 minutes.
```

Also open `https://jalupress.com/checkout/?p=<slug>` and confirm the title and
price match the catalog. Do not send a real payment as a test unless you mean
to buy the product.

## 7. Autodeliver (no extra deploy)

The existing routine already reloads `catalog.json` each run. Once the zip is
in `products/<slug>/` and the catalog entry is saved, a payment that matches
the unique amount in the order email is delivered automatically, with that
product's `whats_inside` lines in the email. Existing Household Binder orders
(subject without a slug, amount in the $12.0001–$12.0999 range) keep working.

If you change autodeliver itself, run `python3 test_run.py` and a
`python3 run.py --dry-run` first, and never edit `run.py` in a half-finished
state: the routine may start at any moment and uses the lock file
`/workspace/ebook-store/autodeliver/.run.lock`.
