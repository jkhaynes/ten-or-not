# Project State

<!-- Session-to-session memory. Claude updates this at the end of each working session. Keep it short: replace old content instead of appending forever. -->

**Last updated:** 2026-10-01

## Current Focus
Tasks for 001 done (`specs/001-capture-centering/tasks.md`, 36 tasks); next is `/speckit-analyze`, then implementation.

## Recently Done
- Pipeline photo set started: Git LFS tracks `backend/tests/pipeline/photos/**/*.jpg`; confirmed tile sheets kept in `photos/evidence/` as proof of each label
- Constitution v1.0.2: VII reworded to "Photos Are Never Retained" (framework temp buffers that die with the request are allowed); dropped the spool-size workaround from 001 research/tasks, which clears analyze finding C1
- Applied analyze fixes U1 (miscut = not measurable), I1 (`expect_reason` column), I2 (card outline in preview), G1 (unreadable HEIC handled in T015)
- Generated 001 tasks.md: setup, foundational, US1 MVP (T009-T019), US2 retake (T020-T028), US3 full-art (T029-T032), polish
- Planned 001: OpenCV contour detect + warp to 20 px/mm, median gradient scan for design edges, pure grading module + PSA table, one `POST /api/centering`, preview image in response
- PSA centering thresholds verified from psacard.com and recorded in the 001 spec (PSA 10 through 1.5; worse than 90/10 = max PSA 1)
- Drafted `specs/001-capture-centering/spec.md` + quality checklist (3 user stories: bordered max grade, retake advice, full-art); clarified: full-art measured against printed frame or 'not measurable', no manual edge adjustment, built local-only until capability 2 adds the allowlist
- Constitution v1.0.1: principle IX clarified to apply to deployed endpoints
- Constitution v1.0.0 (`.specify/memory/constitution.md`): template principles I-V kept, product principles VI-XI added (honest estimates, no photo storage, measure before model, allowlist, measured accuracy, phone-first); technical constraints and workflow filled in
- Repo created from project-template, public at https://github.com/jkhaynes/ten-or-not
- Testing strategy (`docs/testing.md`), PRD (`docs/prd.md`), ADR 0002 (stack), CLAUDE.md, README, architecture sketch

## Next Up
1. `/speckit-analyze` for 001, then implement via Superpowers (worktree + subagent-driven-development)
2. Builder: keep building the pipeline photo set in `backend/tests/pipeline/photos/` before T014. 6 cards labeled (max PSA: Pikachu 10, Pansage 10, Butterfree 8, Caterpie 9, Altaria ex 9, Zoroark-GX full art 9, M Gyarados EX full art 9). Measured cards are done; 3 bad photos are still needed: angled, blurry, glare (wrong-side, no-card, cropped, small done) (phone only, before T024). Full-art reference refined in spec FR-016 / research R5 / T029: card edge to the edge of the artwork, not the first printed line; per-card details and the "Still wanted" list live in that folder's README ("Cards in the set"). Method: each side scanned twice (second turned 180°); `scripts/measure_scan.py --pair` for most cards, `scripts/click_measure.py` when the border is too faint (silver on light green). The scanner lamp shadows whichever edge lies at the top of the glass, so top/bottom borders come from the scan where they lay at the bottom.

## Blockers / Open Questions
- Price API for per-PSA-grade prices (v2, capability 7)
- Centering on full-art cards is a known technical risk, to be worked out in the capability 1 spec

## Notes for Next Session
- `.specify/scripts/python/resolve_template.py` crashes on Windows consoles (cp1252 can't print the arrow character); run with `PYTHONIOENCODING=utf-8`.
