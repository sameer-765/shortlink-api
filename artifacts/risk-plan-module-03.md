# Module 03 Risk-First Plan - SkillSwap

Chosen risk framework: Integration, Novelty, Dependency, Scale.

Chosen first-build strategy: Spike first for the highest-risk external integration.

## 1. Node Risk Annotations

| Work Item | Risk Score (1-5) | Risk Type(s) | Why |
|---|---:|---|---|
| User Authentication | 2 | Dependency | Low implementation uncertainty, but it blocks booking, reviews, and admin access. |
| Listings Data Model | 3 | Dependency, Scale | It is foundational for nearly every workflow and must support categories, pricing, bookings, and future multi-city expansion. |
| Provider Onboarding | 3 | Novelty, Dependency | The pending-to-approved workflow and vetting states are easy to mis-specify even if the UI is simple. |
| Availability Management | 4 | Novelty, Dependency | Preventing double-booking is a real concurrency problem and it sits directly under booking. |
| Search and Browse | 3 | Scale | Search is conceptually familiar, but the "feel instant" requirement becomes risky under larger provider counts and multiple cities. |
| Booking Flow | 4 | Novelty, Dependency | It coordinates user identity, provider state, slot selection, and downstream payment and cancellation behavior. |
| Payment Processing | 5 | Integration, Novelty, Dependency | Stripe integration, commission handling, refunds, and webhook behavior are major unknowns and a failure here invalidates the core product. |
| Cancellation Flow | 4 | Integration, Novelty | Refund behavior depends on payment integration and the product still has policy complexity from provider rules versus platform rules. |
| Notification System | 2 | Integration | Email delivery is an external dependency, but the basic pattern is familiar and non-critical for the first successful booking. |
| Review and No-Show System | 2 | Dependency | It depends on completed bookings, but the technical pattern is mostly standard CRUD plus workflow checks. |
| Admin and Ops Dashboard | 3 | Dependency, Novelty | It integrates booking, payment, provider, and dispute data, but much of the risk can be reduced by splitting minimal and full admin surfaces. |
| Analytics and Reporting | 3 | Scale, Dependency | The implementation can start simply, but the scope is broad and depends on events from nearly every subsystem. |

## 2. Highest-Risk Items

1. Payment Processing - Risk 5 - Integration, Novelty, Dependency
2. Availability Management - Risk 4 - Novelty, Dependency
3. Booking Flow - Risk 4 - Novelty, Dependency

Cancellation Flow is also high risk at 4 because it couples policy decisions to refund behavior, but it can start once payment assumptions are clarified.

## 3. Risk-First Ordered Build Plan

1. Listings Data Model - Risk 3 - Dependency, Scale  
   Build this first because it is the shared foundation for providers, services, categories, bookings, and future city-aware behavior. It is not the highest uncertainty item, but it must exist before nearly every high-risk feature can be exercised.

2. User Authentication - Risk 2 - Dependency  
   Build this immediately after the core data model because bookings, reviews, and admin access need user identity. It is low-risk but unlocks the riskiest transactional path.

3. Provider Onboarding - Risk 3 - Novelty, Dependency  
   Build the pending-state provider submission flow early so approved providers can exist in the system before booking work begins. This also validates the state model that the admin review flow depends on.

4. Payment Processing Spike - Risk 5 - Integration, Novelty, Dependency  
   Do a short Stripe spike as soon as the minimal booking prerequisites are visible in the model. This front-loads the biggest external uncertainty before the team invests deeply in downstream payment-dependent behavior.

5. Availability Management - Risk 4 - Novelty, Dependency  
   Build concurrency-safe slot management next because double-booking risk sits directly on the critical product path. If the slot model or locking strategy is wrong, later booking work will need redesign.

6. Booking Flow - Risk 4 - Novelty, Dependency  
   Build the real booking flow once identity, providers, and availability exist. This is the thinnest end-to-end path to a real transaction and it is the point where the major foundations meet.

7. Payment Processing (Real Implementation) - Risk 5 - Integration, Novelty, Dependency  
   Convert the spike knowledge into production code with error handling, test mode support, webhook handling, and commission logic. This stays early because the product is non-viable without it.

8. Cancellation Flow - Risk 4 - Integration, Novelty  
   Build cancellation and refund behavior after real payments because refund semantics need a working payment boundary. This also forces the remaining policy ambiguity into a concrete executable workflow.

9. Search and Browse - Risk 3 - Scale  
   Build search after listings and availability are real enough to query meaningfully. It is important user-facing functionality, but it is not as schedule-risky as booking and payment.

10. Notification System - Risk 2 - Integration  
    Add confirmations and cancellation notices after booking and cancellation behaviors are stable. This can start with minimal transactional emails and expand later.

11. Admin and Ops Dashboard - Risk 3 - Dependency, Novelty  
    Build the broader operational surface after the core workflows produce meaningful data. Minimal admin review capability can exist earlier, but the full dashboard is more valuable once bookings, payments, and cancellations are flowing.

12. Review and No-Show System - Risk 2 - Dependency  
    Build this after completed bookings exist because the workflow depends on real service completion states. It is useful, but it does not retire the biggest project risks.

13. Analytics and Reporting - Risk 3 - Scale, Dependency  
    Build analytics last because it depends on stable events from the rest of the system. It should be designed early, but the meaningful implementation belongs after core workflows are settled.

## 4. Why This Order Is Risk-First

- It reaches the highest-risk external dependency, payment processing, as early as the DAG allows.
- It puts concurrency risk in availability management before too much user-facing booking logic accumulates on top of it.
- It keeps low-risk but high-dependency foundation work early only when it directly unlocks a higher-risk path.
- It delays comfort work, such as fuller dashboards and secondary workflows, until the transactional spine is proven.

## 5. Notes

- The payment spike is intentionally throwaway work. Its purpose is to answer whether the Stripe flow, test credentials, and basic charge or refund mechanics behave the way the product needs.
- The minimal admin review capability from Module 02 remains a useful split, but the full Admin and Ops Dashboard should not block the first successful booking path.
- The cancellation policy decision from Module 01 still affects final refund behavior, so cancellation implementation should be validated against a product decision before production rollout.
