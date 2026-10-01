---
description: "Task list for 001 capture and centering"
---

# Tasks: Capture and Centering

**Input**: Design documents from `specs/001-capture-centering/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/centering-api.md, quickstart.md

**Tests**: Required. Constitution II makes test-first non-negotiable. Every task is done
red → green → refactor. Write the named test file first and watch it fail, then write the code.
Test levels and locations follow `docs/testing.md`.

**Organization**: Grouped by user story. Paths are relative to the repo root.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3 from spec.md

---

## Phase 1: Setup

- [ ] T001 Scaffold the backend with `uv init` in `backend/`. Use Python 3.13 and add the dependencies `fastapi[standard]`, `opencv-python-headless` and `numpy`, plus the dev dependencies `pytest`, `httpx` and `ruff`. In `backend/pyproject.toml`, configure ruff (line length 100, rules E,F,I,UP,B) and pytest (`testpaths = ["tests"]`, `--ignore=tests/accuracy`). Create empty packages `backend/app/__init__.py` and `backend/app/centering/__init__.py`, and the folders `backend/tests/{unit,pipeline,integration}/`. Done when `uv run pytest` and `uv run ruff check .` both run clean on the empty project.
- [ ] T002 [P] Scaffold the frontend in `frontend/` with Vite's `vue-ts` template. Add Vitest, @vue/test-utils, jsdom, ESLint (the Vue + TS recommended configs) and Playwright. In `frontend/vite.config.ts`, add a dev-server proxy from `/api` to `http://localhost:8000`. In `frontend/playwright.config.ts`, add the projects `iPhone 13` and `Pixel 7`, with a `webServer` entry for both `npm run dev` and `cd ../backend && uv run fastapi dev app/main.py`. Remove the template's demo components. Done when `npm test`, `npm run lint` and `npm run build` pass.
- [ ] T003 [P] Add a `.gitattributes` at the repo root with `* text=auto eol=lf` and `*.jpg binary`, `*.png binary`, then renormalize. This stops the CRLF/LF churn seen in the commits so far.

---

## Phase 2: Foundational (blocks all stories)

- [ ] T004 [P] Create the synthetic card generator in `backend/tests/helpers/synthetic.py`, with tests in `backend/tests/unit/test_synthetic.py`. Write `make_card(left_mm, right_mm, top_mm, bottom_mm, *, border_bgr=(0,200,240), art="noise"|"flat"|"fullart_frame", frame_offset_mm=None, card_mm=(63,88), px_per_mm=27, background_bgr=(40,40,40), canvas_px=(2250,3000), rotate_deg=0, perspective=0.0, blur_sigma=0, glare_rect=None) -> np.ndarray`. It draws a card with exact border widths, art inside the border, and an optional thin 0.3 mm frame line at `frame_offset_mm` for full art. The card is placed on a background, then the optional rotation, perspective, blur and white glare are applied. Also write `encode_jpeg(img, quality=92) -> bytes`. This is a test helper only and is never imported from `app/`.
- [ ] T005 [P] Create the threshold table in `backend/app/centering/thresholds.py`, with tests in `backend/tests/unit/test_thresholds.py`. It holds `PSA_CENTERING: tuple[Threshold, ...]` with `Threshold(grade: float, front: int, back: int)`, using exactly these rows in order: 10 (55, 75), 9 (60, 90), 8 (65, 90), 7 (70, 90), 6 (80, 90), 5 (85, 90), 4 (85, 90), 3 (90, 90), 2 (90, 90), 1.5 (90, 90), and `FALLBACK_GRADE = 1`. This is data only, with no functions. Tests assert the rows are ordered best to worst and that limits never decrease going down the table.
- [ ] T006 [P] Create the response models in `backend/app/schemas.py`, with tests in `backend/tests/unit/test_schemas.py`. These are Pydantic models matching `data-model.md`: `Preview{image: str, design_edges: {left,right,top,bottom: float}}`, `SideResult{side: Literal["front","back"], status: Literal["measured","failed"], lr, tb: str|None, max_grade: float|None, limiting_axis: Literal["lr","tb"]|None, borderline_with: float|None, card_type: Literal["bordered","fullArt"]|None, preview: Preview|None, reason: ReasonCode|None}`, `Overall{max_grade, limiting_side, limiting_axis, borderline_with}`, `CheckResult{front, back, overall: Overall|None, disclaimer: str}` and `ErrorBody{code, message}`. `ReasonCode` is the enum of `CARD_NOT_FOUND, CARD_TOO_SMALL, TOO_ANGLED, TOO_BLURRY, TOO_MUCH_GLARE, CENTERING_NOT_MEASURABLE, WRONG_SIDE`. Use `alias_generator=to_camel` with `populate_by_name=True`, and serialize by alias. Tests check the camelCase output and that a `measured` result omits `reason` while a `failed` result omits the measurement fields (`exclude_none`).
- [ ] T007 Create the app skeleton and error handling in `backend/app/main.py`, with tests in `backend/tests/integration/test_errors.py`. Requirements:
  - `GET /api/health` returns `{"status":"ok"}`.
  - One handler per error, each returning `ErrorBody`: `RequestValidationError` returns 422 `MISSING_SIDE`; any `Exception` returns 500 `INTERNAL_ERROR` with the message "Something went wrong. Try again.", logging the exception type and traceback only (never request data).
  - Middleware rejects any request whose `Content-Length` is over 21 MB with 413 `PHOTO_TOO_LARGE` before the body is read.
  - Tests use TestClient with a test-only route that raises, to check the 500 path, and assert every non-200 body has exactly the keys `code` and `message`.
