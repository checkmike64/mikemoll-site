# Source data for Mike Moll guest appearances

Files here are the reusable research store for building the media page, the
guest-appearance directory, and every episode blog post.

- appearances.json          -> master structured dataset (one object per appearance)
- appearances_notion.json   -> raw Notion-field backbone (links, host, notes, status)
- enrichment.jsonl          -> per-episode public-source results (cover URL, notes, transcript status)
- transcripts/<slug>.txt     -> full transcript / show notes text where retrievable

## Cover art note
GitHub upload of local JPEGs is pending repo access. Until then, cover_url points
to each show's official public artwork (Apple/Spotify/host og:image or YouTube thumb).

## Retired generators
`gen.py` and `build_pages.py` are retired (2026-10-07) and exit before doing anything.
They predate the GTM snippet, canonicals, OG and JSON-LD on the live pages and the
design system v2 chrome, so running them would wipe all of that from `blog/`,
`media.html` and `guest-appearances.html`. The data here stays useful as a research store.
New posts are built with `generator/video-blog/build_post.py`; the written posts were moved
onto v2 by `scripts/migrate_posts_v2.py` (their covers now point at `cover_url`).
