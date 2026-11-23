# Analysis of Two Existing Booking Systems
**Author:** Suleyman Shafizada (m666i1) · **Research date:** 23 November 2026

**Method:** Desk review of public official product pages and help documentation, not hands-on use, interviews, performance tests or user studies. The assignment requires at least two existing products of the same kind, and a record of lessons learned.

## 1. Springshare LibCal
**Sources:**
- https://www.springshare.com/libcal
- https://www.springshare.com/academic-libraries/libcal
- https://blog.springshare.com/2025/05/managing-room-reservations-for-libraries-of-all-sizes

**Documented capabilities:** Academic library space and equipment booking, displayed availability, booking rules and limits, mediated bookings and approval workflows, and configurable restrictions for different groups.

**Takeaways for UniReserve:**
- Each resource should have explicit category and approval-required fields rather than one fixed rule for all rooms/equipment.
- Availability is linked to the chosen interval, not simply the resource's existence.
- Time restrictions and approval criteria should be documented as verifiable requirements.
- A library-grade system contains far more features than an individual coursework prototype needs; payments and multi-module scheduling are out of scope.

**Limit:** Public pages do not reveal the product's implementation, schema or transaction-isolation guarantees.

## 2. Skedda
**Sources:**
- https://www.skedda.com/platform/fully-customizable-booking-system
- https://support.skedda.com/en/articles/11774950-booking-requests-approvals
- https://support.skedda.com/en/articles/3184573-quotas-allowances

**Documented capabilities:** Booking conditions, permission roles, booking quotas and request/approval processes. Official support material distinguishes submitted requests from accepted bookings and discusses user-facing errors on policy limits.

**Takeaways for UniReserve:**
- Distinguish pending requests from confirmed capacity-blocking reservations.
- Recheck the conflict and resource policy when an administrator approves a request.
- Clearly communicate why a booking failed (wrong role, disabled resource, duration, conflict).
- Quota policies add complexity; classify advanced per-user quotas as Should instead of Must.

**Limit:** We did not examine Skedda's internal concurrency implementation or conduct user tests.

## 3. Comparison and resulting choices
| Theme | LibCal official material | Skedda official material | UniReserve design |
|---|---|---|---|
| Intended scope | Library rooms/equipment | Space bookings in multiple workplaces | One small campus resource catalogue |
| Bookability | Availability and limits | Roles, conditions and quotas | Confirmed-overlap rule with 14-day horizon |
| Approval | Mediation and workflows | Pending requests and approvals | Pending does not hold, approval rechecks conflict |
| Administration | Configurable booking settings | Rules and booking management | Simple admin inventory and approval queue |
| Deferred functionality | Payments, events, broad integrations | Complex quotas and external integrations | No payments/SSO; quota Should |

**Derived requirement references:** FR-002/003 (browse and availability), FR-004/005 (valid transaction-safe booking), FR-008 (approval), FR-010 (server role checks), FR-014 (lower-priority quotas).

**Research limitations:** No actual university stakeholder approved the derived values for duration, priority or cancellation. Those remain explicit assumptions and open questions in the SRS. Product claims are cited as evidence of design possibilities, not proof of correctness.
