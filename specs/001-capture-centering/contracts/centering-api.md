# Contract: Centering API

Local only in this feature. There is no auth until capability 2 (spec FR-015). Capability 2 adds
`Authorization: Bearer <Firebase ID token>`, plus 401 and 403, to this same endpoint.

## `POST /api/centering`

**Request**: `multipart/form-data`

| part | type | required | notes |
|------|------|----------|-------|
| `front` | image file (JPEG/PNG) | yes | ≤ 10 MB; the client sends ≤ 3000 px on the long edge |
| `back` | image file (JPEG/PNG) | yes | same |

Retaking one side resends both photos. The client keeps the photo that didn't change.

**200**: `CheckResult` (see [data-model.md](../data-model.md)). Always 200 once both images
decode, even when one or both sides fail to measure.

```json
{
  "front": {
    "side": "front", "status": "measured",
    "lr": "58/42", "tb": "53/47",
    "maxGrade": 9, "limitingAxis": "lr", "borderlineWith": null,
    "cardType": "bordered",
    "preview": { "image": "data:image/jpeg;base64,...",
                 "designEdges": { "left": 33.1, "right": 594.2, "top": 30.0, "bottom": 851.5 } }
  },
  "back": { "side": "back", "status": "failed", "reason": "TOO_MUCH_GLARE" },
  "overall": null,
  "disclaimer": "Estimate only. Not affiliated with or endorsed by PSA."
}
```

**Errors**: the body is always `{ "code": string, "message": string }`.

| status | code | when |
|--------|------|------|
| 413 | `PHOTO_TOO_LARGE` | a file is over 10 MB, or the request is over 21 MB |
| 422 | `MISSING_SIDE` | `front` or `back` is missing |
| 422 | `INVALID_IMAGE` | a part doesn't decode as an image |
| 500 | `INTERNAL_ERROR` | unexpected exception; generic message, no details |

## `GET /api/health`

Returns `200 { "status": "ok" }`. It is unauthenticated even after capability 2 (constitution IX).
