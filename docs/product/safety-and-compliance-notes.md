# Safety And Compliance Notes

Status: working notes for product and implementation

These notes are not legal or medical advice. They summarize implementation
constraints that should be reviewed by qualified counsel and clinical advisors
before handling real athlete data.

## Clinical Source Review

### Bern Return-To-Sport Consensus

Source:
https://bjsm.bmj.com/content/50/14/853

Product implications:

- Return to sport is a continuum, not a single end-of-rehab event.
- The product should model staged progress instead of a binary injured/cleared
  state.
- Decisions should be collaborative across clinicians, athletes, coaches, and
  guardians where appropriate.
- The product should document sport, participation level, context, goals,
  clinical evidence, functional evidence, workload, and stakeholder roles.
- Workload and psychological readiness can matter, so the product should allow
  clinicians to capture more than pain scores and pass/fail tests.
- The product must support removing or reducing participation when symptoms or
  risk signals worsen.

### Team Physician Consensus Statement

Sources:

- 2012 AAOS-hosted consensus PDF:
  https://www.aaos.org/globalassets/about/bylaws-library/information-statements/1036-the-team-physician-and-the-return-to-play-decision---a-consensus-statement.pdf
- 2024 Current Sports Medicine Reports metadata:
  https://scholar.usuhs.edu/en/publications/team-physician-consensus-statement-return-to-sportreturn-to-play--2/

Product implications:

- RTP decisions depend on evaluation, treatment, rehabilitation, participation
  context, and information from multiple sources.
- Functional testing, psychosocial readiness, documentation, communication, and
  disclosure constraints should be represented in the workflow.
- The product should help coordinate evidence, but named clinical users remain
  responsible for decisions.
- Minor athletes need guardian-aware communication patterns and disclosure
  controls.

## Privacy And Regulatory Source Review

### HHS Mobile Health App Developer Resources

Source:
https://www.hhs.gov/hipaa/for-professionals/special-topics/health-apps/index.html

Product implications:

- Health app privacy and security protections can be legally required depending
  on the user, data flow, customer relationship, and integrations.
- HIPAA status cannot be assumed from the product category alone. It depends on
  whether the app is acting for a covered entity or business associate, among
  other facts.
- The implementation should be designed so HIPAA-grade controls are possible
  even if the first demo is not deployed in a HIPAA-regulated setting.
- Cloud service choices, data retention, breach handling, and business associate
  obligations need legal review before provider/clinic sales.

### FTC Health Breach Notification Rule Guidance

Source:
https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0

Product implications:

- Health apps and connected health products not covered by HIPAA may still have
  FTC obligations.
- Unauthorized disclosure can trigger breach obligations even when there is no
  traditional security intrusion.
- Individually identifiable health information can include combinations of
  health facts and identifiers.
- The app should minimize shared data, audit sharing, expire share links, support
  revocation, and avoid unnecessary third-party disclosure.

## Required Product Guardrails

The product must never:

- Diagnose an injury.
- Recommend treatment.
- Clear an athlete automatically.
- Override a clinician.
- Hide red flags.
- Encourage participation through worsening symptoms.
- Present templates as medically authoritative protocols.
- Show coaches or guardians more information than their role requires.

The product may:

- Track clinician-defined plans.
- Track symptoms and function.
- Highlight missing evidence.
- Highlight concerning signals.
- Generate clinician-reviewed reports.
- Require explicit human clearance.
- Provide editable templates.

## Implementation Guardrails

Before real athlete data:

- Authentication is required.
- Role-based access is required.
- Organization isolation is required.
- Audit logging is required for clearance and sharing.
- Field-level response filtering is required for restricted share surfaces.
- Export and deletion requests must follow a documented review path.
- Retention hooks must exist before records are deleted or retained by policy.
- Share tokens must expire and be revocable.
- Share tokens must be stored hashed, not in plaintext.
- Demo data must be synthetic.
- Logs must not leak sensitive fields.
- Exports must be access-controlled and auditable.
- Production deployments must use HTTPS.

## Copy Review Checklist

Before shipping any user-facing page or report, verify that it does not say:

- "Safe to play"
- "No risk"
- "Recovered"
- "Treatment recommendation"
- "Cleared by the system"
- "Automatic clearance"

Prefer:

- "Ready for clinician review"
- "Clearance decision required"
- "Evidence complete for this configured gate"
- "Symptoms require review"
- "Workload progression incomplete"
- "Human decision recorded"
