# Module 06 Simulated Agent Output Bundle

## Stream A Output: Provider Availability API

### Ticket

- `artifacts/tickets/module-05/03-get-api-providers-id-slots-return-provider-details-and-open-slots.md`

### Simulated Output Summary

- Added `GET /api/providers/:id/slots`
- Returns provider profile data and open slots
- Uses UUID identifiers and UTC ISO 8601 slot timestamps

### Simulated Success Payload

```json
{
  "provider": {
    "id": "6f2d4f0c-9e8b-4a9b-a9e4-b5a99642e8a0",
    "name": "Maria's Cleaning",
    "category": "Home Services",
    "rating": 4.8,
    "bio": "Independent cleaner with 5 years of residential experience.",
    "service": {
      "id": "1c8d56f0-5bb7-4897-b8f2-b41e9f969f4d",
      "name": "Standard Home Cleaning",
      "description": "Two-hour cleaning for apartments and small homes."
    }
  },
  "slots": [
    {
      "id": "af4ca7a0-b9b0-4909-bf0f-3e52d1f9c5ee",
      "start_time": "2026-05-10T14:00:00Z",
      "status": "open"
    },
    {
      "id": "b5af7b48-8b58-4887-bd3f-fc6af6b0dbbf",
      "start_time": "2026-05-10T16:00:00Z",
      "status": "open"
    }
  ]
}
```

## Stream B Output: Provider Profile Page Consumer

### Ticket Basis

- Slice 1 provider-detail UI consumer of the provider availability API contract

### Simulated Output Summary

- Builds a provider detail screen
- Shows provider identity, service details, and slot buttons
- Depends entirely on the API contract instead of backend internals

### Simulated Data Mapping

```json
{
  "providerName": "provider.name",
  "category": "provider.category",
  "rating": "provider.rating",
  "bio": "provider.bio",
  "serviceName": "provider.service.name",
  "serviceDescription": "provider.service.description",
  "slotCards": [
    {
      "slotId": "slots[].id",
      "displayTime": "slots[].slot_start_time",
      "isBookable": "slots[].status === 'open'"
    }
  ]
}
```

### Seeded Contract Violation

- Violation: the UI consumer expects `slots[].slot_start_time`
- Contract truth: the API promises `slots[].start_time`
- Why this matters: both streams look reasonable in isolation, but they will fail together at the sync point because the field names do not line up exactly

## Stream C Output: Learner Signup/Login

### Ticket

- `artifacts/tickets/module-05/05-learner-signup-login-with-session-handling.md`

### Simulated Output Summary

- Provides learner session creation and session-backed identity lookup
- Keeps learner identity out of ad hoc request payloads for authenticated endpoints

### Simulated Session Result

```json
{
  "session_id": "sess_12345",
  "learner_id": "3d7a7f2d-c53f-4f42-ae20-8f6db4c5d317",
  "status": "authenticated"
}
```

## Checkpoint Review

### Checkpoint 1 Findings

- Stream A and Stream B are not yet compatible.
- Root cause: field-name drift on the slot time property.
- Required fix: Stream B must consume `slots[].start_time` exactly as defined in the contract.

### Checkpoint 2 Expected Resolution

- After Stream B updates the mapping to `slots[].start_time`, the provider detail pair becomes compatible.
- Stream C remains isolated and does not block the provider-detail pair for this module.
