# Phase 0 Edge Cases — Governance and Corpus Plan

## Objective

Capture edge cases while freezing scope to exactly the five allowlisted Groww URLs.

## Edge cases and handling

- URL has trailing slash or query params (`?utm=...`) but points to same page.
  - Normalize to canonical URL and store only canonical form in manifest.
- One URL redirects to a different path.
  - Accept only if redirected target is one of the five approved URLs; otherwise block.
- URL is temporarily unavailable (5xx / timeout) during scope freeze.
  - Keep URL in manifest with `status=unreachable`; do not replace with new URL.
- Team requests adding AMFI/SEBI/AMC PDF links mid-build.
  - Reject by policy unless architecture and problem statement are explicitly revised.
- Scheme naming mismatch across docs vs URL slug.
  - Treat URL as source of truth; map display names through stable `scheme_id`.
- Duplicate scheme accidentally added in manifest.
  - Enforce uniqueness on canonical URL and `scheme_id`.
- URL uses uppercase/lowercase variants.
  - Normalize host and path comparison to avoid accidental out-of-scope inclusion.
- Legal/compliance asks for broader educational links in refusals.
  - Record as change request; do not change runtime policy until docs are updated.
