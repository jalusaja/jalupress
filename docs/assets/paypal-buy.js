/* Fill a JP-XXXXXX invoice/custom on PayPal Buy Now forms before submit. */
(function () {
  var A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  function makeRef() {
    var rnd = new Uint32Array(2);
    (window.crypto || window.msCrypto).getRandomValues(rnd);
    var s = 'JP-';
    var i;
    for (i = 0; i < 6; i++) s += A.charAt((rnd[0] >>> (i * 5)) & 31);
    return s;
  }
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || !f.classList || !f.classList.contains('paypal-buy')) return;
    var inv = f.querySelector('input[name="invoice"]');
    var custom = f.querySelector('input[name="custom"]');
    var ret = f.querySelector('input[name="return"]');
    var ref = (inv && inv.value.trim()) ? inv.value.trim() : makeRef();
    if (inv) inv.value = ref;
    if (custom) custom.value = ref;
    if (ret && ret.value && ret.value.indexOf('ref=') === -1) {
      ret.value += (ret.value.indexOf('?') >= 0 ? '&' : '?') + 'ref=' + encodeURIComponent(ref);
    }
  }, true);
})();
