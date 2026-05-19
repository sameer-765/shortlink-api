# Module 06 Execution Plan

## Mode

- Selected mode: `standalone_simulated`
- Reason: This mode lets the team practice parallel coordination, interface contracts, and checkpoint synchronization without the extra operational overhead of managing real distributed agent sessions during the exercise.

## Parallel Work Strategy

- `parallelism_strategy`: `isolated_branches`
- `sync_point_design`: `checkpoint_syncs`

This plan treats parallel execution like a film crew working from the same shot list but on separate sets. Each stream gets its own bounded scope and only shares the contract that defines how the work must fit together later.

## Selected Streams

### Stream A: Provider Availability API

- Source ticket: `artifacts/tickets/module-05/03-get-api-providers-id-slots-return-provider-details-and-open-slots.md`
- Goal: Return provider profile data plus open slot data for the provider detail experience.
- Why it can run in parallel: It can be implemented independently as long as the response contract is explicit.

### Stream B: Provider Profile Page Consumer

- Source ticket basis: Slice 1 provider-detail UI consumer of the provider availability contract
- Goal: Render provider details and bookable slots from the API response without making independent schema assumptions.
- Why it can run in parallel: It does not need backend implementation details if the API contract is stable.

### Stream C: Learner Signup/Login

- Source ticket: `artifacts/tickets/module-05/05-learner-signup-login-with-session-handling.md`
- Goal: Establish learner session handling for later Slice 2 user-specific flows.
- Why it can run in parallel: It has no hard dependency on the provider-detail contract and does not need provider-slot data to begin.

## Dependency Check

- Stream A and Stream B are parallel with a shared contract dependency, not an implementation dependency.
- Stream C is independent of the provider-detail pair.
- `POST /api/bookings` is intentionally not selected for parallel execution here because it depends on slot schema, slot-state meaning, and reservation rules from the availability flow.

## Interface Contracts Required Before Execution

### Contract 1: Provider Availability API <-> Provider Profile Page

- Shared identifiers:
  - `provider.id`: UUID
  - `service.id`: UUID
  - `slots[].id`: UUID
- Shared enums:
  - `slots[].status`: `open` only in the API response for Slice 1
- Shared time format:
  - UTC ISO 8601, for example `2026-05-10T14:00:00Z`

### Contract 2: Learner Session Contract

- Session identity source for later authenticated flows must come from the auth ticket and not from ad hoc client-provided learner IDs.
- This stream is monitored separately because it does not synchronize with the provider-detail pair in this step.

## Checkpoint Plan

### Checkpoint 1: First Meaningful Output

- Trigger:
  - Stream A produces a sample `200` response payload for `GET /api/providers/:id/slots`
  - Stream B produces a first-pass data-mapping shape for the provider detail page
- Verify:
  - Field names match exactly
  - Slot status values match the contract
  - Time fields use UTC ISO 8601
  - The UI does not assume fields that the API never promised

### Checkpoint 2: End-of-Stream Compatibility Pass

- Trigger:
  - All simulated outputs are complete
- Verify:
  - Provider profile rendering still matches the API contract
  - Auth stream remains isolated and does not leak unauthenticated assumptions into `My Bookings`
  - Any surfaced mismatch is recorded as a contract issue, not silently patched in one stream only

## Coordination Rules

- Each stream stays inside its own scope and does not add helpful extra features.
- If a stream needs a field that is missing from the contract, the contract is updated first before downstream outputs are treated as correct.
- Any ambiguity found by one stream must be broadcast to all affected streams at the next checkpoint.
- Completion status will be tracked as `on-track`, `needs clarification`, or `complete`.

## Expected Contract Risk

- Highest risk area: field-name drift between the provider availability API and the provider profile page consumer.
- Seeded test violation for this module: the UI consumer will intentionally expect a field name that does not exactly match the API contract so the checkpoint catches it.
