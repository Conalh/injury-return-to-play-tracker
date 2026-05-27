from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_auth_token_revocation_runbook_covers_launch_relevant_controls() -> None:
    runbook = ROOT / "docs" / "operations" / "auth-token-revocation.md"

    text = runbook.read_text(encoding="utf-8")

    for section in [
        "# Auth Token Revocation",
        "## Scope",
        "## Token Contract",
        "## Logout Behavior",
        "## Operational Limits",
        "## Verification",
        "## Launch Gate Impact",
    ]:
        assert section in text

    for required_phrase in [
        "jti",
        "POST /api/auth/logout",
        "Bearer token has been revoked.",
        "RETURN_PLAY_DATABASE_URL",
        "auth_token_revocations",
        "hosted identity provider",
        "durable revocation store",
        "tests/test_authentication.py",
    ]:
        assert required_phrase in text
