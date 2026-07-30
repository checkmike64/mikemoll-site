// If the visitor is known (mm_id cookie, set by forms.js after any lead
// submission), tag their GHL contact for viewing this page. No-ops silently
// for anonymous visitors — this never creates a new contact.
(function () {
  function getCookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  var email = getCookie('mm_id');
  if (!email) return;

  fetch('/api/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, page: window.location.pathname }),
    keepalive: true,
  }).catch(function () {});
})();
