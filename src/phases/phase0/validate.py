from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .manifest import SchemeEntry, load_manifest
from .policy import PHASE0_POLICY


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_phase0_manifest(entries: list[SchemeEntry]) -> ValidationResult:
    errors: list[str] = []

    if len(entries) != PHASE0_POLICY.expected_count:
        errors.append(
            f"Expected {PHASE0_POLICY.expected_count} entries, found {len(entries)}."
        )

    urls = [e.url for e in entries]
    url_set = set(urls)
    scheme_ids = [e.scheme_id for e in entries]

    if len(url_set) != len(urls):
        errors.append("Duplicate URL detected in manifest.")

    if len(set(scheme_ids)) != len(scheme_ids):
        errors.append("Duplicate scheme_id detected in manifest.")

    for entry in entries:
        if entry.doc_type != PHASE0_POLICY.allowed_doc_type:
            errors.append(
                f"{entry.scheme_id}: invalid doc_type '{entry.doc_type}'. "
                f"Expected '{PHASE0_POLICY.allowed_doc_type}'."
            )

        if entry.url not in PHASE0_POLICY.allowed_urls:
            errors.append(
                f"{entry.scheme_id}: URL is out of allowlist policy: {entry.url}"
            )

    missing = PHASE0_POLICY.allowed_urls - url_set
    extra = url_set - PHASE0_POLICY.allowed_urls

    if missing:
        errors.append(f"Missing allowlisted URLs: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected URLs present: {sorted(extra)}")

    return ValidationResult(ok=not errors, errors=errors)


def run(manifest_path: Path) -> int:
    entries = load_manifest(manifest_path)
    result = validate_phase0_manifest(entries)
    if result.ok:
        print("Phase 0 manifest validation passed.")
        return 0

    print("Phase 0 manifest validation failed:")
    for error in result.errors:
        print(f"- {error}")
    return 1

