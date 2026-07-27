# mikemoll.co

Static site for Mike Moll. Plain HTML/CSS, no build step. Deploys on Vercel.

## Structure
- `index.html` — homepage
- `podcast.html` — the podcast page (serves at `/podcast`)
- `public/media/` — images (logos, photos, episode art). Small files, safe to commit.
- `public/audio/` — DO NOT commit audio/video. Host on YouTube/Spotify and embed.
- `vercel.json` — clean URLs + 301 redirects from the old GoHighLevel slugs
- `robots.txt`, `sitemap.xml`, `llms.txt` — SEO + AI-SEO

## Get it live (first time, ~10 minutes)
1. **GitHub:** create a new repo at github.com/new named `mikemoll-site`. Upload this folder (drag-and-drop in the browser works, or use GitHub Desktop).
2. **Vercel:** go to vercel.com → Add New → Project → Import `mikemoll-site` → Deploy. You get a live `*.vercel.app` URL in ~30 seconds.
3. **Domain (later):** in Vercel → Project → Settings → Domains, add `mikemoll.co` and follow the DNS steps. Until then, keep the current site up.

## Adding media
Drop images into `public/media/` and reference them as `/media/your-file.webp`.

## Forms
The opt-in and apply forms are placeholders. Point them at your GoHighLevel form embed, or Formspree, before launch.
