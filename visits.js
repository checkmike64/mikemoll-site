// Site visits for the CRM, plus the clicks and video views analytics needs.
//
// One beacon per page load to the CRM: a random key this browser keeps, the
// page, its title, and the page before it. The key identifies a browser, not a
// person. The CRM attaches it to a contact only when this browser fills in a
// form, books a call, or arrives from a link in an email the CRM sent. That
// link carries a signed reference (crm_ref), which is read here and then taken
// out of the address bar so it is never copied or shared. A link back from the
// CRM's booking pages can carry a visitor key (crm_vid) the same way.
//
// The beacon also carries the Google Analytics and Meta browser IDs when this
// site has set them, so the CRM can tell which ads and campaigns lead to calls.
//
// Browsers that send Global Privacy Control or Do Not Track are not tracked by
// the CRM at all. The privacy page says what is collected and why.
//
// The same script also tells Google Tag Manager about booking clicks, other
// high-intent clicks and Spotlightr video progress, by pushing to dataLayer.
// That part runs for every browser: what reaches Google Analytics is decided
// by the tag container and its consent settings, not here.
(function () {
  var COLLECTOR = 'https://coaching-crm-tau.vercel.app/api/visits';
  var KEY = 'crm_vid';
  var CAMPAIGN = 'crm_utm';
  var UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  var GA_CLIENT = /^\d{1,12}\.\d{1,12}$/;
  var FBP = /^fb\.\d\.\d{10,16}\.\d{1,20}$/;
  var crmOrigin = new URL(COLLECTOR).origin;

  var crmAllowed = !(
    navigator.globalPrivacyControl === true ||
    navigator.doNotTrack === '1' ||
    window.doNotTrack === '1' ||
    navigator.webdriver
  );
  var visitorId = null;

  window.crmVisitor = null;

  function send(body) {
    if (!(navigator.sendBeacon && navigator.sendBeacon(COLLECTOR, body))) {
      fetch(COLLECTOR, { method: 'POST', body: body, keepalive: true, mode: 'no-cors' });
    }
  }

  function push(event) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(event);
  }

  function cookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? match[1] : null;
  }

  // The ad platforms' IDs for this browser, as the CRM stores them. Google
  // Analytics' cookie is GA1.1.<client id>, and only the client id is sent.
  // A value of any other shape is left out rather than guessed at.
  function adIds() {
    var ids = {};
    var ga = cookie('_ga');
    if (ga) {
      var clientId = ga.split('.').slice(-2).join('.');
      if (GA_CLIENT.test(clientId)) ids.ga = clientId;
    }
    var fbp = cookie('_fbp');
    if (fbp && FBP.test(fbp)) ids.fbp = fbp;
    return ids;
  }

  // The page address as the CRM should see it: never with the signed email
  // reference or a handed-over visitor key in it.
  function currentUrl() {
    var url = new URL(location.href);
    url.searchParams.delete('crm_ref');
    url.searchParams.delete(KEY);
    return url.href;
  }

  function isBooking(target) {
    return (
      (target.origin === location.origin && target.pathname.indexOf('/book/') === 0) ||
      target.origin === crmOrigin
    );
  }

  // ---- Page visit, for the CRM ----------------------------------------------
  if (crmAllowed) {
    try {
      var url = new URL(location.href);

      // A key handed over in the address, by a link back from the CRM's booking
      // pages, becomes this browser's key only when it has none of its own. A
      // browser that already has a history keeps it.
      var handed = url.searchParams.get(KEY);
      var id = null;
      try { id = localStorage.getItem(KEY); } catch (e) {}
      if (!id || !UUID.test(id)) {
        id = handed && UUID.test(handed) ? handed : crypto.randomUUID();
        try { localStorage.setItem(KEY, id); } catch (e) {}
      }

      var ref = url.searchParams.get('crm_ref');
      if (ref !== null || handed !== null) {
        url.searchParams.delete('crm_ref');
        url.searchParams.delete(KEY);
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

      var visit = {
        v: id,
        u: url.href,
        t: document.title || null,
        r: document.referrer || null,
        ref: ref
      };
      var ids = adIds();
      if (Object.keys(ids).length > 0) visit.ids = ids;
      send(JSON.stringify(visit));

      // Booking pages are served by the CRM on its own host, where this
      // browser's key does not exist. Links to them carry it across, so a booking
      // joins the same history as the pages read before it.
      var decorate = function () {
        document.querySelectorAll('a[href]').forEach(function (link) {
          var target;
          try { target = new URL(link.getAttribute('href'), location.href); } catch (e) { return; }
          if (!isBooking(target) || target.searchParams.has(KEY)) return;
          target.searchParams.set(KEY, id);
          link.href = target.href;
        });
      };
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', decorate);
      else decorate();

      visitorId = id;
      window.crmVisitor = { id: id, utm: utm };
    } catch (e) {
      // Tracking never gets in the way of the page.
    }
  }

  // ---- High-intent clicks, for Tag Manager ----------------------------------
  // Booking links, and the links a page marks with data-cta, are the clicks
  // that say someone is about to buy or book. Generic link clicks are already
  // covered by GA4's own measurement.
  function onClick(event) {
    try {
      if (event.type === 'auxclick' && event.button !== 1) return;
      var node = event.target;
      if (node && node.nodeType !== 1) node = node.parentElement;
      var link = node && node.closest ? node.closest('a[href]') : null;
      if (!link) return;
      var target = new URL(link.getAttribute('href'), location.href);
      // The visitor key and the email reference are for the CRM only; they are
      // not sent on to analytics.
      target.searchParams.delete(KEY);
      target.searchParams.delete('crm_ref');
      var common = { link_url: target.href, page_path: location.pathname };

      if (isBooking(target)) {
        var slug = target.pathname.match(/^\/book\/([^/]+)/);
        push(Object.assign({
          event: 'booking_click',
          booking_type: slug ? decodeURIComponent(slug[1]) : 'other'
        }, common));
      }

      var host = target.hostname;
      var cta = link.getAttribute('data-cta') ||
        (host === 'wa.me' || /(^|\.)whatsapp\.com$/.test(host) ? 'whatsapp' : '') ||
        (/(^|\.)notion\.site$/.test(host) ? 'course_access' : '');
      if (cta) push(Object.assign({ event: 'cta_click', cta: cta }, common));
    } catch (e) {}
  }
  document.addEventListener('click', onClick, true);
  document.addEventListener('auxclick', onClick, true);

  // ---- Spotlightr video progress --------------------------------------------
  // The Spotlightr player reports its own milestones to the page that embeds
  // it (postMessage, name 'triggerGtmTags'). Each one is recorded once per
  // video, per player, per page load: a pause and resume is not a second start.
  // Players added after the page loads, like the one in the /training modal,
  // are found when their first message arrives.
  var MILESTONES = {
    'play': ['video_start', 0],
    '25%': ['video_progress', 25],
    '50%': ['video_progress', 50],
    '75%': ['video_progress', 75],
    'ended': ['video_complete', 100]
  };
  var seen = new WeakMap();

  function onPlayerMessage(event) {
    try {
      var origin = new URL(event.origin);
      if (origin.protocol !== 'https:' || !/\.spotlightr\.com$/.test(origin.hostname)) return;
      var data = event.data;
      if (typeof data === 'string') {
        try { data = JSON.parse(data); } catch (e) { return; }
      }
      var message = data && data.data;
      if (!message || message.name !== 'triggerGtmTags') return;
      var milestone = MILESTONES[message.event];
      if (!milestone) return;

      var frame = [].slice.call(document.querySelectorAll('iframe')).find(function (f) {
        return f.contentWindow === event.source;
      });
      if (!frame) return;

      var src = frame.getAttribute('src') || '';
      var watch = src.match(/\/watch\/([^/?#]+)/);
      var videoId = watch ? watch[1] : '';
      var done = seen.get(frame);
      if (!done) { done = {}; seen.set(frame, done); }
      var key = videoId + '|' + message.event;
      if (done[key]) return;
      done[key] = true;

      var title = frame.dataset.videoTitle || frame.title || document.title || '';
      var percent = milestone[1];
      push({
        event: milestone[0],
        video_provider: 'spotlightr',
        video_id: videoId,
        video_title: title,
        video_percent: percent
      });

      // How far someone watched goes on their CRM history too, from a quarter
      // onwards. A start alone says little.
      if (percent > 0 && crmAllowed && visitorId) {
        send(JSON.stringify({
          v: visitorId,
          u: currentUrl(),
          video: { provider: 'spotlightr', id: videoId, title: title.slice(0, 200), pct: percent }
        }));
      }
    } catch (e) {}
  }
  window.addEventListener('message', onPlayerMessage);
})();
