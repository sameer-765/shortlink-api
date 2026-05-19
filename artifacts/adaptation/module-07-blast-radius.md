# Module 07 Blast Radius Analysis

## Change 1: Company Accounts

Decision: use the minimal bridge approach for the Meridian demo. This adds company booking support without introducing a full organization model, role hierarchy, or company billing system yet.

| Artifact | Status | Impact |
|----------|--------|--------|
| User data model | In progress / planned through auth ticket | MAJOR: add `company_name` and `can_book_for_others` to the learner/user profile shape. This avoids a full Organization entity for the six-day scope but changes account data and validation. |
| Auth/JWT system | Planned in Ticket 5 | MINOR: session identity still works the same, but authenticated user payloads need to expose whether the user can book for others. No new token pattern or role system in this bridge. |
| Booking flow API | Planned in Ticket 4 | MAJOR: extend `POST /api/bookings` to accept `booked_for_name` and `booked_for_email` only when the authenticated user has `can_book_for_others = true`. Response payloads should include the booked-for fields so confirmation and later views stay consistent. |
| Booking flow UI | Not separately ticketed yet | MAJOR: booking form needs an optional company-booking section when the current user can book for others. Confirmation needs to show both booking user and booked-for person. |
| Provider dashboard | Later-slice work, not in first two slices | MINOR for six-day demo: no provider dashboard changes in scope. Later provider views will need to distinguish booked by vs booked for. |
| Search/listing | Ticket 6 and provider list ticket | NO IMPACT for company-account behavior: company booking does not change provider discovery, search filters, or provider card content for the demo. |
| Payment/billing | Explicitly out of earlier slices | BLOCKED for full company accounts: real company-level invoicing needs product and billing decisions. For the bridge, billing remains attached to the booking user and company reimbursement is outside the product. |
| Interface contracts between streams | Module 06 contracts | MAJOR: booking and future `My Bookings` contracts need booked-for fields and clear ownership rules. Provider availability contract remains unchanged. |
| Tickets: completed | Seed data / completed artifacts | MINOR: seeded users may need one corporate demo learner with `company_name = "Meridian Corp"` and `can_book_for_others = true`. Existing provider and slot seed data remains usable. |
| Tickets: in progress | Provider availability / auth streams | MAJOR for auth stream because user/session payload must include bridge company fields. MINOR for provider availability because slot data does not change. |
| Tickets: not started | Booking, search/My Bookings, later provider/admin work | MAJOR: not-started booking and learner-experience tickets should be replanned around company booking support and the six-day demo path. |

## Change 2: Compressed Timeline

Timeline compression does not change the product requirement by itself. It changes what can responsibly fit into the six-day scope.

| Ticket | Category | Reason |
|--------|----------|--------|
| Ticket 1: Seed provider profiles and test time slots | MUST SHIP | The demo needs seeded providers, slots, and at least one Meridian corporate learner account to show the company booking path. |
| Ticket 2: `GET /api/providers` list available providers | MUST SHIP | The demo needs a starting point where the learner can browse providers before booking. |
| Ticket 3: `GET /api/providers/:id/slots` return provider details and open slots | MUST SHIP | Booking depends on visible open slots and the provider profile contract from Module 06. |
| Ticket 4: `POST /api/bookings` create and persist booking | MUST SHIP | This is the core demo transaction and now needs the company-booking bridge fields. |
| Ticket 5: Learner signup/login with session handling | SHOULD SHIP | The Meridian demo is clearer with a signed-in corporate learner, but a seeded demo session can substitute if auth takes too long. |
| Ticket 6: Search/filter providers and My Bookings view | SHOULD SHIP / PARTIAL | Basic `My Bookings` helps show booked-for data after confirmation. Advanced search/filter behavior can be cut if time tightens. |
| Advanced search filters beyond basic category/query | CUT | Cutting advanced filters does not break the Meridian company-booking demo. Provider discovery can remain simple. |
| Provider dashboard updates | CUT | Providers do not need a dashboard for the six-day investor/Meridian demo. Confirmation and learner-side visibility are enough. |
| Payment integration or company invoicing | CUT | Company billing is a later proper implementation. The bridge keeps billing on the booking user's account and can demo simulated payment if needed. |
| Notifications | CUT | On-screen confirmation is enough for the demo; email or push notification does not block the core company booking story. |

## Highest-Risk Areas

- Booking contract drift: `POST /api/bookings` must clearly define when `booked_for_name` and `booked_for_email` are required.
- Auth/session assumptions: the UI must know whether the current user can book for others without inventing a second permission model.
- Future replacement cost: the bridge should be labeled as temporary so the team does not accidentally build full company-account expectations on top of it.
