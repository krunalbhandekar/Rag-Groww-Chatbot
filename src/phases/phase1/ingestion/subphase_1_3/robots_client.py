"""Subphase 1.3 — robots.txt gate for host (fail closed if unreadable)."""

from __future__ import annotations

import urllib.robotparser
from urllib.parse import urlparse

from src.phases.phase1.ingestion.subphase_1_2.http_fetch import DEFAULT_USER_AGENT


def robots_url_for(target_url: str) -> str:
    parsed = urlparse(target_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {target_url}")
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def can_fetch_url(
    url: str,
    user_agent: str = DEFAULT_USER_AGENT,
) -> tuple[bool, str]:
    """
    Return (allowed, reason). If robots.txt cannot be read, we **disallow** fetch
    to stay compliant (fail closed), per source policy.
    """
    robots_txt = robots_url_for(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_txt)
    try:
        rp.read()
    except Exception as exc:
        return False, f"robots.txt unreadable ({robots_txt}): {exc}"

    try:
        ok = rp.can_fetch(user_agent, url)
    except Exception as exc:
        return False, f"robots can_fetch error: {exc}"

    if not ok:
        return False, "robots.txt disallows this URL for our user-agent"
    return True, "allowed"
