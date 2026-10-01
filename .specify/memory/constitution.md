# TenOrNot Constitution
<!-- Starter constitution from the project template. Run /speckit-constitution to tailor it to this project; it will fill the bracketed placeholders and bump the version. -->

## Core Principles

### I. Spec Before Code
Every feature starts as a spec in `specs/NNN-feature-name/` (spec.md, plan.md, tasks.md) created through Spec Kit. Small changes (bug fixes, refactors, tweaks) may skip the spec, but anything that adds user-visible behavior may not. When implementation shows the spec is wrong, the spec is updated first, then the code.

### II. Test-First (NON-NEGOTIABLE)
Tests are written before implementation and must fail before any production code is written (red, green, refactor). Code written before its test is deleted and rewritten test-first. See `docs/testing.md` for what to test at which level.

### III. Superpowers Owns Implementation
Implementation of any Spec Kit task list MUST follow the Superpowers workflow: git worktree, test-driven development, subagent-driven execution with spec-compliance review then code-quality review, code review, finish branch. `/speckit-implement` is not used in this project.

### IV. Simplicity
Build the smallest thing that satisfies the spec. No speculative abstractions, no features outside the current spec. Added complexity must be justified in plan.md or an ADR.

### V. Decisions Are Recorded
Architectural decisions (libraries, data stores, patterns, notable trade-offs) are captured as ADRs in `docs/adr/`. `docs/architecture.md` reflects the current system, and `docs/state.md` is updated at the end of each working session.

## Technical Constraints

- Stack: [LANGUAGE / FRAMEWORK / DATABASE / FRONTEND]
- Secrets never live in source control.
- [Other constraints: hosting, performance targets, supported platforms, budget]

## Development Workflow

- One feature per branch/worktree; `main` stays releasable.
- Every change passes build, tests and lint before merge.
- Commit messages: [e.g. Conventional Commits]

## Governance

This constitution supersedes other practice docs when they conflict. Amendments are made through `/speckit-constitution`, with the version bumped (MAJOR for removed or redefined principles, MINOR for added ones, PATCH for wording) and a short note of what changed.

**Version**: 0.1.0 | **Ratified**: 2026-10-01 | **Last Amended**: 2026-10-01