- [ ] T008 [P] Create the API client in `frontend/src/api/client.ts`, with tests in `frontend/tests/unit/client.test.ts`. Write `postCentering(front: Blob, back: Blob): Promise<CheckResult>`, which is the only `fetch` in the app. It posts multipart with the parts `front` and `back` to `/api/centering`. On a non-200 response it throws `ApiError{status, code, message}` built from the body. On a network failure it throws `ApiError{status: 0, code: "NETWORK", message}`. Define TS types for `CheckResult`, `SideResult`, `Overall` and `ReasonCode` matching `data-model.md`. Tests mock `fetch`.

**Checkpoint**: Both apps run, the error format is enforced, and the test helpers exist.

---

## Phase 3: User Story 1: Max grade for a bordered card (P1) 🎯 MVP

**Goal**: Front and back photos of a bordered card produce ratios, a max grade per side, an overall max grade, borderline flags and an outlined preview.

**Independent Test**: Post synthetic and real bordered-card photos. The reported ratios match the known borders within ±1 point, and the max grade matches the table (spec SC-001, SC-002).

- [ ] T009 [P] [US1] Create the grading logic in `backend/app/centering/grading.py`, with tests in `backend/tests/unit/test_grading.py`. This module is pure: no OpenCV, no FastAPI. Write:
  - `larger_first(a: float, b: float) -> int`, which is `round(max(a, b) / (a + b) * 100)`.
  - `fmt(larger) -> "58/42"`.
  - `side_max_grade(side, lr: int, tb: int, table=PSA_CENTERING) -> float`, which returns the first row where `max(lr, tb) ≤ limit` for that side, otherwise `FALLBACK_GRADE`.
  - `limiting_axis(lr, tb)`, which is `"lr"` unless `tb > lr`.
  - `borderline_with(side, lr, tb, tol=1.0)`: compute the optimistic grade with both axes at −tol and the pessimistic grade with both at +tol. Return the optimistic grade if it is higher than the max, else the pessimistic grade if it is lower, else None.
  - `overall(front, back)`, which returns max = min of the two sides, `limiting_side` (front on a tie), and borderline applied across both sides.

  Tests must include: front 55/45 → 10, 56/44 → 9, 60/40 → 9, 61/39 → 8, 85/15 → 5, 90/10 → 3, 91/9 → 1; back 75/25 → 10, 76/24 → 9, 91/9 → 1; never 2 or 1.5; 56/44 front → borderline 10; 55/45 → borderline 9; 58/42 → None; `larger_first(3.0, 3.0) == 50`; overall picks the lower side and its axis.
- [ ] T010 [P] [US1] Create card detection and straightening in `backend/app/centering/detect.py`, with tests in `backend/tests/unit/test_detect.py`. Write:
  - `decode(data: bytes) -> np.ndarray | None`, using `cv2.imdecode` (no files).
  - `find_card_quad(img) -> np.ndarray | None`: grayscale, Gaussian blur, Canny, dilate, external contours, `approxPolyDP`, then the largest convex 4-point contour with aspect ratio within ±8% of 63:88 in either orientation, refined with `cornerSubPix`.
  - `warp(img, quad) -> np.ndarray`: perspective-warp to 1260 × 1760 portrait (`PX_PER_MM = 20`), rotating a landscape quad 90°.

  Tests use T004 images: the quad is found when straight, when rotated 7°, at perspective 0.08, and when the card is turned 90°. The warped card has the expected border widths within 0.1 mm. Plain background → None.
