# Feature Specification: Capture and Centering

**Feature Branch**: `001-capture-centering`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "capability 1: capture and centering"

## Clarifications

### Session 2026-10-01

- Q: What reference is full-art centering measured against? → A: The printed frame line or
  text-box edges when found reliably; otherwise "centering not measurable for this card".
- Q: Can users manually adjust detected edges? → A: No; retake only.
- Q: How does this feature satisfy the allowlist principle before capability 2 exists? → A: Built
  and run locally without sign-in; allowlist wired in by capability 2 before any deployment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Max grade for a bordered card (Priority: P1)

A collector holding a raw card with a visible border photographs the front and the back with their
phone. The app finds the card in each photo, measures how centered the printed design is left/right
and top/bottom on both sides, and tells them the highest PSA grade that centering allows (for
example "Max PSA 9: front left/right is 58/42, PSA 10 needs 55/45 or better").

**Why this priority**: This is the core question the product exists to answer: "can this card
reach a 10?" Bordered cards are the majority of cards and the most reliable to measure.

**Independent Test**: Photograph a bordered card with hand-measured centering on both sides, submit
both photos, and confirm the reported ratios match the hand measurements and the max grade matches
the PSA centering table.

**Acceptance Scenarios**:

1. **Given** clear front and back photos of a bordered card, **When** the user submits them,
   **Then** the app shows left/right and top/bottom ratios for each side (larger number first, e.g.
   `55/45`), the max grade for each side, and an overall max grade equal to the lower of the two.
2. **Given** a result, **When** the user reads it, **Then** it is labeled "max grade possible from
   centering", names the axis and side that limit the grade, and states that it is not a predicted
   grade and not affiliated with PSA.
3. **Given** a measured ratio within measurement tolerance of a grade threshold, **When** the
   result is shown, **Then** that grade is marked as borderline (e.g. "borderline 10/9") instead of
   presented as certain.
4. **Given** a result, **When** the user views it, **Then** each photo is shown straightened with
   the detected card edges and design edges outlined, so the user can see what was measured.

---

### User Story 2 - Retake advice for an unusable photo (Priority: P2)

The user takes a photo that can't be measured reliably: the card is cut off, the photo is blurry,
there is glare across a border, or the card is shot at a steep angle. Instead of a wrong number,
the app says which side failed, why, and how to retake it.

**Why this priority**: Without this, bad photos produce confident wrong answers, which violates the
honest-estimates principle and would cost users money. It is also what makes the first-try
experience on a phone workable.

**Independent Test**: Submit known-bad photos (cropped card, heavy glare, steep angle, blur, no
card) and confirm each returns the matching reason and advice and no ratios or grade.

**Acceptance Scenarios**:

