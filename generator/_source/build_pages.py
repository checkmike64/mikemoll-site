import json, pathlib, re, html
ROOT=pathlib.Path(__file__).resolve().parent.parent
css=(ROOT/'assets'/'site.css').read_text()
base=json.loads((ROOT/'_source'/'base.json').read_text())
by_slug={b['slug']:b for b in base.values()}

STOP={"the","of","with","and","a","an","for","in","on"}
def initials(n):
    w=[x for x in re.split(r'[^A-Za-z0-9$]+',n) if x]; sig=[x for x in w if x.lower() not in STOP] or w
    return "".join(x[0].upper() for x in sig[:2])[:3]
def thumb(b):
    if b.get('cover_url'):
        return (f'<img src="{b["image_local"]}" alt="{html.escape(b["show"])}" loading="lazy" '
                f'onerror="this.onerror=null;this.src=\'{b["cover_url"]}\'">')
    return f'<div class="ph">{initials(b["show"])}</div>'

NAV='''<nav><div class="wrap nav-in"><a href="/" class="logo">Mike<span>.Moll</span></a>
    <div class="nav-links"><a href="/#free-resources">Free Resources</a><a href="/media">Media</a><a href="/#work" class="btn btn-primary">How I Help</a></div></div></nav>'''
FOOT='''<footer><div class="wrap foot-in"><a href="/" class="logo">Mike<span>.Moll</span></a>
    <div class="fl"><a href="https://www.youtube.com/@mikemollco" target="_blank" rel="noopener">YouTube</a><a href="https://www.linkedin.com/in/solopreneurcoach/" target="_blank" rel="noopener">LinkedIn</a><a href="https://www.instagram.com/themikemoll/" target="_blank" rel="noopener">Instagram</a></div>
    <p>&copy; 2026 Impact Leads LLC</p></div></footer>'''
CTA='''  <div class="cta" style="margin-top:52px"><h3>Two ways I can help.</h3>
    <p>I work with experts on two things: making your offer more sellable, and getting you on podcasts so the right buyers find you. Feel free to explore.</p>
    <a href="/consulting" class="btn btn-primary">If you need help selling your offer</a>
    <a href="/podcast-workshop" class="btn btn-ghost">If you want to get on podcasts</a></div>'''
def page(title,desc,body):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{css}
</style></head><body>
{NAV}
{body}
{FOOT}
</body></html>'''

# gather built posts (in blog/) with title + blurb from their HTML
built=[]
for f in sorted((ROOT/'blog').glob('*.html')):
    t=f.read_text(); slug=f.stem
    b=by_slug.get(slug)
    if not b: continue
    h1=re.search(r'<h1>(.*?)</h1>',t,re.S); title=re.sub('<.*?>','',h1.group(1)).strip() if h1 else b['show']
    md=re.search(r'<meta name="description" content="(.*?)">',t); blurb=md.group(1) if md else b['notion_description']
    built.append((b,title,blurb))

# ---- DIRECTORY ----
cards=[]
for b,title,blurb in built:
    cards.append(f'''    <a class="pcard" href="/blog/{b['slug']}">
      <div class="top">{thumb(b)}
        <div class="labels"><span class="cat">Guest Appearance</span><span class="kind">Podcast Episode</span></div></div>
      <div class="body"><h3>{html.escape(title)}</h3><p>{html.escape(blurb)}</p>
        <span class="read">See the episode &rarr;</span></div></a>''')
dir_body=f'''<div class="page">
  <div class="page-head">
    <div class="eyebrow">Guest Appearances &middot; The Undervalued Expert</div>
    <h1>Conversations I've been a guest on.</h1>
    <p class="lead">I've been invited onto 60+ podcasts to talk offers, pricing, sales, and building a business that serves your life. Here are the episodes, each with a short write-up and a link to listen.</p>
  </div>
  <div class="post-grid">
{chr(10).join(cards)}
  </div>
