// Floating "back to top" button, injected on every page that includes this script.
(function () {
  var btn = document.createElement('button');
  btn.id = 'scroll-top-btn';
  btn.setAttribute('aria-label', 'Scroll to top');
  btn.innerHTML = '&uarr;';
  document.body.appendChild(btn);

  var style = document.createElement('style');
  style.textContent =
    '#scroll-top-btn{position:fixed;bottom:24px;right:24px;width:48px;height:48px;border-radius:50%;' +
    'background:var(--accent,#c6a06a);color:var(--accent-ink,#141210);border:none;cursor:pointer;' +
    'font-size:20px;line-height:1;display:flex;align-items:center;justify-content:center;' +
    'box-shadow:0 8px 24px rgba(0,0,0,0.35);opacity:0;visibility:hidden;transform:translateY(8px);' +
    'transition:opacity .25s,transform .25s,visibility .25s;z-index:40}' +
    '#scroll-top-btn.show{opacity:1;visibility:visible;transform:translateY(0)}' +
    '#scroll-top-btn:hover{transform:translateY(-2px)}' +
    '@media(max-width:640px){#scroll-top-btn{width:44px;height:44px;bottom:18px;right:18px;font-size:18px}}';
  document.head.appendChild(style);

  function toggle() {
    if (window.scrollY > 500) btn.classList.add('show');
    else btn.classList.remove('show');
  }
  window.addEventListener('scroll', toggle, { passive: true });
  toggle();

  btn.addEventListener('click', function () {
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
  });
})();
