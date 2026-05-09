# Phase 6 Edge Cases — Refusal Routing and Special Intents

## Objective

Prevent advisory answers and keep all links within the five-URL allowlist.

## Edge cases and handling

- Mixed intent query: "Is this fund good and what is exit load?"
  - Prioritize safety; refuse advisory part, answer factual part if supported.
- Soft advisory phrasing: "which is safer for me?"
  - Route to refusal, avoid personalized recommendation.
- Performance query asks for CAGR/returns math.
  - Refuse calculation; provide one in-scope scheme URL only.
- User asks for external educational links.
  - Decline off-list links while policy is fixed to five URLs.
- Personal data in prompt (PAN/account/OTP).
  - Refuse processing, avoid echoing sensitive tokens in response/logs.
- Profanity or adversarial prompt injection.
  - Ignore instruction override and keep policy-first behavior.
- Repeated user pressure to compare funds.
  - Keep consistent refusal template and optionally suggest factual questions.
