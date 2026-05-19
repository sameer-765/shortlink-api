# Module 07 Updated Plan

## Preserved

- Ticket 1: Seed provider profiles and test time slots.
- Ticket 2: `GET /api/providers` list available providers.
- Ticket 3: `GET /api/providers/:id/slots` return provider details and open slots.
- Module 06 provider availability contract: `provider`, `slots[].id`, `slots[].start_time`, and `slots[].status` remain unchanged.

These remain valuable because company accounts do not change the basic provider discovery or availability shape.

## Modified

- Ticket 1: Seed provider profiles and test time slots.
  - Add one seeded Meridian corporate learner with `company_name = "Meridian Corp"` and `can_book_for_others = true`.
  - Keep provider and slot seed data unchanged.

- Ticket 4: `POST /api/bookings` create and persist booking.
  - Add optional request fields `booked_for_name` and `booked_for_email`.
  - Require both booked-for fields when the current authenticated user has `can_book_for_others = true` and chooses company booking mode.
  - Reject booked-for fields for users who are not allowed to book for others.
  - Include booked-for fields in the booking confirmation response.
  - Preserve atomic slot booking behavior and existing `open -> booked` transition.

- Ticket 5: Learner signup/login with session handling.
  - Include `company_name` and `can_book_for_others` in the learner/session payload.
  - Do not introduce organizations, role hierarchies, or company admins in the six-day bridge.

- Ticket 6: Search/filter providers and My Bookings view.
  - Keep basic provider search/filter only if time allows.
  - Prioritize `My Bookings` showing `booked_for_name` and `booked_for_email` for company bookings.
  - Keep ownership tied to the booking user for this bridge.

- Module 06 interface contracts.
  - Keep provider availability contract unchanged.
  - Add a new booking bridge contract that defines booked-for fields, permission rule, response shape, and temporary billing assumption.

## Cut

- Advanced search and ranking.
  - Safe to cut because the demo can use seeded providers and simple browsing without breaking the company booking story.

- Provider dashboard updates.
  - Safe to cut because the demo can prove company booking from the learner side with confirmation and `My Bookings`.

- Real organization model.
  - Safe to cut from six-day scope because the Meridian demo only needs one user booking for another person, not multiple admins, departments, or delegated permissions.

- Company-level billing or invoicing.
  - Safe to cut because the bridge explicitly keeps billing attached to the booking user for now.

- Notifications.
  - Safe to cut because on-screen confirmation is enough to prove the flow in the demo.

## Added

- Add company-account bridge fields to learner model.
  - Scope: add `company_name` and `can_book_for_others` to the learner/user profile and expose them in the session payload.
  - Estimate: S.

- Add company booking fields to booking creation.
  - Scope: extend booking creation to store `booked_for_name` and `booked_for_email` when allowed by the current learner's bridge permission.
  - Estimate: M.

- Add company booking UI state to booking form.
  - Scope: show a booked-for name/email section for eligible corporate learners and include those values in the booking request.
  - Estimate: M.

- Add company booking confirmation and `My Bookings` display.
  - Scope: show who the booking is for on the confirmation screen and in the learner's bookings list.
  - Estimate: S.

- Add bridge contract and rollback note.
  - Scope: document that this is a temporary Meridian bridge, not the final company-account architecture, and name the later replacement path.
  - Estimate: S.

## Six-Day Demo Path

1. Seed Meridian corporate learner plus providers and slots.
2. Log in or use a seeded Meridian session.
3. Browse providers.
4. Open a provider and select an open slot.
5. Book on behalf of an employee with name and email.
6. Show confirmation with provider, time, booking user, and booked-for person.
7. Show `My Bookings` with the company booking visible.

## Deferred Proper Architecture

After the demo, replace the bridge with a real organization model:

- `organizations`
- organization membership table
- company roles and permissions
- booked-by vs booked-for user references
- company billing and invoice ownership
- provider/admin reporting updates
