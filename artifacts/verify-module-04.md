# Module 04 Verify - Slice 1 Clickthrough

## Can I test the first slice without reading code?

Yes.

Clickthrough:

1. I open the browser and land on the SkillSwap home page.
2. I see 3 provider cards, each with a name, category, rating, and starting price.
3. I click one provider card.
4. I see that provider's profile page with one service, a short description, and 3 available time slots.
5. I pick one time slot and click `Book Now`.
6. I see a confirmation page with a booking ID, the provider name, the service name, and the booked time.
7. I refresh the page and still see the same confirmation details, so the booking feels like a real completed action instead of a temporary UI demo.

This walkthrough stays fully in the interface. It does not require checking logs, code, API responses, or the database.

## One Product Learning

The one thing this slice teaches is whether the core browse-to-book flow is understandable and convincing to a learner before we invest in payments, provider tooling, search, or notifications.
