// Generic Vercel serverless function: registers a lead from ANY site form
// into GoHighLevel via the Contacts upsert API (create-or-update, no duplicates).
// One endpoint serves every form. Each form passes a `formId`; the server-side
// config below decides the tag(s), standard-field mapping, and custom-field
// mapping. The GHL Private Integration token lives ONLY in the GHL_TOKEN env
// var (also accepts lowercase ghl_token) — never in client-side code.

const GHL_LOCATION_ID = 'Y6tiQHe96XbqVkTeRY8J';
const GHL_UPSERT_URL = 'https://services.leadconnectorhq.com/contacts/upsert';

// Per-form configuration.
//  tags       : tags always applied for this form.
//  customByKey: maps an incoming field name -> an existing GHL custom-field key.
// (These GHL field keys already exist in the account.)
const FORMS = {
  'podcast-workshop': {
    tags: ['podcast-workshop'],
  },
  'consulting-application': {
    tags: ['consulting-application'],
    customByKey: {
      years_in_business: 'years_in_business',
      deal_size: 'average_deal_size',
      annual_revenue: 'annual_revenue',
      close_rate: 'sales_close_rate',
      timeline: 'when_are_you_looking_for_help_with_your_offer',
    },
  },
  'podcast-guest': {
    tags: ['podcast-guest'],
  },
  'newsletter': {
    tags: ['newsletter'],
  },
};

function slug(s) {
  return String(s).toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

export function createHandler(defaultFormId) {
  return async function handler(req, res) {
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

    const formId = String(body.formId || defaultFormId || '').trim();
    const cfg = FORMS[formId];
    if (!cfg) {
      return res.status(400).json({ ok: false, error: 'Unknown form' });
    }

    const email = String(body.email || '').trim();
    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!emailOk) {
      return res.status(400).json({ ok: false, error: 'Valid email required' });
    }

    const name = String(body.name || '').trim();
    const parts = name.split(/\s+/).filter(Boolean);
    const firstName = parts.length ? parts[0] : '';
    const lastName = parts.length > 1 ? parts.slice(1).join(' ') : '';

    const payload = {
      locationId: GHL_LOCATION_ID,
      email,
      source: formId,
    };
    if (firstName) payload.firstName = firstName;
    if (lastName) payload.lastName = lastName;
    if (name) payload.name = name;
    const company = String(body.company || body.business_name || '').trim();
    if (company) payload.companyName = company;
    const website = String(body.website || '').trim();
    if (website) payload.website = website;
    const phone = String(body.phone || '').trim();
    if (phone) payload.phone = phone;

    // Tags: base tags + dynamic tags from categorical fields.
    const tags = [...(cfg.tags || [])];
    if (body.business_type) tags.push('industry-' + slug(body.business_type));
    if (body.guest_type) {
      const g = slug(body.guest_type);
      tags.push(g.includes('coach') ? 'guest-coaching' : 'guest-expert');
    }
    payload.tags = tags;

    // Custom fields mapped by GHL field key.
    if (cfg.customByKey) {
      const cf = [];
      for (const [inKey, ghlKey] of Object.entries(cfg.customByKey)) {
        const v = body[inKey];
        if (v != null && String(v).trim() !== '') {
          cf.push({ key: ghlKey, field_value: String(v).trim() });
        }
      }
      if (cf.length) payload.customFields = cf;
    }

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
        console.error('GHL upsert failed', formId, ghlRes.status, text);
        return res.status(502).json({ ok: false, error: 'Registration service error' });
      }
      return res.status(200).json({ ok: true });
    } catch (err) {
      console.error('lead handler error', err);
      return res.status(500).json({ ok: false, error: 'Unexpected error' });
    }
  };
}

export default createHandler(null);
