// Site visits for the CRM.
//
// One beacon per page load to the CRM: a random key this browser keeps, the
// page, its title, and the page before it. The key identifies a browser, not a
// person. The CRM attaches it to a contact only when this browser fills in a
// form, books a call, or arrives from a link in an email the CRM sent. That
// link carries a signed reference (crm_ref), which is read here and then taken
// out of the address bar so it is never copied or shared.
//
// Browsers that send Global Privacy Control or Do Not Track are not tracked at
// all. The privacy page says what is collected and why.
(function () {
  var COLLECTOR = 'https://coaching-crm-tau.vercel.app/api/visits';
  var KEY = 'crm_vid';
  var CAMPAIGN = 'crm_utm';
  var UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

  window.crmVisitor = null;
  if (
    navigator.globalPrivacyControl === true ||
    navigator.doNotTrack === '1' ||
    window.doNotTrack === '1' ||
    navigator.webdriver
  ) {
    return;
  }

  try {
    var id = null;
    try { id = localStorage.getItem(KEY); } catch (e) {}
    if (!id || !UUID.test(id)) {
      id = crypto.randomUUID();
      try { localStorage.setItem(KEY, id); } catch (e) {}
    }

    var url = new URL(location.href);
    var ref = url.searchParams.get('crm_ref');
    if (ref !== null) {
      url.searchParams.delete('crm_ref');
      history.replaceState(history.state, '', url.pathname + url.search + url.hash);
    }

    // The campaign a visitor landed with is kept for the rest of the visit, so
    // a form filled in three pages later still says where they came from.
    var utm = {};
    UTM_KEYS.forEach(function (key) {
      var value = url.searchParams.get(key);
      if (value) utm[key] = value.slice(0, 200);
    });
    try {
      if (Object.keys(utm).length > 0) sessionStorage.setItem(CAMPAIGN, JSON.stringify(utm));
      else utm = JSON.parse(sessionStorage.getItem(CAMPAIGN) || '{}');
    } catch (e) {}

    var body = JSON.stringify({
      v: id,
      u: url.href,
      t: document.title || null,
      r: document.referrer || null,
      ref: ref
    });
    if (!(navigator.sendBeacon && navigator.sendBeacon(COLLECTOR, body))) {
      fetch(COLLECTOR, { method: 'POST', body: body, keepalive: true, mode: 'no-cors' });
    }

    // Booking pages are served by the CRM on its own host, where this
    // browser's key does not exist. Links to them carry it across, so a booking
    // joins the same history as the pages read before it.
    var crmOrigin = new URL(COLLECTOR).origin;
    var decorate = function () {
      document.querySelectorAll('a[href]').forEach(function (link) {
        var target;
        try { target = new URL(link.getAttribute('href'), location.href); } catch (e) { return; }
        var booking =
          (target.origin === location.origin && target.pathname.indexOf('/book/') === 0) ||
          target.origin === crmOrigin;
        if (!booking || target.searchParams.has(KEY)) return;
        target.searchParams.set(KEY, id);
        link.href = target.href;
      });
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', decorate);
    else decorate();

    window.crmVisitor = { id: id, utm: utm };
  } catch (e) {
    // Tracking never gets in the way of the page.
  }
})();
