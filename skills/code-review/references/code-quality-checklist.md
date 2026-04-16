# Code Quality Checklist

## Stability & Resources

- Unbounded loops, recursive calls, or large in-memory buffers
- Missing timeouts and retries on external calls
- Blocking operations on request path (sync I/O in async context)
- Resource exhaustion: file handles, connections, memory not released
- Missing connection pool limits or concurrency bounds

> Attacker-exploitable variants (ReDoS, rate limiting, payload bombs) are in [security-checklist.md](security-checklist.md) § DoS & Rate Limiting.

## Error Handling

### Anti-patterns

- **Swallowed exceptions**: Empty catch blocks or catch with only logging
- **Overly broad catch**: Catching `Exception`/`Error` base class instead of specific types
- **Error information leakage**: Stack traces or internal details exposed to users
- **Missing error handling**: No try-catch around fallible operations (I/O, network, parsing)
- **Async error handling**: Unhandled promise rejections, missing `.catch()`, no error boundary

### Questions

- "What happens when this operation fails?"
- "Will the caller know something went wrong?"
- "Is there enough context to debug this error?"

## Performance & Caching

### CPU-Intensive Operations

- Expensive operations in hot paths: regex compilation, JSON parsing, crypto in loops
- Blocking main thread: sync I/O, heavy computation without worker/async
- Unnecessary recomputation: same calculation done multiple times
- Missing memoization: pure functions called repeatedly with same inputs

### Database & I/O

- **N+1 queries**: Loop that makes a query per item instead of batch
- **Missing indexes**: Queries on unindexed columns
- **Over-fetching**: `SELECT *` when only few columns needed
- **No pagination**: Loading entire dataset into memory

### Caching Issues

- Missing cache for expensive operations (repeated API calls, DB queries)
- Cache without TTL: stale data served indefinitely
- Cache without invalidation strategy
- Cache key collisions
- Caching user-specific data globally (security/privacy risk)

### Memory

- Unbounded collections: arrays/maps that grow without limit
- Large object retention: holding references preventing GC
- String concatenation in loops: use builder/join instead
- Loading large files entirely: use streaming instead

### Questions

- "What's the time complexity of this operation?"
- "How does this behave with 10x/100x data?"
- "Is this result cacheable?"
- "Can this be batched instead of one-by-one?"

## Boundary Conditions

### Null/Undefined Handling

- Missing null checks: accessing properties on potentially null objects
- Truthy/falsy confusion: `if (value)` when `0` or `""` are valid
- Optional chaining overuse: `a?.b?.c?.d` hiding structural issues
- Null vs undefined inconsistency: mixed usage without clear convention

### Empty Collections

- Code assumes array has items
- First/last element access without length check

### Numeric Boundaries

- Division by zero
- Integer overflow / safe integer range
- Floating point comparison: `===` instead of epsilon comparison
- Negative values: index or count that shouldn't be negative
- Off-by-one errors: loop bounds, array slicing, pagination

### String Boundaries

- Empty string not handled as edge case
- Whitespace-only string: passes truthy check but is effectively empty
- Very long strings: no length limits causing memory/display issues
- Unicode edge cases: emoji, RTL text, combining characters

### Questions

- "What if this is null/undefined?"
- "What if this collection is empty?"
- "What's the valid range for this number?"
- "What happens at the boundaries (0, -1, MAX_INT)?"
