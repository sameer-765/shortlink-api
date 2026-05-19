# Title

GET /api/providers - List available providers

# Context (Why)

This endpoint powers the first screen of Slice 1. A learner needs to see a small marketplace list before they can decide which provider to open and book.

# Scope (What)

- Create one GET endpoint at `/api/providers`.
- Return the 3 seeded providers with the basic fields required for the marketplace list.
- Sort results consistently so the UI can render a stable order.
- Return JSON only.

# Interface Contract (Inputs/Outputs/Data Shapes)

- Request:
  - Method: `GET`
  - Path: `/api/providers`
  - No request body
- Success response: `200`
  ```json
  {
    "providers": [
      {
        "id": "uuid",
        "name": "string",
        "category": "string",
        "rating": 4.8,
        "starting_price": 40,
        "bio": "string"
      }
    ]
  }
  ```
- Error response:
  - `500`
    ```json
    {
      "error": "internal server error"
    }
    ```

# Acceptance Criteria (Testable Conditions)

- Given seeded provider data exists, when a client sends `GET /api/providers`, then the API returns `200` with a `providers` array of length 3.
- Given a successful providers response, when the payload is inspected, then each provider object includes `id`, `name`, `category`, `rating`, `starting_price`, and `bio`.
- Given the providers endpoint is called multiple times without data changes, when the responses are compared, then the provider order is stable.
- Given a database failure occurs, when `GET /api/providers` is called, then the API returns `500` in the project's standard JSON error format.

# Constraints (Rules to Follow)

- Use the existing project routing and database-access pattern.
- Use the project's standard JSON response format.
- Do not require authentication for this ticket.
- Do not include slot data inline in this endpoint.

# Anti-Scope (What NOT to Build)

- No search or filtering logic.
- No provider detail page behavior.
- No pagination.
- No reviews submission or ratings aggregation work.
- No provider onboarding or approval logic.
