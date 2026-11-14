"""renumber_figs.py -- renumber a chapter's figures after inserting a new one.

Insert the new figure with the placeholder number NEW (id="fig-N-NEW", caption "Figure N.NEW.",
links "[Figure N.NEW](#fig-N-NEW)"), then run

    python tools/renumber_figs.py 18

The figures of chapter N are numbered 1, 2, ... in the order they appear in its page, and every
fig-N-M anchor and "Figure(s) N.M" mention in all chapter pages is updated to match.
"""
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main(n):
    pages = sorted(glob.glob(os.path.join(ROOT, "chapters", "*.md")))
    page = [p for p in pages if os.path.basename(p).startswith(f"{int(n):02d}_")][0]
    ids = re.findall(rf'<figure id="fig-{n}-(\w+)"', open(page).read())
    mapping = {old: str(i + 1) for i, old in enumerate(ids)}
    print(f"chapter {n}: " + ", ".join(f"{o}->{m}" for o, m in mapping.items() if o != m))
    for p in pages:
        s = open(p).read()
        t = re.sub(rf"fig-{n}-(\w+)\b", lambda m: f"fig-{n}-\0{mapping.get(m.group(1), m.group(1))}", s)
        t = re.sub(rf"(Figures? ){n}\.(\d+|NEW)\b",
                   lambda m: f"{m.group(1)}{n}.\0{mapping.get(m.group(2), m.group(2))}", t)
        t = t.replace("\0", "")
        if t != s:
            open(p, "w").write(t)
            print("  updated", os.path.basename(p))
    left = [p for p in pages if "NEW" in open(p).read() and f"{n}.NEW" in open(p).read()]
    if left:
        print("  placeholders left in:", left)


if __name__ == "__main__":
    main(sys.argv[1])