- [ ] T011 [US1] Create bordered design-edge measurement in `backend/app/centering/measure.py`, with tests in `backend/tests/unit/test_measure.py`. Write `find_design_edges(card) -> Edges | None`, where `Edges` holds left, right, top and bottom in canvas px plus a per-edge agreement fraction. Method (research R4): about 200 scan lines over the middle 70% of each side, from the edge inward to 12% of the dimension; Sobel gradient magnitude summed over the L, a and b channels of Lab; the strongest peak per line; the median, refined with a parabolic sub-pixel fit. An edge counts as found when ≥ 60% of lines fall within ±0.3 mm (6 px) of the median; otherwise return None. Tests on T004 cards, warped via T010: borders (3.0, 3.0), (2.0, 4.0), (3.5, 2.5) mm in both axes, with `art="noise"`. Each measured border is within 0.05 mm, and `larger_first` matches the exact value. The silver border `(200,200,200)` and the back blue `(170,90,30)` also pass.
- [ ] T012 [US1] Create the measured-side pipeline in `backend/app/centering/pipeline.py`, with tests in `backend/tests/unit/test_pipeline.py`. Write `measure_side(side, data: bytes) -> SideResult`: decode, find the quad, warp, find the design edges, compute ratios and grades with grading.py, and build the preview. The preview is the warped card resized to 630 × 880, JPEG quality 80, base64 `data:image/jpeg;base64,...`, with `designEdges` scaled to preview px. Set `card_type="bordered"`. On any step returning None, return `status="failed"` with `CARD_NOT_FOUND` (quad) or `CENTERING_NOT_MEASURABLE` (edges); US2 adds the remaining reasons. No logging of image data. Tests: a synthetic 58/42 front gives `lr="58/42"`, max grade 9 and a preview that decodes to 630 × 880.
- [ ] T013 [US1] Add the centering endpoint `POST /api/centering` to `backend/app/main.py`, with tests in `backend/tests/integration/test_centering_api.py`. It takes the multipart parts `front` and `back` (`UploadFile`):
  - Missing part → 422 `MISSING_SIDE`.
  - A part over 10 MB (`UploadFile.size`) → 413 `PHOTO_TOO_LARGE`.
  - Bytes that don't decode → 422 `INVALID_IMAGE`.
  - Otherwise 200 `CheckResult` with `overall` set only when both sides are measured, and `disclaimer` = "Estimate only. Not affiliated with or endorsed by PSA."

  The response matches the example in `contracts/centering-api.md`. Tests:
  - the 200 shape and camelCase keys;
  - each error code, including a single 11 MB part → 413;
  - overall null when one side fails.
