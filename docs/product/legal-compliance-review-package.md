# Legal And Compliance Review Package

Status: Goal 34 review packet

This packet is a product and engineering input for counsel or a compliance
specialist. It is not legal advice and does not classify the product on its
own. The product must not handle real athlete health data until the review
questions and launch gate below are resolved.

Sources checked on 2026-05-27:

- HHS covered entities and business associates:
  https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html
- HHS business associate contract provisions:
  https://www.hhs.gov/hipaa/for-professionals/covered-entities/sample-business-associate-agreement-provisions/index.html
- HHS minimum necessary standard:
  https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html
- FTC Health Breach Notification Rule basics:
  https://www.ftc.gov/node/78112
- FTC Health Breach Notification Rule compliance guidance:
  https://www.ftc.gov/tips-advice/business-center/guidance/complying-ftcs-health-breach-notification-rule
- FTC mobile health apps interactive tool:
  https://www.ftc.gov/business-guidance/resources/mobile-health-apps-interactive-tool

## Review Scope

The current product is a safety-first return-to-play workflow tracker for
athletic medicine. It stores synthetic demo data locally today, but the intended
production workflow can include sensitive injury, symptom, workload, clearance,
guardian, and participation data.

The review should determine:

- Whether each target customer relationship makes the product a HIPAA business
  associate, a non-HIPAA consumer health app, an education/school-adjacent
  service, or another regulated arrangement.
- Which data elements can be collected for the V1 workflow under minimum
  necessary principles.
- Whether a business associate agreement, customer data processing agreement,
  school agreement, parental/guardian consent flow, or other contract exhibit is
  required before onboarding a beta organization.
- Whether the FTC Health Breach Notification Rule or state health privacy laws
  apply when HIPAA does not.
- Which retention, export, deletion, breach response, and support commitments
  must be made before real data is entered.

## Data Flow Map

| Step | Data involved | Actor or system | Storage or exposure | Current controls |
| --- | --- | --- | --- | --- |
| Athlete intake | Athlete name, sport, birth date, guardian contact, injury title, date, clinician owner | Clinician, athletic trainer, admin | API repository and SQL tables | Auth context, organization scoping, role permissions |
| Template application | Plan title, phases, milestone gates, progression thresholds | Clinician, athletic trainer, admin | API repository and SQL tables | Template permissions and organization scoping |
| Evidence entry | Symptom scores, notes, functional tests, workload sessions, milestone evidence | Clinician, athletic trainer, admin | API repository and SQL tables | Evidence permissions, audit events, case scoping |
| Readiness review | Conservative readiness signals derived from evidence and gates | Clinician, athletic trainer, admin | API response and case detail UI | Read-only readiness permission; no automatic clearance |
| Clearance decision | Hold, advance, full clearance, close case, rationale, restrictions, decision maker | Clinician, athletic trainer, admin | API repository, audit log, PDF report | Required rationale, named decision, audit event |
| Limited share link | Current phase, participation status, allowed/restricted activities, next review, clinician note | Coach, athlete, guardian via token-scoped link | Limited share response only | Field-level privacy filter, expiring/revocable token, share-read audit |
| Athlete portal | Current status and athlete symptom check-in | Athlete via share token | Limited response and symptom check-in audit | Token scope, no clinician-only clinical detail |
| Guardian portal | Conservative status, restrictions, next review, acknowledgement | Guardian via share token | Limited response and acknowledgement audit | Token scope, no raw evidence |
| PDF report | Status, phase, evidence summary, restrictions, clearance decisions, readiness, audit metadata | Clinician, athletic trainer, admin | Generated PDF response | Report permission, export audit event |
| Admin/user management | Organization setup, invited users, roles, active flag | Admin | API repository and organization audit log | Admin-only permissions and organization audit trail |
| Backups and restore | Production database snapshot when deployed | Operator | Backup files or object storage | Backup runbook, restore drill, encryption-at-rest requirement |

