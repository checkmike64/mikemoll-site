#!/usr/bin/env python3
"""Build a video blog post page from its content file.

    python3 generator/video-blog/build_post.py generator/video-blog/posts/<slug>.json [--index]

Writes blog/<slug>.html from template.html, then stamps the shared v2 header,
footer and head links into its chrome:* markers (scripts/stamp_chrome.py, the
partials in generator/chrome/). With --index it also updates the blog index
card (blog.html), sitemap.xml and llms.txt. The JSON format is documented in
generator/video-blog/README.md. Standard library only.
"""
import argparse
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SITE = "https://www.mikemoll.co"

sys.path.insert(0, str(REPO / "scripts"))
from stamp_chrome import MarkerError, stamp as stamp_chrome  # noqa: E402  (the one renderer for the shared chrome)

# Site structure: category -> label, hub page, blog.html data-tag.
CATEGORIES = {
    "podcast-episode": {"label": "Podcast", "hub": "/podcast", "hub_file": "podcast.html", "section": "Podcast"},
    "guest-appearance": {"label": "Guest appearance", "hub": "/guest-appearances", "hub_name": "Guest appearances",
                         "hub_file": "guest-appearances.html", "section": "Guest appearances"},
    "video": {"label": "Video", "hub": "/videos", "hub_name": "Videos", "hub_file": "videos.html", "section": "Videos"},
}
REQUIRED = ["slug", "category", "format", "crumb_name", "title_tag", "meta_description", "h1", "sub",
            "date_published", "date_modified", "video", "author", "tags", "short_answer", "takeaways",
            "sections", "further_reading", "related", "cta", "chapters", "transcript"]

e = html.escape
warnings = []


def warn(msg):
    warnings.append(msg)


