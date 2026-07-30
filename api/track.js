// Vercel serverless function: tags a known visitor's GHL contact when they
// view a high-intent page. Identity comes from the mm_id cookie set by
// forms.js (or the podcast-workshop registration form) after any successful
// submission — this endpoint never creates a new contact from scratch, it
// only adds a tag to one identified by email, same GHL_TOKEN/upsert pattern
// as api/lead.js.

const GHL_LOCATION_ID = 'Y6tiQHe96XbqVkTeRY8J';
const GHL_UPSERT_URL = 'https://services.leadconnectorhq.com/contacts/upsert';

// Path -> tag. Explicit allowlist so this endpoint can't be used to write
// arbitrary tags onto a contact. Add new pages here (and to sitemap.xml).
const PAGES = {
  '/': 'viewed-home',
  '/podcast': 'viewed-podcast',
  '/consulting': 'viewed-consulting',
  '/podcast-workshop': 'viewed-podcast-workshop',
  '/blog': 'viewed-blog',
  '/blog/3-steps-to-raising-your-price': 'viewed-blog-3-steps-to-raising-your-price',
  '/blog/defining-your-ideal-client-ignore-everyone-else-susie-ippolito': 'viewed-blog-defining-your-ideal-client',
  '/blog/following-your-nudges-how-to-trust-your-intuition-more-jason-brown': 'viewed-blog-following-your-nudges',
  '/blog/gaining-confidence-to-charge-more-dusty-jenkins': 'viewed-blog-gaining-confidence-to-charge-more',
  '/blog/how-i-quit-my-comfortable-job-to-pursue-business': 'viewed-blog-how-i-quit-my-comfortable-job',
  '/blog/how-to-time-block-to-maximize-productivity-tiffany-taylor': 'viewed-blog-how-to-time-block',
  '/blog/how-to-vet-service-providers-behdad-jamshidi': 'viewed-blog-how-to-vet-service-providers',
  '/blog/marketing-a-live-learning-cohort-mark-latimer': 'viewed-blog-marketing-a-live-learning-cohort',
  '/blog/marketing-your-coaching-offer-on-facebook-megan-van-noy': 'viewed-blog-marketing-on-facebook',
  '/blog/monetizing-ideas-for-a-free-newsletter-patrick-kucharson': 'viewed-blog-monetizing-a-free-newsletter',
  '/blog/the-solopreneur-success-cycle-joe-rando': 'viewed-blog-solopreneur-success-cycle',
  '/free/linkedin-leads': 'viewed-free-linkedin-leads',
  '/free/claude-basics': 'viewed-free-claude-basics',
  '/free/podcast-guesting': 'viewed-free-podcast-guesting',
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const token = process.env.GHL_TOKEN || process.env.ghl_token;
  if (!token) {
    return res.status(500).json({ ok: false, error: 'Server not configured' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  body = body || {};

  const email = String(body.email || '').trim();
  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!emailOk) {
    return res.status(400).json({ ok: false, error: 'Valid email required' });
  }

  const page = String(body.page || '').trim();
  const tag = PAGES[page];
  if (!tag) {
    return res.status(400).json({ ok: false, error: 'Unknown page' });
  }

  const payload = {
    locationId: GHL_LOCATION_ID,
    email,
    tags: [tag],
  };

  try {
    const ghlRes = await fetch(GHL_UPSERT_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Version': '2021-07-28',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const text = await ghlRes.text();
    if (!ghlRes.ok) {
      console.error('GHL tag-on-view failed', page, ghlRes.status, text);
      return res.status(502).json({ ok: false, error: 'Tracking service error' });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('track handler error', err);
    return res.status(500).json({ ok: false, error: 'Unexpected error' });
  }
}