Implementation references:

- `docs/product/privacy-controls.md`
- `docs/product/permission-matrix.md`
- `docs/product/safety-and-compliance-notes.md`
- `docs/product/security-baseline.md`
- `docs/operations/backups-and-recovery.md`
- `docs/operations/observability.md`

## User Role And Data Access Matrix

The canonical role matrix is `docs/product/permission-matrix.md` and
`return_play.permissions`.

Summary for review:

| Role | Direct clinical API access | Limited share access | Admin access | Notes |
| --- | --- | --- | --- | --- |
| Admin | Yes | Yes | Yes | Organization-bound administrative and clinical workflow role. |
| Clinician | Yes | Yes | No | Primary clinical decision maker. |
| Athletic trainer | Yes | Yes | No | Clinical workflow operator under organization policy. |
| Coach | No | Yes | No | Token-scoped participation status only. |
| Athlete | No | Yes | No | Token-scoped athlete portal and symptom check-in only. |
| Guardian | No | Yes | No | Token-scoped conservative status and acknowledgement only. |

Counsel should confirm whether the current coach, athlete, and guardian limited
share fields are sufficient and whether any audience requires consent language,
age gating, additional identity proofing, or no-access defaults.

## Security Controls Summary

Implemented controls:

- Explicit authentication modes: development headers for local work and
  HMAC-signed bearer tokens for production-shaped API requests.
- Central permission matrix enforced at route dependencies and repository entry
  points.
- Organization scoping across roster, templates, cases, evidence, readiness,
  reports, share management, and audit logs.
- Admin-only organization setup, user invitation, role update, deactivation, and
  organization audit log access.
- Security headers, CORS allowlisting, request size caps, and per-process
  auth/share rate limits.
- Field-level privacy filtering for limited share views and an explicit
  restricted-surface data contract.
- Expiring and revocable share links.
- Audit events for evidence writes, clearance decisions, share creation,
  limited share reads, athlete check-ins, guardian acknowledgements, PDF report
  exports, and organization administration.
- CI checks for backend tests, migration heads, web build, Playwright workflow
  tests, Docker compose build, dependency audits, and secret scanning.
- Backup and restore scripts plus a CI restore drill.
- Request IDs, structured API logs, readiness endpoint, metrics endpoint, and an
  error-tracking integration seam.

Known gaps before real data:

- Hosted identity-provider integration is deferred. Local HMAC logout
  revocation exists, and persistent API deployments can share database-backed
  revocation state, but this is not a hosted identity decision.
- Staging and production hosting are not deployed.
- Production secret management, distributed rate limiting, WAF rules, and
  deployment-platform controls are not configured.
- Retention, export, deletion, and breach response workflows are documented as
  policy hooks, not fully automated production operations.
- No signed BAA, data processing agreement, terms, privacy policy, incident
  response policy, or customer onboarding agreement exists in this repository.

## HIPAA And FTC Review Notes

HIPAA classification depends on the customer relationship and data flow, not the
product category alone. HHS guidance says covered entities need written business
associate contracts when engaging a business associate to handle protected
health information for covered functions. Counsel must decide whether the
product is acting for a covered entity, a business associate, a school/team, a
direct-to-consumer health app, or another arrangement.

Minimum necessary review is required for each workflow surface. The current
product already minimizes coach, athlete, and guardian share views, but counsel
should verify:

- Whether birth date and guardian contact are necessary for V1 intake.
- Whether raw symptom, workload, and functional-test data should ever leave the
  clinician surface.
- Whether PDF exports include more evidence than needed for their intended use.
- Whether audit-log metadata can include sensitive context that should be
  filtered from exports.

FTC review is still required if HIPAA does not apply. The FTC Health Breach
Notification Rule guidance highlights that many health apps and similar
technologies can have breach-notification duties for unsecured identifiable
health information. Review must also cover advertising, analytics, pixels,
third-party SDKs, and any future integration that could disclose health-related
events outside the core service.

