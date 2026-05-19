# Module 06 Interface Contracts

## Contract: Provider Availability API <-> Provider Profile Page

### Purpose

This contract defines the exact response shape the provider profile page consumes from the provider availability API. The backend and frontend can work in parallel only if they treat this document as the boundary of truth.

### Endpoint

- Method: `GET`
- Path: `/api/providers/:id/slots`

### Request Input

- Path parameter:
  - `id`: provider UUID string

### Success Response

- Status: `200`
- Body:

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

### Field Definitions

- `provider.id`: UUID string, required
- `provider.name`: string, required
- `provider.category`: string, required
- `provider.rating`: number, required
- `provider.bio`: string, required
- `provider.service.id`: UUID string, required
- `provider.service.name`: string, required
- `provider.service.description`: string, required
- `slots`: array, required, may be empty
- `slots[].id`: UUID string, required
- `slots[].start_time`: UTC ISO 8601 timestamp string, required
- `slots[].status`: enum string, required, allowed value in this endpoint is `open`

### Error Responses

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

### Shared Assumptions

- Slot times are always serialized in UTC ISO 8601 format.
- Slice 1 only returns open slots in this endpoint.
- The provider profile page must not infer or display booked slots from this API.
- The provider profile page must not assume an `end_time`, `pricing`, or alternate slot label unless a later contract revision adds those fields explicitly.

### Consumer Rules

- The provider profile page must map exactly these field names:
  - `provider.name`
  - `provider.category`
  - `provider.rating`
  - `provider.bio`
  - `provider.service.name`
  - `provider.service.description`
  - `slots[].id`
  - `slots[].start_time`
  - `slots[].status`
- The UI must treat `slots[].status = "open"` as bookable.
- The UI must fail safely if the response shape changes instead of guessing alternate field names.

## Contract: Learner Session Boundary for Later Authenticated Flows

### Purpose

This contract keeps authentication work isolated while still making later `My Bookings` integration predictable.

### Session Rules

- Learner identity comes from the auth/session layer, not from arbitrary client-provided IDs.
- Downstream authenticated endpoints must read learner identity from the established session contract.
- Slice 1 anonymous booking behavior remains separate and uses backend-injected `learner_id = "anonymous-demo"` only for the booking ticket where that was explicitly defined.

### Coordination Note

- This contract is not directly consumed by the provider profile page pair in Module 06, but it prevents later drift between the auth stream and learner-specific endpoints.
