# Pipeline photo set

Real phone photos with hand-measured centering. `tests/pipeline/test_labeled_photos.py` (task T014) reads `labels.csv`.

## Folders
- `bordered/`: 8+ bordered cards, one front photo and one back photo each. Include a silver-border card from Scarlet & Violet, a holo, and two cards in a sleeve or top loader (label them with their ratios; if glare defeats them, fill `expect_reason` instead).
- `fullart/`: 3+ full-art fronts.
- `evidence/`: the confirmed tile sheet for every measured photo, named `<card>-<side>-tiles.jpg` (e.g. `pikachu-30c-045-front-tiles.jpg`). It shows how each `lr`/`tb` label was measured, including which tiles were rejected. Add one whenever a label is filled in.
- `bad/`: one photo for each failure: cropped, glare on a border, steep angle (>20°), blurry, no card, card small in frame, and a back submitted as a front.

Name files `<card>-<side>.jpg`, e.g. `bordered/pikachu-151-front.jpg`.

## labels.csv
One row per photo. `file` is relative to this folder.

| column | value |
|--------|-------|
| file | `bordered/pikachu-151-front.jpg` |
| side | `front` or `back` (the side it was submitted as) |
| card_type | `bordered` or `fullArt` |
| lr, tb | hand-measured larger-first number, e.g. `58` for 58/42; empty for bad photos |
| expect_reason | empty for measurable photos; otherwise a reason code, e.g. `TOO_MUCH_GLARE` |

Example rows:
```
bordered/pikachu-151-front.jpg,front,bordered,58,52,
bad/glare-back.jpg,back,bordered,,,TOO_MUCH_GLARE
```

Reason codes: `CARD_NOT_FOUND`, `CARD_TOO_SMALL`, `TOO_ANGLED`, `TOO_BLURRY`, `TOO_MUCH_GLARE`, `CENTERING_NOT_MEASURABLE`, `WRONG_SIDE`.

## Before you start
- **iPhone:** Settings → Camera → Formats → **Most Compatible**, so photos save as JPEG. The tests read files directly and can't open HEIC. Android saves JPEG by default.
- Use the main 1× lens with no zoom, flash off, and no portrait mode or filters.
- Get transfers to the PC right: AirDrop or Google Photos, using "original" or "actual size". Don't send photos through a messaging app, which compresses them.

## Setup for good photos
- **Background:** a plain matte surface that contrasts with the border. Dark grey or black works for yellow and silver borders, and also for the blue backs. Avoid patterned tablecloths and wood grain.
- **Light:** even and indirect, such as daylight from a window to the side or a ceiling light behind you. No direct lamp over the card, because that's what makes glare.
- **Framing:** hold the phone flat and parallel to the card, about 15–20 cm above it. The card should fill about 60–80% of the frame with background visible on all four sides. Never crop a card edge.
- **Focus:** tap the card to focus, hold still, and shoot. Zoom in on the photo afterwards: the border edge should look crisp.
- Keep the shadow of your phone or hand off the card.

## What to shoot
| Folder | Shots | Notes |
|--------|-------|-------|
| `bordered/` | 8+ cards, front **and** back each | Mix of yellow borders, at least one silver-border Scarlet & Violet card, one holo, one visibly off-center card, and two cards in a penny sleeve or top loader |
| `fullart/` | 3+ fronts | Ideally some with a visible frame line or text box near the edge and one without |
| `bad/` | 1 of each | See below |

**The bad photos** (any card from the bordered set works):
| File | How to make it | `expect_reason` |
|------|----------------|-----------------|
| `bad/cropped-front.jpg` | Move close so one edge of the card is cut off | `CARD_NOT_FOUND` |
| `bad/no-card.jpg` | Photograph the empty background | `CARD_NOT_FOUND` |
| `bad/small-front.jpg` | Shoot from about 60 cm so the card is small in frame | `CARD_TOO_SMALL` |
| `bad/angled-front.jpg` | Tilt the phone about 30° or more, so the card looks like a trapezoid | `TOO_ANGLED` |
| `bad/blurry-front.jpg` | Move the phone as you shoot, or tap to focus on the background | `TOO_BLURRY` |
| `bad/glare-back.jpg` | Put a lamp or phone flashlight so the reflection lands on a border | `TOO_MUCH_GLARE` |
| `bad/wrong-side-front.jpg` | Photograph a card **back**, labelled side `front` | `WRONG_SIDE` |

## Hand-measuring centering
**Scan every side twice.** The scanner lamp lights the card from one direction, so the card's thickness (and the sleeve) casts a soft shadow along two edges, which biases those borders by a few pixels. Scan the side, then **turn the card 180° on the glass** and scan it again. Pass both scans together with `--pair` (auto) or as two arguments (click tool); the tools detect the turn and combine the two: the auto helper averages left/right and takes each top/bottom border from the scan where it lay at the bottom of the glass (no shadow there); the click tool averages everything, because you click past the shadow yourself. Use the `PAIR … <- use these` numbers.

**Faster:** `uv run --with opencv-python-headless --with numpy scripts/measure_scan.py --pair <scan> <scan-turned>` (from the repo root) measures the scan and writes `<scan>_tiles.jpg`, which shows every measured spot zoomed in with the card edge (red) and design edge (green). Tiles are named L1–L15, R1–R15, T1–T15 and B1–B15 (left, right, top, bottom; 1 is nearest the start of that side), so you can point to a bad one. Check that every line sits on the real edge; if one doesn't, measure that side by hand as below. The labels are only ground truth once a person has checked them.

Mark wrong tiles with `--drop 1:T11,2:B4` (scan number, then tile); they show as REJECTED and are left out.

**If the auto sheet keeps snagging** (e.g. silver border on light-green art): `uv run --with opencv-python --with numpy scripts/click_measure.py <scan> <scan-turned>` opens 12 zoomed strips (3 per side); click the card edge, then the design edge, Enter to accept, `r` to redo. It writes `<scan>_clicks.jpg`; save both to `evidence/` as `<card>-<side>-clicks-a.jpg` and `-b.jpg` (auto sheets: `<card>-<side>-tiles-a.jpg` / `-b.jpg`). For the card edge, click where the card's printed face begins; ignore any dark shadow line just outside it.

By hand:
A centering ruler is too coarse: 1 percentage point is about 0.06 mm. Use a scan:
1. Scan each card on a flatbed scanner at **600 dpi** (about 24 px per mm), front and back.
2. Open the scan in an image editor that shows cursor pixel coordinates; Windows Paint shows them in the status bar.
3. For each of the four borders, measure the pixel distance from the card edge to the design edge at 3 points along that side, and average them.
4. `lr = round(max(L, R) / (L + R) * 100)` and the same for `tb`. Put those numbers in `labels.csv`.
5. Measure full-art cards to the printed frame line or text-box edge, the same reference the app uses. If there's no clear reference, write `CENTERING_NOT_MEASURABLE` in `expect_reason`.

Label the **photo** with the ratios from the **scan** of the same card and side.
