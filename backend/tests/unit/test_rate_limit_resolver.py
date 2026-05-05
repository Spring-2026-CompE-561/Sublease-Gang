"""X-Forwarded-For trust gating in the rate-limit resolver."""

from types import SimpleNamespace

from app.middleware.rate_limit import _resolve_client_ip


def _req(*, peer: str, xff: str | None = None):
    headers = {}
    if xff is not None:
        headers["x-forwarded-for"] = xff
    return SimpleNamespace(
        client=SimpleNamespace(host=peer),
        headers=headers,
    )


def test_no_xff_uses_direct_peer():
    assert _resolve_client_ip(_req(peer="203.0.113.1"), frozenset()) == "203.0.113.1"


def test_xff_ignored_when_peer_not_trusted():
    """A spoofed X-Forwarded-For from an untrusted client must be ignored."""
    request = _req(peer="203.0.113.1", xff="1.2.3.4")
    assert _resolve_client_ip(request, frozenset()) == "203.0.113.1"


def test_xff_honored_when_peer_is_trusted_proxy():
    request = _req(peer="10.0.0.5", xff="1.2.3.4, 10.0.0.5")
    assert _resolve_client_ip(request, frozenset({"10.0.0.5"})) == "1.2.3.4"


def test_xff_first_hop_used():
    """First IP in XFF is the originating client; honor that one."""
    request = _req(peer="10.0.0.5", xff="  198.51.100.7 , 10.0.0.5 ")
    assert (
        _resolve_client_ip(request, frozenset({"10.0.0.5"})) == "198.51.100.7"
    )


def test_missing_client_falls_back_to_unknown():
    request = SimpleNamespace(client=None, headers={})
    assert _resolve_client_ip(request, frozenset()) == "unknown"
