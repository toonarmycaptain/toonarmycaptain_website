"""Shared request/proxy helpers."""
from flask import request


def client_ip() -> str | None:
    """
    Real visitor IP behind Cloudflare, for signals like Turnstile's ``remoteip``.

    ``request.remote_addr`` is the CF/PA proxy address, not the visitor. The CF
    Worker forwards the visitor IP as ``X-Real-IP`` (see PLAN_CLOUDFLARE_PROXY.md);
    ``CF-Connecting-IP`` covers a direct-CF path with no Worker. Returns None when
    neither header is present, so callers send nothing rather than a wrong (proxy)
    address.

    Header-based, so spoofable by hitting the origin directly — acceptable for an
    optional signal, but never reuse this for a trust decision (auth/rate-limit)
    without CF-only enforcement.

    :return: str | None
    """
    return request.headers.get('X-Real-IP') or request.headers.get('CF-Connecting-IP') or None