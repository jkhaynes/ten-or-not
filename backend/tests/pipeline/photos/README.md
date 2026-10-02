# Pipeline photo set

Real phone photos with hand-measured centering. `tests/pipeline/test_labeled_photos.py` (task T014) reads `labels.csv`.

## Folders
- `bordered/`: 8+ bordered cards, one front photo and one back photo each. Include a silver-border card from Scarlet & Violet, a holo, and two cards in a sleeve or top loader (label them with their ratios; if glare defeats them, fill `expect_reason` instead).
- `fullart/`: 3+ full-art fronts.
- `evidence/`: the confirmed tile sheet for every measured photo, named `<card>-<side>-tiles.jpg` (e.g. `pikachu-30c-045-front-tiles.jpg`). It shows how each `lr`/`tb` label was measured, including which tiles were rejected. Add one whenever a label is filled in.
- `bad/`: one photo for each failure: cropped, glare on a border, steep angle (>20°), blurry, no card, card small in frame, and a back submitted as a front.

Name files `<card>-<side>.jpg`, e.g. `bordered/pikachu-151-front.jpg`.

## Cards in the set
Keep this up to date as cards are added, so coverage gaps are visible.

| Card | Set | Finish | Front border | Measured with | Max grade (centering) |
|------|-----|--------|--------------|---------------|-----------------------|
| Pikachu 045/128 | 30th Celebration (30C) | Holo | Sparkly foil (holo pattern) | Auto helper | PSA 10, borderline (front L/R 55/45) |
| Pansage 004/182 | Paradox Rift (PAR) | Reverse holo | Silver (SV era) | Click tool (front), auto (back) | PSA 10 |
| Butterfree 3/147 | Burning Shadows (BUS) | Reverse holo | Yellow | Auto helper | PSA 8 (front L/R 61/39) |
| Caterpie 1/147 | Burning Shadows (BUS) | Non-holo | Yellow | Auto helper (sleeve edge confused one front scan's right side) | PSA 9 (front T/B 57/43); front photo deliberately ~9% off-angle |
| Altaria ex 253/182 | Paradox Rift (PAR) | Special illustration rare (textured foil) | Full art with a thin textured silver band (~3 mm) | Auto helper | PSA 9 (front L/R 59/41) |
| Zoroark-GX 77a/73 | Shining Legends (SLG) | Full art, textured rainbow foil | Thick black frame line inside the border; border ends at a faint embossed line ~2–3 mm in | Click tool (front, 5 strips/side), auto (back) | PSA 9 (front L/R 58/42) |
| M Gyarados EX 115/122 | BREAKpoint (BKP) | Full art, textured rainbow foil (XY era) | Dark textured band ~2–3 mm; art breaks over it on the left and along the top | Click tool (front, `sh click.sh`), auto (back) | PSA 9 (front L/R 58/42; T/B ±2, see below) |

**Still wanted:** 6 of the 7 bad photos (phone only, no scans; see "The bad photos" below), needed before US2's pipeline tests (T024). Optional: a card in a top loader. Measured cards are complete as of 2026-10-01 (7 cards); no truly borderless full arts exist in the builder's collection, so the full-art "not measurable" path is covered by synthetic tests (T029/T030) and by bad photos.

**Full-art border rule:** the border runs from the card edge to the edge of the artwork, which on SM-era full arts is a faint embossed shadow line. Printed decoration inside that (e.g. the thick black frame line on the Zoroark-GX) is part of the border, not its edge. Where a text box or rule bar covers the line, those strips don't count: skip them in the click tool (`s`), or note them as excluded below.

**Known label uncertainty:** m-gyarados-ex-bkp-115 front T/B (51/49): the inner edge of the dark band along the top runs into the name bar, EX logo and lightning art, so top-border clicks spread ~12 px (56–68). T/B is good to about ±2 points; L/R (58/42) is solid. Every value in that range is under the PSA 10 limit, so the max grade label (PSA 9, from L/R) is unaffected.

**Excluded clicks:** zoroark-gx-slg-077a front: the bottom-border strips at 50% and 75% (scan a: 79.0, 77.0 px) and at 50% (scan b top, 78.5 px) landed on the GX rule box; the label uses the remaining strips (bottom 62.3 px, top 59.2 px).

Note: modern (SV-era) special illustration rares look borderless in phone photos but have a thin textured silver band all round, so they measure like bordered cards. Only cards with art truly to the edge exercise the full-art fallback.

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
| `bad/wrong-side-front.jpg` | Photograph a card **back**, labelled side `front` (done: a copy of `bordered/butterfree-bus-003-back.jpg`) | `WRONG_SIDE` |

## Hand-measuring centering
**Scan every side twice.** The scanner lamp lights the card from one direction, so the card's thickness (and the sleeve) casts a soft shadow along two edges, which biases those borders by a few pixels. Scan the side, then **turn the card 180° on the glass** and scan it again. Pass both scans together with `--pair` (auto) or as two arguments (click tool); the tools detect the turn and combine the two: the auto helper averages left/right and takes each top/bottom border from the scan where it lay at the bottom of the glass (no shadow there); the click tool averages everything, because you click past the shadow yourself. Use the `PAIR … <- use these` numbers.

**Shortcut:** from the repo root, `sh click.sh` click-measures the two newest scans in Downloads (5 strips per side, 20–80%).

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
