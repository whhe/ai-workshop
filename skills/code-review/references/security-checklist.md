# Security & Reliability Checklist

## Input/Output Safety

- **XSS**: Unsafe HTML injection, `dangerouslySetInnerHTML`, unescaped templates, innerHTML assignments
- **Injection**: SQL/NoSQL/command/GraphQL injection via string concatenation or template literals
- **SSRF**: User-controlled URLs reaching internal services without allowlist validation
- **Path traversal**: User input in file paths without sanitization (`../` attacks)
- **Prototype pollution**: Unsafe object merging in JavaScript (`Object.assign`, spread with user input)

## AuthN/AuthZ

- Missing tenant or ownership checks for read/write operations
- New endpoints without auth guards or RBAC enforcement
- Trusting client-provided roles/flags/IDs
- Broken access control (IDOR)
- Session fixation or weak session management

## JWT & Token Security

- Algorithm confusion attacks (accepting `none` or `HS256` when expecting `RS256`)
- Weak or hardcoded secrets
- Missing expiration (`exp`) or not validating it
- Sensitive data in JWT payload (base64, not encrypted)
- Not validating `iss` (issuer) or `aud` (audience)

## Secrets & PII

- API keys, tokens, or credentials in code/config/logs
- Secrets in git history or environment variables exposed to client
- Excessive logging of PII or sensitive payloads
- Missing data masking in error messages

## Supply Chain & Dependencies

- Unpinned dependencies allowing malicious updates
- Dependency confusion (private package name collision)
- Importing from untrusted sources or CDNs without integrity checks
- Outdated dependencies with known CVEs

## CORS & Headers

- Overly permissive CORS (`Access-Control-Allow-Origin: *` with credentials)
- Missing security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- Exposed internal headers or stack traces

## DoS & Rate Limiting

- ReDoS (Regular Expression Denial of Service)
- Missing rate limiting on public-facing endpoints
- Uncontrolled resource consumption triggered by external input (request bombs, zip bombs, oversized payloads)

> Internal reliability items (timeouts, blocking I/O, resource leaks) are in [code-quality-checklist.md](code-quality-checklist.md) § Stability & Resources.

## Cryptography

- Weak algorithms (MD5, SHA1 for security purposes)
- Hardcoded IVs or salts
- Using encryption without authentication (ECB mode, no HMAC)
- Insufficient key length

## Race Conditions

### Shared State Access

- Multiple threads/goroutines/async tasks accessing shared variables without synchronization
- Global state or singletons modified concurrently
- Lazy initialization without proper locking
- Non-thread-safe collections used in concurrent context

### Check-Then-Act (TOCTOU)

- `if (exists) then use` patterns without atomic operations
- `if (authorized) then perform` where authorization can change
- File existence check followed by file operation
- Balance check followed by deduction (financial operations)

### Database Concurrency

- Missing optimistic/pessimistic locking
- Read-modify-write without transaction isolation
- Counter increments without atomic operations
- Unique constraint violations in concurrent inserts

### Distributed Systems

- Missing distributed locks for shared resources
- Cache invalidation races (stale reads after writes)
- Event ordering dependencies without proper sequencing

## Data Integrity

- Missing transactions, partial writes, or inconsistent state updates
- Weak validation before persistence (type coercion issues)
- Missing idempotency for retryable operations
- Lost updates due to concurrent modifications
