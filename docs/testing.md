# Testing Strategy

<!-- The constitution says tests come first. This file says what kind of tests, where they go, and how to run them. Delete sections that don't apply. -->

## Run
```bash
# All tests:         [e.g. dotnet test]
# One project:       [e.g. dotnet test tests/Api.Tests]
# With coverage:     [e.g. dotnet test --collect:"XPlat Code Coverage"]
# Frontend:          [e.g. npm test --prefix src/web]
```

## Levels
| Level | What it covers | Location | Framework |
|-------|----------------|----------|-----------|
| Unit | Pure logic, one class/function, no I/O | `tests/*.UnitTests` | [xUnit / Jest] |
| Integration | Real DB, real HTTP pipeline, external services faked | `tests/*.IntegrationTests` | [xUnit + Testcontainers / WebApplicationFactory] |
| End-to-end | Critical user journeys only | `tests/e2e` | [Playwright] |

## Rules
- Each acceptance scenario in a feature's spec.md maps to at least one test.
- Tests describe behavior, not implementation (name them after the scenario).
- No mocking what you own at the integration level; fake only external services.
- External APIs are never called from tests. Use recorded fixtures or fakes.
- A bug fix starts with a failing test that reproduces the bug.

## Test Data
[How test data is created and cleaned up: builders, seed scripts, per-test databases.]
