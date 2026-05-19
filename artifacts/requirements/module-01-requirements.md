# SkillSwap Requirements Extraction

Chosen structure: categorized matrix by stakeholder and requirement type.

## User - Functional

| ID | Requirement | Type | Stakeholder | Source | Confidence |
|---|---|---|---|---|---|
| U-F1 | Users can browse providers by category. | Functional | User | Paragraph 1, explicit | High |
| U-F2 | Users can view provider profiles. | Functional | User | Paragraph 1, explicit | High |
| U-F3 | Provider profiles display ratings. | Functional | User | Paragraph 1, explicit | High |
| U-F4 | Users can search for providers or services. | Functional | User | Paragraph 1, explicit | High |
| U-F5 | Users can book available time slots. | Functional | User | Paragraph 1, explicit | High |
| U-F6 | Users can pay for sessions through the platform. | Functional | User | Paragraph 1, explicit | High |
| U-F7 | Users receive confirmation emails after successful booking. | Functional | User | Paragraph 1, explicit | High |
| U-F8 | Users can cancel bookings. | Functional | User | Paragraph 1, explicit | High |

## User - Constraint / Quality Attribute

| ID | Requirement | Type | Stakeholder | Source | Confidence |
|---|---|---|---|---|---|
| U-Q1 | Search should feel instant to end users. | Quality attribute | User | Paragraph 1, explicit | High |
| U-C1 | Cancellation behavior must apply the provider's cancellation policy. | Constraint | User | Paragraph 1, explicit | High |
| U-C2 | Booking flow must prevent time-slot conflicts and double-booking. | Constraint | User | Product constraints, explicit | High |

## Provider - Functional

| ID | Requirement | Type | Stakeholder | Source | Confidence |
|---|---|---|---|---|---|
| P-F1 | Providers can publish services on the marketplace. | Functional | Provider | Product summary, explicit | High |
| P-F2 | Providers can set their own availability. | Functional | Provider | Paragraph 2, explicit | High |
| P-F3 | Providers can set their own pricing. | Functional | Provider | Paragraph 2, explicit | High |
| P-F4 | Providers can set their own service descriptions. | Functional | Provider | Paragraph 2, explicit | High |
| P-F5 | Providers have a dashboard showing bookings, earnings, and reviews. | Functional | Provider | Paragraph 2, explicit | High |
| P-F6 | Providers can flag no-show users. | Functional | Provider | Paragraph 2, explicit | High |

## Provider - Constraint / Quality Attribute

| ID | Requirement | Type | Stakeholder | Source | Confidence |
|---|---|---|---|---|---|
| P-C1 | Provider pricing autonomy must still operate within the platform commission model. | Constraint | Provider | Paragraph 2 plus product constraints, implicit | Medium |
| P-C2 | Payout logic must remain consistent as the platform grows. | Constraint | Provider | Product constraints, explicit | High |

## Platform / Ops - Functional

| ID | Requirement | Type | Stakeholder | Source | Confidence |
|---|---|---|---|---|---|
| O-F1 | The platform sends booking confirmation emails. | Functional | Platform/Ops | Paragraph 1, explicit | High |
| O-F2 | The platform applies each provider's cancellation policy during cancellation handling. | Functional | Platform/Ops | Paragraph 1, explicit | High |
| O-F3 | The platform takes a 15% commission on bookings. | Functional | Platform/Ops | Paragraph 2, explicit | High |
| O-F4 | Admin or ops staff vet new providers before they go live. | Functional | Platform/Ops | Paragraph 2, explicit | High |
| O-F5 | Admin staff approve providers. | Functional | Platform/Ops | Paragraph 3, explicit | High |
| O-F6 | Admin or ops staff handle escalated disputes. | Functional | Platform/Ops | Paragraph 3, explicit | High |
| O-F7 | The platform provides analytics coverage across the product. | Functional | Platform/Ops | Paragraph 3, explicit | High |

## Platform / Ops - Constraint / Quality Attribute

| ID | Requirement | Type | Stakeholder | Source | Confidence |
|---|---|---|---|---|---|
| O-Q1 | The system must handle at least a few thousand users. | Quality attribute | Platform/Ops | Paragraph 3, explicit | Medium |
| O-C1 | Expansion from one city to five cities must be possible within 6 months without a full rebuild. | Constraint | Platform/Ops | Paragraph 3 plus product constraints, explicit | High |
| O-C2 | Search responsiveness must remain strong under target load. | Quality attribute | Platform/Ops | Product constraints plus Paragraph 1, explicit | High |
| O-C3 | Commission and payout logic must remain consistent during city expansion. | Constraint | Platform/Ops | Product constraints, explicit | High |
| O-C4 | Cancellation behavior must be explicit and testable. | Constraint | Platform/Ops | Product constraints, explicit | High |
| O-C5 | Time-slot conflict prevention must be enforced at the system level, not just in the UI. | Constraint | Platform/Ops | Product constraints, implicit | Medium |
| O-C6 | Analytics coverage should support tracking key user, provider, and ops actions. | Quality attribute | Platform/Ops | Paragraph 3, explicit | Medium |

## Ambiguities And Open Questions

1. How is a provider cancellation policy represented: free text, structured refund rules, or platform-defined templates?
2. What does "search should feel instant" mean in measurable terms: target latency, percentile, and expected concurrent load?
3. Does the 15% commission apply to all categories, cities, and provider tiers, or are exceptions expected?
4. Who can create or manage service categories: product admins only, or can providers propose new categories?
5. What is the payout schedule and mechanism for the provider's remaining 85% after commission?
6. Can one account act as both a learner and a provider, or are those separate roles with separate onboarding?
7. What exact conflict rules define double-booking prevention for providers operating across cities or time zones?
8. What does "analytics on everything" include: page views, searches, bookings, cancellations, payouts, disputes, and provider vetting actions?

## PM Questions

1. Should we model cancellation policy as a structured rules engine now, or is a simpler text-plus-refund-status approach acceptable for the first release?
2. What measurable performance target should "search feels instant" map to, and under what load should that target hold?
3. When the product expands to five cities, are city rules limited to geography, or do we also need city-specific pricing, commission, tax, or availability behavior?