## Terms And Privacy Policy Input Packet

Counsel and product should use these inputs when drafting terms, privacy policy,
and customer agreements:

- Product purpose: evidence binder and workflow tracker for human
  return-to-play decisions, not diagnosis, treatment recommendation, or
  automatic clearance.
- Data categories: athlete identity, sport, injury case, return-plan phases,
  symptoms, functional tests, workload sessions, milestone evidence, readiness
  signals, clearance decisions, restrictions, clinician notes, share links,
  portal acknowledgements, report exports, user roles, audit events, and
  operational logs.
- User categories: admin, clinician, athletic trainer, coach, athlete,
  guardian, and operator/support roles if added.
- Sharing model: direct clinical access is organization-bound and role-gated;
  coach, athlete, and guardian views are limited, token-scoped, expiring, and
  revocable.
- Decision model: the system never clears an athlete automatically; named human
  decisions are required for hold, advancement, full clearance, or closure.
- Export model: PDF reports are clinician-facing, access-controlled, and
  audited.
- Retention model: current code exposes review hooks but does not yet enforce a
  production retention schedule.
- Breach model: breach response is not yet operationalized and must be defined
  before real data.
- Subprocessor model: not yet defined; hosting, database, email, analytics,
  error tracking, and logging providers must be listed before deployment.
- Support model: no production support, SLA, or incident escalation process is
  currently committed.

## BAA Decision Checklist

Before onboarding a healthcare customer or any organization that may make this
product handle PHI, answer and document:

- Is the customer a HIPAA covered entity or business associate?
- Is the product creating, receiving, maintaining, or transmitting PHI for that
  customer?
- If yes, is a BAA signed before data access?
- Does the BAA define permitted uses and disclosures, safeguard obligations,
  breach/security-incident reporting, subcontractor flow-down requirements,
  individual rights support, audit cooperation, termination return/destruction,
  and cure/termination rights?
- Are hosting, database, logging, email, analytics, monitoring, and support
  vendors covered by compatible terms or excluded from PHI access?
- Does the architecture support the customer's required retention, export,
  deletion, audit, and breach-notice timelines?
- Are minors, school teams, guardian access, and state privacy obligations
  handled in the customer contract and product workflow?
- Has counsel approved whether direct-to-athlete or direct-to-guardian use
  changes the regulatory posture?

## Counsel Review Questions

1. Which exact customer profiles are allowed for beta: clinics, school athletic
   departments, club teams, individual clinicians, or direct-to-consumer teams?
2. For each profile, what is the product's HIPAA, FTC, state health privacy, and
   school/minor data posture?
3. Which data fields must be removed, made optional, or hidden before real data?
4. What consent, notice, and authorization language is required for athlete and
   guardian workflows?
5. Are limited share links acceptable as token-scoped access, or is
   authenticated portal access required before beta?
6. What retention schedule applies to cases, audit logs, reports, revoked
   shares, exports, and deleted athletes?
7. What breach notification clock, escalation path, and customer notice duties
   must the incident response runbook include?
8. Which subprocessors are approved, and which are prohibited from receiving
   health-related data?
9. Can PDF reports be downloaded locally, or must export controls, watermarks,
   expiration, or download logs be expanded first?
10. What beta launch disclaimer, support language, and limitation-of-use terms
    are required?

## Launch Gate

Real athlete data remains blocked until:

- Counsel or a compliance specialist signs off on the customer posture and
  required contracts.
- Terms, privacy policy, BAA or non-BAA decision memo, and subprocessor list are
  ready for the chosen beta customer type.
- Hosted identity, production deployment, secret management, monitoring, backup
  storage, and incident response are complete.
- Retention, export, deletion, and breach response owners are named.
- A beta onboarding checklist explains what data is allowed, which workflows are
  excluded, who can access each role, and how to report concerns.
