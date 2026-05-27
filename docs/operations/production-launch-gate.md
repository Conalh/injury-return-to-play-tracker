# Production Launch Gate

Status: Goal 37 launch checklist

This is the final gate before broader production use. It is a signoff artifact,
not proof that production hosting is complete. Staging and production deployment
remain deferred until Goals 32 and 33 are reopened and verified.

Supporting controls:

- `docs/operations/ci-required-checks.md`
- `docs/product/security-baseline.md`
- `docs/operations/backups-and-recovery.md`
- `docs/operations/observability.md`
- `docs/product/legal-compliance-review-package.md`
- `docs/product/safety-and-compliance-notes.md`
- `docs/operations/beta-readiness.md`
- `docs/operations/environment-configuration.md`
- `docs/operations/local-production-compose.md`
- `docs/product/privacy-controls.md`
- `docs/product/usability-review.md`

## Launch Scope

This launch gate applies only after a target production environment exists and
has passed staging-style smoke checks. Until then, the product remains a local
production-path build with controlled beta documentation.

Allowed launch candidate:

- Named production organization and owner.
- Production web and API services deployed over HTTPS.
- Production database provisioned and migrated.
- Production secrets configured through managed secret storage.
- Hosted identity tenant deployed, OIDC validation configured, and token/session
  revocation behavior verified for the deployment topology.
- Monitoring, alerting, backups, and incident owners assigned.
- Legal/compliance review signed off for the customer/data posture.

Blocked launch candidate:

- Any deployment that still relies on local demo headers or unreviewed demo
  data.
- Any deployment without a restore-tested production database backup path.
- Any deployment without a named clinical safety owner and incident owner.
- Any deployment with unresolved P0/P1 safety, privacy, security, data loss, or
  core workflow blockers.

## Critical Test Gate

Required before signoff:

- GitHub CI is green on the release branch.
- Backend tests pass.
- Alembic migration head check passes.
- Next.js production build passes.
- Web Playwright workflow tests pass.
- Docker compose build validation passes.
- Dependency audit passes.
- Backup restore drill passes.
- The standalone security baseline workflow passes.

Evidence to attach:

- CI run URL and run ID.
- Security Baseline run URL and run ID.
- Release commit SHA.
- Date, signer, and any residual non-blocking annotations.

Reference: `docs/operations/ci-required-checks.md`.

## Security Baseline Gate

Required before signoff:

- Authentication mode is production appropriate; development header trust is not
  enabled for public traffic.
- CORS origins are explicit and limited to production/staging domains.
- Request size limit is configured.
- Auth/share route rate limits are configured for the deployment topology.
- Dependency and secret scans pass.
- Production secret management is configured outside the repository.
- Any platform security controls not covered by the app baseline are documented.

Known required follow-up before real production:

- Distributed/shared rate limiting if running multiple API workers.
- Hosted WAF/platform edge rules if required by the customer risk review.
- Dependency update automation.
- Hosted identity tenant setup, account lifecycle, MFA/password policy, and
  provider-side session controls.

Reference: `docs/product/security-baseline.md`,
`docs/operations/auth-token-revocation.md`, and
`docs/operations/hosted-identity-oidc.md`.

## Backup Restore Gate

Required before signoff:

- Production database backup job is configured.
- Backup storage is encrypted and access-restricted.
- Restore drill has been performed against a non-production target using the
  production-shaped backup process.
- RPO/RTO targets are accepted by the organization owner.
- Restore operator and escalation path are named.
- Backup retention policy is documented.

Evidence to attach:

- Latest restore drill date.
- Backup identifier or sanitized proof of backup inventory.
- Restore operator.
- Any RPO/RTO exception.

Reference: `docs/operations/backups-and-recovery.md`.

## Monitoring Gate

Required before signoff:

- `/health` and `/ready` are reachable from the production monitoring path.
- Request IDs are emitted and visible in logs.
- Structured logs are collected in the target platform.
- Basic metrics are scraped or collected.
- Error tracking is configured if the production environment uses a provider.
- Alert recipients and escalation path are named.
- P0/P1 alert definitions are documented.

Evidence to attach:

- Readiness check URL or monitor name.
- Logging dashboard or query reference.
- Metrics dashboard or query reference.
- Alert route and primary responder.

Reference: `docs/operations/observability.md`.

## Legal And Compliance Gate

Required before signoff:

- Legal/compliance review completed for the exact customer profile and data
  posture.
- Terms, privacy policy, BAA or non-BAA decision memo, and subprocessor list are
  approved.
- Retention, export, deletion, breach notification, and support commitments are
  documented.
- School/minor/guardian-specific obligations are resolved if applicable.
- Real athlete data approval is explicit; otherwise only synthetic or approved
  de-identified data may be used.

Evidence to attach:

- Review date.
- Reviewer or counsel name.
- Approved customer/data posture.
- Contract packet location.
- Open legal/compliance residual risks.

Reference: `docs/product/legal-compliance-review-package.md`.

## Safety Blocker Gate

Required before signoff:

- No unresolved safety notes block launch.
- Non-diagnostic copy remains visible in product surfaces.
- Readiness outputs remain explain-only and cannot auto-clear athletes.
- Named human clearance decisions remain required for advancement, full
  clearance, and closure.
- Limited share views still exclude raw clinical detail and private identifiers.
- Audit events cover sensitive reads, writes, clearance decisions, report
  exports, and share activity.
- Beta P0/P1 feedback has been closed or explicitly accepted as launch-blocking.

Reference: `docs/product/safety-and-compliance-notes.md` and
`docs/operations/beta-readiness.md`.

## Residual Risk Register

Use this table for final signoff. Add rows instead of hiding open risk.

| Risk | Severity | Owner | Decision | Follow-up date |
| --- | --- | --- | --- | --- |
| Staging and production deployment are deferred in this repository state. | Blocker until Goals 32 and 33 are completed | Product/engineering owner | Do not launch broadly from this state | Before production launch |
| Hosted identity-provider tenant deployment and provider-side account/session policy are deferred. | Blocker for broad production | Engineering/security owner | Resolve or document approved compensating control; Goal 40 covers the OIDC adapter but not tenant rollout | Before production launch |
| Legal contracts and subprocessor list are not stored in this repository. | Blocker for real data | Legal/compliance owner | Attach approved external packet before launch | Before production launch |
| Distributed rate limiting and platform edge controls are not implemented here. | Medium or high depending on hosting | Engineering/security owner | Decide during deployment architecture review | Before production launch |
| Automated contrast/accessibility audit is not in CI. | Medium | Product/engineering owner | Complete or accept for limited launch | Before public launch |

## Signoff Checklist

Complete this checklist for the release candidate.

| Gate | Required evidence | Status | Signer | Date |
| --- | --- | --- | --- | --- |
| Critical tests | CI and security run IDs attached | Not signed |  |  |
| Security baseline | Production security controls reviewed | Not signed |  |  |
| Backup restore | Restore drill and RPO/RTO accepted | Not signed |  |  |
| Monitoring | Health, readiness, logs, metrics, alerts active | Not signed |  |  |
| Legal/compliance | Contract/review packet approved | Not signed |  |  |
| Safety blockers | No P0/P1 safety/privacy/security blockers remain | Not signed |  |  |
| Residual risks | Risk register reviewed and accepted | Not signed |  |  |

Final launch decision:

- Release candidate:
- Commit SHA:
- Environment:
- Launch window:
- Product owner:
- Engineering owner:
- Security owner:
- Clinical/safety owner:
- Legal/compliance reviewer:
- Decision: not signed
