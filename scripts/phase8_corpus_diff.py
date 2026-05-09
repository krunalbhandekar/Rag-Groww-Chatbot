import argparse
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.phases.phase8.corpus_diff import diff_content_hashes, load_state, write_alert


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect corpus hash diffs for Phase 8.")
    parser.add_argument("--before", required=True, help="Path to previous state.json")
    parser.add_argument("--after", required=True, help="Path to latest state.json")
    parser.add_argument(
        "--output",
        default="data/evaluation/reports/corpus_diff_alert.json",
        help="Path to write diff alert payload.",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    before_path = base_dir / args.before
    after_path = base_dir / args.after
    if not before_path.exists():
        print(f"Baseline state missing at {before_path}; skipping diff.")
        return 0
    if not after_path.exists():
        raise FileNotFoundError(f"Latest state missing at {after_path}")

    before = load_state(before_path)
    after = load_state(after_path)
    changes = diff_content_hashes(before_state=before, after_state=after)
    write_alert(base_dir / args.output, changes)

    if not changes:
        print("No corpus content hash changes detected.")
        return 0

    print("Corpus content hash changes detected:")
    for row in changes:
        print(
            f"- {row['scheme_id']}: {row['before_hash'][:8]} -> {row['after_hash'][:8]} "
            f"(batch {row['batch_id']})"
        )
    print(f"Alert written to: {base_dir / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
