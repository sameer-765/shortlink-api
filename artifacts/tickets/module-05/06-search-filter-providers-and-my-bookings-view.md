# Title

Search/filter providers and My Bookings view

# Context (Why)

Slice 2 improves the learner experience after authentication by making it easier to find the right provider and review upcoming bookings tied to the learner's account. This makes the booking flow feel like a usable product instead of a one-off demo.

# Scope (What)

- Add provider search by provider name or service title.
- Add category filtering on the providers list.
- Add a learner-only `My Bookings` endpoint or data source that returns the signed-in learner's bookings.
- Keep the provider-search behavior compatible with the seeded providers from Slice 1.

# Interface Contract (Inputs/Outputs/Data Shapes)

- Search request:
  - `GET /api/providers?query=<string>&category=<string>`
- Search success response: `200`
  ```json
  {
    "providers": [
      {
        "id": "uuid",
        "name": "string",
        "category": "string",
        "rating": 4.8,
        "starting_price": 40
      }
    ]
  }
  ```
- My Bookings request:
  - `GET /api/my-bookings`
  - Requires active learner session
- My Bookings success response: `200`
  ```json
  {
    "bookings": [
      {
        "booking_id": "uuid",
        "provider_id": "uuid",
        "provider_name": "string",
        "slot_id": "uuid",
        "status": "confirmed",
        "created_at": "ISO 8601 timestamp"
      }
    ]
  }
  ```
- Error responses:
  - `401`
    ```json
    { "error": "authentication required" }
    ```
  - `500`
    ```json
    { "error": "internal server error" }
    ```

# Acceptance Criteria (Testable Conditions)

- Given seeded provider data exists, when a client sends `GET /api/providers?query=<matching text>`, then the API returns only providers whose name or service title matches the query.
- Given seeded provider data exists, when a client sends `GET /api/providers?category=<existing category>`, then the API returns only providers in that category.
- Given both `query` and `category` are supplied, when `GET /api/providers` is called, then both filters are applied together.
- Given a learner is signed in and has at least one booking attached to their account, when `GET /api/my-bookings` is called, then the API returns only that learner's bookings.
- Given no learner session is active, when `GET /api/my-bookings` is called, then the API returns `401`.
- Given a booking exists for the signed-in learner, when the `My Bookings` payload is inspected, then each booking includes `booking_id`, `provider_id`, `provider_name`, `slot_id`, `status`, and `created_at`.

# Constraints (Rules to Follow)

- Use the existing provider-list response structure as the base for search/filter output.
- Use the learner session created in the auth ticket rather than a new token pattern.
- Keep filter behavior case-insensitive if the underlying stack allows it without adding unusual complexity.
- Do not require search infrastructure beyond the current project database and app stack.

# Anti-Scope (What NOT to Build)

- No recommendations or ranking algorithm.
- No fuzzy search tuning beyond straightforward name/service matching.
- No booking cancellation from `My Bookings`.
- No provider dashboard behavior.
- No payment or notification logic.
