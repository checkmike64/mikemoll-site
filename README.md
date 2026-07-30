# mikemoll.co

Static site for Mike Moll. Plain HTML/CSS, no build step. Deploys on Vercel.

## Structure
- `index.html` — homepage
- `podcast.html` — the podcast page (serves at `/podcast`)
- `public/media/` — images (logos, photos, episode art). Small files, safe to commit.
- `public/audio/` — DO NOT commit audio/video. Host on YouTube/Spotify and embed.
- `vercel.json` — clean URLs + 301 redirects from the old GoHighLevel slugs
- `robots.txt`, `sitemap.xml`, `llms.txt` — SEO + AI-SEO
- `_template.html` — starting point for new pages. Has GTM and the scroll-to-top
  script already wired in. No build step means no automatic includes, so copy
  this file rather than starting a page from scratch. When you add a page,
  also add its URL to `sitemap.xml` (unless it should stay `noindex`, like a
  thank-you page).
- `scroll-top.js` — shared "back to top" button, included via `<script src="/scroll-top.js" defer></script>` before `</body>` on every page.
- Every page includes the same Google Tag Manager container (`GTM-55MG6M63`) — script tag high in `<head>`, noscript iframe right after `<body>`. Keep both when copying/editing pages.

## Get it live (first time, ~10 minutes)
1. **GitHub:** create a new repo at github.com/new named `mikemoll-site`. Upload this folder (drag-and-drop in the browser works, or use GitHub Desktop).
2. **Vercel:** go to vercel.com → Add New → Project → Import `mikemoll-site` → Deploy. You get a live `*.vercel.app` URL in ~30 seconds.
3. **Domain (later):** in Vercel → Project → Settings → Domains, add `mikemoll.co` and follow the DNS steps. Until then, keep the current site up.

## Adding media
Drop images into `public/media/` and reference them as `/media/your-file.webp`.

## Forms
The opt-in and apply forms are placeholders. Point them at your GoHighLevel form embed, or Formspree, before launch.

## Tags are merged, not replaced (and why that's slower)
GHL's `/contacts/upsert` treats the `tags` field you send as a full
**replacement** of the contact's tag list, not an addition — a known,
officially-acknowledged GHL API limitation. `api/lead.js` calls
`getExistingTags()` (in `api/_ghl.js`) before every upsert, merges the new
tag(s) in, and sends the complete set — otherwise every new form submission
would silently erase whatever tags were already on that contact.

There's no reliable "search contact by email" endpoint on this account —
GHL's list endpoint's `query` param mis-parses `+`/`@` in raw email
addresses, so `getExistingTags()` instead paginates the (confirmed
reliable) contact list and matches the email exactly, client-side, capped
at 1,000 contacts. This adds real latency to every form submission —
worst case (a brand-new contact, the common case for lead-magnet forms)
has to scan every page before concluding "not found," which took ~2.5s
against a ~480-contact account in testing. This will get slower as the
contact list grows. If GHL's search-by-email ever gets fixed/documented
properly, replacing the pagination scan with a single indexed lookup would
remove most of this latency.
