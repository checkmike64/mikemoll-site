#!/usr/bin/env python3
"""Move the written blog posts (blog/*.html without the vb-page body class) onto
design system v2. One-off migration, kept in the repo so the change is reviewable.

For each post it:
  1. head: swaps the Google Fonts link, the site.css link and the inline <style>
     block for the chrome:head markers (one font URL + /assets/site-v2.css) and
     <link rel="stylesheet" href="/assets/post.css">. The inline block must be one
     of the five known copies (matched by SHA-256); an unknown block stops the run.
     Nothing else in the head moves: title, canonical, meta, OG/Twitter, JSON-LD,
     GTM and the favicon block stay byte-identical (checked, see 6).
  2. body: replaces the old nav and footer with the chrome:header site and
     chrome:footer full markers, then stamps them (scripts/stamp_chrome.py).
  3. covers: a relative src="images/mike-moll-<show>.jpg" (404s under /blog/, then
     hotlinks through onerror) points straight at its cover_url from
     generator/_source/covers_manifest.json, which must equal the onerror fallback.
  4. the "Two ways I can help" box leaves the article and becomes the full-bleed
     closing band (.section.closing.band-dark): same heading, line and button labels;
     btn-primary -> .btn, btn-ghost -> .btn.line. Mike's call 8: its podcast button
     goes to /podcast-guesting instead of /podcast-workshop (any data-cta is kept).
  5. the back link loses its inline style (.post-back + .tlink).
  6. checks every post before writing and stops on any surprise: head tokens equal
     apart from the swapped links, article text and image count unchanged, hrefs and
     data-cta in the article unchanged apart from the call-8 link.

Usage:
  python3 scripts/migrate_posts_v2.py [--check] [paths...]

With no paths it takes every blog/*.html. Video posts (vb-page) are skipped.
Safe to re-run: a migrated post is only restamped. --check writes nothing and
exits 1 if any post would change. Exit 2 on an unknown style block or any
failed check. Standard library only.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from stamp_chrome import MarkerError, stamp  # noqa: E402

# The five inline style blocks the posts carry today (SHA-256 of the text between <style> and </style>).
KNOWN_BLOCKS = {
    'ed462f07a6c39051e188d1c6a74b8419038edbbd6743bfdd721d334d2eac7d60': 'shared (54 guest posts; media + guest-appearances carry it too)',
    '51c99ce781dc76bf582a51dfa036ff4df1dc961f478abcd0ce9f21ec5cbb3254': 'episode (8 own-show posts)',
    '70afbe8eb34ba1b15c92cc47a12ff7f7f2b2df53245f7063216e99223c0a35a0': 'guest legacy (3 posts)',
    'fd0220163349a96f3de1a028234eb505d95521b3c091fe8e2ec39f8603859ee6': 'single: 3-steps-to-raising-your-price',
    '1ecf2103aba7a1eebc5e93997c5e91561ad96a12efa8994737ea0ee66855557c': 'single: how-i-quit-my-comfortable-job-to-pursue-business',
}

HEAD_RUN = re.compile(
    r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
    r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
    r'<link href="https://fonts\.googleapis\.com/css2\?[^"]+" rel="stylesheet">\s*'
    r'<link rel="stylesheet" href="/assets/site\.css">\s*'
    r'<style>(.*?)</style>', re.S)
HEAD_NEW = ('<!-- chrome:head -->\n<!-- /chrome:head -->\n'
            '<link rel="stylesheet" href="/assets/post.css">')
NAV = re.compile(r'<nav class="site-nav">.*?</nav>', re.S)
FOOTER = re.compile(r'<footer class="site-foot">.*?</footer>', re.S)
BACK = re.compile(r'<(p|div) style="margin-top:3[46]px">(<a href="/blog" class="text-link">&larr; All episodes and writing</a>)</\1>')
COVER = re.compile(r'<img src="images/(mike-moll-[a-z0-9-]+\.jpg)"([^>]*?) onerror="this\.onerror=null;this\.src=\'([^\']+)\'">')
ANCHOR = re.compile(r'<a ([^>]*)>(.*?)</a>', re.S)

PODCAST_OLD, PODCAST_NEW = '/podcast-workshop', '/podcast-guesting'


class Stop(Exception):
    """A post did not look the way the migration expects. Nothing is written."""


# ---------- small HTML helpers (stdlib only) ----------
class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def text_of(fragment):
    p = _Text()
    p.feed(fragment)
    return re.sub(r'\s+', ' ', ''.join(p.out)).strip()


def links_of(fragment):
    """(href, data-cta) for every <a href> in document order."""
    out = []
    for m in re.finditer(r'<a\b([^>]*)>', fragment):
        a = m.group(1)
        h = re.search(r'\shref="([^"]*)"', ' ' + a)
        if h:
            c = re.search(r'\sdata-cta="([^"]*)"', ' ' + a)
            out.append((h.group(1), c.group(1) if c else None))
    return out


def head_tokens(head):
    """Tags and non-blank text of a <head>, in order: what must stay byte-identical."""
    return [t for t in re.findall(r'<[^>]*>|[^<]+', head) if t.strip()]


def balanced_div(text, start):
    """End index of the <div ...> that opens at `start` (nested divs allowed)."""
    depth, pos = 0, start
    tag = re.compile(r'<(/?)div\b[^>]*>')
    while True:
        m = tag.search(text, pos)
        if not m:
            raise Stop('unbalanced <div> in the CTA box')
        depth += -1 if m.group(1) else 1
        pos = m.end()
        if depth == 0:
            return pos


# ---------- the transform ----------
def covers_manifest():
    data = json.loads((ROOT / 'generator' / '_source' / 'covers_manifest.json').read_text(encoding='utf-8'))
    return {row['file']: row['url'] for row in data}


def closing_band(cta_html):
    """The old .cta box -> the closing navy band. Copy and attributes are carried over."""
    inner = re.sub(r'^<div class="cta">|</div>$', '', cta_html.strip())
    h3 = re.findall(r'<h3>(.*?)</h3>', inner, re.S)
    paras = re.findall(r'<p>(.*?)</p>', inner, re.S)
    anchors = ANCHOR.findall(inner)
    if len(h3) != 1 or len(paras) > 1 or len(anchors) != 2:
        raise Stop(f'CTA box has {len(h3)} heading(s), {len(paras)} paragraph(s), {len(anchors)} link(s); expected 1, 0-1, 2')
    leftover = ANCHOR.sub('', inner)
    leftover = re.sub(r'<h3>.*?</h3>|<p>.*?</p>|<div style="display:flex;flex-wrap:wrap;gap:12px">|</div>', '', leftover, flags=re.S)
    if leftover.strip():
        raise Stop(f'CTA box has unexpected content: {leftover.strip()[:80]!r}')
    buttons, changed = [], 0
    for attrs, label in anchors:
        cls = re.search(r'\sclass="([^"]*)"', ' ' + attrs)
        cls = cls.group(1) if cls else ''
        if cls == 'btn btn-primary':
            new_cls = 'btn'
        elif cls == 'btn btn-ghost':
            new_cls = 'btn line'
        else:
            raise Stop(f'CTA link with unexpected class "{cls}"')
        attrs = re.sub(r'(^|\s)class="[^"]*"', rf'\1class="{new_cls}"', attrs, count=1)
        href = re.search(r'\shref="([^"]*)"', ' ' + attrs).group(1)
        if href == PODCAST_OLD:   # Mike's call 8: podcast interest goes to the offer page
            attrs = attrs.replace(f'href="{PODCAST_OLD}"', f'href="{PODCAST_NEW}"', 1)
            changed += 1
        elif href != '/consulting':
            raise Stop(f'CTA link to unexpected href "{href}"')
        buttons.append(f'      <a {attrs}>{label}</a>')
    para = f'    <p>{paras[0]}</p>\n' if paras else ''
    band = ('<section class="section closing band-dark post-close">\n  <div class="wrap">\n'
            f'    <h2>{h3[0]}</h2>\n{para}    <div class="btns">\n' + '\n'.join(buttons) +
            '\n    </div>\n  </div>\n</section>')
    return band, changed


def migrate(text, path, manifest):
    """Return (new_text, report) for one post. Raises Stop on anything unexpected."""
    if '<body class="vb-page"' in text:
        return text, 'video post (generator/video-blog), skipped'
    if '/assets/post.css' in text:
        new, _ = stamp(text, path)
        return new, 'already on v2, restamped'

    head, sep, body = text.partition('</head>')
    if not sep:
        raise Stop('no </head>')

    # 1. head: fonts + site.css + the inline block -> chrome:head + post.css
    runs = list(HEAD_RUN.finditer(head))
    if len(runs) != 1:
        raise Stop(f'expected one font/site.css/<style> run in <head>, found {len(runs)}')
    run = runs[0]
    digest = hashlib.sha256(run.group(1).encode('utf-8')).hexdigest()
    if digest not in KNOWN_BLOCKS:
        raise Stop(f'unknown inline <style> block (sha256 {digest[:12]}); add it to KNOWN_BLOCKS only after a review')
    if head.count('<style') != 1 or text.count('<style') != 1:
        raise Stop('more than one <style> block')
    tail = head[run.end():]
    new_head = head[:run.start()] + HEAD_NEW + ('' if tail.startswith('\n') else '\n') + tail

    # 2. body chrome
    if len(NAV.findall(body)) != 1 or len(FOOTER.findall(body)) != 1:
        raise Stop('expected exactly one <nav class="site-nav"> and one <footer class="site-foot">')
    new_body = NAV.sub('<!-- chrome:header site -->\n<!-- /chrome:header -->', body, count=1)
    new_body = FOOTER.sub('<!-- chrome:footer full -->\n<!-- /chrome:footer -->', new_body, count=1)

    # article
    art = re.search(r'<article class="article">(.*?)</article>', new_body, re.S)
    if not art or new_body.count('<article') != 1:
        raise Stop('expected exactly one <article class="article">')
    old_article = art.group(1)
    article = old_article

    # 4. the CTA box -> closing band after the article
    starts = [m.start() for m in re.finditer(r'<div class="cta">', article)]
    if len(starts) != 1:
        raise Stop(f'expected one <div class="cta">, found {len(starts)}')
    end = balanced_div(article, starts[0])
    cta_html = article[starts[0]:end]
    band, podcast_changed = closing_band(cta_html)
    if podcast_changed != 1:
        raise Stop(f'expected one {PODCAST_OLD} button in the CTA box, found {podcast_changed}')
    article = article[:starts[0]].rstrip(' ') + article[end:].lstrip('\n')
    article = re.sub(r'\n[ \t]*\n(\s*\n)+', '\n\n', article)

    # 5. back link
    if len(BACK.findall(article)) != 1:
        raise Stop('expected one "All episodes and writing" back link')
    article = BACK.sub(r'<p class="post-back"><a href="/blog" class="tlink">&larr; All episodes and writing</a></p>', article, count=1)

    # 3. covers
    covers = 0

    def fix_cover(m):
        nonlocal covers
        fname, attrs, fallback = m.groups()
        url = manifest.get(fname)
        if url is None:
            raise Stop(f'cover {fname} is not in covers_manifest.json')
        if url != fallback:
            raise Stop(f'cover {fname}: manifest URL and onerror fallback differ')
        covers += 1
        return f'<img src="{url}"{attrs}>'
    article = COVER.sub(fix_cover, article)
    if 'src="images/' in article:
        raise Stop('a relative images/ src is left that the migration does not recognise')

    new_body = (new_body[:art.start(1)] + article + new_body[art.end(1):])
    new_body = new_body.replace('</article>', '</article>\n\n' + band, 1)
    new = new_head + sep + new_body

    # stamp the chrome (head links, header, footer)
    new, blocks = stamp(new, path)
    if blocks != 3:
        raise Stop(f'expected 3 chrome blocks, stamped {blocks}')

    # 6. checks
    nh = new.partition('</head>')[0]
    nh_wo = re.sub(r'<!-- chrome:head -->.*?<!-- /chrome:head -->\s*<link rel="stylesheet" href="/assets/post\.css">', '', nh, flags=re.S)
    oh_wo = HEAD_RUN.sub('', head)
    if head_tokens(nh_wo) != head_tokens(oh_wo):
        raise Stop('head changed beyond the stylesheet and font links')
    new_art = re.search(r'<article class="article">(.*?)</article>', new, re.S).group(1)
    new_band = re.search(r'<section class="section closing band-dark post-close">.*?</section>', new, re.S).group(0)
    old_wo_cta = old_article[:starts[0]] + old_article[end:]
    if text_of(new_art) != text_of(old_wo_cta):
        raise Stop('article text changed')
    if text_of(new_band) != text_of(cta_html):
        raise Stop('CTA text changed')
    if new_art.count('<img') != old_article.count('<img') or new_art.count('<iframe') != old_article.count('<iframe'):
        raise Stop('image or embed count changed')
    want = [(PODCAST_NEW if h == PODCAST_OLD else h, c) for h, c in links_of(old_wo_cta) + links_of(cta_html)]
    if links_of(new_art) + links_of(new_band) != want:
        raise Stop('article links or data-cta changed beyond the call-8 podcast link')
    if 'site.css' in new or '<style' in new:
        raise Stop('v1 stylesheet or an inline <style> block is left')

    return new, f'{KNOWN_BLOCKS[digest]}; covers fixed {covers}; podcast button -> {PODCAST_NEW}'


def main():
    ap = argparse.ArgumentParser(description='Move the written blog posts onto design system v2.')
    ap.add_argument('--check', action='store_true', help='write nothing; exit 1 if any post would change')
    ap.add_argument('paths', nargs='*', help='posts to migrate (default: every blog/*.html)')
    a = ap.parse_args()
    paths = [Path(p) for p in a.paths] if a.paths else sorted((ROOT / 'blog').glob('*.html'))
    manifest = covers_manifest()
    pending, done = 0, 0
    for p in paths:
        rel = p.resolve().relative_to(ROOT).as_posix()
        text = p.read_text(encoding='utf-8')
        try:
            new, report = migrate(text, p, manifest)
        except (Stop, MarkerError) as err:
            print(f'error  {rel}: {err}', file=sys.stderr)
            return 2
        if new == text:
            print(f'ok     {rel}: {report if "skipped" in report else "no change"}')
            continue
        if a.check:
            print(f'drift  {rel}: {report}')
            pending += 1
            continue
        p.write_text(new, encoding='utf-8')
        done += 1
        print(f'write  {rel}: {report}')
    print(f'{done} migrated' + (f', {pending} pending' if a.check else ''))
    return 1 if pending else 0


if __name__ == '__main__':
    sys.exit(main())
