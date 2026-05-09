from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def load_state(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    schemes = state.get("schemes")
    if not isinstance(schemes, dict) or len(schemes) != 5:
        raise ValueError("State file must contain exactly five scheme entries.")
    return state


def diff_content_hashes(before_state: Dict[str, Any], after_state: Dict[str, Any]) -> List[Dict[str, str]]:
    changes: List[Dict[str, str]] = []
    before_schemes = before_state.get("schemes", {})
    after_schemes = after_state.get("schemes", {})

    for scheme_id, after_row in sorted(after_schemes.items()):
        before_row = before_schemes.get(scheme_id, {})
        before_hash = before_row.get("last_ok_content_hash_sha256")
        after_hash = after_row.get("last_ok_content_hash_sha256")
        if before_hash != after_hash:
            changes.append(
                {
                    "scheme_id": scheme_id,
                    "before_hash": before_hash or "",
                    "after_hash": after_hash or "",
                    "batch_id": after_row.get("last_ok_batch_id", ""),
                }
            )
    return changes


def write_alert(alert_path: Path, changes: List[Dict[str, str]]) -> None:
    alert_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "changed": bool(changes),
        "changes": changes,
    }
    with alert_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
