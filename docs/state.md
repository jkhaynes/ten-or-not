# Project State

<!-- Session-to-session memory. Claude updates this at the end of each working session. Keep it short: replace old content instead of appending forever. -->

**Last updated:** 2026-10-01

## Current Focus
Project setup complete; constitution next.

## Recently Done
- Repo created from project-template (dry run, local only)
- PRD drafted (`docs/prd.md`): 7 capabilities across v1/v2
- Stack chosen: ADR 0002 (Vue + FastAPI/OpenCV on Cloud Run, Firebase Auth)
- CLAUDE.md, README, architecture sketch filled in

## Next Up
1. `/speckit-constitution` with the input below
2. `/speckit-specify` for capability 1: capture and centering

## Blockers / Open Questions
- Price API for per-PSA-grade prices (v2, capability 7)
- Centering on full-art cards is a known technical risk, to be worked out in the capability 1 spec

## Notes for Next Session
Constitution input (pass to `/speckit-constitution`):
1. Honest estimates: never show more certainty than the evidence supports; centering-only results say "max grade possible", never a predicted grade.
2. Photos are never stored: processed in memory, never written to disk, logs, or error reports.
3. Measure before you model: anything measurable deterministically (centering) is computed and unit-tested, not left to AI; AI only for what can't be measured.
4. Allowlist on every request: no endpoint works without a verified token from an allowlisted email.
5. Accuracy is measured, not claimed: pipeline or threshold changes are checked against the labeled slab photos once that set exists.
6. Phone-first: every feature must work in a mobile browser on cellular data.
