"""Subphase 1.2 — fetch and transport."""

from .http_fetch import DEFAULT_USER_AGENT, FetchResult, fetch_url, parse_http_date

__all__ = [
    "DEFAULT_USER_AGENT",
    "FetchResult",
    "fetch_url",
    "parse_http_date",
]
