# Phase 4 Edge Cases — Retrieval Layer

## Objective

Retrieve only relevant evidence from the five allowlisted URLs.

## Edge cases and handling

- Query uses shorthand scheme name ("HDFC ELSS") with ambiguity.
  - Resolve via alias map; if ambiguous, ask a clarifying follow-up.
- Query is factual but too broad ("tell me everything about this fund").
  - Return concise summary from highest relevance chunks and include one citation.
- Top-k retrieval returns only generic boilerplate sections.
  - Add heading-aware scoring and rerank using query intent terms.
- Retrieved chunk has stale date vs newer snapshot.
  - Prefer most recent snapshot by `snapshot_id` timestamp.
- Retrieval returns chunks from multiple schemes.
  - Enforce scheme filter if scheme is detected confidently.
- No chunk crosses relevance threshold.
  - Return uncertainty-safe answer and one allowlisted link.
- Retrieved chunk has broken or non-canonical URL metadata.
  - Drop from candidate set before generation.
