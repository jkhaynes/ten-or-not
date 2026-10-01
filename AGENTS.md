# AGENTS.md

Instructions for AI coding agents other than Claude Code (Copilot, Codex, Cursor, etc.).

The canonical agent instructions for this repo live in **`CLAUDE.md`**. Read it first and follow it. The workflow, commands, conventions and doc map there apply to every agent.

Notes for non-Claude agents:
- The Superpowers skills referenced in CLAUDE.md may not be installed in your harness. If not, follow the same discipline by hand: work on a branch, write the failing test first, implement one task at a time from `specs/NNN-*/tasks.md`, and review against the spec before moving on.
- Spec Kit skills are installed for Claude Code under `.claude/skills/`. To add Spec Kit commands for another agent, run `specify integration install <agent>` (see `specify integration list`).
