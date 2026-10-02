# Research: Capture and Centering

Phase 0 decisions for `001-capture-centering`. All values marked *initial* get tuned against
the pipeline photo set (see [quickstart.md](quickstart.md)) and only change with a test that
shows why.

## R1. Upload size and format

- **Decision**: The phone downscales each photo so its long edge is at most 3000 px, re-encodes it
  as JPEG at quality 0.92 (`createImageBitmap` → canvas → `toBlob`), and uploads both photos in
  one multipart request. The server rejects any single file over 10 MB with 413.
- **Rationale**: If the card fills about 80% of a 3000 px frame, it is about 2400 px tall, or
  about 27 px/mm on an 88 mm card. A Pokémon border is about 3 mm, so one percentage point of
  left/right centering is about 0.06 mm, or about 1.6 px. That is enough room for sub-pixel edge
  fitting (R4). The file comes out around 1–2 MB, which is fine on cellular. Re-encoding also
  turns iPhone HEIC into JPEG and applies EXIF rotation in the browser, so the server only ever
  decodes plain JPEG/PNG.
- **Alternatives**: Full-resolution upload (12 MP, 4–8 MB): slow on cellular and gains nothing
  below the measurement noise. 2000 px long edge: about 1 px per percentage point, too tight.
  Server-side HEIC support: adds a native dependency for a case the browser already handles.

## R2. Card detection and straightening

- **Decision**: Convert to grayscale, apply a Gaussian blur, then Canny edges plus a dilate step.
  Take the external contours, simplify each with `approxPolyDP`, and pick the largest convex
  quadrilateral whose aspect ratio is within ±8% of 63:88. Refine the corners with
  `cornerSubPix`, then perspective-warp to a fixed **1260 × 1760 px canvas (20 px/mm)** in
  portrait orientation.
- **Rationale**: This is the standard OpenCV document-scanner pipeline: deterministic, fast
  (under 1 s per photo on one vCPU) and easy to unit-test with synthetic images. A fixed canvas
  means every downstream threshold is in millimetres, not dependent on the photo.
- **Orientation**: A landscape quad is rotated 90° to portrait. A 180° flip doesn't matter
  because larger-first ratios are symmetric, so upside-down cards need no special handling.
- **Alternatives**: An ML card detector would break principle VIII; it's only worth it if
  contour detection fails on the pipeline set. Hough lines for the card outline are more fragile
  on busy backgrounds.

- **Update from labeling real cards (2026-10-01)**: a loose penny sleeve can stand off the card by
  a few mm, and its outline is then the largest quad, so detection measures the sleeve instead of
  the card (seen on Caterpie BUS 001 front and Zoroark-GX back scans). Sleeved cards are in scope
  (spec Assumptions), so T010 needs a test where the quad is refined inward to the card's own edge
  (strong colour change) when a fainter outline sits 1–5 mm outside it.

## R3. Photo quality checks → reason codes

Run in this order. The first one that fails becomes that side's reason. All thresholds are *initial*.

| Check | Rule | Reason |
|-------|------|--------|
| Decodable image | `cv2.imdecode` returns an image | 422 `INVALID_IMAGE` (an error, not a result) |
| Card found | a quad passes R2 | `CARD_NOT_FOUND` |
| Size in frame | quad area ≥ 25% of the image | `CARD_TOO_SMALL` |
| Angle | every quad corner within 90° ± 12°, and opposite sides differ by ≤ 15% | `TOO_ANGLED` |
| Sharpness | variance of the Laplacian on the warped card ≥ 100 | `TOO_BLURRY` |
| Glare | in any border band, ≥ 3% of pixels have V > 245 and S < 30 (HSV) | `TOO_MUCH_GLARE` |
| Design edges | R4 finds all four edges with enough confidence | `CENTERING_NOT_MEASURABLE` |
| Side | side classifier (R6) is confident the photo is the other side | `WRONG_SIDE` |

## R4. Design (inner) edge measurement on bordered cards

- **Decision**: For each of the four sides of the warped card, take about 200 scan lines
  perpendicular to that edge, spread across the middle 70% of its length (this skips the rounded
  corners). Each line runs from the card edge inward to 12% of the card's width or height. Along
  each line, find the position of the strongest colour gradient (Sobel on the Lab image,
  summing the L, a and b channels). The edge position is the **median** of those positions,
  refined to sub-pixel with a parabolic fit. The edge is "found" only when at least 60% of the
  lines agree within ±0.3 mm. Border widths are measured in px on the 20 px/mm canvas, and
  `lr = left / (left + right)`, reported larger-first.
- **Rationale**: Fronts have a uniform yellow or silver border and backs a blue one, so the
  border-to-design change is the strongest gradient near the edge. The median over many lines
  ignores text, holo foil and print specks. The agreement rule is what turns "unsure" into
  `CENTERING_NOT_MEASURABLE` instead of a wrong number (principle VI).
- **Alternatives**: A single global threshold on border colour fails on holo and silver borders.
  Hough line fitting is less robust to the art crossing near the edge.

## R5. Full-art cards (Story 3, FR-016)

