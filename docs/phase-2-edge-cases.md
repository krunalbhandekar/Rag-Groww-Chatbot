# Phase 2 Edge Cases — Chunking and Metadata

## Objective

Ensure chunk quality and strict metadata correctness for citation safety.

## Edge cases and handling

- Chunk exceeds model token limits due to long tables.
  - Split by semantic boundaries, then by token windows with overlap.
- Chunk starts mid-sentence, causing poor answer quality.
  - Add sentence-aware splitting and heading anchors.
- Important value appears in image/table not extracted as text.
  - Mark as missing extraction and avoid confident numeric answers.
- `source_url` missing in some chunks.
  - Reject chunk from index; never allow uncited chunks.
- Wrong `scheme_id` attached after parser merge.
  - Validate scheme metadata against URL-level manifest before indexing.
- Duplicate chunks inflate retrieval bias.
  - Deduplicate by normalized text hash + heading path.
- Footer/disclaimer text becomes high-frequency irrelevant chunks.
  - Tag as low-priority or exclude from retrieval.
- Date fields parsed inconsistently.
  - Standardize to ISO date and include parse confidence.
