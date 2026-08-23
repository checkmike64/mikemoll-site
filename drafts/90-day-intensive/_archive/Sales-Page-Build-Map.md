# 30-30-30 Sales Page — Build Map (rough)

A once-over of the whole page before we finalize. Purpose: agree on (a) the order, and (b) what lives in an HTML graphic vs. plain page copy. Nothing here is designed yet. Content is rough on purpose.

---

## The one big change we're making

Out: the hypothetical "here's what your numbers could become" table ($4,500 → $5,850, etc.). It reads like a projection, and "testimonial + what this could mean for you" feels weak.

In: **real client results.** Sean is the anchor (commodity offer → named system → multiples more income at the same hours). Tyler is the second beat (the ten-minute distillation). We show what actually happened, attributed, instead of a made-up forecast.

One thing to keep straight: the hero's **+30% / +30% / −30%** is the program's promise and its name (the 30-30-30). That stays. What we're cutting is the invented earnings projection further down, not the offer's headline promise.

---

## Page map

Legend: **[GRAPHIC]** = HTML block from the graphics file · **[COPY]** = plain page text · **[EXISTING]** = already on your page.

| # | Section | Type | Rough content |
|---|---|---|---|
| 1 | Hero | [COPY] headline + subhead, [GRAPHIC] stat tiles, [COPY] button | Headline (pick 1 of 6) + one-line subhead. Stat tiles graphic shows the three 30s. Apply button. |
| 2 | The skill was never the problem | [COPY] | 3-4 sentences naming the gap: value created vs. the invoice number. |
| 3 | Is this you | [COPY] | The three lived scenes (pricing, closing, delivery) as flowing prose. |
| 4 | Meet Mike | [COPY] + [EXISTING] photo | Corktown story + why he can find your constraint fast. |
| 5 | The Compression Method | [COPY] intro + [GRAPHIC] chevron | Short intro, then the three-constraint graphic. |
| 6 | **Real results** (replaces the projection) | [COPY] lead + [GRAPHIC] Sean From:To + Tyler quote | Sean's real before/after (commodity → named system, multiples more, same hours) and Tyler's distillation quote. |
| 7 | What you get | [COPY] lead + [GRAPHIC] 8-card grid | One-line lead, then the deliverables graphic. |
| 8 | Client voices | [EXISTING] | Your third-party widget (the ~40 Google / LinkedIn / YouTube reviews). |
| 9 | Who it's for | [COPY] or [GRAPHIC] two-column | Right fit / not the right fit. Could stay copy, or become a small graphic. |
| 10 | Investment | [COPY] + [EXISTING] price buttons | Two payment options, cohort of 10, ROI note. Uses your existing blue/terracotta buttons. |
| 11 | Close | [COPY] + button | Calm invitation that echoes the hero. |
| 12 | Not ready yet | [COPY] + button | Diagnostic Session on-ramp. |

So: **5 HTML graphics** (hero tiles, method chevron, real-results, what-you-get, and optionally who-it's-for), everything else is page copy or already on the site.

---

## Section 6 in detail (the real-results rework)

This is the section that changes most. Rough direction, not final copy:

**Lead (copy):** one line. Something like: "Here's what that looked like for Sean."

**Graphic — Sean, real From:To:**

- BEFORE: A proposal with the same eight services every Google Ads agency lists. Every sales call turned into a fight over price.
- AFTER: One named offer, his four-step Client Revenue System. Nobody could line him up against three cheaper agencies, because nobody else had his system.
- RESULT (his words): "a few multiples higher" income than when he started, a team of three to four, working the same hours or less.

**Second beat — Tyler quote (graphic or pull-quote):** "I can bring Mike a problem that feels business-crushing, and within ten minutes he distills it into three different solutions that would all work."

This keeps everything real and attributed. No projections.

*(If you have exact figures for Sean or another client, we can make the "after" side numeric. Otherwise the qualitative version is still real and strong.)*

---

## The graphics: voice flags

You're right that some of the graphic microcopy has an AI ring. Lines I want to rework with you into your voice:

- "Three numbers we build the ninety days around." → a touch clever. Maybe just: "The three numbers we move."
- Method sub: "One knotted problem, narrowed to the two or three moves that fix it." → more you: "You bring one problem that feels like ten. We find the two or three moves that matter."
- Constraint names: "Fix what the offer says / Rebuild the conversation / Give the work an edge." → "Give the work an edge" is the softest. Maybe "Put a hard edge on scope."
- Tile tags: "Charge what the work is worth / Win more of the calls you take / Get your week back." → these are close, but let's confirm they sound like you, not a brochure.

Once we lock structure, I'll do one voice pass across every graphic line so nothing reads generic.

---

## Real client data on file (verbatim, so we don't invent)

**Sean** — Google Ads agency. Commodity 8-service proposal, competed on price. Built a named four-step Client Revenue System. Outcome in his words: "making a few multiples higher than what I was when I came to you, which was already a good income," team of 3-4, "same time or less."

**Tyler** — "I can bring Mike a problem that feels like a world-ending, business-crushing thing, and within ten minutes he distills it into three different solutions that would all work."

**Others available if useful:** Jenni (rates quadrupled, $16K month), Daniella ($30-40K/mo recurring, team of 4), Mark (+30% sales), Alvin (productized, systems), Andy (messaging).

---

## Open questions (let's lock these)

1. **Sean/Tyler numbers:** use their real qualitative outcomes, or do you have exact before/after figures you want plugged in?
2. **Order:** does the 12-section order above look right, or do you want to move anything?
3. **Who it's for (section 9):** keep as plain copy, or make it a small graphic too?

---

## Build status (updated as we go)

Single-file blocks and their state:

- **Hero** — `Hero.html` — BUILT + placed. Button → `#apply`.
- **Curated proof ("Results Speak Louder Than Promises")** — `Proof-Section.html` — BUILT + placed high. Still needs the three "See full review" URLs; "See all reviews" → `#reviews`.
- **Investment** — `Investment.html` — BUILT but **DEFERRED**. Not the next to place. Mike wants to revisit and adjust it later (payback anchor stays, more tweaks to come).

Builder anchors to set: `#apply` (application section), `#reviews` (bottom review widget).

Order still to place, top to bottom (after hero + proof): the skill was never the problem → is this you → meet Mike → the Compression Method → real results → what you get → who it's for → client-voices widget → **investment (deferred)** → close → diagnostic.