- **Decision**: Use the same R4 scan, but in the band 0.5–6 mm from the edge, looking for a
  **thin straight printed line or text-box edge**. It is accepted only if (a) at least 60% of the
  lines agree, (b) the opposite edge is found too, and (c) the line is parallel to the card edge
  within 0.5°. Otherwise the side gets `CENTERING_NOT_MEASURABLE`. The pipeline decides
  bordered vs full-art per side: if no edge is found in the bordered band, it tries the
  full-art band.
- **Rationale**: This matches the clarified spec: measure when there is a reliable reference,
  and say so honestly when there isn't. Expect many full-art cards to return
  `CENTERING_NOT_MEASURABLE` at first; that's the intended outcome while this is a known risk.
- **Risk**: This has the highest uncertainty. Its tasks come after Stories 1 and 2 and can ship
  last, or be cut without affecting them.
- **Update from labeling real cards (2026-10-01)**: the reference is the edge of the artwork, not
  the first printed line. On the Zoroark-GX (SM era) the border holds a thick black frame line,
  and the true edge is a faint embossed shadow line about 2–3 mm in; the strongest-gradient rule
  finds the black line instead. Text boxes and rule bars cover the edge along parts of the bottom.
  The band must therefore extend to about 4 mm, the detector should prefer the innermost
  consistent line before the art, and it must ignore spots covered by boxes. SV-era special
  illustration rares (Altaria ex) have a textured silver band and measure like bordered cards.

## R6. Wrong-side detection

- **Decision**: Work out the dominant hue of the border band on the warped card. A Pokémon back
  has a blue border (hue about 100–130 in OpenCV's 0–180 scale, saturation > 80). A photo
  submitted as `front` whose border is confidently back-blue gets `WRONG_SIDE`. A photo
  submitted as `back` whose border is clearly not blue gets `WRONG_SIDE`. When unsure, the photo
  is measured as given.
- **Rationale**: The spec asks for detection "where it can", and the back design is uniform, so
  one hue test covers it.
- **Alternatives**: A template match on the back's Poké Ball is more work for the same result.

## R7. Grading logic and borderline flags

- **Decision**: Grading is pure Python with no OpenCV. Each ratio is rounded to a whole
  percentage point on the larger side (`57.6` → `58/42`). A side's max grade is the highest
  grade in the threshold table whose front or back limits both of that side's axes meet
  (`rounded ≤ limit`). The overall max grade is the lower of the two sides. Borderline uses a
  tolerance `T` of **1.0 percentage point (initial)**. Recompute the side's grade with each axis
  moved by −T (optimistic) and +T (pessimistic). If the optimistic grade is higher than the max,
  `borderlineWith` is that grade. Otherwise, if the pessimistic grade is lower, `borderlineWith`
  is that grade. Otherwise it is null.
- **Rationale**: Rounding before comparing means the numbers the user sees always agree with the
  grade ("exactly 55/45 counts"). T matches SC-001's ±1 point accuracy target.
- **Alternatives**: Comparing unrounded values can show "55/45 → max 9", which is confusing.

## R8. Preview image (FR-010)

- **Decision**: The response returns each warped card as a 630 × 880 px JPEG (quality 0.8,
  about 60 KB, base64 data URI) plus the four design-edge positions in that image's pixels. The
  frontend draws the outline as an SVG over the image.
- **Rationale**: Drawing a perspective warp in a browser canvas is awkward. Sending the derived
  image back to the user who uploaded it doesn't store anything (principle VII).
- **Alternatives**: Return the quad corners and warp in the browser: more frontend code for no
  user benefit.

## R9. Stack details

- **Backend**: Python 3.13, `uv`, FastAPI (`fastapi[standard]`, which includes
  `python-multipart`), `opencv-python-headless`, `numpy`. Tests: pytest. Lint: ruff.
  Pydantic `alias_generator=to_camel` for camelCase JSON.
- **Frontend**: Vue 3 + TypeScript + Vite; Vitest + @vue/test-utils; Playwright (mobile
  emulation). No router, state library or UI kit: one screen with three states (capture →
  measuring → result).
- **Local wiring**: The Vite dev server proxies `/api` to `localhost:8000`, so no CORS
  configuration is needed. CORS arrives with deployment (capability 3).
- **Versions**: the current stable release of each, pinned in the lockfile at scaffold time.

## R10. Error handling and privacy

- **Decision**: FastAPI handlers for `RequestValidationError` (→ 422 `MISSING_SIDE` or
  `INVALID_IMAGE`), an oversized upload (→ 413 `PHOTO_TOO_LARGE`) and `Exception` (→ 500
  `INTERNAL_ERROR`, a generic message, and a log of the exception type and traceback only). No
  handler or log line includes request bodies, file bytes or image arrays. Image bytes go
  from `UploadFile.read()` into `cv2.imdecode`.
- **Upload buffering**: Starlette buffers each upload in a `SpooledTemporaryFile`, which moves to
  a temp file above 1 MB and is deleted when the request ends. Constitution VII (v1.0.2) allows
  this: it bans retention, not transient framework buffers. On Cloud Run the filesystem is
  in-memory anyway. We don't tune the spool size. Requests whose `Content-Length` is over 21 MB
  get 413 before the body is parsed, and parts over 10 MB get 413 in the handler. A unit test
  (T033) asserts that our code never calls `cv2.imwrite`, opens files for writing, or uses
  `tempfile`.
- **Rationale**: Principle VII, and the error format in CLAUDE.md.
