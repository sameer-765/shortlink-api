# Module 08 Integration Test Plan

## Purpose

These tests should run at every future integration checkpoint. They target the highest-risk boundaries: provider availability to UI, booking reservation behavior, and role-aware booking visibility.

## Test 1: Provider API Response Matches UI Slot Contract

- Components involved: Provider availability API, provider profile UI consumer.
- Setup: Seed one provider with at least one open slot.
- Steps:
  1. Request provider detail and slots.
  2. Render the provider profile using the returned payload.
  3. Inspect the rendered slot time and bookable state.
- Expected result:
  - UI reads `slots[].start_time`.
  - UI does not reference `slots[].slot_start_time`.
  - Slot is bookable when `slots[].status` is `open`.
- Contract points validated:
  - Nested `provider` object.
  - `slots[].id` UUID string.
  - `slots[].start_time` UTC ISO-8601 string.
  - `slots[].status` enum.

## Test 2: Booking Creation Rejects Already-Booked Slot

- Components involved: Provider availability API, booking creation API, slot state storage.
- Setup: Seed one provider slot with `status = "booked"`.
- Steps:
  1. Attempt to create a booking for the booked slot.
  2. Observe the booking API response.
  3. Re-fetch the slot.
- Expected result:
  - Booking request is rejected.
  - No duplicate booking is created.
  - Slot remains `booked`.
  - Error uses the agreed simple JSON shape.
- Contract points validated:
  - Slot status semantics.
  - Booking conflict behavior.
  - Error response shape.

## Test 3: Booking Creation Makes Slot Unavailable

- Components involved: Provider profile UI, booking creation API, provider availability API.
- Setup: Seed one provider slot with `status = "open"`.
- Steps:
  1. Open provider profile and select the open slot.
  2. Submit booking request.
  3. Re-fetch provider slots.
- Expected result:
  - Booking is created successfully.
  - Booking response includes the selected slot and booked time.
  - Re-fetched slot is no longer available as `open`.
- Contract points validated:
  - Booking-to-availability state propagation.
  - `open -> booked` transition.
  - UUID string IDs.
  - UTC ISO-8601 slot time.

## Test 4: Role-Based Booking Visibility Works

- Components involved: Auth/session payload, booking API, My Bookings view.
- Setup:
  - Seed one manager, one employee, and one department head.
  - Seed bookings for multiple employees and departments.
- Steps:
  1. Log in as employee and open My Bookings.
  2. Log in as manager and create a booking for an employee.
  3. Log in as department head and open My Bookings.
- Expected result:
  - Employee sees only their own bookings.
  - Manager can create bookings for employees.
  - Department head sees department bookings only.
  - Users do not see bookings outside their role or department rules.
- Contract points validated:
  - `company_name`, `department`, and `company_role` session fields.
  - Role-aware booking access checks.
  - `booked_for` persistence and display.

## Test 5: My Bookings Reflects Booking API Writes

- Components involved: Booking creation API, booking storage, My Bookings view.
- Setup: Seed a learner or company user with no existing bookings.
- Steps:
  1. Create a booking through the booking API.
  2. Open My Bookings for the same user or allowed role.
  3. Compare booking details in the API response and UI.
- Expected result:
  - My Bookings displays the booking created through the API.
  - Provider, slot time, status, and booked-for details match.
  - No separate mock-only booking appears in the integrated view.
- Contract points validated:
  - Booking persistence.
  - Booking read/write consistency.
  - Role-aware query filtering.

## Test 6: Contract Drift Fails Fast

- Components involved: Contract validation, provider availability API, provider profile UI fixtures.
- Setup: Run contract validation against API payloads and UI mock fixtures.
- Steps:
  1. Validate the provider availability response against the shared contract.
  2. Validate UI fixture fields against the same contract.
  3. Introduce or detect `slots[].slot_start_time`.
- Expected result:
  - Validation passes only when the field is `slots[].start_time`.
  - Validation fails if any stream uses `slots[].slot_start_time`.
- Contract points validated:
  - Shared field names.
  - Slot datetime contract.
  - Checkpoint-sync protection against field-name drift.
