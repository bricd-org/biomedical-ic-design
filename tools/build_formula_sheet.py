"""build_formula_sheet.py -- write appendices/a_formulas.md from the chapters' key-equation boxes.

    python tools/build_formula_sheet.py

Every `tbox-keyeq` box in chapters/*.md is copied, with its title and a link back to its chapter,
grouped by part. Rerun after changing a key equation, so that Appendix A never drifts from the text.
"""
import glob
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PARTS = [(1, 4, "Part I · Foundations"), (5, 12, "Part II · The analog front-end"),
         (13, 22, "Part III · Data converters"), (23, 28, "Part IV · Biosignal processing and systems"),
         (29, 31, "Part V · Putting it together")]

HEAD = """---
title: A. Formula Sheet
parent: Appendices
nav_order: 1
permalink: /appendix/a/
---

# <span class="chapnum">Appendix A</span>Formula Sheet

Every key equation of the tutorial on one page, in the order of the chapters, each with a link to the chapter that derives it and explains its terms.
{: .chapterlead }

This page is generated from the chapters by `tools/build_formula_sheet.py`; the symbols are defined where each equation first appears.
"""


def main():
    out = [HEAD]
    pages = sorted(glob.glob(os.path.join(ROOT, "chapters", "*.md")))
    for lo, hi, part in PARTS:
        block = []
        for p in pages:
            num = int(os.path.basename(p)[:2])
            if not lo <= num <= hi:
                continue
            s = open(p).read()
            title = re.search(r"^title:\s*(.+)$", s, re.M).group(1).strip().strip('"')
            boxes = re.findall(r'<div class="tbox tbox-keyeq" markdown="1">\s*<div class="tbox-title">Key equation · (.*?)</div>\s*(.*?)\n</div>', s, re.S)
            if not boxes:
                continue
            block.append(f"\n### [{title}]({{% link chapters/{os.path.basename(p)} %}})\n")
            for name, body in boxes:
                block.append(f"\n**{name.strip()}**\n\n{body.strip()}\n")
        if block:
            out.append(f"\n## {part}\n")
            out.extend(block)
    os.makedirs(os.path.join(ROOT, "appendices"), exist_ok=True)
    dst = os.path.join(ROOT, "appendices", "a_formulas.md")
    with open(dst, "w") as fh:
        fh.write("".join(out))
    n = sum(1 for line in out if line.startswith("\n**"))
    print(f"wrote {dst}: {n} key equations")


if __name__ == "__main__":
    main()
