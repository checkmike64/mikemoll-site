// Shared form handler. Any <form data-lead="FORM_ID"> posts its named fields
// to /api/lead as JSON, then swaps in a success message on success.
// Optional attributes: data-success (message), data-success-note (second line).
//
// Also sets the mm_id cookie (their email) on success, so track-view.js can
// recognize them as a known contact on later page views and tag high-intent
// pages via /api/track.
(function () {
  function rememberVisitor(email) {
    if (!email) return;
    document.cookie = 'mm_id=' + encodeURIComponent(email) + '; path=/; max-age=31536000; SameSite=Lax';
  }
  window.mmRememberVisitor = rememberVisitor;

  function wire(form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type=submit]') || form.querySelector('button');
      var orig = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
      var data = Object.fromEntries(new FormData(form).entries());
      data.formId = form.getAttribute('data-lead');
      try {
        var res = await fetch('/api/lead', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('bad status ' + res.status);
        rememberVisitor(data.email);
        var redirect = form.getAttribute('data-redirect');
        if (redirect) { window.location.href = redirect; return; }
        var msg = form.getAttribute('data-success') || "You're in.";
        var note = form.getAttribute('data-success-note') || '';
        form.innerHTML =
          '<p style="font-family:var(--display);font-weight:600;font-size:1.15rem;color:var(--accent);margin:6px 0">' + msg + '</p>' +
          (note ? '<p style="color:var(--muted);margin:0">' + note + '</p>' : '');
      } catch (err) {
        if (btn) { btn.disabled = false; btn.textContent = orig; }
        alert('Something went wrong. Please try again.');
      }
    });
  }
  document.querySelectorAll('form[data-lead]').forEach(wire);
})();
