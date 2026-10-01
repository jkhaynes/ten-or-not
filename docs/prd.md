# TenOrNot Product Requirements

<!-- Product-level PRD: the whole thing, not one feature. Individual features get their own spec via /speckit-specify in specs/. Keep this to what stays true across features. -->

**Status:** Draft | **Last updated:** 2026-10-01

## Problem
Pokémon collectors pay to send cards to PSA without knowing whether a card can reach the grade that makes the fee worth it. Centering decides a lot of grades, but judging it by eye is unreliable, and a card that's 58/42 can never be a PSA 10 no matter how clean it looks. Collectors find out weeks later, after paying.

## Users
| User | What they need | Notes |
|------|----------------|-------|
| Me (the builder) | A fast, trustworthy read on whether a card can reach a 10 before submitting | Often away from home when evaluating cards |
| My collector friends | The same read from their own phones, with no setup | Access via allowlist only |

## Goals
- Before a PSA submission, we skip cards that can't reach the grade we'd need, and know that before paying.
- Checking a card on a phone, anywhere, takes less than a minute.
- The estimate is honest: it never claims more certainty than the evidence supports.
- The project demonstrates vision AI combined with deterministic measurement, as a working tool rather than a demo.

## Non-Goals
<!-- The most useful section for keeping AI agents from over-building. Be explicit. -->
- **No official grade.** Estimate only; not affiliated with or endorsed by PSA, and the app says so.
- **No price tracking or collection value.** Prices are used only for the submit-or-not calculation. No portfolio value, price history, or alerts.
- **No automatic card identification.** The user picks the card when prices are needed.
- **No native mobile app in v1.** Web app in the phone browser.
- **No submission or marketplace features.** No PSA submission forms, buying/selling, or listings.
- **No user profiles or social features in v1.** Sign-in exists only to restrict access to an allowlist. No profiles, saved history, sharing, or leaderboards.
- **No custom model training in v1.**
- **No other TCGs or graders in v1.** Pokémon and PSA only; designed so CGC/BGS/TAG can be added later.

## Core Capabilities
<!-- High level. Each one usually becomes one or more Spec Kit features. -->
| # | Capability | Release | Priority | Spec |
|---|------------|---------|----------|------|
| 1 | Capture and centering: photograph front and back, detect and straighten the card, measure L/R and T/B centering on both sides (bordered and full-art), report the max PSA grade possible | v1 | Must | not started |
| 2 | Allowlist sign-in: Google/GitHub sign-in limited to approved emails | v1 | Must | not started |
| 3 | Deployment: frontend on Cloudflare Pages, backend on Cloud Run, reachable from a phone anywhere; ships only once sign-in exists | v1 | Must | not started |
| 4 | Accuracy check: run slab photos with known grades and confirm the real grade never beats the predicted max | v1 | Should | not started |
| 5 | AI condition scoring: edges, corners, and surface, front and back | v2 | Must | not started |
| 6 | PSA grade odds: probability per grade (e.g. "60% PSA 10, 35% PSA 9"), never a single number | v2 | Must | not started |
| 7 | Submit or not: pick the card, look up per-grade prices, subtract grading fees, show worth it / not worth it in dollars | v2 | Should | not started |

## Success Measures
- **Accuracy (primary).** v1: on the slab check, the real PSA grade never exceeds the predicted max. v2: the real grade falls within the predicted odds for at least 8 of 10 cards. Quick check on existing slabs first, then a real test on the next raw submission.
- **Decisions.** Before a submission, we run our cards through it and skip some we'd otherwise have sent.
- **Speed.** Under a minute from opening the app to a result for two photos.
- **Portfolio.** A write-up and screen recording showing the app working on real cards; live access available by adding someone to the allowlist.

## Constraints and Assumptions
- v1 is deployed and works from a phone browser on mobile data, wherever the cards are.
- Budget is a few dollars a month. Access is restricted to an allowlist from day one.
- Both sides of the card are required; PSA grades front and back centering separately.
- Full-art cards are in scope for v1. Measuring their centering is a known technical risk, to be worked out in capability 1's spec.
- Slab photos are taken through the plastic case, so the accuracy check must tolerate glare and reflections.
- Centering limits come from PSA's published grading standards.

## Open Questions
- [ ] Which price API has per-PSA-grade prices for Pokémon, and what does it cost? (Needed for capability 7, v2.)