- [ ] T014 [US1] Add pipeline accuracy tests in `backend/tests/pipeline/test_labeled_photos.py`. Read `backend/tests/pipeline/photos/labels.csv` (`file, side, card_type, lr, tb, expect_reason`, where `expect_reason` is empty for measurable photos). Parametrize per row. For measured rows, assert the reported larger value is within ±1 of the label and the max grade equals `side_max_grade(label)` or is flagged borderline toward it. Skip the whole module with a clear message if the CSV is absent. **Depends on the builder supplying the photo set (quickstart).** Run it, record the results in the PR, and fix pipeline issues before moving on.
- [ ] T015 [P] [US1] Create the check composable in `frontend/src/composables/useCheck.ts`, with tests in `frontend/tests/unit/useCheck.test.ts`. State: `photos: {front?: Blob, back?: Blob}`, `status: "capture"|"measuring"|"result"`, `result?: CheckResult`, `error?: ApiError`. `setPhoto(side, file)` downscales: `createImageBitmap(file)` (EXIF-aware), long edge ≤ 3000 px, canvas `toBlob("image/jpeg", 0.92)`. `submit()` requires both photos and calls `postCentering`. `newCard()` clears everything. Photos live only in memory; never touch localStorage or IndexedDB. If `createImageBitmap` rejects (e.g. a HEIC photo on Android Chrome), set `error` with code `UNREADABLE_PHOTO` and the message "Couldn't read this photo. Take a new one with the camera.", and keep the other side's photo. Tests stub `createImageBitmap`/canvas and the client, and cover the state changes, the downscale target size and the unreadable-photo path.
- [ ] T016 [P] [US1] Create the photo slot component in `frontend/src/components/PhotoSlot.vue`, with tests in `frontend/tests/unit/PhotoSlot.test.ts`. Props: `side`, `photo?: Blob`. Use `<input type="file" accept="image/*">` with **no** `capture` attribute, so iOS and Android offer both camera and library (FR-001). Show a thumbnail via `URL.createObjectURL`, revoked on change and unmount. Emit `select(file)`. Use a large tap target (≥ 48 px) and a visible label "Front" or "Back".
- [ ] T017 [P] [US1] Create the measured-side result component in `frontend/src/components/SideResult.vue`, with tests in `frontend/tests/unit/SideResult.test.ts`. For `status="measured"`, show the side name, `L/R lr` and `T/B tb`, "Max PSA {maxGrade}", "borderline {maxGrade}/{borderlineWith}" when set, and which axis limits the grade. Show `preview.image` with an absolutely positioned SVG (viewBox 0 0 630 880) drawing two rectangles: the card outline (0, 0, 630, 880) and the design-edge rectangle, in contrasting colours (spec FR-010). Tests render a fixture result and assert the text and both SVG rects' attributes.
- [ ] T018 [US1] Create the main screen in `frontend/src/App.vue`, with tests in `frontend/tests/unit/App.test.ts`. It wires `useCheck`:
  - Capture state: two `PhotoSlot`s and a "Check centering" button enabled only when both photos are set.
  - Measuring state: a spinner.
  - Result state: an overall headline "Max grade possible from centering: PSA {n}" with borderline text, the limiting side and axis, the line "This is a centering limit, not a predicted grade", and `disclaimer`. Below that, two `SideResult`s and a "New card" button.

  The layout is designed at 375 px width first; no horizontal scroll at 320 px.
- [ ] T019 [US1] Add the bordered happy-path end-to-end test in `frontend/tests/e2e/check.spec.ts`. Commit two fixture JPEGs, generated once by a small script `backend/tests/helpers/make_e2e_fixtures.py` that uses T004: a 58/42 front and a 52/48 back, saved to `frontend/tests/e2e/fixtures/`. Flow: set both inputs, tap "Check centering", and assert "PSA 9", "58/42" and the visible preview, on iPhone and Pixel projects against the real backend.

**Checkpoint**: The MVP is complete. A bordered card gives a correct max grade on a phone-sized screen.

---

## Phase 4: User Story 2: Retake advice for an unusable photo (P2)

**Goal**: Bad photos give a per-side reason with retake advice, never numbers. A failed side can be retaken while the other photo is kept.

**Independent Test**: The known-bad photos (cropped, glare, angle, blur, no card, small, wrong side) each return the matching reason and no ratios (SC-003).

- [ ] T020 [US2] Add photo quality checks to `backend/app/centering/detect.py`, with tests in `backend/tests/unit/test_quality.py`. Write `check_quality(img, quad, card) -> ReasonCode | None`, run in this order with named module constants:
  - `CARD_TOO_SMALL`: quad area < `MIN_CARD_AREA_FRAC = 0.25`.
  - `TOO_ANGLED`: any corner outside 90° ± `MAX_CORNER_DEV_DEG = 12`, or opposite sides differing by more than `MAX_SIDE_DIFF = 0.15`.
  - `TOO_BLURRY`: Laplacian variance on `card` < `MIN_SHARPNESS = 100`.
  - `TOO_MUCH_GLARE`: in any 0–4 mm border band, ≥ `MAX_GLARE_FRAC = 0.03` of pixels have HSV V > 245 and S < 30.

  Tests use T004 variants per reason (small card on a big canvas, perspective 0.4, blur_sigma 6, a glare_rect over the left border), plus a clean card → None. These thresholds are initial values (research R3).
