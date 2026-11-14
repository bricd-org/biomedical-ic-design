"""check_arrows.py -- flag cramped arrows in the hand-drawn SVG diagrams.

For every <path> or <line> with a marker-end (or marker-start), the script measures the straight
segment that carries the arrowhead and reports it when that segment is shorter than MIN_SHAFT
(default 24 px in viewBox units). An arrowhead is about 7-9 px long, so a shorter segment shows
almost no shaft and the arrow looks squashed between its blocks.

    python tools/check_arrows.py                 # all assets/figs/*.svg without a matplotlib header
    python tools/check_arrows.py assets/figs/ch29_testchip.svg --min 28
"""
import argparse
import glob
import math
import os
import re
import xml.etree.ElementTree as ET

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?")


def points(d):
    """Vertices of a path (curves reduced to their control polygon end points)."""
    toks = TOK.findall(d)
    pts, i, cmd = [], 0, None
    x = y = sx = sy = 0.0
    nargs = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                x, y = sx, sy
                pts.append((x, y))
                continue
        n = nargs[cmd.upper()]
        args = [float(v) for v in toks[i:i + n]]
        i += n
        rel = cmd.islower()
        c = cmd.upper()
        if c == "H":
            x = args[0] + (x if rel else 0)
        elif c == "V":
            y = args[0] + (y if rel else 0)
        else:
            nx, ny = args[-2], args[-1]
            if rel:
                nx, ny = nx + x, ny + y
            if c in "CSQ":
                # keep the last control point so the final tangent is right
                cx, cy = args[-4], args[-3]
                if rel:
                    cx, cy = cx + x, cy + y
                pts.append((cx, cy))
            x, y = nx, ny
            if c == "M":
                sx, sy = x, y
                if cmd == "m":
                    cmd = "l"
                elif cmd == "M":
                    cmd = "L"
        pts.append((x, y))
    return pts


def check(path, min_shaft):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f"parse error: {e}"]
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        me, ms = el.get("marker-end"), el.get("marker-start")
        if not (me or ms) or tag not in ("path", "line", "polyline"):
            continue
        if tag == "path":
            pts = points(el.get("d", ""))
        elif tag == "line":
            pts = [(float(el.get("x1", 0)), float(el.get("y1", 0))), (float(el.get("x2", 0)), float(el.get("y2", 0)))]
        else:
            nums = [float(v) for v in re.findall(r"-?\d*\.?\d+", el.get("points", ""))]
            pts = list(zip(nums[::2], nums[1::2]))
        pts = [p for k, p in enumerate(pts) if k == 0 or p != pts[k - 1]]
        if len(pts) < 2:
            continue
        ends = []
        if me:
            ends.append(("end", pts[-2], pts[-1]))
        if ms:
            ends.append(("start", pts[1], pts[0]))
        for which, (x0, y0), (x1, y1) in ends:
            L = math.hypot(x1 - x0, y1 - y0)
            if L < min_shaft:
                out.append(f"{which:5s} shaft {L:5.1f} px at ({x1:.0f}, {y1:.0f})  {tag} d={el.get('d', '')[:50]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--min", type=float, default=24.0)
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(os.path.join(ROOT, "assets", "figs", "*.svg")))
    total = 0
    for f in files:
        head = open(f, encoding="utf-8").read(400)
        if "matplotlib" in head.lower() and not a.files:
            continue
        bad = check(f, a.min)
        if bad:
            total += len(bad)
            print(os.path.basename(f))
            for b in bad:
                print("   " + b)
    print(f"{total} cramped arrow(s) under {a.min:g} px")


if __name__ == "__main__":
    main()
