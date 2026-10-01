# Project State

<!-- Session-to-session memory. Claude updates this at the end of each working session. Keep it short: replace old content instead of appending forever. -->

**Last updated:** 2026-10-01

## Current Focus
Spec for capability 1 (`specs/001-capture-centering/spec.md`) written and clarified; ready for planning.

## Recently Done
- PSA centering thresholds verified from psacard.com and recorded in the 001 spec (PSA 10 through 1.5; worse than 90/10 = max PSA 1)
- Drafted `specs/001-capture-centering/spec.md` + quality checklist (3 user stories: bordered max grade, retake advice, full-art); clarified: full-art measured against printed frame or 'not measurable', no manual edge adjustment, built local-only until capability 2 adds the allowlist
- Constitution v1.0.1: principle IX clarified to apply to deployed endpoints
- Constitution v1.0.0 (`.specify/memory/constitution.md`): template principles I-V kept, product principles VI-XI added (honest estimates, no photo storage, measure before model, allowlist, measured accuracy, phone-first); technical constraints and workflow filled in
- Repo created from project-template, public at https://github.com/jkhaynes/ten-or-not
- Testing strategy (`docs/testing.md`), PRD (`docs/prd.md`), ADR 0002 (stack), CLAUDE.md, README, architecture sketch

## Next Up
1. Optional `/speckit-clarify` pass on 001, then `/speckit-plan`

## Blockers / Open Questions
- Price API for per-PSA-grade prices (v2, capability 7)
- Centering on full-art cards is a known technical risk, to be worked out in the capability 1 spec

## Notes for Next Session
- `.specify/scripts/python/resolve_template.py` crashes on Windows consoles (cp1252 can't print the arrow character); run with `PYTHONIOENCODING=utf-8`.