- [ ] T021 [US2] Add wrong-side detection to `backend/app/centering/detect.py`, with tests in `backend/tests/unit/test_wrong_side.py`. Write `looks_like_back(card) -> bool | None`. Take the median hue and saturation of the 0–2 mm border band. Return True if the hue is 100–130 (OpenCV scale) and saturation > 80, False if saturation > 80 with a hue outside 90–140, or a low-saturation silver border; return None when unsure. Tests: yellow, silver and blue borders, and a grey ambiguous border → None.
- [ ] T022 [US2] Wire the failure paths into `backend/app/centering/pipeline.py` and extend `backend/tests/unit/test_pipeline.py`. Order: `CARD_NOT_FOUND` → `check_quality` → wrong side (front with `looks_like_back is True`, or back with `looks_like_back is False` → `WRONG_SIDE`) → measure edges (None → `CENTERING_NOT_MEASURABLE`). A failed `SideResult` carries only `side`, `status` and `reason`. Tests: one per reason through `measure_side`.
- [ ] T023 [US2] Add API-level failure tests in `backend/tests/integration/test_centering_api.py`: one side glare and the other clean returns 200 with front measured, back failed `TOO_MUCH_GLARE` and `overall: null`; two fronts returns back `WRONG_SIDE`.
- [ ] T024 [US2] Extend `backend/tests/pipeline/test_labeled_photos.py` so rows with `expect_reason` assert `status == "failed"` and the reason matches, with no ratios (SC-003).
- [ ] T025 [P] [US2] Create the reason messages in `frontend/src/reasons.ts`, with tests in `frontend/tests/unit/reasons.test.ts`. Write `REASONS: Record<ReasonCode, {title, advice}>`:
  - CARD_NOT_FOUND: "Card not found" / "Fill most of the frame with the card, on a plain background that contrasts with the border."
  - CARD_TOO_SMALL: "Card too small" / "Move closer so the card fills most of the photo."
  - TOO_ANGLED: "Photo too angled" / "Hold the phone flat above the card and shoot straight down."
  - TOO_BLURRY: "Photo blurry" / "Hold steady and tap to focus on the card before shooting."
  - TOO_MUCH_GLARE: "Too much glare" / "Tilt the card slightly or move away from direct light. Sleeves and top loaders add glare."
  - CENTERING_NOT_MEASURABLE: "Can't measure centering" / "The design edges couldn't be found reliably. Retake straight on in even light. Some full-art cards can't be measured, and a miscut card with a border running off the edge can't be measured either."
  - WRONG_SIDE: "Wrong side?" / "This looks like the other side of the card. Retake the {side}."

  Tests assert every `ReasonCode` has an entry.
- [ ] T026 [US2] Add the failed-side display and retake in `frontend/src/components/SideResult.vue`, `frontend/src/composables/useCheck.ts` and `frontend/src/App.vue`, extending their tests:
  - For `status="failed"`, show the `REASONS` title and advice and a "Retake {side}" control (a file input).
  - `useCheck.retake(side, file)` replaces only that side's photo, keeps the other Blob (FR-011), and resubmits both.
  - The overall headline is hidden when `overall` is null, replaced by "Retake the {side} to get a max grade".
- [ ] T027 [US2] Add API error handling in the UI in `frontend/src/App.vue` and `useCheck.ts`, extending the tests. An `ApiError` shows a message from one table in `frontend/src/api/client.ts` (`PHOTO_TOO_LARGE`, `INVALID_IMAGE`, `MISSING_SIDE`, `INTERNAL_ERROR`, `NETWORK`) with a "Try again" button that resubmits the same photos without retaking them (spec edge case: weak signal).
- [ ] T028 [US2] Add the retake end-to-end test in `frontend/tests/e2e/retake.spec.ts`. Add a glare fixture to `make_e2e_fixtures.py` (T019). Flow: submit a clean front and a glare back, assert the glare advice is shown and there is no overall result, retake the back with a clean fixture, and assert PSA 9 overall and that the front was not re-picked.

**Checkpoint**: US1 and US2 both work on their own. Bad photos never produce numbers.

---

## Phase 5: User Story 3: Max grade for a full-art card (P3)

**Goal**: Full-art cards are measured against the printed frame line or text-box edge, or honestly return `CENTERING_NOT_MEASURABLE`.

**Independent Test**: Hand-measured full-art photos give correct ratios or the "not measurable" reason, never a wrong confident number.