1. **Given** a photo where no card can be found, **When** submitted, **Then** the app reports
   "card not found" for that side with advice (e.g. "fill most of the frame with the card, on a
   plain contrasting background").
2. **Given** a photo with glare covering a border, **When** submitted, **Then** the app reports
   glare with advice (e.g. "tilt the card or move away from direct light").
3. **Given** a photo shot at too steep an angle to correct accurately, **When** submitted, **Then**
   the app reports the angle with advice to shoot straight on.
4. **Given** one usable side and one unusable side, **When** submitted, **Then** the app shows the
   measured side's ratios and grade, shows retake advice for the other side, and shows no overall
   max grade until both sides are measured.
5. **Given** a retake prompt, **When** the user retakes only the failed side, **Then** the other
   side's photo is kept for the current check and not re-requested.

---

### User Story 3 - Max grade for a full-art card (Priority: P3)

The user photographs a full-art card (artwork running to the edge, no plain border). The app
measures centering against the card's printed frame where one can be identified and reports the max
grade the same way as for bordered cards, or says honestly that centering can't be measured for
this card.

**Why this priority**: In scope for v1 per the PRD, but it is a known technical risk; bordered
cards must work first.

**Independent Test**: Submit photos of full-art cards with hand-measured centering and confirm
either correct ratios or an explicit "can't measure centering on this card" reason, never a wrong
confident number.

**Acceptance Scenarios**:

1. **Given** a full-art card, **When** submitted, **Then** the app measures centering against
   the card's printed frame line or text-box edges and reports ratios and max grade as in Story 1.
2. **Given** a full-art card whose reference edges can't be found reliably, **When** submitted,
   **Then** the app returns a "centering not measurable for this card" reason instead of a number.

---

### Edge Cases

- Photo of the wrong side submitted (two fronts or two backs): the app detects a mismatch where
  it can and asks for the missing side; otherwise it measures what it was given.
- Card in a sleeve or top loader: measurement is attempted; glare or edge-detection failures
  return the matching reason. Slabbed cards are out of scope here (capability 4).
- Card rotated in the frame (sideways or upside down): measured normally; orientation does not
  affect left/right vs top/bottom labeling beyond normalizing to portrait.
- Landscape-format cards: measured with the card's own long and short axes, still reported as
  left/right and top/bottom of the card as printed.
- Damaged or miscut card with a border that runs off the edge: reported as the extreme ratio
  (e.g. `100/0`) with max grade per the table, not as an error.
- Photo too large to upload: the app reduces it on the phone before sending; if it still exceeds
  the limit, the user is told to retake at a lower resolution.
- Upload fails on a weak cellular signal: the user is told and can retry without retaking photos.
- Ratio exactly on a threshold (e.g. exactly 55/45): counts as meeting that threshold.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to provide one front photo and one back photo per check, either
  by taking a photo with the phone camera or choosing an existing photo from the phone.
- **FR-002**: The system MUST require both sides before producing an overall max grade.
- **FR-003**: The system MUST locate the card in each photo and correct for perspective and
  rotation before measuring.
- **FR-004**: The system MUST measure left/right and top/bottom centering for each side and report
  each as a ratio with the larger number first, to whole percentage points (e.g. `58/42`).
- **FR-005**: The system MUST determine a max grade per side from PSA's published centering limits
  (front and back limits differ) using the worse of that side's two axes, and an overall max grade
  equal to the lower of the two sides.
- **FR-006**: Grade limits MUST come from a single reference table of PSA centering thresholds so
  that limits can be corrected or other graders added without changing the measurement.
- **FR-007**: Every result MUST be labeled as the maximum grade centering allows, MUST identify the
  limiting side and axis, and MUST NOT be presented as a predicted grade.
- **FR-008**: When a measured ratio is within the measurement tolerance of a grade threshold, the
  result MUST mark that grade as borderline.
- **FR-009**: When a photo can't be measured reliably, the system MUST return a reason for that
  side instead of ratios, from at least: card not found, too much glare, too angled, too blurry,
  card too small in frame, centering not measurable for this card. Each reason MUST map to
  specific retake advice shown to the user.
- **FR-010**: The system MUST show the user each straightened card image with the detected card
  edges and design edges outlined.
- **FR-011**: When one side fails, the user MUST be able to retake only that side and keep the
  other side's photo for the current check.
- **FR-012**: Photos MUST be processed in memory only and MUST NOT be stored, logged, or included
  in error reports by any part of the system. Nothing about a check persists after the user leaves
  the result.
- **FR-013**: The capture and result screens MUST be usable at phone width in current iOS Safari
  and Android Chrome, and photos MUST be reduced in size on the phone before upload.
- **FR-014**: The result MUST state that TenOrNot is an estimate and is not affiliated with or
  endorsed by PSA.
- **FR-015**: This feature runs locally without sign-in. The allowlist check (capability 2) MUST be
  applied to every measurement request before the feature is deployed anywhere reachable from
  outside the developer's machine (capability 3).
- **FR-016**: For full-art cards, the system MUST measure centering against the printed frame line
  or text-box edges when they can be found reliably, and otherwise return "centering not
  measurable for this card".

### Key Entities

- **Check**: one front photo plus one back photo, and the result produced from them. Exists only
  for the current session; never stored.
- **Side result**: for `front` or `back`: either the `lr` and `tb` ratios plus that side's max
  grade and any borderline flags, or a reason with retake advice.
- **Centering threshold**: per grade, the worst allowed ratio for the front and for the back,
  taken from PSA's published standards.
- **Overall result**: overall max grade (lower of the two sides), limiting side and axis, and
  disclaimer; present only when both sides were measured.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the pipeline reference set of hand-measured bordered cards, every reported ratio
  is within 1 percentage point of the hand measurement (e.g. hand 57/43 → reported 56/44 to 58/42).
- **SC-002**: On the same set, the reported max grade matches the max grade from the hand
  measurements for every card, or is marked borderline when the hand measurement is within
  tolerance of a threshold.
- **SC-003**: Every known-bad test photo (cropped, glare, steep angle, blur, no card) gets a reason
  and retake advice; none gets ratios or a grade.
- **SC-004**: A user can go from opening the check screen to a result for both sides in under
  1 minute on a phone over cellular data, assuming photos are usable on the first try.
- **SC-005**: After a check, no copy of either photo exists anywhere outside the user's phone, as
  confirmed by review and by tests on the processing path.
- **SC-006**: On the slab accuracy set (once it exists, capability 4), the real PSA grade never
  exceeds the reported max grade.

## Assumptions

- PSA centering limits, from PSA's grading standards (psacard.com/gradingstandards, verified by
  the user 2026-10-01); the reference table is the single source and can be corrected:

  | Grade | Front | Back |
  |-------|-------|------|
  | PSA 10 | 55/45 | 75/25 |
  | PSA 9 | 60/40 | 90/10 |
  | PSA 8 | 65/35 | 90/10 |
  | PSA 7 | 70/30 | 90/10 |
  | PSA 6 | 80/20 | 90/10 |
  | PSA 5 | 85/15 | 90/10 |
  | PSA 4 | 85/15 | 90/10 |
  | PSA 3 | 90/10 | 90/10 |
  | PSA 2 | 90/10 | 90/10 |
  | PSA 1.5 | 90/10 | 90/10 |

  Each value is the worst ratio allowed for that grade. A side worse than 90/10 on either axis is
  reported as "max PSA 1". Because several grades share a limit, the max grade is always the
  highest grade whose limits the side meets (so PSA 2 and 1.5 are never the reported max).
- Users photograph raw cards (optionally in a penny sleeve or top loader) on a contrasting surface;
  slabbed cards are handled by capability 4.
- No live camera overlay or auto-capture in this feature; the phone's own camera/photo picker is
  used.
- No history: results are not saved and cannot be revisited after leaving the result screen.
- The measurement tolerance used for borderline flags is set during planning from pipeline test
  results.
- Pokémon cards and PSA only; standard card size.
- No manual adjustment of detected edges; users who disagree with the outline retake the photo.
