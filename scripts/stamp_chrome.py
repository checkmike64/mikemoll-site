#!/usr/bin/env python3
"""Stamp the shared v2 chrome (head links, header, footer) into static pages.

The partials live in generator/chrome/. A page opts in with marker pairs;
only the text between a pair is replaced:

  <!-- chrome:head --> ... <!-- /chrome:head -->
      preconnects, the one font URL, /assets/site-v2.css
  <!-- chrome:header site --> ... <!-- /chrome:header -->
      logo + Consulting, Podcast guesting, Results, Media. No button.
  <!-- chrome:header podcast --> ... <!-- /chrome:header -->
      the same + outlined "Free assessment" (podcast-guesting-nav)
  <!-- chrome:header focus href="#apply" label="Apply" cta="mastermind-nav" --> ... <!-- /chrome:header -->
      logo + the page's one action (cta is optional)
  <!-- chrome:footer full --> ... <!-- /chrome:footer -->
  <!-- chrome:footer focus --> ... <!-- /chrome:footer -->

The nav link that matches the page's clean URL gets aria-current="page".
Override it with current="/path" on the header marker (current="" for none).

Never touched: anything outside the markers (GTM, the favicon block, title,
canonical, OG, JSON-LD, scripts, page content).

Usage:
  python3 scripts/stamp_chrome.py [--check] [paths...]

  With no paths it stamps every .html in the repo that carries a marker
  (drafts/, generator/ and node_modules/ are skipped). --check changes
  nothing and exits 1 if any page has drifted from the partials.
  Exit 2 on a malformed marker. Safe to re-run: the output is deterministic.
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = ROOT / 'generator' / 'chrome'
SKIP_DIRS = {'drafts', 'generator', 'node_modules', 'scripts', 'api', 'assets', 'media', 'images', '_data'}

PARTIALS = {
    'head': {'': 'head.html'},
    'header': {'site': 'header-site.html', 'podcast': 'header-podcast.html', 'focus': 'header-focus.html'},
    'footer': {'full': 'footer-full.html', 'focus': 'footer-focus.html'},
}
OPEN = re.compile(r'<!-- chrome:(head|header|footer)\b(.*?)-->')
CLOSE = re.compile(r'<!-- /chrome:(head|header|footer) -->')
ATTR = re.compile(r'([a-z]+)="([^"]*)"')


class MarkerError(Exception):
    pass


def partial(name):
    return (CHROME / name).read_text(encoding='utf-8').rstrip('\n')


def clean_url(path):
    rel = path.resolve().relative_to(ROOT).as_posix()
    rel = re.sub(r'\.html$', '', rel)
    if rel == 'index':
        return '/'
    if rel.endswith('/index'):
        rel = rel[:-len('/index')]
    return '/' + rel


def parse_args(raw, where):
    raw = raw.strip()
    m = re.match(r'([a-z]+)?\s*(.*)$', raw, re.S)
    variant, rest = (m.group(1) or ''), m.group(2).strip()
    attrs = dict(ATTR.findall(rest))
    leftover = ATTR.sub('', rest).strip()
    if leftover:
        raise MarkerError(f'{where}: cannot read marker arguments "{leftover}"')
    return variant, attrs


def render(kind, variant, attrs, page_url, where):
    files = PARTIALS[kind]
    if variant not in files:
        raise MarkerError(f'{where}: unknown {kind} variant "{variant}" (expected one of: {", ".join(k or "(none)" for k in files)})')
    out = partial(files[variant])
    if kind == 'header' and variant in ('site', 'podcast'):
        nav = partial('nav.html')
        current = attrs.get('current', page_url)
        if current:
            nav = nav.replace(f'<a href="{current}">', f'<a href="{current}" aria-current="page">', 1)
        out = out.replace('{{nav}}', nav)
    if kind == 'header' and variant == 'focus':
        for need in ('href', 'label'):
            if not attrs.get(need):
                raise MarkerError(f'{where}: focus header needs {need}="..."')
        cta = attrs.get('cta')
        out = (out.replace('{{href}}', html.escape(attrs['href'], quote=True))
                  .replace('{{label}}', html.escape(attrs['label'], quote=False))
                  .replace('{{cta}}', f' data-cta="{html.escape(cta, quote=True)}"' if cta else ''))
    if '{{' in out:
        raise MarkerError(f'{where}: unfilled placeholder in {files[variant]}')
    return out


def stamp(text, path):
    page_url = clean_url(path)
    out, pos, blocks = [], 0, 0
    opens = list(OPEN.finditer(text))
    closes = list(CLOSE.finditer(text))
    if len(opens) != len(closes):
        raise MarkerError(f'{path}: {len(opens)} opening vs {len(closes)} closing chrome markers')
    for m in opens:
        kind = m.group(1)
        line = text.count('\n', 0, m.start()) + 1
        where = f'{path}:{line}'
        if m.start() < pos:
            raise MarkerError(f'{where}: chrome marker inside another chrome block')
        close = CLOSE.search(text, m.end())
        if not close or close.group(1) != kind:
            raise MarkerError(f'{where}: <!-- chrome:{kind} --> has no matching <!-- /chrome:{kind} -->')
        nxt = OPEN.search(text, m.end())
        if nxt and nxt.start() < close.start():
            raise MarkerError(f'{where}: <!-- chrome:{kind} --> is not closed before the next marker')
        variant, attrs = parse_args(m.group(2), where)
        body = render(kind, variant, attrs, page_url, where)
        out.append(text[pos:m.end()])
        out.append('\n' + body + '\n')
        out.append(close.group(0))
        pos = close.end()
        blocks += 1
    out.append(text[pos:])
    return ''.join(out), blocks


def find_pages():
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = Path(dirpath).relative_to(ROOT)
        dirnames[:] = sorted(d for d in dirnames if not d.startswith('.') and not (rel == Path('.') and d in SKIP_DIRS))
        for f in sorted(filenames):
            if f.endswith('.html'):
                p = Path(dirpath) / f
                if '<!-- chrome:' in p.read_text(encoding='utf-8'):
                    pages.append(p)
    return pages


def main():
    ap = argparse.ArgumentParser(description='Stamp the shared v2 header/footer/head links into pages.')
    ap.add_argument('--check', action='store_true', help='change nothing; exit 1 if any page drifted from the partials')
    ap.add_argument('paths', nargs='*', help='pages to stamp (default: every page with a chrome marker)')
    a = ap.parse_args()
    paths = [Path(p) for p in a.paths] if a.paths else find_pages()
    drift = 0
    try:
        for p in paths:
            text = p.read_text(encoding='utf-8')
            new, blocks = stamp(text, p)
            rel = p.resolve().relative_to(ROOT).as_posix()
            if not blocks:
                print(f'skip   {rel} (no chrome markers)')
            elif new == text:
                print(f'ok     {rel} ({blocks} blocks)')
            elif a.check:
                print(f'drift  {rel}: run python3 scripts/stamp_chrome.py {rel}')
                drift += 1
            else:
                p.write_text(new, encoding='utf-8')
                print(f'stamp  {rel} ({blocks} blocks)')
    except MarkerError as e:
        print(f'error: {e}', file=sys.stderr)
        return 2
    return 1 if drift else 0


if __name__ == '__main__':
    sys.exit(main())
