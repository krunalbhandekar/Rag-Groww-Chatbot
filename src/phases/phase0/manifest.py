from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True)
class SchemeEntry:
    scheme_id: str
    scheme_name: str
    url: str
    doc_type: str = "groww_scheme_page"


def canonicalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url.strip())
    path = parsed.path.rstrip("/") or "/"
    canonical = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=path,
        params="",
        query="",
        fragment="",
    )
    return urlunparse(canonical)


def load_manifest(path: Path) -> list[SchemeEntry]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = [
        SchemeEntry(
            scheme_id=item["scheme_id"],
            scheme_name=item["scheme_name"],
            url=canonicalize_url(item["url"]),
            doc_type=item.get("doc_type", "groww_scheme_page"),
        )
        for item in payload
    ]
    return entries

