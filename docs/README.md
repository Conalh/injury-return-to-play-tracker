# Documentation Index

## Foundation

- `foundation/project-foundation.md`: repo structure, tooling decisions, and
  Goal 0 exit criteria.
- `foundation/goal-roadmap.md`: staged goals for creating the project.

## Product

- `product/product-spec.md`: safety-first V1 product specification.
- `product/safety-and-compliance-notes.md`: source-backed safety, privacy, and
  compliance notes that shape implementation.
- `product/permission-matrix.md`: current role-to-permission matrix and
  enforcement points.
- `product/privacy-controls.md`: field filtering, share-view data contract,
  retention hooks, export/delete request plan, and PHI checklist.
- `product/security-baseline.md`: secure headers, CORS, rate limits, input
  size limits, dependency scan, and secret scan baseline.
- `product/legal-compliance-review-package.md`: data flow map, access matrix,
  controls summary, HIPAA/FTC review notes, policy inputs, and BAA checklist.
- `product/usability-review.md`: Goal 35 copy, state, mobile, accessibility,
  workflow timing, and beta polish review.

## Operations

- `operations/ci-required-checks.md`: CI jobs and required branch-protection
  status checks.
- `operations/local-production-compose.md`: local production-shaped Docker
  Compose runbook.
- `operations/environment-configuration.md`: backend and frontend runtime
  environment contract.
- `operations/observability.md`: request IDs, structured API logs, error
  tracking seam, readiness, and metrics.
- `operations/backups-and-recovery.md`: Postgres backup strategy, restore
  runbook, verification checklist, RPO/RTO targets, and restore drill.
- `operations/beta-readiness.md`: controlled beta onboarding, feedback,
  limitations, support, incident, and launch-gate runbook.
