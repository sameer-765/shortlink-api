# Module 04 Vertical Slices - SkillSwap

## Slice 1 - Browse and Book (Seeded Providers)

**Scope (What Is In)**  
User opens the app and sees a marketplace home page with 3 seeded provider cards showing name, category, rating, and starting price. User clicks a provider card and sees a profile page with one service, a short description, and 3 seeded time slots. User selects a slot, clicks `Book Now`, and sees a confirmation page with booking ID, provider name, service name, and booked time. The booking is stored so refreshing the confirmation page still shows the same booking details.

**Anti-Scope (What Is Explicitly Out)**  
No user authentication; booking is anonymous. No provider self-service; providers and slots come from seed data only. No payment processing; booking is free in this slice. No search or filtering. No confirmation email or SMS. No cancellation or rescheduling. No provider dashboard. No admin approval flow. No double-booking protection beyond the seeded single-user demo path. No reviews or analytics.

**Dependencies**  
None.

**Acceptance Criteria**  
1. Open the app and see 3 provider cards with name, category, rating, and price.
2. Click a provider and see a profile page with one service and 3 available time slots.
3. Select a slot and click `Book Now`.
4. See a confirmation page with booking ID, provider name, service name, and booked time.
5. Refresh the confirmation page and still see the saved booking instead of losing it.

**Estimated Complexity**  
S

## Slice 2 - Learner Accounts and Search

**Scope (What Is In)**  
Learners can sign up, log in, and log out. The marketplace home page now includes search by provider name or service title plus category filtering. A signed-in learner can make a booking and then open a `My Bookings` page to see upcoming bookings tied to their account. Existing slice-1 seeded providers remain the supply source so the user flow is still browse -> view profile -> book -> view saved booking history.

**Anti-Scope (What Is Explicitly Out)**  
No provider registration or editing tools yet. No payment checkout. No cancellation flow. No provider approval workflow. No email confirmation. No saved favorites. No advanced ranking, recommendations, or geo-based search. No password reset or social login. No reviews. No provider earnings data.

**Dependencies**  
Slice 1.

**Acceptance Criteria**  
1. Create a learner account and log in.
2. Search for a provider or service and see the list narrow to matching results.
3. Filter by category and see only providers in that category.
4. Open a provider profile, book a slot, and reach the confirmation screen.
5. Open `My Bookings` and see the new booking attached to the signed-in learner account.

**Estimated Complexity**  
M

## Slice 3 - Provider Signup, Listing, and Approval

**Scope (What Is In)**  
Providers can create an account, submit a profile, add one or more services, set pricing, and define available time slots. Newly submitted providers enter a `Pending Approval` state and do not appear in the learner marketplace until approved. A minimal admin approval screen lets an ops user review pending providers and approve them. Once approved, the provider appears in search and browse results, and learners can book that provider through the existing flow.

**Anti-Scope (What Is Explicitly Out)**  
No provider earnings dashboard yet. No payout handling. No provider editing after approval beyond basic service and slot updates. No provider-side cancellation policy rules yet. No dispute handling. No bulk imports. No provider analytics. No multi-role account switching. No public reviews. No rejection email workflow.

**Dependencies**  
Slice 1 and Slice 2.

**Acceptance Criteria**  
1. Sign up as a provider and submit a profile with a service, price, and available slots.
2. See that the provider does not appear in the learner marketplace immediately.
3. Open the admin approval screen and approve the pending provider.
4. Return to the learner marketplace and find the newly approved provider in browse or search results.
5. Book that provider successfully through the existing booking flow.

**Estimated Complexity**  
M

## Slice 4 - Paid Booking with Real Availability Protection

**Scope (What Is In)**  
The booking flow now includes real payment checkout for a session and records the platform's 15% commission on the booking. Slot availability is enforced at the system level so two learners cannot successfully pay for the same provider slot. The learner sees a paid-booking confirmation screen with payment status, provider name, service, time, and booking reference. Providers can manage their own future slots so availability shown to learners comes from real provider-managed data rather than seeded static slots.

**Anti-Scope (What Is Explicitly Out)**  
No cancellation refunds yet. No saved payment methods. No subscriptions, coupons, taxes, or invoicing. No waitlist flow when a slot is taken. No wallet or provider payout disbursement. No multi-city pricing rules. No dispute workflow. No promotional notifications. No review submission after payment.

**Dependencies**  
Slice 2 and Slice 3.

**Acceptance Criteria**  
1. Log in as an approved provider and publish at least one real future slot.
2. Log in as a learner, open that provider, and choose the slot.
3. Complete payment checkout and reach a confirmation screen showing paid status and booking details.
4. Open the same provider page in another learner session and confirm the booked slot is no longer available.
5. Attempt to book the same slot from two browser sessions at nearly the same time and observe that only one booking succeeds.

**Estimated Complexity**  
M

## Slice 5 - Booking Lifecycle: Notifications, Cancellation, and Core Dashboards

**Scope (What Is In)**  
Successful bookings send a confirmation email to the learner and provider. Learners can cancel an upcoming booking, and the system applies the provider's configured cancellation policy to determine the visible outcome such as `Full Refund`, `Partial Refund`, or `No Refund`. Providers get a basic dashboard showing upcoming bookings, completed bookings, and earnings summary for paid sessions. Admin or ops users get a basic operational view showing approved providers, bookings, payments, and cancellations so the core marketplace can be monitored end to end.

**Anti-Scope (What Is Explicitly Out)**  
No full dispute resolution workflow. No automated payout transfers to providers. No no-show reporting. No public reviews and ratings submission. No advanced analytics beyond simple operational summaries. No push notifications or SMS. No reschedule flow. No dynamic policy rule builder beyond a limited supported cancellation-policy format. No five-city expansion features.

**Dependencies**  
Slice 4.

**Acceptance Criteria**  
1. Complete a paid booking and receive a confirmation email for the learner and provider.
2. Open the provider dashboard and see the booking listed with its paid amount.
3. Cancel the booking as the learner and see the cancellation outcome explained on screen.
4. Verify the provider dashboard and admin view both reflect the cancelled booking and updated status.
5. Check that the learner can still view the booking record and its final cancellation result in `My Bookings`.

**Estimated Complexity**  
M
