# Implementation Plan: Capture and Centering

**Branch**: `001-capture-centering` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-capture-centering/spec.md`

## Summary

The phone takes or picks a front and a back photo, downscales them, and posts both to one local
FastAPI endpoint. The backend decodes them in memory and runs a deterministic OpenCV pipeline:
find the card quad, run quality checks, warp to a 20 px/mm canvas, locate the design edges with
a median of many gradient scan lines, compute larger-first ratios, then look up the max PSA
grade in a data table with borderline flags. It returns per-side results or reason codes, plus
a straightened preview with the measured edges. Full-art cards use the same scan against a
printed frame line or text-box edge, or honestly return `CENTERING_NOT_MEASURABLE`. No sign-in
and no deployment in this feature.

## Technical Context

**Language/Version**: Python 3.13 (backend); TypeScript + Vue 3 (frontend)

**Primary Dependencies**: FastAPI, opencv-python-headless, numpy; Vue 3, Vite

**Storage**: None. Photos are in memory only (research R10 covers the Starlette disk-spool gotcha).

**Testing**: pytest (unit, pipeline, integration); Vitest + @vue/test-utils; Playwright mobile
emulation

**Target Platform**: Backend runs locally (a Linux container later, in capability 3); frontend
targets current iOS Safari and Android Chrome

**Project Type**: Web application (frontend + backend)

**Performance Goals**: Under 3 s on the server for both photos; under 1 min from opening the app
to a result (SC-004)

**Constraints**: Upload ≤ 10 MB per photo (the client sends about 1–2 MB); no disk writes of
image data; ±1 percentage point ratio accuracy (SC-001)

**Scale/Scope**: A handful of users; one endpoint; one screen with three states

## Constitution Check

*GATE: checked before Phase 0 and re-checked after Phase 1. Status: PASS.*

| Principle | How this plan complies |
|-----------|------------------------|
| I. Spec before code | The spec has been clarified, and this plan follows it |
| II. Test-first | The pure grading module and the pipeline are driven by synthetic-image unit tests, then the labeled photo set; every acceptance scenario maps to a test (quickstart) |
| III. Superpowers implements | Tasks run via worktree plus subagent-driven development; `/speckit-implement` is not used |
| IV. Simplicity | One endpoint; no router, state library, UI kit or database; no auth code (that's capability 2); retaking resends both photos instead of adding a per-side endpoint |
| V. Decisions recorded | No new architectural decision; detection is the standard OpenCV approach, recorded in research.md. `docs/architecture.md` is updated for the preview image and dev proxy |
| VI. Honest estimates | "Max grade possible" labelling, borderline flags, reason codes instead of numbers, and the full-art "not measurable" path |
| VII. Photos never stored | In-memory decode; spool size raised so uploads never roll to disk (test); no image data in logs or the error handler; the preview goes only to the uploader |
| VIII. Measure before model | Fully deterministic; no AI. Thresholds are in `thresholds.py`, separate from the math |
| IX. Allowlist | Local-only, per constitution v1.0.1; nothing deployed until capability 2 |
| X. Accuracy measured | The pipeline set with hand-measured labels gates any pipeline or threshold change; the slab check is capability 4 |
| XI. Phone-first | Client-side downscale, phone-width layout, Playwright mobile emulation, and a manual check on a real phone over cellular |

Post-design re-check: PASS. There are no violations, so the Complexity Tracking table is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-capture-centering/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/centering-api.md
├── checklists/requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml            # uv; ruff config
├── app/
│   ├── main.py               # FastAPI app, routes, error handlers, spool-size fix
│   ├── schemas.py            # Pydantic response models (camelCase aliases)
│   └── centering/            # pure: no FastAPI imports
│       ├── thresholds.py     # PSA table (data only)
│       ├── grading.py        # ratios, max grade, borderline (pure math, no OpenCV)
│       ├── detect.py         # find quad, quality checks, warp, wrong-side hue
│       ├── measure.py        # design-edge scan (bordered + full-art)
│       └── pipeline.py       # bytes -> SideResult; orchestrates the above
└── tests/
    ├── unit/                 # grading, thresholds, detect/measure on synthetic images
    ├── pipeline/             # labeled real photos + labels.csv
    └── integration/          # TestClient: contract, errors, no-disk-spool

frontend/
├── package.json
├── vite.config.ts            # /api proxy -> :8000
├── src/
│   ├── App.vue               # capture / measuring / result states
│   ├── api/client.ts         # the only fetch; maps {code, message} errors
│   ├── composables/useCheck.ts      # photos (Blobs), downscale, submit, retake
│   ├── components/PhotoSlot.vue     # one side: take/pick, thumbnail, retake
│   ├── components/SideResult.vue    # ratios, grade, borderline, preview + SVG edges
│   └── reasons.ts            # ReasonCode -> title + retake advice
└── tests/
    ├── unit/
    └── e2e/
```

**Structure Decision**: A web application with `backend/` and `frontend/` at the repo root, as
CLAUDE.md requires. The centering package is framework-free so it can be tested without HTTP, and
`grading.py` doesn't even need OpenCV.

## Delivery Order

1. **Story 1 (P1)**: grading and thresholds, then detect and warp, then bordered measure, then
   the endpoint, then the UI result.
2. **Story 2 (P2)**: quality checks and reason codes, retake advice, keeping the other photo on
   retake, wrong side.
3. **Story 3 (P3)**: full-art scan. This is the highest-risk part; it can slip without blocking
   Stories 1 and 2.

The pipeline photo set (quickstart) is a builder-supplied dependency needed before Story 1's
pipeline tests. Unit work on synthetic images can start without it.

## Complexity Tracking

None.
