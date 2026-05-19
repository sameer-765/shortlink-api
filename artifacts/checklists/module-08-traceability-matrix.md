# Module 08 Requirements Traceability Matrix

## Traceability Summary

Every updated Module 07 requirement maps to at least one end-to-end scenario and one contract or integration test check.

| Requirement / Scope Item | Current Status | Implementation Location | Scenario Coverage | Contract / Test Coverage |
|---|---|---|---|---|
| Seed provider profiles and available slots. | Built | Slice 1 seed data and provider availability stream. | Learner views provider list and provider profile. | Provider API response matches UI slot contract. |
| List available providers. | Built | `GET /api/providers` listing behavior. | Learner views provider list. | Provider list must use UUID provider IDs and stable provider fields. |
| Return provider details and open slots. | Built | `GET /api/providers/:id/slots` contract. | Learner opens provider profile and sees open slots. | Availability response must include nested `provider`, `slots[].id`, `slots[].start_time`, and `slots[].status`. |
| Use UUID string IDs across provider, service, slot, learner, and booking records. | Built | Module 06 interface contract and simulated availability payload. | All scenarios. | Contract check validates UUID string usage. |
| Use UTC ISO-8601 slot timestamps. | Built | Module 06 interface contract and availability response. | Provider profile and booking scenarios. | Contract test validates timestamp format. |
| Use `slots[].start_time` as the slot time field. | Built after correction | Provider availability API and provider profile UI mapping. | Provider profile renders open slots. | Contract test fails if `start_time` drifts to `slot_start_time`. |
| Create and persist a booking. | Built | `POST /api/bookings` workflow. | Learner creates booking from selected slot. | Booking creation rejects already-booked slot. |
| Transition slot from `open` to `booked`. | Built | Booking creation flow. | Learner books slot and slot becomes unavailable. | Slot-state integration test validates `open -> booked`. |
| Prevent duplicate booking for the same slot. | Built | Booking creation flow. | Concurrent booking edge case. | Already-booked slot rejection test. |
| Add lightweight company/RBAC fields. | Simplified | Session or membership payload. | Manager books for employee; role-aware My Bookings. | RBAC visibility test across manager, employee, and department head. |
| Managers can book for employees. | Built for demo | Booking form and booking API role checks. | Manager books for employee and booking records `booked_for`. | Role-based booking visibility test. |
| Employees can only access their own bookings. | Built for demo | My Bookings role-aware query. | Employee views only own bookings. | RBAC visibility test for employee account. |
| Department heads can view department bookings only. | Built for demo | My Bookings role-aware query and department session data. | Department head views department bookings only. | RBAC visibility test for department head account. |
| Company billing or invoicing. | Deferred | Not in six-day demo scope. | Not covered by scenarios. | Explicitly cut to protect demo timeline. |
| Configurable enterprise administration. | Deferred | Not in six-day demo scope. | Not covered by scenarios. | Explicitly cut; demo uses fixed roles. |
| Advanced notifications. | Deferred | Not in six-day demo scope. | Not covered by scenarios. | Explicitly cut; confirmation is visible in app. |
| Advanced dashboard/search polish. | Deferred | Not in six-day demo scope. | Not required for role-aware booking demo. | Explicitly cut or time-boxed. |

## Lost Requirements

- None identified in this pass.

## Simplified Requirements

- Company-account support is simplified into fixed demo RBAC rather than a full organization model.
- Company booking visibility is simplified into manager, employee, and department-head rules.
- Confirmation is in-app only; notifications remain deferred.

## Deferred Requirements

- Company billing and invoicing.
- Configurable enterprise administration.
- Advanced notifications.
- Nonessential dashboard and search polish.
