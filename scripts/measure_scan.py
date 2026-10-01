"""One-off helper: measure border widths on a flatbed card scan, with a visual check sheet.

Usage: uv run --with opencv-python-headless --with numpy scripts/measure_scan.py SCAN [SCAN ...] [--drop T11,B4]
--drop removes tiles a person marked wrong on the sheet: T11 for every scan, 1:T11 for scan 1 only.
--pair treats scans as pairs of the same side, the second turned 180° on the glass, and averages
each physical border across the two scans, taking top/bottom from the scan where that edge lay at
the bottom of the glass (the lamp shadows whichever edge is at the top).
For each scan prints L/R/T/B border widths (px) and lr/tb, and writes <scan>_tiles.jpg
showing every measured spot zoomed, with the card edge (red) and design edge (green).
Not part of the app; the human check of the sheet is what makes these labels ground truth.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

SAMPLES = tuple(round(0.15 + i * 0.05, 2) for i in range(15))  # 15%..85%: skips rounded corners
OUTLIER_MM = 0.75  # samples this far from the side's median are rejected (printed text, etc.)
STRIP = 30  # px averaged across each sample line, to smooth holo sparkle


def deskew_crop(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sat = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1]  # yellow border on white: only saturation differs
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 30, 90)
    edges |= cv2.Canny(cv2.GaussianBlur(sat, (5, 5), 0), 30, 90)
    edges = cv2.dilate(edges, None, iterations=2)
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rect = cv2.minAreaRect(max(cnts, key=cv2.contourArea))
    (cx, cy), (w, h), ang = rect
    # Only ever correct a small tilt: bring the angle into (-45, 45]. minAreaRect's angle
    # convention differs across OpenCV versions; without this a card could be turned 180°,
    # which silently breaks the --pair left/right matching.
    while ang > 45:
        ang -= 90
        w, h = h, w
    while ang <= -45:
        ang += 90
        w, h = h, w
    if w > h:
        raise SystemExit("Card is sideways on the scan; place it portrait (upright or upside down).")
    m = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
    rot = cv2.warpAffine(img, m, (img.shape[1], img.shape[0]), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    pad = int(0.08 * w)
    x0, y0 = int(cx - w / 2) - pad, int(cy - h / 2) - pad
    crop = rot[max(y0, 0):int(cy + h / 2) + pad, max(x0, 0):int(cx + w / 2) + pad]
    return crop, min(pad, int(cx - w / 2), int(cy - h / 2)), h / 88  # crop, edge offset, px/mm


def profile(lab, side, pos):
    """1-D Lab profile from outside the card inward, averaged over a STRIP-wide band."""
    h, w = lab.shape[:2]
    if side in ("left", "right"):
        y = int(pos * h)
        band = lab[y - STRIP // 2:y + STRIP // 2, :, :].mean(axis=0)
        return band if side == "left" else band[::-1]
    x = int(pos * w)
    band = lab[:, x - STRIP // 2:x + STRIP // 2, :].mean(axis=1)
    return band if side == "top" else band[::-1]


def peak(grad, lo, hi):
    i = lo + int(np.argmax(grad[lo:hi]))
    if 0 < i < len(grad) - 1:  # parabolic sub-pixel refinement
        a, b, c = grad[i - 1], grad[i], grad[i + 1]
        d = a - 2 * b + c
        return i + (0.5 * (a - c) / d if d else 0.0)
    return float(i)


MIN_AGREE = 4  # spots that must agree for a group of readings to count


def first_cluster(widths, px_mm):
    """Centre of the narrowest group of >= MIN_AGREE agreeing widths. The design edge is the FIRST
    boundary in from the card edge; when it's faint (yellow next to light green) most spots jump
    to art frames or text further in, so the majority group can be the wrong one."""
    tol = OUTLIER_MM * px_mm
    groups = [v for v in sorted(widths) if sum(abs(w - v) <= tol for w in widths) >= MIN_AGREE]
    if not groups:
        return float(np.median(widths))
    near = [w for w in widths if abs(w - groups[0]) <= tol]
    return float(np.median(near))


def measure(img, pad, dpi_px_per_mm):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    out = {}
    for side in ("left", "right", "top", "bottom"):
        rows = []
        for pos in SAMPLES:
            p = profile(lab, side, pos)
            grad = np.linalg.norm(np.diff(p, axis=0), axis=1)
            grad = np.convolve(grad, np.ones(3) / 3, mode="same")
            n = len(grad)
            win = int(1.5 * dpi_px_per_mm)  # card edge: within 1.5 mm of the detected outline
            card = peak(grad, max(pad - win, 0), pad + win)
            lo = int(card + 0.6 * dpi_px_per_mm)  # design edge: 0.6–7 mm inside the card edge
            hi = int(card + 7 * dpi_px_per_mm)
            design = peak(grad, lo, min(hi, n - 1))
            rows.append((pos, card, design))
        out[side] = [(p, c, d, abs(d - c - center) <= OUTLIER_MM * dpi_px_per_mm)
                     for center in [first_cluster([d - c for _, c, d in rows], dpi_px_per_mm)]
                     for p, c, d in rows]
    return out


def check_sheet(img, res, path, unused=()):
    lab_free = img  # tiles are cut from the same orientation the profiles used
    tiles = []
    for side, rows in res.items():
        oriented = {"left": lab_free, "right": lab_free[:, ::-1],
                    "top": cv2.rotate(lab_free, cv2.ROTATE_90_COUNTERCLOCKWISE)[::-1],
                    "bottom": cv2.rotate(lab_free, cv2.ROTATE_90_CLOCKWISE)}[side]
        # every orientation now reads outside -> inward along x, with the side's length along y
        h = oriented.shape[0]
        for n, (pos, card, design, kept) in enumerate(rows, 1):
            y = int(pos * h)
            x0 = max(int(card) - 30, 0)
            x1 = int(design) + 30
            tile = np.ascontiguousarray(oriented[y - 40:y + 40, x0:x1]).copy()
            tile = cv2.resize(tile, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
            for x, col in ((card, (0, 0, 255)), (design, (0, 255, 0))):
                xs = int(round((x - x0) * 4))
                cv2.line(tile, (xs, 0), (xs, tile.shape[0]), col, 2)
            tile = cv2.copyMakeBorder(tile, 56, 6, 6, 6, cv2.BORDER_CONSTANT, value=(255, 255, 255))
            tile_id = f"{side[0].upper()}{n}"  # L1..L15, R1.., T1.., B1..
            if side in unused:
                label, color = f"{tile_id}  SHADOW SIDE - not used", (150, 150, 150)
            else:
                label = f"{tile_id}  {design - card:.1f}px" + ("  REJECTED" if not kept else "")
                color = (0, 0, 0) if kept else (0, 0, 220)
            cv2.putText(tile, label, (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3)
            tiles.append(tile)
    th = max(t.shape[0] for t in tiles)
    tw = max(t.shape[1] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, th - t.shape[0], 0, tw - t.shape[1], cv2.BORDER_CONSTANT,
                                value=(255, 255, 255)) for t in tiles]
    n = len(SAMPLES)  # one column per side, one row per sample position
    cols = [np.vstack(tiles[i * n:(i + 1) * n]) for i in range(4)]
    if not cv2.imwrite(str(path), np.hstack(cols), [cv2.IMWRITE_JPEG_QUALITY, 85]):  # fails silently if the file is open elsewhere
        print(f"  (couldn't update {path.name}; it's open in a viewer. Numbers above are current.)")
        return
    print(f"  sheet: {path}")


def ratios(w):
    def one(a, b):
        return None if np.isnan(a + b) else round(max(a, b) / (a + b) * 100)
    return one(w["left"], w["right"]), one(w["top"], w["bottom"])


def fmt(x):
    return "n/a" if x is None else f"{x}/{100 - x}"


def is_flipped(card_a, card_b):
    """True if card_b is card_a turned 180° (compares small grayscale thumbnails)."""
    def thumb(c):
        return cv2.resize(cv2.cvtColor(c, cv2.COLOR_BGR2GRAY), (64, 88)).astype(np.float32)
    a, b = thumb(card_a), thumb(card_b)
    return float(np.abs(a - b[::-1, ::-1]).mean()) < float(np.abs(a - b).mean())


def combine(wa, wb, flipped, top_shadow=False):
    """Each physical border across two scans of the same side (second turned 180°).

    Left/right are averaged. With top_shadow (auto helper), the edge lying at the top of the
    glass picks up a lamp shadow whose width varies scan to scan (~4-8 px), so each of the card's
    top/bottom borders is taken from the scan where it lay at the BOTTOM of the glass instead.
    The click tool averages everything, because a person clicks past the shadow."""
    if flipped:
        wb = {"left": wb["right"], "right": wb["left"], "top": wb["bottom"], "bottom": wb["top"]}
    w = {s: float(np.nanmean([wa[s], wb[s]])) for s in wa}  # NaN = no valid spots in that scan
    if flipped and top_shadow:  # each from its unshadowed scan, unless that one has no reading
        w["top"] = wb["top"] if not np.isnan(wb["top"]) else wa["top"]
        w["bottom"] = wa["bottom"] if not np.isnan(wa["bottom"]) else wb["bottom"]
    return w


def print_pair(name_a, name_b, wa, wb, card_a, card_b, top_shadow=False):
    flipped = is_flipped(card_a, card_b)
    w = combine(wa, wb, flipped, top_shadow)
    lr, tb = ratios(w)
    print(f"PAIR {name_a} + {name_b} ({'second turned 180°' if flipped else 'same orientation'})")
    print("  " + "  ".join(f"{s} {w[s]:.1f}" for s in w))
    print(f"  lr {fmt(lr)}   tb {fmt(tb)}   <- use these")
    if not flipped:
        print("  WARNING: second scan is not turned 180°, so the edge shadow does not cancel.")


def main():
    drops = {t for a in sys.argv[1:] if a.startswith("--drop") for t in a.split("=", 1)[-1].split(",")}
    if "--drop" in sys.argv:  # also accept "--drop T11,B4" as two args
        drops |= set(sys.argv[sys.argv.index("--drop") + 1].split(","))
    scans = [a for a in sys.argv[1:] if not a.startswith("--drop") and a.split(",")[0] not in drops]
    pair = "--pair" in scans
    scans = [a for a in scans if a != "--pair"]
    done = []
    for idx, arg in enumerate(scans, 1):
        mine = {d.split(":")[-1] for d in drops if ":" not in d or d.startswith(f"{idx}:")}
        raw = cv2.imread(arg)
        card, pad, px_per_mm = deskew_crop(raw)
        res = measure(card, pad, px_per_mm)
        for side, rows in res.items():  # person-rejected tiles count as outliers
            res[side] = [(p, c, d, k and f"{side[0].upper()}{i}" not in mine)
                         for i, (p, c, d, k) in enumerate(rows, 1)]
        kept = {s: [d - c for _, c, d, k in rows if k] for s, rows in res.items()}
        # a side with every spot rejected is NaN; --pair then uses the other scan's reading
        widths = {s: float(np.median(v)) if v else float("nan") for s, v in kept.items()}
        spread = {s: float(np.ptp(v)) if v else float("nan") for s, v in kept.items()}
        lr, tb = ratios(widths)
        sheet = Path(arg).with_name(Path(arg).stem + "_tiles.jpg")
        print(Path(arg).name)
        for s in widths:
            print(f"  {s:6} {widths[s]:6.1f}px  (kept {len(kept[s])}/{len(SAMPLES)}, "
                  f"spread {spread[s]:.1f})")
        print(f"  lr {fmt(lr)}   tb {fmt(tb)}")
        check_sheet(card, res, sheet, unused=("top",) if pair else ())
        done.append((Path(arg).name, widths, card))
    if pair:
        for (na, wa, ca), (nb, wb, cb) in zip(done[::2], done[1::2]):
            print_pair(na, nb, wa, wb, ca, cb, top_shadow=True)


if __name__ == "__main__":
    main()
