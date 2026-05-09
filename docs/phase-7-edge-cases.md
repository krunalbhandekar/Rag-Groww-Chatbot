# Phase 7 Edge Cases — API and Minimal UI

## Objective

Keep the user experience stable, minimal, and policy-compliant.

## Edge cases and handling

- API returns valid text but missing `citation_url`.
  - Treat as failed response; do not render answer.
- Frontend sends empty message.
  - Return validation error with friendly prompt.
- Large input payload causes timeout.
  - Enforce max input length and graceful timeout messaging.
- Scheme selector missing while query is ambiguous.
  - Ask user to choose one of the five schemes.
- UI accidentally displays more than one link.
  - Render only validated `citation_url` from API contract.
- Disclaimer hidden on small screens.
  - Keep disclaimer pinned/visible in responsive layout.
- Concurrent duplicate submits.
  - Debounce submit and idempotency token per request.
