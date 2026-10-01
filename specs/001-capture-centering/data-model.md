# Data Model: Capture and Centering

Nothing here is persisted. These are in-memory shapes for one check, and the response that goes
back to the phone. Wire names are camelCase. The backend uses snake_case with a Pydantic alias
generator.

## Grade threshold table (`thresholds.py`, data only)

One row per grade. Each limit is the larger number of the worst allowed ratio. Order goes from
best grade to worst. A different grader is a second table with the same shape.

| grade | front | back |
|-------|-------|------|
| 10 | 55 | 75 |
| 9 | 60 | 90 |
| 8 | 65 | 90 |
| 7 | 70 | 90 |
| 6 | 80 | 90 |
| 5 | 85 | 90 |
| 4 | 85 | 90 |
| 3 | 90 | 90 |
| 2 | 90 | 90 |
| 1.5 | 90 | 90 |

**Fallback**: if no row's limits are met, the max grade is **1**.

**Rule**: a side's max grade is the first row (best first) where `max(lr, tb) ≤ limit` for that
side, using rounded larger-first values. A side can therefore never report 2 or 1.5, because
grade 3 has the same limits and comes first.

## Ratio

The larger-first percentage pair for one axis.

| field | type | rule |
|-------|------|------|
| `larger` | int 50–100 | `round(max(a, b) / (a + b) * 100)` from the measured border widths `a` and `b` |
| display | string | `f"{larger}/{100 - larger}"`, e.g. `"58/42"` |

On the wire this is sent as the display string. Grading uses `larger`.

## SideResult

One per side. It is either **measured** or **failed**, never both.

| field | type | when |
|-------|------|------|
| `side` | `"front"` \| `"back"` | always |
| `status` | `"measured"` \| `"failed"` | always |
| `lr` | Ratio string | measured |
| `tb` | Ratio string | measured |
| `maxGrade` | number | measured |
| `limitingAxis` | `"lr"` \| `"tb"` | measured (the axis with the larger `larger`; `lr` wins ties) |
| `borderlineWith` | number \| null | measured (see research R7) |
| `cardType` | `"bordered"` \| `"fullArt"` | measured |
| `preview` | Preview | measured |
| `reason` | ReasonCode | failed |

## Preview

| field | type | rule |
|-------|------|------|
| `image` | string | `data:image/jpeg;base64,...`, a 630 × 880 straightened card |
| `designEdges` | `{left, right, top, bottom}` numbers | px from the image's left or top edge, in preview coordinates |

## ReasonCode

`CARD_NOT_FOUND`, `CARD_TOO_SMALL`, `TOO_ANGLED`, `TOO_BLURRY`, `TOO_MUCH_GLARE`,
`CENTERING_NOT_MEASURABLE`, `WRONG_SIDE`.

The frontend maps each code to a title and retake advice in one table. The backend sends only
the code.

## CheckResult (response body)

| field | type | rule |
|-------|------|------|
| `front` | SideResult | always |
| `back` | SideResult | always |
| `overall` | Overall \| null | non-null only when both sides are `measured` |
| `disclaimer` | string | always: "Estimate only. Not affiliated with or endorsed by PSA." |

## Overall

| field | type | rule |
|-------|------|------|
| `maxGrade` | number | `min(front.maxGrade, back.maxGrade)` |
| `limitingSide` | `"front"` \| `"back"` | the side with the lower max grade; `front` on a tie |
| `limitingAxis` | `"lr"` \| `"tb"` | that side's `limitingAxis` |
| `borderlineWith` | number \| null | same rule as SideResult, applied to both sides together |

## State (frontend, one check)

```
capture ──(both photos chosen)──▶ measuring ──(200)──▶ result
   ▲                                  │                  │
   └──────────(error)─────────────────┘                  │
   ▲                                                     │
   └──(retake side X: keep the other photo, clear X)─────┘
```

Photos exist only as in-memory `Blob`s in the composable. "New card" clears both photos.
Nothing is written to `localStorage` or IndexedDB.
