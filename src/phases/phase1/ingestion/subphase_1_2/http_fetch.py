"""Subphase 1.2 — HTTP fetch with timeouts, retries, allowlisted final URL."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
import urllib.error
import urllib.request

from src.phases.phase0.manifest import canonicalize_url
from src.phases.phase0.policy import PHASE0_POLICY


DEFAULT_USER_AGENT = (
    "rag-grow-chatbot/1.0 (+https://github.com/local/rag-grow-chatbot; ingestion)"
)
DEFAULT_TIMEOUT_S = 45.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_BASE = 1.5


@dataclass
class FetchResult:
    ok: bool
    source_url: str
    final_url: str | None
    status_code: int | None
    body: bytes
    headers: dict[str, str]
    last_modified: str | None
    etag: str | None
    content_type: str | None
    error: str | None
    attempts: int


def _header_map(msg: urllib.response.addinfourl) -> dict[str, str]:
    return {k.lower(): v for k, v in msg.headers.items()}


def fetch_url(
    url: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_RETRY_BACKOFF_BASE,
) -> FetchResult:
    """
    GET url; follow redirects (urllib default). Final URL must match Phase 0 allowlist.
    """
    canonical_target = canonicalize_url(url)
    allow = PHASE0_POLICY.allowed_urls

    last_error: str | None = None
    attempts = 0

    for attempt in range(1, max_retries + 1):
        attempts = attempt
        req = urllib.request.Request(
            canonical_target,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-IN,en;q=0.9",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                final = canonicalize_url(resp.geturl())
                if final not in allow:
                    return FetchResult(
                        ok=False,
                        source_url=canonical_target,
                        final_url=final,
                        status_code=getattr(resp, "status", None),
                        body=b"",
                        headers=_header_map(resp),
                        last_modified=resp.headers.get("Last-Modified"),
                        etag=resp.headers.get("ETag"),
                        content_type=resp.headers.get("Content-Type"),
                        error=f"Final URL not on allowlist after redirects: {final}",
                        attempts=attempts,
                    )
                body = resp.read()
                hdr = _header_map(resp)
                status = getattr(resp, "status", 200)
                return FetchResult(
                    ok=True,
                    source_url=canonical_target,
                    final_url=final,
                    status_code=status,
                    body=body,
                    headers=hdr,
                    last_modified=hdr.get("last-modified"),
                    etag=hdr.get("etag"),
                    content_type=hdr.get("content-type"),
                    error=None,
                    attempts=attempts,
                )
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}: {exc.reason}"
            if exc.code is not None and exc.code >= 500 and attempt < max_retries:
                time.sleep(backoff_base ** attempt + random.random() * 0.5)
                continue
            return FetchResult(
                ok=False,
                source_url=canonical_target,
                final_url=None,
                status_code=exc.code,
                body=exc.read() if exc.fp else b"",
                headers=dict(exc.headers or {}),
                last_modified=None,
                etag=None,
                content_type=None,
                error=last_error,
                attempts=attempts,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(backoff_base ** attempt + random.random() * 0.5)
                continue
            return FetchResult(
                ok=False,
                source_url=canonical_target,
                final_url=None,
                status_code=None,
                body=b"",
                headers={},
                last_modified=None,
                etag=None,
                content_type=None,
                error=last_error,
                attempts=attempts,
            )

    return FetchResult(
        ok=False,
        source_url=canonical_target,
        final_url=None,
        status_code=None,
        body=b"",
        headers={},
        last_modified=None,
        etag=None,
        content_type=None,
        error=last_error or "fetch failed",
        attempts=attempts,
    )


def parse_http_date(value: str | None) -> str | None:
    """Normalize Last-Modified to ISO-ish string when parsable."""
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt is None:
            return value
        return dt.isoformat()
    except (TypeError, ValueError, OverflowError):
        return value
