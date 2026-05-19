# Title

GET /api/providers/:id/slots - Return provider details and open slots

# Context (Why)

After a learner chooses a provider from the marketplace list, Slice 1 needs a provider-detail view with visible bookable slots. This endpoint supplies the data for that second screen.

# Scope (What)

- Create one GET endpoint at `/api/providers/:id/slots`.
- Return basic provider profile fields plus that provider's open slots.
- Exclude booked or unavailable slots from the returned list.
- Return JSON only.

# Interface Contract (Inputs/Outputs/Data Shapes)

- Request:
  - Method: `GET`
  - Path: `/api/providers/:id/slots`
  - Path parameter:
    - `id`: provider UUID
- Success response: `200`
  ```json
  {
    "provider": {
      "id": "uuid",
      "name": "string",
      "category": "string",
      "rating": 4.8,
      "bio": "string",
      "service": {
        "id": "uuid",
        "name": "string",
        "description": "string"
      }
    },
    "slots": [
      {
        "id": "uuid",
        "start_time": "2026-05-10T14:00:00Z",
        "status": "open"
      }
    ]
  }
  ```
- Error responses:
  - `400`
    ```json
    { "error": "invalid provider id" }
    ```
  - `404`
    ```json
    { "error": "provider not found" }
    ```
  - `500`
    ```json
    { "error": "internal server error" }
    ```

# Acceptance Criteria (Testable Conditions)

- Given seeded provider data exists, when a client sends `GET /api/providers/:id/slots` with a valid provider ID, then the API returns `200` with provider details and exactly that provider's open slots.
- Given a provider has 3 open seeded slots, when the endpoint is called, then the response includes those 3 slots and no slots from other providers.
- Given an invalid UUID-like value is sent as `:id`, when the endpoint is called, then the API returns `400`.
- Given a well-formed but unknown provider ID is sent, when the endpoint is called, then the API returns `404`.
- Given some slots later become booked, when the endpoint is called, then booked slots are not returned in the `slots` array.
- Given the response is used by the booking endpoint contract, when slot objects are inspected, then every slot includes exactly `id`, `start_time`, and `status`.

# Constraints (Rules to Follow)

- Use the existing project routing and data-access pattern.
- Use UUID provider IDs.
- Return times in ISO 8601 format.
- Use UTC timestamps in the slot response.
- Do not require authentication for this ticket.
- Allowed slot states at the data-model level are `open` and `booked`, but this endpoint returns only `open` slots.
- Do not add pagination for Slice 1; return the full open-slot list for the seeded demo provider in one response.
- Do not add response caching behavior in this slice; always read current slot state from the application's source of truth.

# Anti-Scope (What NOT to Build)

- No booking creation in this endpoint.
- No provider editing behavior.
- No recommendations or related-provider logic.
- No search/filter query params.
- No payment or notification behavior.
- No pagination UI or cursor contract.
- No cache layer or stale-availability optimization.