def dur(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def iso_dur(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    out = "PT" + (f"{h}H" if h else "") + (f"{m}M" if m else "") + (f"{s}S" if s or not (h or m) else "")
    return out


def nice_date(iso):
    y, mo, d = iso[:10].split("-")
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    return f"{int(d)} {months[int(mo) - 1]} {y}"


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def validate(p):
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        sys.exit(f"Missing fields: {', '.join(missing)}")
    if p["category"] not in CATEGORIES:
        sys.exit(f"category must be one of {list(CATEGORIES)}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["slug"]):
        sys.exit("slug must be lowercase words joined by hyphens")
    if p["category"] == "guest-appearance" and not p.get("show"):
        sys.exit("guest-appearance posts need a 'show' block")
    ids = [s["id"] for s in p["sections"]]
    if len(ids) != len(set(ids)):
        sys.exit("section ids must be unique")
    if not 50 <= len(p["title_tag"]) <= 60:
        warn(f"title_tag is {len(p['title_tag'])} chars (target 50-60)")
    if not 140 <= len(p["meta_description"]) <= 160:
        warn(f"meta_description is {len(p['meta_description'])} chars (target 150-160)")
    if not 5 <= len(p["takeaways"]) <= 7:
        warn(f"{len(p['takeaways'])} takeaways (target 6)")
    if not 6 <= len(p["sections"]) <= 10:
        warn(f"{len(p['sections'])} sections (target 6-9)")
    if len(p["related"]) != 3:
        warn("related should have exactly 3 cards")
    cat = CATEGORIES[p["category"]]
    if not (REPO / cat["hub_file"]).exists():
        warn(f"hub page {cat['hub_file']} doesn't exist yet; the breadcrumb link to {cat['hub']} will 404")
    chap_ts = [c["t"] for c in p["chapters"]]
    if chap_ts != sorted(chap_ts) or (chap_ts and chap_ts[0] != 0):
        sys.exit("chapters must start at 0 and be in time order")
    tr_ts = [c["t"] for c in p["transcript"]["chapters"]]
    if not set(tr_ts) <= set(chap_ts):
        sys.exit("every transcript chapter 't' must match a chapter start")
    for s in p["sections"]:
        if re.search(r"class=\"(def|table-wrap)\"|<table", s["html"]):
            warn(f"section {s['id']} contains a definition box or table; those are dropped from this format")


def cta_labels(cta):
    """Button labels for the post's one offer: (full label, short label for the phone bar).

    Mike's call 8 (2026-10-07): a button lands where it promises. /consulting#apply is the
    application form (the booking step comes after it), so every button that goes there is
    labelled as applying, whatever the JSON's cta.button says. Any other destination (a real
    booking link) keeps the JSON label.
    """
    href = cta["href"].replace(SITE, "", 1)
    if href.split("?")[0] == "/consulting#apply":
        return "Apply for a free assessment", "Apply"
    return cta["button"], "Book"


def yt(p, t=None):
    base = f"https://www.youtube.com/watch?v={p['video']['youtube_id']}"
    return base if t is None else f"{base}&t={t}s"


def render(p):
    cat = CATEGORIES[p["category"]]
    url = f"{SITE}/blog/{p['slug']}"
    v = p["video"]
    thumb = f"https://i.ytimg.com/vi/{v['youtube_id']}/maxresdefault.jpg"
    h1_full = p["h1"] + (" " + p["h1_accent"] if p.get("h1_accent") else "")
    h1_html = e(p["h1"]) + (f' <span class="vb-ac">{e(p["h1_accent"])}</span>' if p.get("h1_accent") else "")
    author, cta = p["author"], p["cta"]
    cta_button, cta_short = cta_labels(cta)

    # article word count (takeaways + sections) -> read time
    words = len(" ".join(p["takeaways"]).split()) + sum(len(text_of(s["h2"] + " " + s["html"]).split()) for s in p["sections"])
    read = max(1, round(words / 230))

    crumbs = (f'<a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/blog">Blog</a> '
              f'<span aria-hidden="true">/</span> <a href="{cat["hub"]}">{e(cat.get("hub_name", cat["label"]))}</a> '
              f'<span aria-hidden="true">/</span> <span>{e(p["crumb_name"])}</span>')
    date_label = "Updated" if p["date_modified"] != p["date_published"] else "Published"
    date_val = p["date_modified"]
    facts = (f'<span>{date_label} <time datetime="{date_val}">{nice_date(date_val)}</time></span>'
             f'<span>{read} min read</span><span>{dur(v["duration_seconds"])} video</span>')
    chips = "".join(f'<span class="vb-chip">{e(t)}</span>' for t in p["tags"])
    toc = "".join(f'<li><a href="#{s["id"]}">{e(s["h2"])}</a></li>' for s in p["sections"])
    takeaways = "".join(f"<li>{e(t)}</li>" for t in p["takeaways"])
    sections = "\n".join(
        f'      <section class="vb-sec" id="{s["id"]}">\n        <h2>{e(s["h2"])}</h2>\n        {s["html"].strip()}\n      </section>'
        for s in p["sections"])

    guest_box = ""
    if p["category"] == "guest-appearance":
        sh = p["show"]
        links = f'<a class="tlink" href="{e(sh["episode_url"])}" target="_blank" rel="noopener">Listen to the full episode</a>'
        if sh.get("url"):
            links += f'<a class="tlink" href="{e(sh["url"])}" target="_blank" rel="noopener">{e(sh["name"])}</a>'
        guest_box = (f'      <aside class="vb-guest" aria-label="About the show">\n        <div class="vb-mono" aria-hidden="true">{e(sh.get("initials", sh["name"][:2].upper()))}</div>\n'
                     f'        <div>\n          <span class="vb-kl" style="margin-bottom:6px">About the show</span>\n          <h3>{e(sh["name"])}</h3>\n'
                     f'          <p class="vb-role">Hosted by {e(sh["host"])}</p>\n          <p>{e(sh["about"])}</p>\n          <div class="vb-links">{links}</div>\n        </div>\n      </aside>')
    elif p.get("guest"):
        g = p["guest"]
        links = "".join(f'<a class="tlink" href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in g.get("links", []))
        guest_box = (f'      <aside class="vb-guest" aria-label="About the guest">\n        <div class="vb-mono" aria-hidden="true">{e(g["initials"])}</div>\n'
                     f'        <div>\n          <span class="vb-kl" style="margin-bottom:6px">About the guest</span>\n          <h3>{e(g["name"])}</h3>\n'
                     f'          <p class="vb-role">{e(g["role"])}</p>\n          <p>{e(g["bio"])}</p>\n          <div class="vb-links">{links}</div>\n        </div>\n      </aside>')

    further = "".join(f'<li><a href="{e(f["url"])}">{e(f["label"])}</a></li>' for f in p["further_reading"])
    titles = {c["t"]: c["title"] for c in p["chapters"]}
    chapters = "".join(
        f'<li><a href="{e(yt(p, c["t"]))}" data-t="{c["t"]}" target="_blank" rel="noopener"><time datetime="{iso_dur(c["t"])}">{dur(c["t"])}</time><span>{e(c["title"])}</span></a></li>'
        for c in p["chapters"])

    tr_blocks, tr_plain = [], []
    for c in p["transcript"]["chapters"]:
        paras, last, plain = [], None, []
        for para in c["paragraphs"]:
            sp = para.get("speaker")
            label = f"<b>{e(sp)}:</b> " if sp and sp != last else ""
            paras.append(f"<p>{label}{e(para['text'])}</p>")
            plain.append((f"{sp}: " if sp and sp != last else "") + para["text"])
            last = sp or last
        tr_blocks.append(
            f'            <div class="vb-tr-sec"><h3 class="vb-tr-h"><a href="{e(yt(p, c["t"]))}" data-t="{c["t"]}" target="_blank" rel="noopener">'
            f'<time datetime="{iso_dur(c["t"])}">{dur(c["t"])}</time></a> {e(titles[c["t"]])}</h3>{"".join(paras)}</div>')
        tr_plain.append(f"[{dur(c['t'])}] " + " ".join(plain))
    mike_only = p["transcript"].get("policy") == "mike-only"
    if mike_only:
        tr_label = "Mike's answers"
        tr_note = (f"Mike's answers from the episode, lightly cleaned. The host's questions are left out; "
                   f"the full conversation is on {e(p['show']['name'])}. Timestamps open that moment in the video.")
    else:
        tr_label = "Full transcript"
        tr_note = "From the YouTube captions, lightly cleaned for punctuation and filler words. Timestamps open that moment in the video."
    panel_label = "Episode chapters and transcript" if p["category"] != "video" else "Video chapters and transcript"

    author_links = "".join(f'<a class="tlink" href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in author.get("links", []))
    related = "".join(
        f'<a class="vb-card" href="{e(r["url"])}"><span class="vb-tag">{e(r["tag"])}</span><h3>{e(r["title"])}</h3><p>{e(r["desc"])}</p><span class="vb-go">{e(r["go"])} &rarr;</span></a>'
        for r in p["related"])
    cta_headline = e(cta["headline"]) + (f' <span class="vb-ac">{e(cta["headline_accent"])}</span>' if cta.get("headline_accent") else "")

    # ---- JSON-LD graph ----
    org, mike = f"{SITE}/#organization", f"{SITE}/#mike"
    clips = []
    for i, c in enumerate(p["chapters"]):
        end = p["chapters"][i + 1]["t"] if i + 1 < len(p["chapters"]) else int(v["duration_seconds"])
        clips.append({"@type": "Clip", "@id": f"{url}#clip-{c['t']}", "name": c["title"], "startOffset": c["t"], "endOffset": end, "url": yt(p, c["t"])})
    graph = [
        {"@type": "Organization", "@id": org, "name": "Mike Moll", "url": f"{SITE}/",
         "sameAs": [l["url"] for l in author.get("links", [])]},
        {"@type": "Person", "@id": mike, "name": author["name"], "url": f"{SITE}/", "jobTitle": author["job_title"],
         "image": f"{SITE}{author['image']}", "worksFor": {"@id": org}, "knowsAbout": author.get("knows_about", []),
         "sameAs": [l["url"] for l in author.get("links", [])]},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Mike Moll", "publisher": {"@id": org}},
        {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": h1_full, "description": p["meta_description"], "inLanguage": "en",
         "isPartOf": {"@id": f"{SITE}/#website"}, "breadcrumb": {"@id": f"{url}#breadcrumb"}, "primaryImageOfPage": thumb,
         "datePublished": p["date_published"], "dateModified": p["date_modified"],
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".vb-answer-p", ".vb-takeaways"]}},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog"},
            {"@type": "ListItem", "position": 3, "name": cat.get("hub_name", cat["label"]), "item": f"{SITE}{cat['hub']}"},
            {"@type": "ListItem", "position": 4, "name": h1_full, "item": url}]},
        {"@type": "BlogPosting", "@id": f"{url}#article", "headline": h1_full, "description": p["meta_description"], "inLanguage": "en",
         "author": {"@id": mike}, "publisher": {"@id": org}, "mainEntityOfPage": {"@id": f"{url}#webpage"}, "isPartOf": {"@id": f"{SITE}/#website"},
         "datePublished": p["date_published"], "dateModified": p["date_modified"], "image": thumb, "articleSection": cat["section"],
         "wordCount": words, "timeRequired": f"PT{read}M", "keywords": p["tags"],
         "about": [{"@type": "Thing", "name": p.get("about", h1_full)}, {"@id": f"{SITE}/#service"}],
         "video": {"@id": f"{url}#video"},
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".vb-answer-p", ".vb-takeaways"]}},
        {"@type": "ProfessionalService", "@id": f"{SITE}/#service", "name": "Mike Moll Coaching", "provider": {"@id": org}, "url": f"{SITE}{cta['href'].split('#')[0]}"},
        {"@type": "VideoObject", "@id": f"{url}#video", "name": v["title"], "description": v["description"],
         "thumbnailUrl": [thumb, f"https://i.ytimg.com/vi/{v['youtube_id']}/hqdefault.jpg"], "uploadDate": v["upload_date"],
         "duration": iso_dur(v["duration_seconds"]), "contentUrl": yt(p), "embedUrl": f"https://www.youtube.com/embed/{v['youtube_id']}",
         "inLanguage": "en", "author": {"@id": mike}, "publisher": {"@id": org}, "transcript": " ".join(tr_plain), "hasPart": clips},
    ]
    mentions = []
    if p["category"] == "podcast-episode":
        ep = {"@type": "PodcastEpisode", "@id": f"{url}#episode", "name": v["title"], "url": url, "datePublished": v["upload_date"][:10],
              "timeRequired": iso_dur(v["duration_seconds"]), "partOfSeries": {"@id": f"{SITE}/podcast#series"}, "author": {"@id": mike},
              "associatedMedia": {"@id": f"{url}#video"}}
        if p.get("guest"):
            ep["contributor"] = {"@id": f"{url}#guest"}
        graph.append(ep)
    if p["category"] == "guest-appearance":
        sh = p["show"]
        graph.append({"@type": "Person", "@id": f"{url}#host", "name": sh["host"]})
        graph.append({"@type": "PodcastEpisode", "@id": f"{url}#episode", "name": v["title"], "url": sh["episode_url"],
                      "datePublished": v["upload_date"][:10], "partOfSeries": {"@type": "PodcastSeries", "name": sh["name"], **({"url": sh["url"]} if sh.get("url") else {})},
                      "author": {"@id": f"{url}#host"}, "contributor": {"@id": mike}, "associatedMedia": {"@id": f"{url}#video"}})
        mentions.append({"@id": f"{url}#host"})
    if p.get("guest"):
        g = p["guest"]
        gp = {"@type": "Person", "@id": f"{url}#guest", "name": g["name"], "jobTitle": g["role"], "sameAs": [l["url"] for l in g.get("links", [])]}
        if g.get("org"):
            gp["worksFor"] = {"@type": "Organization", "name": g["org"], **({"url": g["org_url"]} if g.get("org_url") else {})}
        graph.append(gp)
        mentions.append({"@id": f"{url}#guest"})
    if mentions:
        graph[5]["mentions"] = mentions
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/")

    slots = {
        "SLUG": p["slug"], "TITLE_TAG": e(p["title_tag"]), "META_DESCRIPTION": e(p["meta_description"]), "URL": url,
        "URL_ENC": urllib.parse.quote(url, safe=""), "OG_TITLE": e(h1_full), "THUMB_URL": thumb,
        "DATE_PUBLISHED": p["date_published"], "DATE_MODIFIED": p["date_modified"], "JSONLD": jsonld,
        "CTA_HREF": e(cta["href"]), "CTA_BUTTON": e(cta_button), "CTA_SHORT": e(cta_short), "CRUMBS": crumbs,
        "EYEBROW": f'<span class="vb-ac">{e(cat["label"])}</span> · {e(p["format"])}', "H1_HTML": h1_html, "SUB": e(p["sub"]),
        "AUTHOR_IMAGE": e(author["image"]), "AUTHOR_NAME": e(author["name"]), "BYLINE_ROLE": e(author["byline_role"]),
        "FACTS": facts, "CHIPS": chips, "YT_ID": v["youtube_id"], "VIDEO_TITLE_ATTR": e(v["title"]), "DURATION": dur(v["duration_seconds"]),
        "ANSWER_Q": e(p["short_answer"]["q"]), "ANSWER_A": e(p["short_answer"]["a"]), "TOC": toc, "TAKEAWAYS": takeaways,
        "SECTIONS": sections, "GUEST_BOX": guest_box, "FURTHER": further, "EPISODE_PANEL_LABEL": panel_label,
        "CHAPTER_COUNT": str(len(p["chapters"])), "CHAPTERS": chapters, "TRANSCRIPT_LABEL": tr_label, "TRANSCRIPT_NOTE": tr_note,
        "TRANSCRIPT": "\n".join(tr_blocks), "AUTHOR_ROLE": e(author["role"]), "AUTHOR_BIO": e(author["bio"]), "AUTHOR_LINKS": author_links,
        "RAIL_LABEL": e(cta["rail_label"]), "RAIL_TEXT": e(cta["rail_text"]), "RELATED": related, "CTA_HEADLINE_HTML": cta_headline,
        "CTA_SUB": e(cta["sub"]), "CTA_MICRO": e(cta["micro"]), "MCTA_TEXT": e(cta["mobile_text"]),
    }
    out = (HERE / "template.html").read_text()
    for k, val in slots.items():
        out = out.replace("{{" + k + "}}", val)
    left = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if left:
        sys.exit(f"Unfilled template slots: {sorted(set(left))}")
    return out, words, read, url, h1_full


