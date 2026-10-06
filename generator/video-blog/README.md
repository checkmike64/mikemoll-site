# Video blog posts

Turns a YouTube video (own podcast episode, guest appearance, or solo video) into a
blog page at `/blog/<slug>`. The writing process lives in the `video-blog` skill in
`ai-skills/coaching/video-blog`. This folder is the site side: the page template and the
builder.

```
generator/video-blog/
  template.html        page shell (GTM, favicon block, nav, footer, slots)
  build_post.py        posts/<slug>.json -> blog/<slug>.html (+ index updates)
  posts/<slug>.json    one content file per post; the source of truth for that page
assets/video-blog.css  post styles (all classes prefixed vb-), loaded after site.css
assets/video-blog.js   player facade, chapter seeking, contents scroll-spy, CTA events
```

Build a post (standard library Python, no installs):

```bash
python3 generator/video-blog/build_post.py generator/video-blog/posts/<slug>.json --index
```

`--index` also updates the post's card on `blog.html` (adds one for a new podcast episode
or video), its `sitemap.xml` lastmod, and `llms.txt`. Guest-appearance cards live on
`guest-appearances.html` and are added by hand.

**Don't hand-edit a built page.** Edit its JSON and rebuild. A design change goes into
`template.html` or `video-blog.css`, then every post is rebuilt:

```bash
for f in generator/video-blog/posts/*.json; do python3 generator/video-blog/build_post.py "$f"; done
```

## The page, top to bottom

Breadcrumb · hero (eyebrow, H1, promise, byline, facts, topic tags, CTA) · video facade
(the only player; loads youtube-nocookie on click) · short answer · contents · key
takeaways · question sections · about the guest / about the show · further reading ·
one collapsed panel holding the chapters and the transcript · author box · side rail
(tags, share, offer) · keep reading (3 cards) · closing CTA · phone CTA bar.

Not used in this format (Mike's call, 2026-10-05): definition boxes, comparison tables,
a second video player.

## JSON fields

| Field | Notes |
|---|---|
| `slug` | Lowercase, hyphens. Existing posts keep their slug (rebuild in place). New posts: short, 3–5 words. |
| `category` | `podcast-episode` (hub `/podcast`), `guest-appearance` (hub `/guest-appearances`), `video` (hub `/videos`, page not built yet). |
| `format` | Second half of the eyebrow, e.g. `Live coaching`, `Interview`, `Solo`. |
| `crumb_name` | Short last breadcrumb item, e.g. the guest's name. |
| `title_tag` | 50–60 characters, keyword first, ends `\| Mike Moll`. |
| `meta_description` | 150–160 characters. |
| `h1`, `h1_accent` | The search question. `h1_accent` (optional) is the last few words, shown in blue. |
| `about` | Topic name for the schema `about` field. |
| `sub` | Two-sentence promise under the H1. |
| `date_published`, `date_modified` | `YYYY-MM-DD`. A rebuild keeps the original `date_published`. |
| `video` | `youtube_id`, `title` (YouTube title), `description`, `upload_date` (ISO with offset), `duration_seconds`. |
| `author` | `name`, `image`, `byline_role`, `role`, `job_title`, `knows_about[]`, `bio`, `links[{label,url}]`. Bio lines come from the brain. |
| `guest` | Podcast episodes with a guest: `name`, `initials`, `role`, `org`, `org_url`, `bio`, `links[]`. |
| `show` | Guest appearances only: `name`, `url`, `host`, `episode_url`, `about`, optional `initials`. |
| `tags` | 2–4 from the fixed tag list in the brain. |
| `short_answer` | `q` (one question) and `a` (3–4 sentences, plain text). |
| `takeaways` | 6 plain-text sentences. The last one carries the strongest point. |
| `sections` | 6–9 of `{id, h2, html}`. `id` = the slugged question. `html` may use `p`, `b`, `a`, `figure.vb-pull`, `aside.vb-callout`, `ol.vb-steps`. Timestamp links get `data-t="<seconds>"`. |
| `further_reading` | 2–3 `{label, url}` site links. |
| `related` | Exactly 3 `{url, tag, title, desc, go}` cards. |
| `cta` | `href`, `button`, `headline`, `headline_accent`, `sub`, `micro`, `rail_label`, `rail_text`, `mobile_text`. Values come from the brain. |
| `chapters` | `{t, title}` in time order, first at `t: 0`. |
| `transcript` | `policy` (`full` or `mike-only`) and `chapters[{t, paragraphs[{speaker, text}]}]`. Each `t` matches a chapter. |
| `index_card` | `badge`, `title`, `desc` for the `blog.html` card. |
