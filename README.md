# Jalu Press storefront

Static storefront for **Jalu Press** (practical English ebooks and light tools), hosted on
GitHub Pages from the `main` branch, `/docs` folder.

- `docs/` is the published website. All internal links are relative, so it works at
  `https://jalusaja.github.io/jalupress/` and at `https://jalupress.com/`.
- `build.py` regenerates the HTML pages in `docs/` (`python3 build.py`).
- `CNAME` (repo root) holds `jalupress.com`. It is kept outside `docs/` on purpose so the
  temporary github.io address keeps working until DNS is in place. To switch the site to the
  custom domain, set it in Settings → Pages (or
  `gh api -X PUT repos/jalusaja/jalupress/pages -f cname=jalupress.com`), which writes
  `docs/CNAME`.

## Payments (USDC on Solana, USDT on TRC20 only)
Checkout reads `docs/assets/payment-config.json`, which does **not** exist yet. Until it
exists with at least one valid receive address **and** an order email, checkout shows
"Checkout is not open yet" and displays no address. To open checkout, copy
`payment-config.example.json` to `docs/assets/payment-config.json`, fill in the real
values and commit.

| Key | Meaning |
| --- | --- |
| `usdcSolanaAddress` | Solana wallet address that receives USDC |
| `usdtTronAddress` | Tron wallet address that receives USDT (TRC20) |
| `orderEmail` | Mailbox buyers send their order reference and transaction ID to |

## Product files
Full product files (PDF, XLSX, ZIP) are never committed or published (`.gitignore`).
Only cover and preview images live in `docs/assets/img/`.
