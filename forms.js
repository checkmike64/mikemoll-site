// Shared form handler. Any <form data-lead="FORM_ID"> posts its named fields
// to /api/lead as JSON, then swaps in a success message on success.
// Optional attributes: data-success (message), data-success-note (second line).
//
// Also pushes GA4 events to dataLayer (picked up by a GTM GA4 Event tag) —
// generate_lead on success, lead_form_error on failure. GA4's own Enhanced
// Measurement already sees clicks/scroll/generic form_submit, but it can't
// know whether OUR fetch to /api/lead actually succeeded.
(function () {
  function pushEvent(name, formId) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: name,
      form_id: formId || '',
      page_path: window.location.pathname,
    });
  }

  // Honeypot: a field real users never see or fill in, since it's named to
  // look plausible to bots but hidden from sighted users and screen readers.
  // Bots that auto-fill every field trip it; server rejects if it's non-empty.
  function addHoneypot(form) {
    var wrap = document.createElement('div');
    wrap.style.cssText = 'position:absolute;left:-9999px;top:-9999px;width:1px;height:1px;overflow:hidden;';
    wrap.setAttribute('aria-hidden', 'true');
    var input = document.createElement('input');
    input.type = 'text';
    input.name = 'website_url';
    input.tabIndex = -1;
    input.autocomplete = 'off';
    wrap.appendChild(input);
    form.appendChild(wrap);
    form.dataset.renderedAt = String(Date.now());
  }

  function wire(form) {
    addHoneypot(form);
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type=submit]') || form.querySelector('button');
      var orig = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
      var data = Object.fromEntries(new FormData(form).entries());
      data.formId = form.getAttribute('data-lead');
      data.renderedAt = form.dataset.renderedAt;
      try {
        var res = await fetch('/api/lead', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('bad status ' + res.status);
        pushEvent('generate_lead', data.formId);
        var redirect = form.getAttribute('data-redirect');
        if (redirect) { window.location.href = redirect; return; }
        var msg = form.getAttribute('data-success') || "You're in.";
        var note = form.getAttribute('data-success-note') || '';
        form.innerHTML =
          '<p style="font-family:var(--display);font-weight:600;font-size:1.15rem;color:var(--accent);margin:6px 0">' + msg + '</p>' +
          (note ? '<p style="color:var(--muted);margin:0">' + note + '</p>' : '');
      } catch (err) {
        pushEvent('lead_form_error', data.formId);
        if (btn) { btn.disabled = false; btn.textContent = orig; }
        alert('Something went wrong. Please try again.');
      }
    });
  }
  document.querySelectorAll('form[data-lead]').forEach(wire);
})();
