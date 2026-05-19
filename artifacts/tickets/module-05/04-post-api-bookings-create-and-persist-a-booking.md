# Title

POST /api/bookings - Create and persist a booking

# Context (Why)

This is the core transaction in Slice 1. After a learner picks a provider and slot, the system must create a durable booking record and return a confirmation payload the UI can display immediately.

# Scope (What)

- Create one POST endpoint at `/api/bookings`.
- Validate required request fields.
- Confirm the provider and slot exist.
- Reject attempts to book a slot that is not open.
- Persist a booking record.
- Mark the booked slot as no longer open.
- Return a booking confirmation payload.

# Interface Contract (Inputs/Outputs/Data Shapes)

- Request:
  - Method: `POST`
  - Path: `/api/bookings`
  - JSON body:
    ```json
    {
      "provider_id": "uuid",
      "slot_id": "uuid",
      "notes": "optional string up to 500 chars"
    }
    ```
- Success response: `201`
  ```json
  {
    "booking_id": "uuid",
    "status": "confirmed",
    "provider_id": "uuid",
    "slot_id": "uuid",
    "learner_id": "anonymous-demo",
    "created_at": "ISO 8601 timestamp"
  }
  ```
- Error responses:
  - `400`
    ```json
    { "error": "<field> is required" }
    ```
  - `403`
    ```json
    { "error": "provider unavailable" }
    ```
  - `404`
    ```json
    { "error": "provider not found" }
    ```
    or
    ```json
    { "error": "slot not found" }
    ```
  - `409`
    ```json
    { "error": "slot unavailable" }
    ```
  - `500`
    ```json
    { "error": "internal server error" }
    ```

# Acceptance Criteria (Testable Conditions)

- Given a valid provider ID and an open slot ID, when a client sends `POST /api/bookings` with the required body, then the API returns `201` with `booking_id`, `status`, `provider_id`, `slot_id`, `learner_id`, and `created_at`.
- Given a successful booking response, when the booking data is checked through the application's persistence layer, then the booking record exists in storage.
- Given a successful booking response, when the related slot is checked, then its state is no longer `open`.
- Given `provider_id` is missing, when `POST /api/bookings` is called, then the API returns `400` with a field-specific error message.
- Given `slot_id` does not exist, when `POST /api/bookings` is called, then the API returns `404`.
- Given the target slot is already booked or unavailable, when `POST /api/bookings` is called, then the API returns `409` with `slot unavailable`.
- Given two requests try to book the same open slot at nearly the same time, when both requests are processed, then at most one request succeeds with `201` and the other returns `409`.
- Given the target provider is inactive, deleted, or unapproved, when `POST /api/bookings` is called, then the API returns `403` with `provider unavailable`.

# Constraints (Rules to Follow)

- Use the existing project database connection and error-response format.
- Use `apps/api/app/database.py` for the shared database session/connection pattern.
- Use the existing transaction helper from the same database layer if the codebase exposes one; do not create a new parallel database-access pattern for this ticket.
- Use the project's shared JSON error response utility from the existing API error-handling layer; if the project keeps that helper beside the route layer, reuse that file instead of inventing a ticket-local formatter.
- Use UUID v4 for generated `booking_id`.
- Treat this Slice 1 booking as anonymous demo flow by having the backend inject `learner_id = "anonymous-demo"` automatically. The client must not send `learner_id` in the request body for this slice.
- The allowed slot states for Slice 1 are `open` and `booked`.
- Provider records must be treated as bookable only when their state is `active`. Requests for `inactive`, `deleted`, or `unapproved` providers must be rejected.
- All slot times and booking timestamps must use UTC ISO 8601 format in storage and API responses.
- The booking write and slot-state update must be handled atomically through transactional locking or an equivalent concurrency-safe pattern so only one booking can win a contested slot.
- Ensure the booking write and slot-state update are handled consistently so the slot transitions from `open` to `booked` after a successful booking and cannot remain `open`.
- No payment dependency in this ticket.

# Anti-Scope (What NOT to Build)

- No payment processing.
- No email or push notification.
- No cancellation or rescheduling.
- No authentication enforcement.
- No provider dashboard updates.
- No client-side time-zone conversion logic in this ticket.
