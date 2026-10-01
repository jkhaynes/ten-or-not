# Project State

<!-- Session-to-session memory. Claude updates this at the end of each working session. Keep it short: replace old content instead of appending forever. -->

**Last updated:** 2026-10-01

## Current Focus
Constitution ratified (v1.0.0); next is the first feature spec.

## Recently Done
- Constitution v1.0.0 (`.specify/memory/constitution.md`): template principles I-V kept, product principles VI-XI added (honest estimates, no photo storage, measure before model, allowlist, measured accuracy, phone-first); technical constraints and workflow filled in
- Repo created from project-template, public at https://github.com/jkhaynes/ten-or-not
- Testing strategy (`docs/testing.md`), PRD (`docs/prd.md`), ADR 0002 (stack), CLAUDE.md, README, architecture sketch

## Next Up
1. `/speckit-specify` for capability 1: capture and centering

## Blockers / Open Questions
- Price API for per-PSA-grade prices (v2, capability 7)
- Centering on full-art cards is a known technical risk, to be worked out in the capability 1 spec

## Notes for Next Session
- `.specify/scripts/python/resolve_template.py` crashes on Windows consoles (cp1252 can't print the arrow character); run with `PYTHONIOENCODING=utf-8`.
