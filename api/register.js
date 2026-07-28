// Vercel serverless function: registers a workshop lead in GoHighLevel.
// Upserts the contact (create-or-update, no duplicates) and applies a tag.
// The GHL Private Integration token lives ONLY in the GHL_TOKEN env var —
// never in client-side code.

const GHL_LOCATION_ID = 'Y6tiQHe96XbqVkTeRY8J';
const GHL_UPSERT_URL = 'https://services.leadconnectorhq.com/contacts/upsert';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const token = process.env.GHL_TOKEN;
  if (!token) {
    return res.status(500).json({ ok: false, error: 'Server not configured' });
  }

  // Body may arrive parsed (Vercel) or as a raw string.
  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  body = body || {};

  const email = String(body.email || '').trim();
  const name = String(body.name || '').trim();
  const source = String(body.source || 'website').trim();

  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!emailOk) {
    return res.status(400).json({ ok: false, error: 'Valid email required' });
  }

  const parts = name.split(/\s+/).filter(Boolean);
  const firstName = parts.length ? parts[0] : '';
  const lastName = parts.length > 1 ? parts.slice(1).join(' ') : '';

  const payload = {
    locationId: GHL_LOCATION_ID,
    email,
    firstName,
    lastName,
    name: name || undefined,
    source: source,
    tags: ['podcast-workshop'],
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
      // Log server-side for debugging; don't leak details to the client.
      console.error('GHL upsert failed', ghlRes.status, text);
      return res.status(502).json({ ok: false, error: 'Registration service error' });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('register handler error', err);
    return res.status(500).json({ ok: false, error: 'Unexpected error' });
  }
}
