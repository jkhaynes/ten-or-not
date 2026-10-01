# TenOrNot Constitution

## Core Principles

### I. Spec Before Code
Every feature starts as a spec in `specs/NNN-feature-name/` (spec.md, plan.md, tasks.md) created
through Spec Kit. Small changes (bug fixes, refactors, tweaks) may skip the spec, but anything that
adds user-visible behavior may not. When implementation shows the spec is wrong, the spec is
updated first, then the code.

### II. Test-First (NON-NEGOTIABLE)
Tests are written before implementation and must fail before any production code is written (red,
green, refactor). Code written before its test is deleted and rewritten test-first. See
`docs/testing.md` for what to test at which level.

### III. Superpowers Owns Implementation
Implementation of any Spec Kit task list MUST follow the Superpowers workflow: git worktree,
test-driven development, subagent-driven execution with spec-compliance review then code-quality
review, code review, finish branch. `/speckit-implement` is not used in this project.

### IV. Simplicity
Build the smallest thing that satisfies the spec. No speculative abstractions, no features outside
the current spec. Added complexity must be justified in plan.md or an ADR.

### V. Decisions Are Recorded
Architectural decisions (libraries, data stores, patterns, notable trade-offs) are captured as ADRs
in `docs/adr/`. `docs/architecture.md` reflects the current system, and `docs/state.md` is updated
at the end of each working session.

### VI. Honest Estimates
The app MUST NOT show more certainty than the evidence supports. A centering-only result is
labeled "max grade possible" (`maxGrade`) and MUST NOT be presented as a predicted grade. When a
photo cannot be measured reliably, the app returns a reason code and retake advice instead of a
number.
Rationale: users decide whether to pay for grading based on this output; false confidence costs
them money.

### VII. Photos Are Never Stored
Photos are processed in memory only. They MUST NOT be written to disk, databases, logs, error
reports, or analytics, on either backend or frontend. Tests and reviews check that no code path
persists image bytes.
Rationale: no storage means no privacy liability and nothing to secure or delete.

### VIII. Measure Before You Model
Anything that can be measured deterministically (centering ratios, max-grade lookup) is computed in
a pure, framework-free module and unit-tested against known card measurements. AI/ML is used only
for what cannot be measured this way, and each such use MUST be justified in the feature's plan.md.
Grade thresholds live in one data table, not in the math.
Rationale: deterministic results are reproducible, testable, and explainable to the user.

### IX. Allowlist on Every Request
No API endpoint (other than an unauthenticated health check) works without a verified Firebase ID
token whose email is on the allowlist. Missing or invalid token returns 401; valid token not on the
allowlist returns 403. The allowlist comes from configuration, never from source control.
Rationale: this is a private tool for a small group; every open endpoint is cost and abuse risk.

### X. Accuracy Is Measured, Not Claimed
Any change to the measurement pipeline or grade thresholds MUST be checked against the labeled
slab-photo set once that set exists, and the before/after results recorded in the PR or plan.
Until the set exists, such changes are verified against unit-test fixtures from known card
measurements, and accuracy claims are not made in the UI or docs.
Rationale: "it looks right" is not evidence; regressions in accuracy are invisible without a
reference set.

### XI. Phone-First
Every user-facing feature MUST work in a current mobile browser (iOS Safari, Android Chrome) on
cellular data. Uploads are sized for mobile networks (client-side downscale before upload), and
layouts are designed at phone width first.
Rationale: cards are photographed with a phone, at a table or a card show, not at a desk.

## Technical Constraints

- Stack: Vue 3 + TypeScript (Vite) on Cloudflare Pages; Python FastAPI + OpenCV on Google Cloud
  Run; Firebase Auth. No database in v1 (see `docs/adr/0002-vue-fastapi-cloud-run-firebase.md`).
- Secrets never live in source control. Allowlist and Firebase config come from env vars; local
  values live in gitignored `backend/.env` and `frontend/.env.local`.
- API JSON is camelCase; every non-200 body is `{ "code", "message" }`. An unmeasurable photo is a
  200 result with a reason code, not an error.
- Hosting stays within free or near-free tiers for a small group of users.

## Development Workflow

- One feature per branch/worktree; `main` stays releasable.
- Every change passes build, tests and lint (ruff for backend, ESLint for frontend) before merge.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, ...).

## Governance

This constitution supersedes other practice docs when they conflict. Amendments are made through
`/speckit-constitution`, with the version bumped (MAJOR for removed or redefined principles, MINOR
for added ones, PATCH for wording) and a short note of what changed. Every plan.md includes a
constitution check, and code review verifies compliance; deviations must be justified in plan.md or
an ADR. Day-to-day guidance lives in `CLAUDE.md`.

**Version**: 1.0.0 | **Ratified**: 2026-10-01 | **Last Amended**: 2026-10-01
