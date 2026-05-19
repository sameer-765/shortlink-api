# Module 08 Integration Checklist

## Execution Mode

- Integration approach: incremental.
- Execution source: standalone simulated.
- Inputs:
  - `artifacts/parallel/module-06-agent-output-bundle.md`
  - `artifacts/adaptation/module-07-updated-plan.md`

## Pre-Integration Contract Check

| Contract Point | Agreed Contract | Check Result | Notes |
|---|---|---|---|
| ID format | Provider, service, slot, learner, and booking IDs are UUID strings. | Pass | Streams must not treat IDs as integers. |
| Slot datetime | Slot times use UTC ISO-8601 strings. | Pass | Example: `2026-05-10T14:00:00Z`. |
| Slot time field | Availability responses use `slots[].start_time`. | Fixed before merge | UI-oriented output drifted to `slots[].slot_start_time`; consumer must use `slots[].start_time`. |
| Slot status values | Slot status uses shared enum values such as `open` and `booked`. | Pass | Booking creation owns the final `open -> booked` transition. |
| Error response shape | Error responses use the agreed simple JSON shape. | Pass | Example: `{ "error": "provider not found" }`. |
| Provider detail shape | Provider detail response contains nested `provider` object plus `slots` array. | Pass | UI consumer maps from this contract rather than backend internals. |
| RBAC session fields | Company role and department live on the membership/session payload. | Pass with demo scope | Demo roles are fixed: manager, employee, department head. |
| Booking visibility rules | Booking reads are filtered by current user's role. | Pass with demo scope | Employee sees own bookings; manager can book for employees; department head sees department bookings. |

## Incremental Merge Order

| Order | Workstream | Reason for Position | Result |
|---|---|---|---|
| 1 | Provider availability API contract | It provides the shared provider and slot data shape used by later streams. | Merged as source-of-truth contract. |
| 2 | Provider profile UI consumer | Validates the highest-risk known contract boundary: slot field naming. | Merged after correcting `slot_start_time` to `start_time`. |
| 3 | Booking creation flow | Depends on provider/slot contract and owns slot reservation. | Merged with atomic slot booking and `open -> booked` expectation. |
| 4 | Lightweight company/RBAC adaptation | Changes booking ownership and access rules after core booking works. | Merged with fixed demo roles and session-backed role checks. |
| 5 | My Bookings role-aware view | Depends on bookings and RBAC visibility rules. | Merged after role-aware query behavior is defined. |

## Merge Verification Notes

- Provider availability API and provider profile UI are compatible only after the UI consumes `slots[].start_time`.
- Booking creation must reject already-booked slots and avoid corrupt duplicate reservations.
- Company/RBAC adaptation remains a demo model, not full enterprise administration.
- My Bookings must reflect records created through the booking API rather than using separate mock data.

## End-to-End Scenario Results

| Scenario | Components Crossed | Expected Result | Result |
|---|---|---|---|
| Learner views provider list, opens provider profile, and sees open slots. | Provider list, availability API, provider profile UI. | Open slots render from `slots[].start_time` and `slots[].status`. | Pass after slot field correction. |
| Learner selects slot, creates booking, and slot becomes unavailable. | Provider profile UI, booking API, slot state. | Booking persists and slot transitions from `open` to `booked`. | Pass in plan; requires integration test coverage. |
| Manager books for employee and booking records `booked_for`. | Session/RBAC, booking form, booking API. | Manager can submit booked-for fields and confirmation includes booked-for person. | Pass with simplified RBAC scope. |
| Employee views only own bookings. | Auth session, My Bookings query, booking records. | Employee cannot see company or department-wide bookings. | Pass with role-aware filtering. |
| Department head views department bookings only. | Auth session, department membership, My Bookings query. | Department head sees bookings for their department and not other departments. | Pass with fixed department demo data. |

## Open Risks

- The standalone simulation proves the integration plan, but the real codebase still needs executable tests.
- Simplified RBAC must stay clearly labeled as demo scope so it does not get mistaken for enterprise-grade permissions.
- Contract validation should be automated so `start_time` cannot drift back to `slot_start_time`.