def update_index(p, url, h1_full):
    slug, cat = p["slug"], p["category"]
    card = p.get("index_card", {})
    # blog.html card (podcast episodes and videos live on the blog index)
    blog = REPO / "blog.html"
    s = blog.read_text()
    m = re.search(r'<a class="pcard" href="/blog/' + re.escape(slug) + r'"[^>]*>.*?</a>', s, re.S)
    if m:
        block = m.group(0)
        if card.get("badge"):
            block = re.sub(r'(<div class="pc-badge">)[^<]*', lambda x: x.group(1) + e(card["badge"]), block, count=1)
        block = re.sub(r"<h3>.*?</h3>", lambda x: f"<h3>{e(card.get('title', h1_full))}</h3>", block, count=1, flags=re.S)
        block = re.sub(r"<p>.*?</p>", lambda x: f"<p>{e(card.get('desc', p['meta_description']))}</p>", block, count=1, flags=re.S)
        s = s[:m.start()] + block + s[m.end():]
        blog.write_text(s)
        print("blog.html: card updated")
    elif cat in ("podcast-episode", "video"):
        tmpl = re.search(r'      <a class="pcard" href="/blog/[^"]+" data-tag="podcast-episode">.*?</a>\n', s, re.S)
        if not tmpl:
            warn("blog.html: no card to copy; add the card by hand")
        else:
            block = tmpl.group(0)
            block = re.sub(r'href="/blog/[^"]+"', f'href="/blog/{slug}"', block, count=1)
            block = re.sub(r'data-tag="[^"]+"', f'data-tag="{cat}"', block, count=1)
            block = re.sub(r'(<div class="pc-badge">)[^<]*', lambda x: x.group(1) + e(card.get("badge", p["format"])), block, count=1)
            block = re.sub(r'(<span class="pc-tag">)[^<]*', lambda x: x.group(1) + ("Podcast Episode" if cat == "podcast-episode" else "Video"), block, count=1)
            block = re.sub(r"<h3>.*?</h3>", lambda x: f"<h3>{e(card.get('title', h1_full))}</h3>", block, count=1, flags=re.S)
            block = re.sub(r"<p>.*?</p>", lambda x: f"<p>{e(card.get('desc', p['meta_description']))}</p>", block, count=1, flags=re.S)
            s = s.replace('<div class="grid" id="grid">\n', '<div class="grid" id="grid">\n' + block, 1)
            blog.write_text(s)
            print("blog.html: card added at the top")
    else:
        if f"/blog/{slug}" not in (REPO / "guest-appearances.html").read_text():
            warn("guest-appearances.html has no card for this post; add it by hand")

    # videos.html: the Videos hub mirrors every video post's blog.html card
    if cat == "video":
        vh = REPO / "videos.html"
        card_m = re.search(r'      <a class="pcard" href="/blog/' + re.escape(slug) + r'"[^>]*>.*?</a>\n', blog.read_text(), re.S)
        if not vh.exists() or not card_m:
            warn("videos.html or the blog.html card is missing; the Videos hub was not updated")
        else:
            v = vh.read_text()
            old = re.search(r'      <a class="pcard" href="/blog/' + re.escape(slug) + r'"[^>]*>.*?</a>\n', v, re.S)
            if old:
                v = v[:old.start()] + card_m.group(0) + v[old.end():]
            else:
                marker = "    <!-- vb-hub: build_post.py adds each video post's card at the top of this grid -->\n"
                v = v.replace(marker, marker + card_m.group(0), 1)
            v = re.sub(r'<meta name="robots" content="noindex, follow"><!-- vb-hub:[^>]*-->',
                       '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">', v)
            vh.write_text(v)
            print("videos.html: card added/updated, page indexable")

    # sitemap.xml
    sm = REPO / "sitemap.xml"
    s = sm.read_text()
    entry = f"<loc>{url}</loc>"
    if entry in s:
        s = re.sub(re.escape(entry) + r"<lastmod>[^<]*</lastmod>", f"{entry}<lastmod>{p['date_modified']}</lastmod>", s)
    else:
        s = s.replace("</urlset>", f"  <url>{entry}<lastmod>{p['date_modified']}</lastmod></url>\n</urlset>")
    if cat == "video" and f"<loc>{SITE}/videos</loc>" not in s:
        s = s.replace("</urlset>", f"  <url><loc>{SITE}/videos</loc><lastmod>{p['date_modified']}</lastmod></url>\n</urlset>")
    sm.write_text(s)
    print("sitemap.xml: lastmod set")

    # llms.txt
    lt = REPO / "llms.txt"
    s = lt.read_text()
    if url not in s:
        heading = "## Guest appearance write-ups" if cat == "guest-appearance" else "## Podcast episodes and videos"
        line = f"- [{h1_full[0].upper() + h1_full[1:]}]({url}): {p['meta_description']}"
        if heading in s:
            i = s.index(heading) + len(heading)
            s = s[:i] + "\n" + line + s[i:]
        else:
            s = s.rstrip("\n") + f"\n\n{heading}\n{line}\n"
        lt.write_text(s)
        print("llms.txt: entry added")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("post", help="path to posts/<slug>.json")
    ap.add_argument("--index", action="store_true", help="also update blog.html, sitemap.xml and llms.txt")
    a = ap.parse_args()
    p = json.loads(Path(a.post).read_text())
    validate(p)
    out, words, read, url, h1_full = render(p)
    dest = REPO / "blog" / f"{p['slug']}.html"
    try:
        out, _ = stamp_chrome(out, dest)
    except MarkerError as err:
        sys.exit(f"template.html chrome markers: {err}")
    dest.write_text(out)
    print(f"wrote {dest.relative_to(REPO)}  ({words} words, {read} min read)")
    if a.index:
        update_index(p, url, h1_full)
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
