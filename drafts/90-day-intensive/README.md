# Sales Page — 90-Day Intensive (The Compression Method)

Live page: https://www.mikemoll.co/90-days-growth-intensive (GoHighLevel)

Each file below is one self-contained block. Paste each into its own **Custom HTML** element in GHL, in this order. (A Text element will show the raw code — it must be Custom HTML.)

## Paste order

| # | Section | File | Background |
|---|---------|------|------------|
| 1 | Hero | `01-Hero.html` | light |
| 2 | Proof (3 curated reviews) | `02-Proof.html` | light |
| 3 | Sound Familiar? (problem + loop + constraints) | `03-Sound-Familiar.html` | light |
| 4 | Meet Mike | `04-Meet-Mike.html` | light |
| 5 | The Compression Method | `05-Compression-Method.html` | light |
| 6 | Real Results (Sean & Tyler) | `06-Real-Results.html` | light |
| 7 | What You Get (6 items + Apply button) | `07-What-You-Get.html` | light |
| 8 | Who It's For | `08-Who-Its-For.html` | **dark** (transparent — sits on your dark blue section) |
| — | Client Voices | *native testimonial widget — not a file* | — |
| 9 | Investment + "Not ready?" soft CTA | `09-Investment.html` | light |
| 10 | The Close | `10-The-Close.html` | light |

## Anchors (set these in the builder)

- `#apply` — the native application section. Every "Apply to Work With Me" button links here.
- `#reviews` — the bottom review widget. The "See all reviews" link in the Proof block points here.
- Add `<div id="apply" style="scroll-margin-top:100px"></div>` at the top of the application section so it doesn't hide under the nav.

## Notes

- **Who It's For (08)** has a transparent background and light text — it's built to sit on your existing dark blue section. Everything else is on white.
- **Investment (09)**: the "Message Mike" button opens WhatsApp at `https://wa.me/16466208082`. Confirm that's the right number.
- **Proof (02)** predates the recent voice cleanup — give it a read/refresh pass before relying on it.
- All buttons are **Apply** (application), not buy. Price is shown to qualify, not to sell a checkout.

## Design system (for any future block)

- Fonts (matches homepage): **League Spartan 700** for headlines + big display numbers; **Poppins** for all body copy, labels, and buttons. Both imported in each block.
- Headline highlight: wrap a key phrase in `<span class="hl">…</span>` for the cream marker accent (`#FAE3CC`, skewed bar behind the lower half of the text). The `.hl` rule is already in each light-background block.
- Colors: ink `#27323D`, slate `#4E6F8A`, sky `#38B6FF` (deep `#1E9BE6`, bg `#EAF6FF`), navy `#3D5A72` (bg `#EDF2F6`), terracotta `#C9773A` (bg `#FBF0E6`), highlight cream `#FAE3CC`, line `#E7EBEF`.
- Buttons: sky pill primary (Poppins 600), sky-outline secondary.

## `_archive/`

Old drafts, alternate hero options, the original combined-graphics files, and the planning docs. Kept for reference — safe to delete whenever.
