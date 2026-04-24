# Log Redaction

**Scope:** applies **only** to pasted logs, errors, stack traces, command output, and other machine-generated content. It does **not** apply to narrative prose authored for the issue/PR.

## Bucket 1 — Always redact (no confirmation needed)

- Absolute filesystem path prefixes → trim to the repo-relative suffix, or replace the prefix with `<PATH>` if not derivable (e.g., `/Users/alice/proj/src/foo.py:12` → `src/foo.py:12`)
- Unambiguous credentials: API keys, access tokens, bearer tokens, passwords, session cookies, private keys, signed URLs → `<REDACTED>`

## Bucket 2 — Ask the user before pasting

For anything that *might* be sensitive but whose sensitivity depends on the project/tenant context, list the concrete occurrences to the user and ask whether to redact, keep, or replace. Typical items:

- IP addresses (public or private)
- Email addresses, phone numbers
- OS-level usernames, hostnames
- Internal company domains, internal service names
- Database names, bucket names, queue names, and similar identifiers

**In the draft:** do not leave original Bucket 2 values. Replace each occurrence with a numbered placeholder (`<?IP-1>`, `<?EMAIL-1>`, `<?HOST-1>`, …) and keep a local mapping of `placeholder → original` to surface in Step 4's Open questions. This prevents silently pasting ambiguous sensitive values, even into the conversation window.

## Bucket 3 — Never redact

GitHub `@username`, `owner/repo`, issue/PR numbers and same-host URLs, author/reviewer names.

## Preservation

Preserve line structure and the signal needed to diagnose the issue (error codes, stack frame order, timestamps with tz).
