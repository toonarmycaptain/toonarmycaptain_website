"""Cloudflare Turnstile verification for the contact form.

Uses only the standard library so no extra runtime dependency is needed.
"""
import json

from urllib import parse, request

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token: str,
                     secret: str,
                     remoteip: str | None = None,
                     timeout: float = 5.0,
                     ) -> bool:
    """
    Verify a Turnstile token against Cloudflare's siteverify endpoint.

    Fails closed: any missing token, network/timeout error, or malformed
    response returns False rather than letting the submission through.

    :param token: str
    :param secret: str
    :param remoteip: str | None
    :param timeout: float
    :return: bool
    """
    if not token:
        return False

    fields = {"secret": secret, "response": token}
    if remoteip:
        fields["remoteip"] = remoteip
    data = parse.urlencode(fields).encode()

    try:
        with request.urlopen(SITEVERIFY_URL, data=data, timeout=timeout) as resp:
            result = json.loads(resp.read().decode())
    except Exception as e:  # network error, timeout, non-JSON body, etc.
        print(f"Turnstile verification error: {e}")
        return False

    return bool(result.get("success"))
