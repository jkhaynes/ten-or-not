# Testing Strategy

<!-- The constitution says tests come first. This file says what kind of tests, where they go, and how to run them. Delete sections that don't apply. -->

## Run
```bash
# Backend all:        cd backend && uv run pytest
# Backend unit only:  cd backend && uv run pytest tests/unit
# With coverage:      cd backend && uv run pytest --cov
# Frontend:           cd frontend && npm test
# E2E:                cd frontend && npx playwright test
# Accuracy check:     cd backend && uv run pytest tests/accuracy   (not part of the default run)
```

## Levels
| Level | What it covers | Location | Framework |
|-------|----------------|----------|-----------|
| Unit | Centering math, max-grade lookup, reason codes; Vue composables and components | `backend/tests/unit`, `frontend/tests/unit` | pytest, Vitest |
| Pipeline | Full photo → result pipeline on real card photos with known measurements | `backend/tests/pipeline` | pytest |
| Integration | FastAPI endpoints end to end: auth, allowlist, error format, upload limits. Firebase token check faked | `backend/tests/integration` | pytest + FastAPI TestClient |
| End-to-end | Critical journeys only (sign in → two photos → result; retake advice), phone-sized viewport | `frontend/tests/e2e` | Playwright (mobile emulation) |
| Accuracy | Slab photos with known PSA grades: the real grade never beats the predicted max | `backend/tests/accuracy` | pytest, run on demand |

## Rules
- Each acceptance scenario in a feature's spec.md maps to at least one test.
- Tests describe behavior, not implementation (name them after the scenario).
- No mocking what you own at the integration level; fake only external services.
- External APIs are never called from tests. Use recorded fixtures or fakes.
- A bug fix starts with a failing test that reproduces the bug.
- Centering math is tested first with synthetic card images: generated borders with exact known widths, so expected ratios are exact.
- Tests never call real Firebase; tokens are faked at the verification boundary.
- Pipeline or threshold changes run the accuracy check before merge (constitution principle 5).

## Test Data
- **Synthetic:** generated in code by test helpers; nothing stored.
- **Pipeline set:** a small labeled set of the builder's own card photos with hand-measured centering, committed in the repo (Git LFS if it grows).
- **Slab set:** photos of graded slabs with their PSA grade, kept outside the repo in private storage and pulled by a script; accuracy tests skip when it's absent. Storage location is decided in capability 4's spec.
