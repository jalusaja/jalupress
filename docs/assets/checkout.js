/* Jalu Press checkout. Static, no backend.
   Receive addresses come from assets/payment-config.json (see
   payment-config.example.json in the repo root). That file does not exist until
   the real wallet addresses and order email are ready. If it is missing, or an
   address or the email is malformed, checkout stays closed and shows no address.
   The product and price come from assets/catalog.json and ?p=<slug>. */
(function () {
  var root = document.getElementById('checkout');
  if (!root) return;
  var B58 = /^[1-9A-HJ-NP-Za-km-z]+$/;
  var HEX40 = /^0x[0-9a-fA-F]{40}$/;
  var METHODS = {
    usdc_sol: { key: 'usdcSolanaAddress', token: 'USDC', net: 'Solana',
      label: 'USDC on Solana',
      detail: 'Official USDC mint: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
      valid: function (a) { return B58.test(a) && a.length >= 32 && a.length <= 44; } },
    usdt_trx: { key: 'usdtTronAddress', token: 'USDT', net: 'Tron (TRC20)',
      label: 'USDT on TRC20 (Tron)',
      detail: 'Official USDT contract on Tron: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
      valid: function (a) { return a.length === 34 && a.charAt(0) === 'T' && B58.test(a); } },
    usdc_pol: { key: 'usdcPolygonAddress', token: 'USDC', net: 'Polygon',
      label: 'USDC on Polygon',
      detail: 'Native USDC on Polygon (not USDC.e): 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
      valid: function (a) { return HEX40.test(a); } },
    usdt_pol: { key: 'usdtPolygonAddress', token: 'USDT', net: 'Polygon',
      label: 'USDT on Polygon',
      detail: 'Official USDT contract on Polygon: 0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
      valid: function (a) { return HEX40.test(a); } }
  };
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var LEGACY_SLUG = 'grab-and-go-household-binder';
  var $ = function (id) { return document.getElementById(id); };
  var slug = (new URLSearchParams(location.search).get('p') || '').trim();

  var catalogUrl = root.dataset.catalog;
  var configUrl = root.dataset.config;
  Promise.all([
    fetch(catalogUrl, { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : { products: [] }; }).catch(function () { return { products: [] }; }),
    fetch(configUrl, { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
  ]).then(function (pair) {
    var catalog = pair[0] || {};
    var cfg = pair[1] || {};
    var list = (catalog.products || []).filter(function (p) { return (p.status || 'for_sale') === 'for_sale'; });
    var bySlug = {};
    list.forEach(function (p) { bySlug[p.slug] = p; });

    var showPick = function (unknown) {
      $('co-closed').classList.add('hidden');
      $('co-form').classList.add('hidden');
      $('co-resume').classList.add('hidden');
      $('co-pay').classList.add('hidden');
      if (unknown) $('co-unknown').classList.remove('hidden');
      else $('co-unknown').classList.add('hidden');
      var box = $('co-pick-list');
      box.innerHTML = '';
      list.forEach(function (p) {
        var a = document.createElement('a');
        a.href = '?p=' + encodeURIComponent(p.slug);
        var img = (p.images && p.images[0] && p.images[0].file)
          ? '../assets/img/' + p.images[0].file + '-800.webp' : '';
        a.innerHTML = (img ? '<img src="' + img + '" width="800" height="600" alt="">' : '') +
          '<span><strong>' + p.title + '</strong><br><span class="small">$' +
          (Number(p.price_usd) === parseInt(p.price_usd, 10) ? parseInt(p.price_usd, 10) : Number(p.price_usd).toFixed(2)) +
          '</span></span>';
        box.appendChild(a);
      });
      $('co-pick').classList.remove('hidden');
      $('co-title').textContent = unknown ? 'Product not found' : 'Choose a product';
      $('co-format').textContent = 'Digital download';
      $('co-price').textContent = '';
      $('co-price').dataset.price = '';
    };

    if (!slug) { showPick(false); return; }
    var product = bySlug[slug];
    if (!product) { showPick(true); return; }

    var price = String(product.price_usd);
    var priceLabel = Number(product.price_usd) === parseInt(product.price_usd, 10)
      ? String(parseInt(product.price_usd, 10))
      : Number(product.price_usd).toFixed(2);
    var cover = (product.images && product.images[0] && product.images[0].file)
      ? '../assets/img/' + product.images[0].file + '-800.webp' : '';
    if (cover) {
      $('co-cover').src = cover;
      $('co-cover').alt = product.images[0].alt || product.title;
    }
    $('co-title').textContent = product.title;
    $('co-format').textContent = product.format_blurb || 'Digital download';
    $('co-price').dataset.price = price;
    $('co-price').innerHTML = '$' + priceLabel;

    var available = Object.keys(METHODS).filter(function (k) {
      var a = (cfg[METHODS[k].key] || '').trim();
      return a && METHODS[k].valid(a);
    });
    var support = (cfg.orderEmail || '').trim();
    if (!available.length || !EMAIL.test(support)) return;
    var box = $('methods');
    box.innerHTML = '';
    available.forEach(function (k, i) {
      var l = document.createElement('label');
      l.innerHTML = '<input type="radio" name="method" value="' + k + '"' + (i === 0 ? ' checked' : '') +
        '><span><strong>' + METHODS[k].label + '</strong><br><span class="small">Pay about ' + priceLabel + ' ' + METHODS[k].token + ' (exact amount shown next)</span></span>';
      box.appendChild(l);
    });
    $('co-closed').classList.add('hidden');
    $('co-form').classList.remove('hidden');

    var KEY = 'jp_order_v2_' + slug;
    var LEGACY_KEY = 'jp_order_v2';
    var show = function (o) {
      var m = METHODS[o.k]; var addr = cfg[m.key].trim();
      var amt = o.amount + ' ' + m.token;
      $('o-ref').textContent = o.ref; $('o-ref2').textContent = o.ref;
      $('o-amount').textContent = amt; $('o-amount2').textContent = amt;
      $('o-net').textContent = m.net; $('o-net2').textContent = m.net; $('o-tok2').textContent = m.token;
      $('o-addr').textContent = addr; $('o-token').textContent = m.detail;
      $('o-email').textContent = o.email; $('o-support').textContent = support;
      if (cfg.qr && cfg.qr[o.k]) {
        $('o-qr-img').src = cfg.qr[o.k];
        $('o-qr').classList.remove('hidden');
      } else {
        $('o-qr').classList.add('hidden');
        $('o-qr-img').removeAttribute('src');
      }
      var subject = 'Jalu Press order ' + o.ref + ' ' + slug;
      var body = function () {
        return 'Order reference: ' + o.ref + '\nProduct: ' + product.title + '\nAmount: ' + amt +
          '\nNetwork: ' + m.net + '\nPaid to: ' + addr + '\nTransaction ID: ' + ($('txid').value.trim() || '(optional)') +
          '\nDelivery email: ' + o.email + '\nName: ' + (o.name || '-') + '\nCreated: ' + new Date(o.created).toISOString() + '\n';
      };
      var mail = function () {
        $('o-mail').href = 'mailto:' + support + '?subject=' + encodeURIComponent(subject) +
          '&body=' + encodeURIComponent(body());
        $('o-mailtext').value = 'To: ' + support + '\nSubject: ' + subject + '\n\n' + body();
      };
      mail(); $('txid').oninput = mail;
      $('o-copymail').onclick = function () {
        var t = $('o-mailtext').value;
        (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject())
          .then(function () { $('o-copiedmail').textContent = 'Copied. Paste it into a new email to ' + support + '.'; })
          .catch(function () { $('o-mailtext').select(); $('o-copiedmail').textContent = 'Select the text above and copy it.'; });
      };
      $('co-form').classList.add('hidden'); $('co-resume').classList.add('hidden');
      $('co-pay').classList.remove('hidden');
      $('co-pay').scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    var saved = null;
    try { saved = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { saved = null; }
    if (!saved && slug === LEGACY_SLUG) {
      try {
        var legacy = JSON.parse(localStorage.getItem(LEGACY_KEY) || 'null');
        if (legacy && (!legacy.slug || legacy.slug === LEGACY_SLUG)) saved = legacy;
      } catch (e) { /* ignore */ }
    }
    if (saved && saved.ref && METHODS[saved.k] && available.indexOf(saved.k) >= 0 &&
        Date.now() - saved.created < 72 * 3600 * 1000) {
      $('r-ref').textContent = saved.ref;
      $('r-amount').textContent = saved.amount + ' ' + METHODS[saved.k].token + ' (' + METHODS[saved.k].net + ')';
      $('co-resume').classList.remove('hidden');
      $('r-open').addEventListener('click', function () { show(saved); });
      $('r-new').addEventListener('click', function () {
        try { localStorage.removeItem(KEY); localStorage.removeItem(LEGACY_KEY); } catch (e) {}
        $('co-resume').classList.add('hidden');
      });
    }

    $('co-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var email = $('email').value.trim();
      if (!EMAIL.test(email)) { $('co-err').textContent = 'Please enter a valid email address for delivery.'; $('email').focus(); return; }
      $('co-err').textContent = '';
      var k = (document.querySelector('input[name=method]:checked') || {}).value;
      var rnd = new Uint32Array(2);
      (window.crypto || window.msCrypto).getRandomValues(rnd);
      var A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
      var ref = 'JP-';
      for (var i = 0; i < 6; i++) ref += A.charAt((rnd[0] >>> (i * 5)) & 31);
      var cents = 1 + (rnd[1] % 999); /* 0.0001 to 0.0999 */
      var base = Math.round(Number(price) * 10000);
      var units = base + cents;
      var o = { ref: ref, k: k, slug: slug, email: email, name: $('name').value.trim(), created: Date.now(),
        amount: Math.floor(units / 10000) + '.' + ('000' + (units % 10000)).slice(-4) };
      try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (err) {}
      show(o);
    });
    $('o-copy').addEventListener('click', function () {
      var t = $('o-addr').textContent;
      (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject())
        .then(function () { $('o-copied').textContent = 'Copied'; })
        .catch(function () { $('o-copied').textContent = 'Select and copy the address above'; });
    });
  });
})();
