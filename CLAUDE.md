# CLAUDE.md

<!-- Keep this file short. It loads into every session. Put detail in docs/ and link to it. -->

## Project
**TenOrNot**: [One sentence on what this is and who it's for.]
Full product context: `docs/prd.md`. Current status and next step: `docs/state.md`.

## Commands
```bash
# Build:   [e.g. dotnet build]
# Test:    [e.g. dotnet test]
# Run:     [e.g. dotnet run --project src/Api]
# Lint:    [e.g. dotnet format --verify-no-changes]
```

## Stack
[e.g. .NET 9 / C#, SQL Server, Angular 19. Keep to one or two lines; the why lives in docs/adr/.]

## Conventions
<!-- Top 5 or so rules Claude would otherwise get wrong. Delete what doesn't apply. -->
- [Folder layout / where new code goes]
- [Naming conventions]
- [Error handling pattern]
- [Data access pattern]
- Never commit secrets. Config goes in [appsettings.Development.json / .env], both gitignored.

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
