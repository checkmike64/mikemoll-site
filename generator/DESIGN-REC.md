# Player / preview embed - recommendation & what shipped

## Recommendation
Lead with the branded look, not a third-party player. Every one of the 49 pages now defaults to Mike's dark cover-hero (cover art + show/host + a gold "Play this episode" cue). Clicking loads the real episode player inline via a single consistent affordance, so the page reads as Mike's brand by default and only shows vendor chrome once a visitor opts in. This beats embedding a raw player on load, which would put three different vendor styles (Apple light card, Spotify green, YouTube red) on a near-black editorial site. Click-to-load is also faster and better for privacy. Player priority behind the click: Spotify episode embed (dark theme) -> Apple Podcasts episode embed -> YouTube -> Captivate -> (cover + Listen buttons if none exists). Every player sits in one identical bordered, rounded, dark wrapper.

## What shipped (49 pages)
- In-page player behind the branded cover: 35 of 49
  - Spotify (dark): 1
  - Apple Podcasts episode embed: 29
  - YouTube: 4
  - Captivate: 1
- Cover art + Listen buttons only (no embeddable episode player found): 14

## Note on Spotify-dark
Spotify was the preferred behind-click player for brand fit, but Spotify's episode pages are JavaScript-gated and could not be enumerated with the current tools (web_fetch is down); only one Spotify episode ID was findable. Apple episode embeds (which we already have IDs for) are the workhorse behind the click. Once web_fetch returns or a Spotify API token is available, converting the Apple embeds and the 14 cover-only pages to Spotify-dark is a fast follow-up.

## Cover-only episodes (14)
These have no findable Apple/Spotify/YouTube episode embed, so they use cover + Listen buttons (the buttons still link straight to the episode):
- 21st Century Entrepreneurship
- 6 Figure Rebels Podcast
- BE-Bonfire Entrepreneurs
- DoGoodWork Podcast
- Global Citizen Life Podcast
- Hailey Rowe Podcast
- Innovabuzz Podcast
- The Agency Spark
- Livin That Life - Digital Nomad Lifestyles
- Sales Genius
- Startup Canada Podcast
- The 10 Minute Entrepreneur
- The Story Engine
- The Unforget Yourself Show