- [ ] T029 [US3] Add the full-art scan to `backend/app/centering/measure.py`, with tests in `backend/tests/unit/test_measure_fullart.py`. Write `find_frame_edges(card) -> Edges | None`, using the same scan as T011 but limited to the band 0.5–6 mm from each edge, looking for a thin line (a gradient peak pair less than 1 mm apart). An edge is accepted only if ≥ 60% of lines agree within ±0.3 mm, the opposite edge is also found, and the fitted line is within 0.5° of parallel to the card edge (research R5). Tests: a T004 `art="fullart_frame"` card with frame offsets (2.0, 2.6) mm → the measured ratio is exact within ±1; `art="noise"` filling to the edge with no frame → None.
- [ ] T030 [US3] Add the full-art fallback in `backend/app/centering/pipeline.py`, extending `test_pipeline.py`. When `find_design_edges` returns None, try `find_frame_edges`. If found, return the measurement with `card_type="fullArt"`. If neither is found → `CENTERING_NOT_MEASURABLE`. Tests: a full-art synthetic → measured fullArt; a frameless synthetic → failed `CENTERING_NOT_MEASURABLE`.
- [ ] T031 [US3] Run full-art pipeline accuracy using `card_type=fullArt` rows in `backend/tests/pipeline/test_labeled_photos.py` (already parametrized by T014). Assert each is either within ±1 of the label or failed with `CENTERING_NOT_MEASURABLE`. A measured value outside ±1 fails the test.
- [ ] T032 [P] [US3] Add a full-art label in `frontend/src/components/SideResult.vue` with a test: show "Full art, measured to the printed frame" when `cardType="fullArt"`.

**Checkpoint**: All three stories work.

---

## Phase 6: Polish and cross-cutting

- [ ] T033 [P] Add privacy guard tests in `backend/tests/unit/test_privacy.py` (constitution VII, SC-005):
  - Scan the source of `backend/app/**/*.py` and assert there is no `cv2.imwrite`, no `open(` with a `"w"` or `"wb"` mode, and no `tempfile`.
  - An integration case posts photos with `caplog` at DEBUG, forces a 500, and asserts no log record contains bytes or the base64 prefix `/9j/`.
- [ ] T034 Tune the quality thresholds and the borderline tolerance against the pipeline set. Change the constants in `backend/app/centering/detect.py` and `grading.py` only when a labeled photo misbehaves, and record the before/after per-photo results and the final values in `specs/001-capture-centering/research.md` R3 and R7 (constitution X).
- [ ] T035 Run every row of `specs/001-capture-centering/quickstart.md`, including a real phone over cellular through a temporary tunnel (for example `cloudflared tunnel --url http://localhost:5173`, torn down afterwards). Record the time from opening the app to a result (SC-004) in the PR description.
- [ ] T036 [P] Update the docs: confirm the commands in `CLAUDE.md` and `docs/testing.md` match what actually runs, add the local run steps to `README.md`, update `docs/architecture.md` if anything changed during the build, and update `docs/state.md`.

---

## Dependencies and execution order

- **Setup (T001–T003)**: T002 and T003 can run alongside T001.
- **Foundational (T004–T008)**: needs T001 (backend) or T002 (T008). T004, T005, T006 and T008 are parallel. T007 needs T006.
- **US1**: T009 needs T005. T010 needs T004. T011 needs T010. T012 needs T006, T009 and T011. T013 needs T007 and T012. T014 needs T012 and the builder's photo set. T015 needs T008. T016 and T017 are parallel with T015. T018 needs T015–T017. T019 needs T013 and T018.
- **US2**: needs US1's T012, T013 and T017. T020 and T021 are parallel (both in `detect.py`, so do them one after another if they're in one worktree). T022 needs T020 and T021. T023 and T024 need T022. T025 is parallel with all backend work. T026 needs T025. T027 needs T026. T028 needs T026 and T023.
- **US3**: needs T011 and T012. Independent of US2 apart from the shared `pipeline.py` (merge order: US2 then US3).
- **Polish**: after the stories it covers. T034 needs T014 and T024.

## Parallel examples

- **Foundational**: T004 (synthetic.py), T005 (thresholds.py), T006 (schemas.py) and T008 (client.ts) at once.
- **US1**: backend T009 (grading) and T010 (detect) together, while the frontend runs T015, T016 and T017 together.
- **US2**: T025 (reasons.ts) alongside T020 to T022 on the backend.

## Implementation strategy

1. **MVP = Phases 1–3**: bordered cards, end to end on a phone screen. Stop and check SC-001/002 on the photo set (T014) before going on.
2. **Then US2**: this makes it trustworthy with real-world photos, and is needed before friends use it.
3. **Then US3**: full art is the highest risk. If T029 can't meet ±1 on the photo set, ship "not measurable" for full art and record that in the spec. The spec already allows it.
4. Capability 2 (allowlist) must land before any deployment (constitution IX).
