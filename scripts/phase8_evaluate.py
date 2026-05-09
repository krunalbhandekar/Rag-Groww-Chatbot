import argparse
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.phases.phase8.evaluator import Phase8Evaluator, Thresholds, format_human_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 8 golden-set evaluation.")
    parser.add_argument(
        "--golden-set",
        default="data/evaluation/golden_set.json",
        help="Path to golden set JSON file (default: data/evaluation/golden_set.json).",
    )
    parser.add_argument(
        "--output",
        default="data/evaluation/reports/latest_report.json",
        help="Path to output report JSON.",
    )
    parser.add_argument(
        "--fail-on-threshold",
        action="store_true",
        help="Exit with code 1 when rollout gate fails.",
    )
    parser.add_argument("--citation-min", type=float, default=0.95)
    parser.add_argument("--refusal-min", type=float, default=0.95)
    parser.add_argument("--semantic-health-min", type=float, default=1.0)
    parser.add_argument("--p95-latency-max-ms", type=float, default=12000.0)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    evaluator = Phase8Evaluator(base_dir=base_dir)
    report = evaluator.evaluate(
        golden_set_path=base_dir / args.golden_set,
        output_path=base_dir / args.output,
        thresholds=Thresholds(
            citation_validity_min=args.citation_min,
            refusal_precision_min=args.refusal_min,
            semantic_health_min=args.semantic_health_min,
            p95_latency_ms_max=args.p95_latency_max_ms,
        ),
    )
    print(format_human_summary(report))
    print(f"Report written to: {base_dir / args.output}")

    if args.fail_on_threshold and not report["summary"]["rollout_gate_passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
