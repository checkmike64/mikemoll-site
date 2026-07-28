// Backward-compatible alias for the podcast-workshop form.
// Delegates to the generic lead handler with a default formId so any
// existing/cached client that still posts to /api/register keeps working.
import { createHandler } from './lead.js';

export default createHandler('podcast-workshop');
