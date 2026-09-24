// Generic Vercel serverless function: registers a lead from ANY site form
// into GoHighLevel via the Contacts upsert API (create-or-update, no duplicates).
// One endpoint serves every form. Each form passes a `formId`; the server-side
// config below decides the tag(s), standard-field mapping, and custom-field
// mapping. The GHL Private Integration token lives ONLY in the GHL_TOKEN env
// var (also accepts lowercase ghl_token) — never in client-side code.

const GHL_LOCATION_ID = 'Y6tiQHe96XbqVkTeRY8J';
const GHL_UPSERT_URL = 'https://services.leadconnectorhq.com/contacts/upsert';

// Second destination. Every form id above is also a form slug in the CRM, so
// no mapping table is needed -- the id IS the route. While GoHighLevel still
// runs the lead-magnet sequences both systems get the lead; when the
// sequences move, GHL comes out and this stays.
const CRM_URL = (process.env.CRM_URL || 'https://coaching-crm-tau.vercel.app').replace(/\/+$/, '');

// Per-form configuration.
//  tags       : tags always applied for this form.
//  customByKey: maps an incoming field name -> an existing GHL custom-field key.
// (These GHL field keys already exist in the account.)
const FORMS = {
  'podcast-workshop': {
    tags: ['podcast-workshop'],
  },
  // Evergreen opt-in for the workshop recording. Same 'podcast-workshop'
  // tag as the live-era registrants; the GHL workflow "Podcast Workshop -
  // Pre-Event Sequence" (rebuilt 2026-08-31 with recording-delivery emails,
  // triggered by this tag) owns the entire email sequence. Do not add a
  // welcomeEmail here or contacts will get the delivery email twice.
  'workshop-recording': {
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
  // Training library: light email unlock on /training. Re-captures the email
  // and tags them so you can see who is browsing your trainings.
  'training-library': {
    tags: ['training-library'],
  },
  // Engagement pings from the /training library (return visits, video plays).
  'training-engagement': {
    tags: ['training-engaged'],
  },
  // Lead magnets: each fires one tag. Wire the matching GHL workflow's
  // "Contact Tag Added" trigger to this tag so the email sequence still runs.
  // 'linkedin-leads' and 'podcast-guesting' were retired in September 2026:
  // their pages are gone and both paths redirect, so the ids are not accepted.
  'claude-basics': {
    tags: ['lm-claude-basics'],
  },
  // AI Mastermind application. Tags the lead so the follow-up/interview
  // workflow can trigger. Mike reviews and reaches out personally.
  'mastermind-application': {
    tags: ['mastermind-application'],
  },
};

function slug(s) {
  return String(s).toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

// Only keys shaped like a CRM answer key can be answers at all; the CRM drops
// any key the form does not define, so sending a few extra is harmless.
const ANSWER_KEY = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const NOT_AN_ANSWER = new Set([
  'formid', 'email', 'name', 'first_name', 'phone', 'website_url', 'renderedat',
]);

function answersFrom(body) {
  const answers = {};
  for (const [key, value] of Object.entries(body)) {
    if (NOT_AN_ANSWER.has(key.toLowerCase()) || !ANSWER_KEY.test(key)) continue;
    if (value == null || String(value).trim() === '') continue;
    answers[key] = String(value).trim().slice(0, 5000);
  }
  return answers;
}

// The CRM only accepts E.164. A number it would reject is dropped rather than
// guessed at -- a wrong country code is worse than no number.
function e164(phone) {
  const digits = String(phone || '').replace(/[\s().-]/g, '');
  return /^\+[0-9]{8,15}$/.test(digits) ? digits : null;
}

// Never fails the visitor: a CRM outage must not turn a registration into an
// error page while GoHighLevel already has the lead.
async function sendToCrm(formId, body, { email, firstName, phone, clientIp }) {
  try {
    const response = await fetch(`${CRM_URL}/api/forms/${encodeURIComponent(formId)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // So the CRM rate-limits the visitor, not this function.
        ...(clientIp ? { 'X-Forwarded-For': clientIp } : {}),
      },
      body: JSON.stringify({
        name: firstName || email.split('@')[0],
        email,
        phone: e164(phone),
        answers: answersFrom(body),
        sourceUrl: String(body.sourceUrl || body.source_url || '').trim() || null,
        utm: {},
      }),
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) {
      console.error('crm forward failed', formId, response.status, await response.text());
    }
  } catch (err) {
    console.error('crm forward error', formId, err);
  }
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

    // Anti-spam: honeypot field bots tend to auto-fill, plus a minimum
    // render-to-submit time real users can't beat. Respond 200 without
    // actually registering the lead, so bots don't learn to adapt.
    if (String(body.website_url || '').trim() !== '') {
      return res.status(200).json({ ok: true });
    }
    const renderedAt = Number(body.renderedAt);
    if (!renderedAt || Date.now() - renderedAt < 1500) {
      return res.status(200).json({ ok: true });
    }

    const email = String(body.email || '').trim();
    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!emailOk) {
      return res.status(400).json({ ok: false, error: 'Valid email required' });
    }

    // We only collect a first name. Take the first token defensively and store
    // it as firstName only (no last name, no combined name field) so the CRM
    // stays clean for first-name personalization.
    const firstName = String(body.first_name || body.name || '').trim().split(/\s+/)[0] || '';

    const payload = {
      locationId: GHL_LOCATION_ID,
      email,
      source: formId,
    };
    if (firstName) payload.firstName = firstName;
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
    if (formId === 'training-engagement' && body.event) {
      const ev = slug(body.event);
      const allow = ['training-unlock','training-return','watched-claude-basics'];
      if (allow.includes(ev)) tags.push(ev);
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

      const forwarded = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
      await sendToCrm(formId, body, {
        email,
        firstName,
        phone,
        clientIp: forwarded || String(req.headers['x-real-ip'] || '').trim(),
      });

      // Delivery email for forms that define one (the workshop recording).
      // Failure here never fails the registration -- the page redirects the
      // visitor to the content either way.
      if (cfg.welcomeEmail) {
        try {
          let contactId = null;
          try { contactId = (JSON.parse(text).contact || {}).id || null; } catch {}
          if (contactId) {
            const w = cfg.welcomeEmail;
            const sendRes = await fetch('https://services.leadconnectorhq.com/conversations/messages', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Version': '2021-04-15',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
              },
              body: JSON.stringify({
                type: 'Email',
                contactId,
                subject: w.subject,
                emailFrom: w.from,
                html: w.html,
              }),
            });
            if (!sendRes.ok) {
              console.error('welcome email failed', formId, sendRes.status, await sendRes.text());
            }
          } else {
            console.error('welcome email skipped: no contact id in upsert response', formId);
          }
        } catch (e) {
          console.error('welcome email error', formId, e);
        }
      }
      return res.status(200).json({ ok: true });
    } catch (err) {
      console.error('lead handler error', err);
      return res.status(500).json({ ok: false, error: 'Unexpected error' });
    }
  };
}

export default createHandler(null);
