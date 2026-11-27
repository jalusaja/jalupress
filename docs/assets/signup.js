/* Fill the hidden "ref" field on signup forms with where the visitor came from (for traffic measurement). */
(function () {
  var q = new URLSearchParams(location.search);
  var ref = (q.get('utm_source') || q.get('ref') || q.get('src') || '').trim();
  if (!ref && document.referrer) {
    try { ref = new URL(document.referrer).hostname; } catch (e) {}
    if (ref === location.hostname) ref = 'internal';
  }
  ref = (ref || 'direct').slice(0, 60);
  var els = document.querySelectorAll('form.signup input[name="ref"]');
  for (var i = 0; i < els.length; i++) els[i].value = ref;
})();
