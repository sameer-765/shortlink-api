# Title

Seed provider profiles and test time slots

# Context (Why)

Slice 1 needs realistic marketplace data so a learner can browse providers, open a provider page, choose a slot, and complete a booking without waiting on provider self-service features. This ticket creates the fixed demo data that the first vertical slice depends on.

# Scope (What)

- Insert exactly 3 provider records into the development database.
- Insert exactly 1 service per provider.
- Insert exactly 3 future time slots per provider.
- Ensure the seeded data can be read by the provider listing, provider slots, and booking tickets.
- Provide stable seed values so acceptance testing can refer to known provider names and slot times.

# Interface Contract (Inputs/Outputs/Data Shapes)

- Input:
  - No runtime API input.
  - One repeatable seed operation through the project's existing seeding mechanism.
- Data to create:
  - `providers`
    - `id`: UUID
    - `name`: string
    - `category`: string
    - `rating`: numeric string or decimal-compatible value
    - `starting_price`: integer or decimal-compatible value
    - `bio`: string
  - `services`
    - `id`: UUID
    - `provider_id`: UUID
    - `name`: string
    - `description`: string
  - `slots`
    - `id`: UUID
    - `provider_id`: UUID
    - `service_id`: UUID
    - `start_time`: ISO 8601 timestamp
    - `status`: `open`
- Output:
  - Seed operation completes without duplicate records on repeated local runs.
  - The 3 providers are queryable through the application's existing database connection.

# Acceptance Criteria (Testable Conditions)

- Given an empty or reset local database, when the seed operation runs, then exactly 3 provider records are created.
- Given the seed operation has run, when provider data is queried, then each provider has exactly 1 service attached.
- Given the seed operation has run, when slot data is queried, then each provider has exactly 3 future slots with status `open`.
- Given the seed operation runs a second time in the same local environment, when the seed completes, then it does not create duplicate providers or duplicate slots.
- Given Slice 1 API tickets are implemented, when the providers list and provider slot endpoints are called, then they can return the seeded data without requiring any manual database edits.

# Constraints (Rules to Follow)

- Use the existing project database connection and project config.
- Use UUIDs for seeded IDs.
- Use the project's existing seeding or migration pattern rather than inventing a new standalone script style.
- Seed times must be in the future relative to the local environment so the booking flow remains testable.
- Do not assume provider self-registration exists yet.

# Anti-Scope (What NOT to Build)

- No provider registration UI or API.
- No provider profile editing.
- No search indexing.
- No payment data.
- No booking creation logic.
- No notifications.
