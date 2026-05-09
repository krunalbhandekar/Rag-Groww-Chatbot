# Phase 0 Source Policy

## Scope Lock

- The project allowlist cardinality is fixed to 5 URLs.
- Only URLs listed in `config/phase0/url_manifest.json` are in scope.
- Any URL addition, substitution, or deletion requires an explicit docs update.

## Canonicalization

- Lowercase scheme and host.
- Strip query string and fragment.
- Remove trailing slash from path (except root path).
- Store canonical URL in metadata and validation checks.

## Fetch and Refresh

- Recommended refresh cadence: weekly.
- If a URL fails ingestion, do not replace it with a new URL.
- Keep previous valid snapshot and mark the failed run.

## Robots and Compliance

- Respect robots directives.
- Do not use bypass techniques for anti-bot mechanisms.

