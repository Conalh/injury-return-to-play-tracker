# Role And Permission Matrix

Goal 13 moves the API from broad role gates to named permissions. The current
matrix is intentionally conservative: clinical workflow access is limited to
admin, clinician, and athletic trainer roles. Athlete, coach, and guardian roles
are limited to shared-status surfaces until their portals land.

## Roles

| Role | Current scope |
| --- | --- |
| `admin` | Organization-bound clinical workflow administration. |
| `clinician` | Organization-bound clinical workflow ownership and decisions. |
| `athletic_trainer` | Organization-bound clinical workflow operation. |
| `coach` | Limited shared status only. |
| `athlete` | Limited shared status only. |
| `guardian` | Limited shared status only. |

## Permissions

| Permission | Admin | Clinician | Athletic trainer | Coach | Athlete | Guardian |
| --- | --- | --- | --- | --- | --- | --- |
| `read_athletes` | Yes | Yes | Yes | No | No | No |
| `manage_athletes` | Yes | Yes | Yes | No | No | No |
| `read_clinical_cases` | Yes | Yes | Yes | No | No | No |
| `manage_clinical_cases` | Yes | Yes | Yes | No | No | No |
| `read_templates` | Yes | Yes | Yes | No | No | No |
| `manage_templates` | Yes | Yes | Yes | No | No | No |
| `read_evidence` | Yes | Yes | Yes | No | No | No |
| `manage_evidence` | Yes | Yes | Yes | No | No | No |
| `read_readiness` | Yes | Yes | Yes | No | No | No |
| `record_clearance_decisions` | Yes | Yes | Yes | No | No | No |
| `manage_shares` | Yes | Yes | Yes | No | No | No |
| `generate_reports` | Yes | Yes | Yes | No | No | No |
| `read_audit_log` | Yes | Yes | Yes | No | No | No |
| `seed_demo` | Yes | Yes | Yes | No | No | No |
| `read_shared_status` | Yes | Yes | Yes | Yes | Yes | Yes |

## Enforcement

The canonical matrix lives in `return_play.permissions`.

- `ROLE_PERMISSIONS` defines allowed permissions per role.
- `assert_permission(context, permission)` is the service-level guard.
- `require_permission(permission)` is the FastAPI route dependency.
- Concrete repositories call `assert_permission` at public workflow entry
  points so direct service calls cannot bypass route checks.

## Current Limitations

The shared status view is still token-based and public at
`GET /api/share/{token}`. Coach, athlete, and guardian authenticated portals are
future goals; until then, those roles do not receive direct clinical API access.
