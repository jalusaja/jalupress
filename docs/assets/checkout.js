/* Jalu Press checkout. Static, no backend.
   Receive addresses come from assets/payment-config.json (see
   payment-config.example.json in the repo root). That file does not exist until
   the real wallet addresses and order email are ready. If it is missing, or an
   address or the email is malformed, checkout stays closed and shows no address. */
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
  var $ = function (id) { return document.getElementById(id); };
  var price = $('co-price').dataset.price;
  var product = 'The Grab-and-Go Household Binder';

  fetch(root.dataset.config, { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : {}; })
    .catch(function () { return {}; })
    .then(function (cfg) {
      cfg = cfg || {};
      var available = Object.keys(METHODS).filter(function (k) {
        var a = (cfg[METHODS[k].key] || '').trim();
        return a && METHODS[k].valid(a);
      });
      var support = (cfg.orderEmail || '').trim();
      if (!available.length || !EMAIL.test(support)) return;
      var box = $('methods');
      available.forEach(function (k, i) {
        var l = document.createElement('label');
        l.innerHTML = '<input type="radio" name="method" value="' + k + '"' + (i === 0 ? ' checked' : '') +
          '><span><strong>' + METHODS[k].label + '</strong><br><span class="small">Pay ' + price + ' ' + METHODS[k].token + '</span></span>';
        box.appendChild(l);
      });
      $('co-closed').classList.add('hidden');
      $('co-form').classList.remove('hidden');

      $('co-form').addEventListener('submit', function (e) {
        e.preventDefault();
        var email = $('email').value.trim();
        if (!EMAIL.test(email)) { $('co-err').textContent = 'Please enter a valid email address for delivery.'; $('email').focus(); return; }
        $('co-err').textContent = '';
        var k = (document.querySelector('input[name=method]:checked') || {}).value;
        var m = METHODS[k]; var addr = cfg[m.key].trim();
        var ref = 'JP-' + Date.now().toString(36).toUpperCase().slice(-5) +
          Math.random().toString(36).slice(2, 5).toUpperCase();
        var amt = Number(price).toFixed(2) + ' ' + m.token;
        $('o-ref').textContent = ref; $('o-amount').textContent = amt;
        $('o-net').textContent = m.net; $('o-net2').textContent = m.net; $('o-tok2').textContent = m.token;
        $('o-addr').textContent = addr; $('o-token').textContent = m.detail;
        $('o-email').textContent = email; $('o-support').textContent = support;
        if (cfg.qr && cfg.qr[k]) {
          $('o-qr-img').src = cfg.qr[k];
          $('o-qr').classList.remove('hidden');
        } else {
          $('o-qr').classList.add('hidden');
          $('o-qr-img').removeAttribute('src');
        }
        var mail = function () {
          var body = 'Order reference: ' + ref + '\nProduct: ' + product + '\nAmount: ' + amt +
            '\nNetwork: ' + m.net + '\nPaid to: ' + addr + '\nTransaction ID: ' + ($('txid').value.trim() || '(add here)') +
            '\nDelivery email: ' + email + '\nName: ' + ($('name').value.trim() || '-') + '\n';
          $('o-mail').href = 'mailto:' + support + '?subject=' + encodeURIComponent('Jalu Press order ' + ref) +
            '&body=' + encodeURIComponent(body);
        };
        mail(); $('txid').addEventListener('input', mail);
        $('co-form').classList.add('hidden'); $('co-pay').classList.remove('hidden');
        $('co-pay').scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      $('o-copy').addEventListener('click', function () {
        var t = $('o-addr').textContent;
        (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject())
          .then(function () { $('o-copied').textContent = 'Copied'; })
          .catch(function () { $('o-copied').textContent = 'Select and copy the address above'; });
      });
    });
})();