</div>'''
(ROOT/'guest-appearances.html').write_text(page("Guest Appearances | Mike Moll on 60+ Podcasts","Every podcast Mike Moll has guested on, each with a write-up and where to listen.",dir_body))

# ---- MEDIA PAGE ----
# featured = the 3 approved
feat_slugs=["why-youre-working-too-hard-for-too-little-joe-rando","leveraging-video-to-close-contracts-sara-nay","downsizing-and-rebuilding-a-team-alicia-butler-pierre"]
featmap={b['slug']:(b,t,bl) for b,t,bl in built}
feat_cards=[]
for s in feat_slugs:
    if s in featmap:
        b,t,bl=featmap[s]
        feat_cards.append(f'''    <a class="pcard" href="/blog/{s}"><div class="top">{thumb(b)}
        <div class="labels"><span class="cat">Guest Appearance</span><span class="kind">Podcast Episode</span></div></div>
      <div class="body"><h3>{html.escape(t)}</h3><p>{html.escape(bl)}</p><span class="read">See the episode &rarr;</span></div></a>''')

# marquee: all usable shows, two rows, real covers where present
shows=sorted(base.values(), key=lambda b:b['ref'])
def mqtile(b):
    inner = thumb(b) if b.get('cover_url') else initials(b['show'])
    return f'<div class="mq-icon" title="{html.escape(b["show"])}">{inner}</div>'
row1=shows[0::2]; row2=shows[1::2]
def track(row,rev=False):
    tiles="".join(mqtile(b) for b in row); cls="track rev" if rev else "track"
    return f'<div class="{cls}">{tiles}{tiles}</div>'
marquee=f'''<div class="marquee-wrap">
        <div class="marquee">{track(row1)}</div>
        <div class="marquee">{track(row2,rev=True)}</div>
      </div>'''

media_body=f'''<div class="page">
  <div class="page-head"><div class="eyebrow">Media &amp; Speaking</div>
    <h1>Featured on 60+ podcasts and stages.</h1>
    <p class="lead">Hosts and event organizers bring me on to teach one thing: how experts make themselves and their offers more sellable. Here is where I have shared it, from the shows your buyers already listen to, to conferences and the classroom.</p></div>
  <div class="stats"><div class="stat"><div class="n">60+</div><div class="l">Podcast appearances</div></div>
    <div class="stat"><div class="n">$386K</div><div class="l">Revenue from podcast guesting</div></div>
    <div class="stat"><div class="n">120+</div><div class="l">Podcasts hosted</div></div></div>

  <div class="sec"><div class="k">Featured Appearances</div><h2>A few conversations worth starting with.</h2>
    <p class="sub">The appearances I would point a new listener to first, each with a full write-up and where to listen.</p></div>
  <div class="post-grid">
{chr(10).join(feat_cards)}
  </div>
  <div class="section-link"><a href="/guest-appearances" class="text-link">See all episodes &rarr;</a></div>

  <div class="sec"><div class="k">Podcasts</div><h2>The shows that have had me on.</h2>
    <p class="sub">A sample of the 60+ podcasts where I have been a guest.</p></div>
  {marquee}

  <div class="sec"><div class="k">Speaking Engagements</div><h2>Conferences and the classroom.</h2>
    <p class="sub">Talks and teaching beyond the podcast mic.</p></div>
  <div class="speak-grid">
    <div class="speak"><span class="lab">Conference Talk</span><div class="where">AppSumo Online Conference</div>
      <h3>How to Save Your Business</h3><p>Spoke at AppSumo's online conference on saving your business, sharing the stage with a lineup of well-known founders and marketers.</p></div>
    <div class="speak"><span class="lab">Guest Lecture</span><div class="where">MBA Program</div>
      <h3>Marketing, Offers &amp; Pricing for Founders</h3><p>Invited to guest lecture an MBA class on how founders build offers that sell and price for the value they create.</p></div>
  </div>
{CTA}
</div>'''
(ROOT/'media.html').write_text(page("Media &amp; Speaking | Mike Moll","Mike Moll has been featured on 60+ podcasts and invited to speak at conferences and an MBA program.",media_body))
print("directory cards:",len(cards)," | featured:",len(feat_cards)," | marquee shows:",len(shows))
