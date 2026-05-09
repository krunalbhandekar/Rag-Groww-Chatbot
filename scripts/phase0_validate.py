from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.phases.phase0.validate import run


if __name__ == "__main__":
    manifest = Path("config/phase0/url_manifest.json")
    sys.exit(run(manifest))

