"""Click-to-measure fallback for card scans the auto helper can't read (e.g. silver border on
light green art).

Usage: uv run --with opencv-python --with numpy scripts/click_measure.py SCAN [SCAN_TURNED_180]
Shows 3 strips per side (12 per scan) in their natural orientation, with a map of the whole card
marking where the strip is. In each strip click the CARD edge (where the card's printed face
begins; ignore any dark shadow line outside it), then the DESIGN edge (where the border ends).
Keys: Enter = accept, r = redo strip, Esc = quit.
With two scans of the same side (second turned 180° on the glass) it averages each physical
border, cancelling the scanner lamp's one-sided edge shadow.
Prints border widths and lr/tb, and writes <scan>_clicks.jpg with every click drawn, as evidence.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

from measure_scan import deskew_crop, print_pair, ratios

POSITIONS = (0.25, 0.5, 0.75)
ZOOM = 2
OUT_MM, IN_MM = 3, 12  # strip covers 3 mm outside the card edge to 12 mm inside
HALF_MM = 6  # strip half-thickness along the edge (12 mm of context)
MAP_H = 480  # height of the whole-card map shown beside each strip
HEADER = 50  # instruction bar above the strip in the window


def strip_box(card, pad, px_mm, side, pos):
    """(x0, y0, x1, y1) of the strip in card-crop px, in natural orientation."""
    h, w = card.shape[:2]
    out, inn, half = int(OUT_MM * px_mm), int(IN_MM * px_mm), int(HALF_MM * px_mm)
    if side in ("left", "right"):
        y = int(pos * h)
        x = pad if side == "left" else w - pad
        x0, x1 = (x - out, x + inn) if side == "left" else (x - inn, x + out)
        return max(x0, 0), y - half, min(x1, w), y + half
    x = int(pos * w)
    y = pad if side == "top" else h - pad
    y0, y1 = (y - out, y + inn) if side == "top" else (y - inn, y + out)
    return x - half, max(y0, 0), x + half, min(y1, h)


def card_map(card, box):
    scale = MAP_H / card.shape[0]
    m = cv2.resize(card, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    x0, y0, x1, y1 = (int(v * scale) for v in box)
    cv2.rectangle(m, (x0 - 3, y0 - 3), (x1 + 3, y1 + 3), (0, 0, 255), 3)
    return m


def pick(strip, vertical, cmap, title):
    """Two clicks along the strip's measuring axis -> (a, b) in strip px, or None on Esc."""
    clicks = []
    view = cv2.resize(strip, None, fx=ZOOM, fy=ZOOM, interpolation=cv2.INTER_CUBIC)

    def on_mouse(event, x, y, _flags, _param):
        y -= HEADER  # window coords -> strip coords
        inside = 0 <= x < view.shape[1] and 0 <= y < view.shape[0]
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < 2 and inside:
            clicks.append((y if vertical else x) / ZOOM)

    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(title, on_mouse)
    while True:
        shown = view.copy()
        for v, col in zip(clicks, ((0, 0, 255), (0, 200, 0))):
            p = int(v * ZOOM)
            if vertical:
                cv2.line(shown, (0, p), (shown.shape[1], p), col, 2)
            else:
                cv2.line(shown, (p, 0), (p, shown.shape[0]), col, 2)
        hint = ["1) click CARD edge", "2) click DESIGN edge", "Enter = accept, r = redo"][len(clicks)]
        hh = max(shown.shape[0], cmap.shape[0])
        canvas = np.full((hh + HEADER, shown.shape[1] + cmap.shape[1] + 20, 3), 255, np.uint8)
        canvas[HEADER:HEADER + shown.shape[0], :shown.shape[1]] = shown
        canvas[HEADER:HEADER + cmap.shape[0], shown.shape[1] + 20:] = cmap
        cv2.putText(canvas, hint, (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.imshow(title, canvas)
        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            cv2.destroyAllWindows()
            return None
        if key == ord("r"):
            clicks.clear()
        if key in (13, 32) and len(clicks) == 2:
            cv2.destroyWindow(title)
            return tuple(clicks)



def click_scan(scan):
    card, pad, px_mm = deskew_crop(cv2.imread(scan))
    widths, tiles = {}, []
    for side in ("left", "right", "top", "bottom"):
        widths[side] = []
        vertical = side in ("top", "bottom")
        for n, pos in enumerate(POSITIONS, 1):
            box = strip_box(card, pad, px_mm, side, pos)
            x0, y0, x1, y1 = box
            strip = np.ascontiguousarray(card[y0:y1, x0:x1])
            name = f"{side[0].upper()}{n}"
            got = pick(strip, vertical, card_map(card, box),
                       f"{Path(scan).stem}  {name}: {side} border, {int(pos * 100)}% along")
            if got is None:
                raise SystemExit("Quit; nothing saved.")
            a, b = got
            widths[side].append(abs(b - a))
            tile = cv2.resize(strip, None, fx=ZOOM, fy=ZOOM, interpolation=cv2.INTER_CUBIC)
            for v, col in ((a, (0, 0, 255)), (b, (0, 200, 0))):
                p = int(v * ZOOM)
                if vertical:
                    cv2.line(tile, (0, p), (tile.shape[1], p), col, 2)
                else:
                    cv2.line(tile, (p, 0), (p, tile.shape[0]), col, 2)
            if vertical:  # evidence sheet: lay every tile out horizontally for one grid
                tile = cv2.rotate(tile, cv2.ROTATE_90_COUNTERCLOCKWISE)
            tile = cv2.copyMakeBorder(tile, 56, 6, 6, 6, cv2.BORDER_CONSTANT, value=(255, 255, 255))
            cv2.putText(tile, f"{name}  {abs(b - a):.1f}px  (clicked)", (8, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3)
            tiles.append(tile)

    med = {s: float(np.median(v)) for s, v in widths.items()}
    lr, tb = ratios(med)
    print(Path(scan).name)
    for s, v in widths.items():
        print(f"  {s:6} {med[s]:6.1f}px  (clicks: {', '.join(f'{w:.1f}' for w in v)})")
    print(f"  lr {lr}/{100 - lr}   tb {tb}/{100 - tb}")

    th = max(t.shape[0] for t in tiles)
    tw = max(t.shape[1] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, th - t.shape[0], 0, tw - t.shape[1], cv2.BORDER_CONSTANT,
                                value=(255, 255, 255)) for t in tiles]
    cols = [np.vstack(tiles[i * 3:(i + 1) * 3]) for i in range(4)]
    out = Path(scan).with_name(Path(scan).stem + "_clicks.jpg")
    if cv2.imwrite(str(out), np.hstack(cols), [cv2.IMWRITE_JPEG_QUALITY, 85]):
        print(f"  evidence: {out}")
    else:
        print(f"  (couldn't write {out.name}; close it in any viewer)")
    return med, card


def main():
    done = [(Path(a).name, *click_scan(a)) for a in sys.argv[1:3]]
    if len(done) == 2:
        (na, wa, ca), (nb, wb, cb) = done
        print_pair(na, nb, wa, wb, ca, cb)


if __name__ == "__main__":
    main()
