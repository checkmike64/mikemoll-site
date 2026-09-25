// Generic Vercel serverless function: registers a lead from ANY site form into
// the CRM. One endpoint serves every form. Each form passes a `formId`, which
// is also its form slug in the CRM, so the id IS the route and no mapping
// table is needed.
//
// GoHighLevel was the original destination and ran the lead-magnet sequences.
// Those sequences now live in the CRM, so GHL has been removed rather than
// left running alongside: two systems holding the same people is how they
// drift apart, and a contact record nobody reads is worse than none.
//
// What the CRM owns that this file used to: tags (per form, in the CRM's own
// form configuration) and custom fields (mapped from answers). This file no
// longer decides either. It validates the visitor, shapes the answers, and
// hands them over.

const CRM_URL = (process.env.CRM_URL || 'https://coaching-crm-tau.vercel.app').replace(/\/+$/, '');

// The forms this endpoint will accept. The CRM holds the same slugs and owns
// what each one tags; this list exists so an unknown id is refused here rather
// than travelling. 'linkedin-leads' and 'podcast-guesting' were retired in
// September 2026 -- their pages are gone and both paths redirect, so the ids
// are deliberately absent.
const FORM_IDS = new Set([
  'podcast-workshop',
  'workshop-recording',
  'consulting-application',
  'podcast-guest',
  'newsletter',
  'training-library',
  'training-engagement',
  'claude-basics',
  'mastermind-application',
]);

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

// The CRM is now the only destination, so unlike before, a failure here is the
// lead being lost. It is reported rather than swallowed: the visitor sees the
// form fail and can try again, which is recoverable. A cheerful success page
// over a dropped registration is not.
async function sendToCrm(formId, body, { email, firstName, phone, clientIp }) {
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
    signal: AbortSignal.timeout(8000),
  });
  if (!response.ok) {
    throw new Error(`crm ${response.status}: ${(await response.text()).slice(0, 300)}`);
  }
}

export function createHandler(defaultFormId) {
  return async function handler(req, res) {
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      return res.status(405).json({ ok: false, error: 'Method not allowed' });
    }

    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch { body = {}; }
    }
    body = body || {};

    const formId = String(body.formId || defaultFormId || '').trim();
    if (!FORM_IDS.has(formId)) {
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
    const forwarded = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();

    try {
      await sendToCrm(formId, body, {
        email,
        firstName,
        phone: String(body.phone || '').trim(),
        clientIp: forwarded || String(req.headers['x-real-ip'] || '').trim(),
      });
      return res.status(200).json({ ok: true });
    } catch (err) {
      console.error('lead handler error', formId, err);
      return res.status(502).json({ ok: false, error: 'Registration service error' });
    }
  };
}

export default createHandler(null);
