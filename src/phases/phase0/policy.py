from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Phase0Policy:
    allowed_urls: frozenset[str]
    allowed_doc_type: str = "groww_scheme_page"
    expected_count: int = 5


PHASE0_POLICY = Phase0Policy(
    allowed_urls=frozenset(
        {
            "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
            "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        }
    )
)

