# CLAUDE.md

<!-- Keep this file short. It loads into every session. Put detail in docs/ and link to it. -->

## Project
**TenOrNot**: Pokémon card pre-grader that measures centering from phone photos and estimates PSA grade potential, for me and my collector friends before we pay to submit.
Full product context: `docs/prd.md`. Current status and next step: `docs/state.md`.

## Commands
```bash
# (expected, verify once scaffolded)
# Backend:  cd backend && uv run pytest | uv run ruff check . | uv run fastapi dev
# Frontend: cd frontend && npm test | npm run lint | npm run dev
```

## Stack
Vue 3 + TypeScript (Vite) on Cloudflare Pages; Python FastAPI + OpenCV on Google Cloud Run; Firebase Auth. No database in v1. Why: `docs/adr/0002-vue-fastapi-cloud-run-firebase.md`.

## Conventions
<!-- Top 5 or so rules Claude would otherwise get wrong. Delete what doesn't apply. -->
- Layout: `frontend/` (Vue) and `backend/` (FastAPI) in one repo.
- Never commit secrets. Allowlist and Firebase config come from env vars; local values in `backend/.env` and `frontend/.env.local`, both gitignored.
- Photos are processed in memory and never written to disk, logs, or error reports.
- Centering math and max-grade logic live in a pure module (no web/framework code) with unit tests from known card measurements.
- PSA grade thresholds live in one data table so other graders can be added without touching the math.
- Naming: language-standard (Python PEP 8 via ruff; Vue `PascalCase.vue` components, `useXxx` composables, camelCase TS). API JSON is camelCase via a Pydantic alias generator. Domain terms: `side` = `front`|`back`, `axis` = `lr`|`tb`, ratios always larger-first (`55/45`), `maxGrade` = highest grade centering allows.
- Errors: an unmeasurable photo is a result, not an error: return 200 with a reason code (`CARD_NOT_FOUND`, `TOO_MUCH_GLARE`, `TOO_ANGLED`, ...) the UI turns into retake advice. 401 not signed in, 403 not on allowlist, 413 photo too large, 422 missing side. Unexpected exceptions are caught in one handler and return 500 with a generic message. Every non-200 body is `{ "code", "message" }`. The frontend handles errors in one API client, not per component.

## Where things live
| Need | Read |
|------|------|
| What we're building and why | `docs/prd.md` |
| How the system fits together | `docs/architecture.md` |
| Why a past decision was made | `docs/adr/` (index in `docs/adr/README.md`) |
| How to test | `docs/testing.md` |
| Non-negotiable engineering rules | `.specify/memory/constitution.md` |
| Feature specs, plans, tasks | `specs/NNN-feature-name/` |

Read these when the task needs them, not up front.

## Workflow

This project uses **Spec Kit for design** and **Superpowers for implementation**.

**1. Pick the track by size of change**
- **Feature** (new behavior, touches several files, worth remembering why): full Spec Kit track below.
- **Small change** (bug fix, tweak, refactor): skip Spec Kit. Use Superpowers directly (systematic-debugging for bugs, test-driven-development for everything else).
- **Spike / experiment**: Superpowers brainstorming, throwaway branch, no spec. If it survives, promote it to a feature.

**2. Feature track: design (Spec Kit owns this)**
1. `/speckit-specify` : what and why, no tech choices
2. `/speckit-clarify` : resolve ambiguity before planning
3. `/speckit-plan` : technical approach
4. `/speckit-tasks` : ordered task list
5. `/speckit-analyze` : consistency check across spec, plan, tasks

During these steps Spec Kit is the source of truth. Do not run Superpowers brainstorming or writing-plans on top of a Spec Kit feature; that creates a second, competing plan.

**3. Feature track: implementation (Superpowers owns this)**
Do NOT use `/speckit-implement`. Instead, for `specs/NNN-*/tasks.md`:
1. using-git-worktrees : isolated branch/worktree for the feature
2. subagent-driven-development : one fresh subagent per task from tasks.md, test-first (red, green, refactor), spec-compliance review then code-quality review
3. requesting-code-review : before merge
4. finishing-a-development-branch : merge or PR

If implementation reveals the spec was wrong, stop and update spec.md/plan.md first, then continue.

**4. Before ending a session**
- Update `docs/state.md` (what changed, what's next, any blockers).
- Made a real architectural decision (library, data store, pattern, trade-off)? Add an ADR in `docs/adr/`.
- Changed how components connect? Update `docs/architecture.md`.
