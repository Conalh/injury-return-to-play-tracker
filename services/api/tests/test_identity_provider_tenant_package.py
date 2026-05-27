from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_identity_provider_tenant_rollout_package_covers_launch_controls() -> None:
    package = ROOT / "docs" / "operations" / "identity-provider-tenant-rollout.md"

    assert package.exists()
    text = package.read_text(encoding="utf-8")

    for section in [
        "# Identity Provider Tenant Rollout",
        "## Scope",
        "## Tenant Configuration Checklist",
        "## Account Lifecycle",
        "## MFA And Password Policy",
        "## Session And Token Policy",
        "## Claims And Role Mapping",
        "## Smoke Test Plan",
        "## Evidence To Attach",
        "## Launch Gate Impact",
    ]:
        assert section in text

    for required_phrase in [
        "RETURN_PLAY_AUTH_PROVIDER=oidc",
        "RETURN_PLAY_OIDC_ISSUER",
        "RETURN_PLAY_OIDC_AUDIENCE",
        "RETURN_PLAY_OIDC_JWKS_URL",
        "return_play_role",
        "return_play_organization_id",
        "MFA",
        "deprovision",
        "provider-side session",
        "docs/operations/hosted-identity-oidc.md",
    ]:
        assert required_phrase in text
