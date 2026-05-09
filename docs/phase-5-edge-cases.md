# Phase 5 Edge Cases — Generation and Formatting

## Objective

Guarantee output format: facts-only, max 3 sentences, exactly one allowlisted URL.

## Edge cases and handling

- Model generates more than three sentences.
  - Enforce sentence-count validator and truncate safely.
- Model emits multiple URLs.
  - Keep highest-confidence allowlisted citation; remove others.
- Model emits a non-allowlisted URL.
  - Replace with matched chunk `source_url` from allowlist or fail closed.
- Model invents values not present in retrieved text.
  - Require extractive grounding check for numbers and key facts.
- Footer date missing or malformed.
  - Compute from selected chunk metadata and append in fixed format.
- Contradictory values across retrieved chunks.
  - Acknowledge discrepancy briefly and cite one relevant scheme page.
- Output drifts into advisory language ("best", "should invest").
  - Run advisory phrase guardrail and convert to refusal route.
