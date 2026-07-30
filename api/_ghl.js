// Shared GHL helpers for api/lead.js and api/track.js.
// Filename starts with "_" so Vercel does not deploy it as its own route.
//
// GHL's /contacts/upsert treats the "tags" field as a full REPLACEMENT of
// the contact's tag list, not an addition (a known, officially acknowledged
// GHL API limitation — see
// https://ideas.gohighlevel.com/apis/p/contact-upsert-should-add-tags-instead-of-overwriting-or-replacing-them).
// Every upsert call must therefore read the contact's current tags, merge
// in whatever this call wants to add, and send the full merged set —
// otherwise each new tag silently wipes out everything applied before it.

export const GHL_LOCATION_ID = 'Y6tiQHe96XbqVkTeRY8J';
export const GHL_BASE = 'https://services.leadconnectorhq.com';
export const GHL_UPSERT_URL = `${GHL_BASE}/contacts/upsert`;

const PAGE_LIMIT = 100;
const MAX_PAGES = 10; // caps the scan at 1,000 contacts

// GHL's /contacts/ list endpoint takes a free-text "query" param, but it
// mis-parses raw email addresses (the "+"/"@" break its query-string
// parsing — verified: a plain substring like "workshoptracktest" matches
// correctly, but the same contact's full "user+tag@example.com" email does
// not). Rather than guess at escaping rules that might silently fail for
// some real customer emails too, this paginates the list endpoint (which is
// confirmed reliable) and matches the email exactly, client-side.
//
// Known limitation: a brand-new contact (never seen before) can take ~30s
// to appear in this list endpoint after creation, vs. an update to an
// already-indexed contact which is fast (seconds). Two tagging calls for
// the SAME brand-new contact within that window could still race and lose
// a tag — a real visitor navigating the site won't hit this in practice,
// but it's worth knowing about if two calls ever need to fire back-to-back
// programmatically.
export async function getExistingTags(email, token) {
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Version': '2021-07-28',
    'Accept': 'application/json',
  };
  const target = email.toLowerCase();
  try {
    for (let page = 1; page <= MAX_PAGES; page++) {
      const url = `${GHL_BASE}/contacts/?locationId=${GHL_LOCATION_ID}&limit=${PAGE_LIMIT}&page=${page}`;
      const res = await fetch(url, { headers });
      if (!res.ok) return [];
      const data = await res.json();
      const contacts = Array.isArray(data.contacts) ? data.contacts : [];
      const match = contacts.find((c) => String(c.email || '').toLowerCase() === target);
      if (match) return Array.isArray(match.tags) ? match.tags : [];
      if (contacts.length < PAGE_LIMIT) break; // last page
    }
    return [];
  } catch (err) {
    console.error('getExistingTags failed', err);
    return [];
  }
}

export function mergeTags(existing, additions) {
  const seen = new Set((existing || []).map((t) => String(t).toLowerCase()));
  const merged = [...(existing || [])];
  for (const t of additions) {
    const key = String(t).toLowerCase();
    if (!seen.has(key)) {
      merged.push(t);
      seen.add(key);
    }
  }
  return merged;
}
