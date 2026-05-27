from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_hosted_identity_oidc_runbook_covers_goal_40_controls() -> None:
    runbook = ROOT / "docs" / "operations" / "hosted-identity-oidc.md"

    text = runbook.read_text(encoding="utf-8")

    for section in [
        "# Hosted Identity OIDC",
        "## Runtime Configuration",
        "## Token Contract",
        "## Revocation Boundary",
        "## Verification",
        "## Launch Gate Impact",
    ]:
        assert section in text

    for required_phrase in [
        "RETURN_PLAY_AUTH_PROVIDER=oidc",
        "RETURN_PLAY_OIDC_ISSUER",
        "RETURN_PLAY_OIDC_AUDIENCE",
        "RETURN_PLAY_OIDC_JWKS_URL",
        "RS256",
        "jti",
        "auth_token_revocations",
        "OIDC bearer token is invalid.",
        "not proof that a hosted identity tenant has been deployed",
    ]:
        assert required_phrase in text
