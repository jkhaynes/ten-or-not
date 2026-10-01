# Project Template: Spec Kit + Superpowers

Starter repo for new projects built with Claude Code. **Spec Kit** handles design (spec, plan, tasks) and **Superpowers** handles implementation (worktrees, TDD, subagent execution, review).

> Replace this README with the real project README once the project has a name and a purpose. The workflow details live in `CLAUDE.md`, so nothing is lost.

## What's in here

```
CLAUDE.md                     Agent instructions + workflow (short, points to docs)
AGENTS.md                     Pointer for non-Claude agents (Copilot, Codex, Cursor)
docs/
  prd.md                      Product-level requirements, goals, NON-goals
  architecture.md             Current system shape across all features
  testing.md                  Test levels, locations, rules, commands
  state.md                    Session-to-session status and next steps
  adr/                        One file per architectural decision + index
.specify/                     Spec Kit (templates, Python scripts, constitution)
  memory/constitution.md      Pre-filled starter: TDD, Superpowers owns implementation
.claude/
  settings.json               Enables Superpowers, allows Spec Kit scripts
  skills/speckit-*            Spec Kit skills (/speckit-specify, /speckit-plan, ...)
scripts/init-project.(ps1|sh) One-time placeholder fill + Superpowers install
specs/                        Created by /speckit-specify, one folder per feature
```

## Prerequisites

- [Claude Code](https://code.claude.com)
- Python 3, callable as `python3` (Spec Kit's skills use it)
- [uv](https://docs.astral.sh/uv/) and the Spec Kit CLI (only needed for upgrades):
  `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`

## Starting a new project

1. On GitHub: **Use this template** > **Create a new repository**, then clone it.
2. Run the init script from the repo root:
   ```powershell
   ./scripts/init-project.ps1 -Name "MyProject"
   ```
   ```bash
   ./scripts/init-project.sh "MyProject"
   ```
   This fills `[PROJECT_NAME]` and date placeholders and installs Superpowers at user scope.
3. Write `docs/prd.md` yourself (or with Claude in chat). Non-goals matter most.
4. In Claude Code: `/speckit-constitution` to tailor the rules to this project.
5. Fill in **Commands** and **Stack** in `CLAUDE.md` once they exist.
6. First feature: `/speckit-specify`.

## Which track?

| Situation | Track |
|-----------|-------|
| New behavior, several files, worth remembering why | Spec Kit design, then Superpowers implementation |
| Bug fix, refactor, small tweak | Superpowers only (TDD or systematic-debugging) |
| Spike or experiment | Superpowers brainstorming on a throwaway branch |
| Existing repo without this setup | Copy `docs/`, `CLAUDE.md`, `AGENTS.md`, then `specify init --here --integration claude --script py` |

Full step-by-step is in `CLAUDE.md` under **Workflow**.

## Notes and gotchas

- **Don't use `/speckit-implement`.** Implementation goes through Superpowers (see constitution principle III). The skill is left installed because Spec Kit manages its own files; deleting it would come back on upgrade.
- **Plan mode:** if Claude Code switches into plan mode during Spec Kit or Superpowers planning steps, exit it. Both tools write their own plan files and plan mode fights them.
- **Superpowers install:** `.claude/settings.json` enables it for the project, but project-scoped plugins have been flaky, which is why the init script also installs it at user scope. If skills don't show up, run `/plugin install superpowers@claude-plugins-official` inside Claude Code.
- **Upgrading Spec Kit:** `specify self upgrade`, then `specify integration upgrade` from the repo root. Check `git diff` afterward, especially `.specify/memory/constitution.md`.
- **Optional bridge extension:** Spec Kit's catalog has a community "Superpowers Implementation Bridge" extension that formalizes the handoff. This template does the same thing through the constitution and CLAUDE.md, with no extra dependency.

Scaffolded with Spec Kit 1.0.14.dev0.
