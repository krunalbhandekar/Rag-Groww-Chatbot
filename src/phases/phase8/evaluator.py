from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Optional

from src.orchestrator import ChatOrchestrator

ALLOWLISTED_URLS = {
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
}


@dataclass(frozen=True)
class Thresholds:
    citation_validity_min: float = 0.95
    refusal_precision_min: float = 0.95
    semantic_health_min: float = 1.0
    p95_latency_ms_max: float = 12000.0


def _percentile(values: List[float], percentile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    rank = (len(sorted_values) - 1) * percentile
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return sorted_values[lower]
    fraction = rank - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return numerator / denominator


class Phase8Evaluator:
    """Runs golden-set evaluation and computes rollout gates."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.orchestrator = ChatOrchestrator(base_dir=base_dir)

    def _load_golden_set(self, path: Path) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise ValueError("Golden set must be a JSON array.")
        return payload

    def _validate_case(self, case: Dict[str, Any]) -> None:
        required = {"id", "kind", "message"}
        missing = required - set(case.keys())
        if missing:
            raise ValueError(f"Golden case {case!r} missing keys: {sorted(missing)}")

    def evaluate(
        self,
        golden_set_path: Path,
        output_path: Path,
        thresholds: Optional[Thresholds] = None,
    ) -> Dict[str, Any]:
        thresholds = thresholds or Thresholds()
        golden_set = self._load_golden_set(golden_set_path)
        rows: List[Dict[str, Any]] = []

        refusal_total = 0
        refusal_correct = 0
        citation_total = 0
        citation_valid = 0
        semantic_healthy = 0
        latencies_ms: List[float] = []

        for case in golden_set:
            self._validate_case(case)
            case_kind = case["kind"]
            expected_route = case.get("expected_route")
            expected_url = case.get("expected_citation_url")

            started = time.perf_counter()
            result = self.orchestrator.process_message(
                case["message"],
                case.get("scheme_id"),
            )
            latency_ms = (time.perf_counter() - started) * 1000
            latencies_ms.append(latency_ms)

            route = (result.get("route") or "").strip().lower()
            answer = (result.get("answer") or "").strip()
            citation_url = result.get("citation_url")
            citation_is_allowlisted = citation_url in ALLOWLISTED_URLS if citation_url else False
            citation_matches_expected = (
                (expected_url is None) or (citation_url == expected_url)
            )

            # Semantic health check protects against HTTP-200 style empty payloads.
            is_semantically_healthy = bool(answer) and (
                route != "factual" or citation_is_allowlisted
            )
            if is_semantically_healthy:
                semantic_healthy += 1

            if case_kind == "factual":
                citation_total += 1
                if citation_is_allowlisted and citation_matches_expected:
                    citation_valid += 1

            if case_kind in {"negative", "edge"}:
                refusal_total += 1
                should_refuse = expected_route in {"advisory", "comparison", "ood"}
                if should_refuse and route == expected_route:
                    refusal_correct += 1
                elif not should_refuse and route == "factual":
                    refusal_correct += 1

            route_ok = expected_route is None or route == expected_route
            rows.append(
                {
                    "id": case["id"],
                    "kind": case_kind,
                    "message": case["message"],
                    "expected_route": expected_route,
                    "actual_route": route,
                    "route_ok": route_ok,
                    "citation_url": citation_url,
                    "citation_allowlisted": citation_is_allowlisted,
                    "citation_matches_expected": citation_matches_expected,
                    "answer_non_empty": bool(answer),
                    "latency_ms": round(latency_ms, 2),
                }
            )

        route_accuracy = _safe_rate(sum(1 for r in rows if r["route_ok"]), len(rows))
        citation_validity_rate = _safe_rate(citation_valid, citation_total)
        refusal_precision = _safe_rate(refusal_correct, refusal_total)
        semantic_health_rate = _safe_rate(semantic_healthy, len(rows))

        summary = {
            "golden_set_path": str(golden_set_path),
            "total_cases": len(rows),
            "route_accuracy": round(route_accuracy, 4),
            "citation_validity_rate": round(citation_validity_rate, 4),
            "refusal_precision": round(refusal_precision, 4),
            "semantic_health_rate": round(semantic_health_rate, 4),
            "latency_ms": {
                "p50": round(median(latencies_ms) if latencies_ms else 0.0, 2),
                "p95": round(_percentile(latencies_ms, 0.95), 2),
                "max": round(max(latencies_ms) if latencies_ms else 0.0, 2),
            },
            "thresholds": {
                "citation_validity_min": thresholds.citation_validity_min,
                "refusal_precision_min": thresholds.refusal_precision_min,
                "semantic_health_min": thresholds.semantic_health_min,
                "p95_latency_ms_max": thresholds.p95_latency_ms_max,
            },
        }

        rollout_gate = (
            summary["citation_validity_rate"] >= thresholds.citation_validity_min
            and summary["refusal_precision"] >= thresholds.refusal_precision_min
            and summary["semantic_health_rate"] >= thresholds.semantic_health_min
            and summary["latency_ms"]["p95"] <= thresholds.p95_latency_ms_max
        )
        summary["rollout_gate_passed"] = rollout_gate

        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = {"summary": summary, "cases": rows}
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)

        return report


def format_human_summary(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "=== Phase 8 Evaluation Report ===",
        f"Cases: {summary['total_cases']}",
        f"Route accuracy: {summary['route_accuracy']:.2%}",
        f"Citation validity rate: {summary['citation_validity_rate']:.2%}",
        f"Refusal precision: {summary['refusal_precision']:.2%}",
        f"Semantic health rate: {summary['semantic_health_rate']:.2%}",
        (
            "Latency (ms): "
            f"p50={summary['latency_ms']['p50']}, "
            f"p95={summary['latency_ms']['p95']}, "
            f"max={summary['latency_ms']['max']}"
        ),
        f"Rollout gate passed: {summary['rollout_gate_passed']}",
    ]
    return "\n".join(lines)
