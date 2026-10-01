# Quickstart: Capture and Centering

How to prove 001 works. Contract: [contracts/centering-api.md](contracts/centering-api.md).
Shapes: [data-model.md](data-model.md).

## Prerequisites

- Python 3.13 and `uv`; Node LTS and npm.
- Phone and laptop on the same Wi-Fi, for the phone check.
- **Pipeline photo set**, supplied by the builder and committed under
  `backend/tests/pipeline/photos/`, with a `labels.csv` (`file, side, card_type, lr, tb`, using
  hand-measured larger-first ratios). Minimum to start:
  - 8 bordered cards, front and back (including a silver-border SV card and a holo)
  - 3 full-art fronts
  - 1 of each bad photo: cropped, glare on a border, steep angle (>20°), blurry, no card,
    card small in frame, two backs
  - Hand-measure the ratios with a centering ruler or by counting pixels on a flatbed scan;
    note which method was used in the CSV header comment.

## Run

```bash
cd backend && uv sync && uv run fastapi dev app/main.py      # http://localhost:8000
cd frontend && npm install && npm run dev -- --host          # http://<laptop-ip>:5173 on the phone
```

## Validate

| # | Scenario | How | Expected |
|---|----------|-----|----------|
| 1 | Math is exact | `cd backend && uv run pytest tests/unit` | Synthetic cards with known borders produce exact ratios; threshold table rows such as 55/45 → 10, 56/44 → 9 and 91/9 → 1 pass |
| 2 | Pipeline accuracy (SC-001, SC-002) | `uv run pytest tests/pipeline` | Every labeled photo is within ±1 percentage point of its label, and every max grade matches or is flagged borderline |
| 3 | Bad photos (SC-003) | same run | Every bad photo returns its reason code and no ratios |
| 4 | API contract | `uv run pytest tests/integration` | 200 shape matches the contract; 413, 422 `MISSING_SIDE`, 422 `INVALID_IMAGE` and 500 all use `{code, message}`; the upload never spills to disk |
| 5 | Phone journey (SC-004) | `cd frontend && npx playwright test` (iPhone and Pixel emulation), then by hand on a real phone over cellular via a tunnel | Two photos to a result in under 1 minute; retaking one side keeps the other photo |
| 6 | No photo persisted (SC-005) | Review the diff, test 4 above, and `grep -rn "imwrite\|wb\"" backend/app` | No writes; no image data in logs |
| 7 | Lint | `uv run ruff check .` and `npm run lint` | Clean |
