# AI MASTERMIND — Handoff Package

Paste this into a new chat to continue. It captures the full state of the AI Mastermind landing page project as of 2026-08-14.

---

## 1. What this is

A landing page for Mike Moll's men-only mastermind, repositioned around one idea: a hand-picked room of **established founders who use AI to run leaner**. Two threads bind the room: (1) serious, established operators, (2) active in AI (using it to streamline ops, build processes, and build internal tools, NOT necessarily building AI products). The differentiator is the calibre of the operator, deliberately the opposite of the beginner-heavy free AI Facebook/Skool groups.

- **Name:** resolved to **"AI Mastermind"** (dropped the old working title "The Solo Brotherhood").
- **Price:** $85/month, billed quarterly. Priced low on purpose so money isn't the filter; the selection bar is. NOT pay-to-join.
- **Model:** hand-selected, interviewed by Mike. No numeric member cap; exclusivity comes from the vetting bar, not scarcity.

---

## 2. Files (all in the `Coaching Business` folder)

- `mikemoll-site/mastermind.html` — the FINAL live page, serves at `/mastermind`. Native to the site (matches tokens, nav, footer). THIS is the source of truth for the page.
- `mikemoll-site/public/media/fb-*.jpg` — the six muted, name-blurred Facebook screenshots.
- `mikemoll-site/api/lead.js` — edited: added a `mastermind-application` form config so the apply form works.
- `mikemoll-site/sitemap.xml` — added `/mastermind`.
- `Solo-Brotherhood-Landing-Page-Content.md` — the copy doc (v4, humanized). Content matches the live page. (Filename still says Solo-Brotherhood; the live page is titled AI Mastermind.)
- `/outputs/mastermind-preview/mastermind-preview.html` — standalone local preview with working images (relative paths). For eyeballing only.

---

## 3. TO PUBLISH (the one remaining step)

The site is a static HTML site on Vercel, auto-deploys from a GitHub repo (`mikemoll-site`). Everything is staged. To go live:

Push the `mikemoll-site` folder to GitHub (GitHub Desktop → Commit → Push, or `git add -A && git commit -m "Add AI Mastermind page" && git push`). Vercel auto-deploys and `/mastermind` goes live with a working apply form. The existing `/join-mastermind → /mastermind` redirect in `vercel.json` will start working automatically.

**Why it wasn't pushed from the last chat:** the Vercel connector there was linked to an empty team ("mike-8166's projects", 0 projects), not the account that owns mikemoll.co. **The new chat needs the GitHub repo and/or the Vercel project that owns mikemoll.co connected** to deploy directly. Otherwise, Mike pushes via GitHub himself.

**Apply form note:** posts to `/api/lead` with `formId: mastermind-application`, tags the lead `mastermind-application` in GoHighLevel. Needs the `GHL_TOKEN` env var that already exists on the production Vercel project. Fields collected: first name, email, business name, and a "how do you use AI" select. Mike reviews and books the call manually.

---

## 4. OPEN DECISIONS (need Mike)

1. **Men-only line (FAQ):** currently a draft I wrote so nothing shows as a placeholder live: *"It's men only. That's the room I set out to build, and it's the one I can keep at the standard I want. No deeper reason than that."* Approve or replace.
2. **Testimonials:** omitted from the live page for now (Mike's proof database is being cleaned up). Slot in 3-5 short, real quotes when ready: a decision the room helped make, an intro that paid off, or an AI build a member handed over. A few, not a wall.
3. **Nav:** intentionally NOT added to site navigation yet (Mike's call). It's a standalone/shareable page for now.

---

## 5. VOICE RULES (enforce on every edit)

- No em dashes. Use periods, commas, colons. (Exception already in the page: the browser `<title>` uses one to match the rest of the site's title convention.)
- No filler words: quietly, just, actually, really, whole, very, simply, literally.
- Plain, first person, contractions, fifth-grade readable, peer-to-peer. Match the tone of Mike's invite emails, not slick landing-page voice.
- AI wording: always "use AI to run the business better" (ops, processes, internal tools). Never imply members must build AI products.
- Run a humanizer pass before delivering. The recurring failure mode is copy that reads AI-written: no contractions and uniform sentence length.

---

## 6. SCREENSHOT WALL (the punchy proof section)

Six real posts from a free Claude/AI Facebook community (lazy, beginner-level: "does anyone have products they built with Claude making money," "nothing new to create, the AI market is full," "hopeless after hitting my weekly limits," a docx-won't-open question, "has Claude fallen behind," a basic React/Tailwind issue). They sit right under "Why now" as the enemy, in the posters' own words.

- Processed: desaturated ~58%, warm dark overlay so bright pink/blue don't pop, resized to 760px wide.
- The three showing a real poster name/avatar have the header band blurred (privacy + avoids punching down).
- Caption is reader-focused, not mocking: "This is the conversation in the free AI groups. If you're past this, you already know why you're leaving it." A gold "This room is the opposite" panel resolves it.

---

## 7. COACH GUIDANCE ALREADY APPLIED

Audited with cro-laja, design-gardner, copy-wiebe, emotion-wolf, copy-kennedy. Key moves baked in: credibility moved up (hero + proof band + About), word count roughly halved from the first draft, "why now" cut to three beats, the strongest emotional line pulled up ("You're the most advanced operator in every room you're in, and it's gotten quiet"), the redundant text comparison replaced by the screenshot wall, and the apply CTA made a clean single path (WhatsApp demoted to a text link).

Credibility facts to keep accurate: running founder rooms since 2018, dinners in 7 countries, agency built to $700K/yr, Fractional CMO. Every member interviewed personally.

---

## 8. SUGGESTED FIRST MESSAGE FOR THE NEW CHAT

"Continuing the AI Mastermind landing page. The finished page is at `Coaching Business/mikemoll-site/mastermind.html` and is staged to deploy. Please connect my GitHub/Vercel for mikemoll.co and push it live at /mastermind. Read `AI-Mastermind-HANDOFF.md` first. Open items: approve the men-only FAQ line, and I'll send testimonials to add."

---

## PUBLISHED 2026-08-14

Deployed live. /mastermind is up on mikemoll.co with working images and apply form. Images moved to media/ in the repo (a root public/ folder makes Vercel serve only that folder, which took the whole site down for a few minutes before the fix). Repo images live at media/fb-*.jpg; local public/media kept as originals. Men-only FAQ line approved by Mike as written. Still open: testimonials, adding /mastermind to site nav.

## v2 LIVE 2026-08-14

The reworked v2 page is live at /mastermind (coach-audited copy, unblurred correctly-named wall images, distributed Notion quotes). Three photo slots show placeholders until Mike sends: group shot (media/mastermind-group.jpg), facilitating (media/mastermind-room-1.jpg), group screenshot (media/mastermind-room-2.jpg). Still to confirm: quote attributions, 2019 vs 2021 coaching start.
