#!/usr/bin/env python3
"""build_site.py -- turn the LaTeX book in book/ into the Jekyll (just-the-docs) website.

Adapted from the Open-SERDES Tutorial builder for the Open-BioAFE Tutorial.

The LaTeX book (the same files as the Overleaf project) is the single source of truth.
This script regenerates everything the website shows:

  chapters/*.html, appendices/*.html, preface.html, references.html   (pages)
  parts/*.md                                                           (part landing pages)
  assets/figs/...                                                      (figures, SVG/PNG)
  assets/pdf/Open-BioAFE_Tutorial.pdf                                   (the compiled book)

Usage (from the repository root):
    python3 tools/build_site.py            # compiles the book if needed, then converts
    python3 tools/build_site.py --no-latex # reuse the existing build in book/_build

Requirements: TeX Live (latexmk, pdflatex, bibtex), pandoc >= 3.0, poppler-utils
(pdftoppm, pdftocairo, pdfinfo). Python >= 3.9, standard library only.

How it works: every chapter is pre-processed in Python (cross-references and figure,
table, equation and example numbers are taken from the LaTeX .aux files so the web
numbers match the PDF exactly; siunitx quantities, boxes and TikZ pictures are
rewritten), converted to HTML with pandoc, and wrapped in a Jekyll page.
"""
import argparse, html, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
BUILD = BOOK / "_build"
SRC = BOOK / "tutorial"
FIGOUT = ROOT / "assets" / "figs"
PDF_NAME = "Open-BioAFE_Tutorial.pdf"
WARN = []


def warn(msg):
    WARN.append(msg)
    print("  warning:", msg, file=sys.stderr)


# ----------------------------------------------------------------------------- LaTeX build
def build_latex():
    (BUILD / "tutorial" / "chapters").mkdir(parents=True, exist_ok=True)
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-shell-escape",
           f"-outdir={BUILD}", "tutorial.tex"]
    print("compiling the book:", " ".join(cmd))
    r = subprocess.run(cmd, cwd=BOOK, capture_output=True, text=True)
    if not (BUILD / "tutorial.pdf").exists():
        print(r.stdout[-3000:]); sys.exit("LaTeX build failed")


# ----------------------------------------------------------------------------- aux data
def brace(s, i):
    """s[i] == '{' -> (content, index after the matching '}')."""
    assert s[i] == "{", (s[i:i + 30])
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced braces near: " + s[i:i + 60])


def bracket(s, i):
    """s[i] == '[' -> (content, index after the matching ']') (respects braces)."""
    depth, j = 0, i + 1
    while j < len(s):
        c = s[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "]" and depth == 0:
            return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced [ near: " + s[i:i + 60])


def skip_ws(s, i):
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def read_aux():
    labels, cites = {}, {}
    for f in [BUILD / "tutorial.aux"] + sorted((BUILD / "tutorial" / "chapters").glob("*.aux")):
        if not f.exists():
            continue
        t = f.read_text(errors="replace")
        for m in re.finditer(r"\\newlabel\{([^}]*)@cref\}\{\{\[([a-z]+)\]\[[^]]*\]\[[^]]*\]([^}]*)\}", t):
            labels[m.group(1)] = (m.group(2), m.group(3))
        for m in re.finditer(r"\\bibcite\{([^}]*)\}\{\{(\d+)\}", t):
            cites[m.group(1)] = int(m.group(2))
    return labels, cites


# ----------------------------------------------------------------------------- book structure
ROMAN = ["I", "II", "III", "IV", "V", "VI"]


def book_structure():
    """Parse tutorial.tex: the preface, parts (title + blurb) and chapter files in order."""
    t = (BOOK / "tutorial.tex").read_text()
    t = re.sub(r"(?<!\\)%.*", "", t)
    items, i, part = [], 0, 0
    pat = re.compile(r"\\(tutpart|include|input|appendix)\b")
    while True:
        m = pat.search(t, i)
        if not m:
            break
        kind, j = m.group(1), m.end()
        if kind == "tutpart":
            title, j = brace(t, skip_ws(t, j)); blurb, j = brace(t, skip_ws(t, j))
            part += 1
            items.append(("part", part, title, blurb))
        elif kind == "appendix":
            items.append(("appendix",))
        else:
            arg, j = brace(t, skip_ws(t, j))
            if "/chapters/" in arg and kind == "include":
                items.append(("file", arg.split("/")[-1], part))
        i = j
    return items


# ----------------------------------------------------------------------------- math-region mask
MATH_ENVS = ("equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*")


def math_mask(s):
    """Boolean list: True where s[i] is inside math mode (approximate, good for our sources)."""
    mask = bytearray(len(s))
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            if s.startswith("\\(", i) or s.startswith("\\[", i):
                close = "\\)" if s[i + 1] == "(" else "\\]"
                j = s.find(close, i + 2)
                j = n if j < 0 else j + 2
                mask[i:j] = b"\x01" * (j - i); i = j; continue
            m = re.match(r"\\begin\{(" + "|".join(re.escape(e) for e in MATH_ENVS) + r")\}", s[i:])
            if m:
                end = "\\end{" + m.group(1) + "}"
                j = s.find(end, i)
                j = n if j < 0 else j + len(end)
                mask[i:j] = b"\x01" * (j - i); i = j; continue
            if s.startswith("\\ensuremath{", i):
                _, j = brace(s, i + len("\\ensuremath"))
                mask[i:j] = b"\x01" * (j - i); i = j; continue
            i += 2; continue
        if c == "$":
            dbl = s.startswith("$$", i)
            k = i + (2 if dbl else 1)
            while k < n:
                if s[k] == "\\":
                    k += 2; continue
                if s.startswith("$$" if dbl else "$", k):
                    break
                k += 1
            j = min(n, k + (2 if dbl else 1))
            mask[i:j] = b"\x01" * (j - i); i = j; continue
        i += 1
    return mask


# ----------------------------------------------------------------------------- siunitx
PREFIX = {"giga": "G", "mega": "M", "kilo": "k", "milli": "m", "micro": "µ", "nano": "n",
          "pico": "p", "femto": "f", "deci": "d", "tera": "T", "centi": "c", "atto": "a"}
UNIT = {"volt": "V", "second": "s", "ohm": "Ω", "hertz": "Hz", "bel": "B", "meter": "m",
        "metre": "m", "bit": "b", "farad": "F", "ampere": "A", "watt": "W", "siemens": "S",
        "henry": "H", "joule": "J", "kelvin": "K", "degree": "°", "percent": "%", "radian": "rad",
        "ppm": "ppm", "UIunit": "UI", "dBc": "dBc", "dBm": "dBm", "decibel": "dB", "celsius": "°C",
        "coulomb": "C", "byte": "B", "electronvolt": "eV", "gram": "g", "minute": "min", "hour": "h",
        "Vpp": "V_pp", "Vppd": "V_ppd", "mVpp": "mV_pp", "mVppd": "mV_ppd",
        "Vrms": "V_rms", "mVrms": "mV_rms", "uVrms": "µV_rms", "uVpp": "µV_pp", "liter": "L", "litre": "L"}
SUP = {"2": "²", "3": "³", "-1": "⁻¹", "-2": "⁻²", "0.5": "^0.5"}


def parse_units(u):
    """siunitx unit string -> list of (text, power, per, sqrt) with power as str."""
    out, per, power_next, i = [], False, None, 0
    pend_prefix = ""
    while i < len(u):
        if u[i] in " ~":
            i += 1; continue
        if u[i] == "\\":
            m = re.match(r"\\([a-zA-Z]+)", u[i:]); name = m.group(1); i += m.end()
            if name == "per":
                per = True
            elif name in ("squared", "cubed"):
                if out:
                    out[-1][1] = "2" if name == "squared" else "3"
            elif name in ("square", "cubic"):
                power_next = "2" if name == "square" else "3"
            elif name == "sqrt":
                j = skip_ws(u, i)
                if j < len(u) and u[j] == "{":
                    inner, i = brace(u, j)
                    sub = parse_units(inner)
                    txt = "".join(x[0] for x in sub)
                else:
                    m2 = re.match(r"\s*\\([a-zA-Z]+)", u[i:]); i += m2.end()
                    txt = pend_prefix + UNIT.get(m2.group(1), m2.group(1)); pend_prefix = ""
                out.append([txt, None, per, True]); per = False
            elif name in PREFIX:
                pend_prefix += PREFIX[name]
            elif name in UNIT:
                out.append([pend_prefix + UNIT[name], power_next, per, False])
                pend_prefix, power_next, per = "", None, False
            elif name in ("text", "mathrm", "mathit"):
                inner, i = brace(u, skip_ws(u, i)); out.append([inner, None, per, False]); per = False
            else:
                warn(f"unknown siunitx unit \\{name}")
                out.append([name, None, per, False]); per = False
        elif u[i] == "^":
            j = i + 1
            if u[j] == "{":
                p, j = brace(u, j)
            else:
                p, j = u[j], j + 1
            if out:
                out[-1][1] = p
            i = j
        elif u[i] == "{":
            inner, i = brace(u, i)
            out.append([inner, None, per, False]); per = False
        else:
            m = re.match(r"[^\\^{ ~]+", u[i:]); i += m.end()
            txt = m.group(0)
            if txt in ("/",):
                per = True; continue
            out.append([pend_prefix + txt, None, per, False]); pend_prefix = ""; per = False
    return out


def units_text(u, math):
    parts = parse_units(u)
    res = ""
    for k, (txt, pw, per, sq) in enumerate(parts):
        sub = None
        if "_" in txt:
            txt, sub = txt.split("_", 1)
        if math:
            t = txt.replace("Ω", "\\Omega ").replace("µ", "\\mu ").replace("°", "^{\\circ}").replace("%", "\\%")
            piece = "\\mathrm{" + t + "}" if not t.startswith(("\\Omega", "\\mu", "^")) else t
            if t.startswith("\\mu ") and len(t) > 4:
                piece = "\\mu\\mathrm{" + t[4:] + "}"
            if sub:
                piece += "_\\mathrm{" + sub + "}"
            if sq:
                piece = "\\sqrt{" + piece + "}"
            if pw:
                piece += "^{" + pw + "}"
        else:
            piece = txt + (f"\\textsubscript{{{sub}}}" if sub else "")
            if sq:
                piece = "√" + piece
            if pw:
                piece += SUP.get(pw, "^" + pw)
        if k > 0:
            res += "/" if per else ("\\," if math else "\u202f")
        elif per:
            res += "1/"
        res += piece
    return res


def fmt_number(x, math):
    """siunitx-like number formatting."""
    x = x.strip().replace("~", "")
    pm = None
    if "+-" in x or "\\pm" in x:
        x, pm = re.split(r"\+-|\\pm", x, maxsplit=1)
        x, pm = x.strip(), pm.strip()
    m = re.fullmatch(r"([+-]?)([0-9.,]*)(?:[eE]([+-]?\d+))?", x)
    if not m:
        return x  # literal (e.g. a macro), leave it
    sign, mant, exp = m.groups()
    if "." in mant:
        ip, fp = mant.split(".", 1)
    else:
        ip, fp = mant, None
    if len(ip) >= 5:
        groups = []
        while len(ip) > 3:
            groups.insert(0, ip[-3:]); ip = ip[:-3]
        groups.insert(0, ip)
        ip = ("\\," if math else "\u2009").join(groups)
    num = ip + ("." + fp if fp is not None else "")
    if sign == "-":
        num = ("-" if math else "−") + num
    if pm:
        num = (num + "\\pm " + pm) if math else (num + " ± " + pm)
    if exp is not None:
        e = str(int(exp))
        if mant in ("", "1") and sign == "":
            core = "10^{" + e + "}"
        else:
            core = num + "\\times 10^{" + e + "}"
        return core if math else "$" + core + "$"
    return num


def replace_siunitx(s):
    """Rewrite \\qty, \\unit, \\num, \\qtyrange, \\numrange, \\ang, \\SI, \\si."""
    out, i = [], 0
    pat = re.compile(r"\\(qtyrange|numrange|qty|unit|num|ang|SI|si)(?![a-zA-Z])")
    while True:
        mask = None
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); break
        out.append(s[i:m.start()])
        mask = math_mask(s[:m.start()] + "X")  # recompute is slow; but files are small
        math = bool(mask[m.start()])
        cmd, j = m.group(1), m.end()
        j = skip_ws(s, j)
        if j < len(s) and s[j] == "[":
            _, j = bracket(s, j)
        args = []
        nargs = {"qtyrange": 3, "numrange": 2, "qty": 2, "SI": 2, "unit": 1, "si": 1, "num": 1, "ang": 1}[cmd]
        for _ in range(nargs):
            j = skip_ws(s, j)
            a, j = brace(s, j); args.append(a)
        sp = "\\," if math else "\u202f"
        if cmd in ("qty", "SI"):
            u = units_text(args[1], math)
            rep = fmt_number(args[0], math) + ("" if u.startswith("°") or u.startswith("^{\\circ}") else sp) + u
        elif cmd in ("unit", "si"):
            rep = units_text(args[0], math)
        elif cmd == "num":
            rep = fmt_number(args[0], math)
        elif cmd == "ang":
            rep = fmt_number(args[0], math) + ("^{\\circ}" if math else "°")
        elif cmd == "numrange":
            rep = fmt_number(args[0], math) + ("\\text{–}" if math else "–") + fmt_number(args[1], math)
        else:  # qtyrange
            rep = (fmt_number(args[0], math) + ("\\text{–}" if math else "–") + fmt_number(args[1], math)
                   + sp + units_text(args[2], math))
        if math and "\u202f" in rep:
            rep = rep.replace("\u202f", "\\,")
        out.append(rep)
        i = j
    return "".join(out)


# ----------------------------------------------------------------------------- environments
def find_env_end(s, name, start):
    """start = index right after \\begin{name}; returns (index of \\end{name}, index after it)."""
    depth, i = 1, start
    b, e = "\\begin{" + name + "}", "\\end{" + name + "}"
    while True:
        nb, ne = s.find(b, i), s.find(e, i)
        if ne < 0:
            raise ValueError("no \\end{%s}" % name)
        if 0 <= nb < ne:
            depth += 1; i = nb + len(b)
        else:
            depth -= 1
            if depth == 0:
                return ne, ne + len(e)
            i = ne + len(e)


def strip_comments(s):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in s.split("\n"))


# ----------------------------------------------------------------------------- references
CREF = {"chapter": ("Chapter", "Chapters"), "section": ("Section", "Sections"),
        "subsection": ("Section", "Sections"), "figure": ("Figure", "Figures"),
        "subfigure": ("Figure", "Figures"), "table": ("Table", "Tables"),
        "equation": ("Equation", "Equations"), "wexample": ("Worked Example", "Worked Examples"),
        "appendix": ("Appendix", "Appendices"), "lstlisting": ("Listing", "Listings"),
        "part": ("Part", "Parts")}


def join_list(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


class Refs:
    def __init__(self, labels, cites):
        self.labels, self.cites = labels, cites

    def num(self, key):
        if key not in self.labels:
            warn(f"unresolved reference {key}")
            return "??", "figure"
        t, n = self.labels[key]
        return n, t

    def link(self, key, text):
        return "\\href{REF:%s}{%s}" % (key, text)

    def cref(self, keys):
        groups = []
        for k in keys:
            n, t = self.num(k)
            if groups and groups[-1][0] == t:
                groups[-1][1].append((k, n))
            else:
                groups.append((t, [(k, n)]))
        parts = []
        for t, lst in groups:
            sing, plur = CREF.get(t, ("Item", "Items"))
            fmt = (lambda n: "(" + n + ")") if t == "equation" else (lambda n: n)
            if len(lst) == 1:
                k, n = lst[0]
                parts.append(self.link(k, sing + "~" + fmt(n)))
            else:
                parts.append(plur + "~" + join_list([self.link(k, fmt(n)) for k, n in lst]))
        return join_list(parts)

    def cite(self, keys):
        nums = []
        for k in keys:
            if k not in self.cites:
                warn(f"unknown citation {k}"); continue
            nums.append((self.cites[k], k))
        nums.sort()
        items, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1][0] == nums[j][0] + 1:
                j += 1
            if j - i >= 2:
                items.append("\\href{REF:cite:%s}{%d}--\\href{REF:cite:%s}{%d}" %
                             (nums[i][1], nums[i][0], nums[j][1], nums[j][0]))
            else:
                items += ["\\href{REF:cite:%s}{%d}" % (k, n) for n, k in nums[i:j + 1]]
            i = j + 1
        return "[" + ", ".join(items) + "]"


def replace_refs(s, refs):
    def rep(m):
        cmd, arg = m.group(1), m.group(2)
        keys = [k.strip() for k in arg.split(",") if k.strip()]
        if cmd in ("cref", "Cref", "autoref"):
            return refs.cref(keys)
        if cmd == "eqref":
            return " and ".join(refs.link(k, "(" + refs.num(k)[0] + ")") for k in keys)
        if cmd == "ref":
            return " and ".join(refs.link(k, refs.num(k)[0]) for k in keys)
        if cmd in ("pageref", "cpageref"):
            return "the PDF"
        if cmd in ("cite", "citep", "citet"):
            return refs.cite(keys)
        return m.group(0)
    s = re.sub(r"\\(cite[pt]?)\[[^]]*\]\{", r"\\\1{", s)
    return re.sub(r"\\(cref|Cref|autoref|eqref|ref|pageref|cpageref|cite|citep|citet)\{([^}]*)\}", rep, s)


# ----------------------------------------------------------------------------- per-chapter preprocessing
BOX_DEFAULT = {"keyeq": "Key equation", "insight": "What this means for your design",
               "pitfall": "Common pitfall", "tryit": "Try it in Python", "derivation": "Derivation",
               "specnote": "Open-BioAFE target", "objectives": "In this chapter you will learn",
               "takeaways": "Key takeaways"}


def preprocess(src, chap_num, refs, tikz_names, page_labels, tikz_start=0):
    """chap_num: '4', 'A', or 'P' (preface). Returns LaTeX ready for pandoc."""
    s = src
    # inline \input{tutorial/tikz/...}
    def inp(m):
        p = BOOK / (m.group(1) + ("" if m.group(1).endswith(".tex") else ".tex"))
        return p.read_text() if p.exists() else ""
    s = re.sub(r"\\input\{(tutorial/[^}]*)\}", inp, s)
    # protect listings
    verb = []
    def protect(m):
        verb.append(m.group(0)); return f"@@VERB{len(verb) - 1}@@"
    s = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", protect, s, flags=re.S)
    s = strip_comments(s)
    # TikZ pictures -> pre-compiled images (tutorial/tikzext/<prefix><k>.pdf)
    m = re.search(r"\\tikzsetfigurename\{([^}]*)\}", s)
    prefix = m.group(1) if m else None
    s = re.sub(r"\\tikzsetfigurename\{[^}]*\}", "", s)
    k, out, i = tikz_start, [], 0
    while True:
        j = s.find("\\begin{tikzpicture}", i)
        if j < 0:
            out.append(s[i:]); break
        out.append(s[i:j])
        _, e = find_env_end(s, "tikzpicture", j + len("\\begin{tikzpicture}"))
        name = f"{prefix}{k}"
        if name not in tikz_names:
            warn(f"missing TikZ image {name}")
        out.append("\\includegraphics{tikzext/%s}" % name)
        k += 1; i = e
    s = "".join(out)
    # tikz-only helper commands
    s = s.replace("\\tikzset{", "\\ignoredarg{")
    # local helper macros
    s = s.replace("\\providecommand", "\\newcommand")
    while "\\appGrp{" in s:                      # balanced braces: the argument holds \cref{..}
        k = s.index("\\appGrp{")
        arg, j = brace(s, k + len("\\appGrp"))
        s = s[:k] + "\\multicolumn{2}{l}{\\textbf{" + arg + "}}\\\\" + s[j:]
    s = re.sub(r"\\newcommand\{\\appGrp\}\[1\]\{.*\n", "\n", s)
    s = re.sub(r"\\rowcolor\{[^}]*\}", "", s)
    s = re.sub(r"\\renewcommand\{\\(arraystretch|topfraction|bottomfraction|textfraction|floatpagefraction|thewexample)\}\{[^}]*\}", "", s)
    s = re.sub(r"\\setlength\{[^}]*\}\{[^}]*\}", "", s)
    for c in ("suppressfloats", "noindent", "centering", "raggedright", "smallskip", "medskip", "bigskip",
              "clearpage", "newpage", "FloatBarrier", "sffamily", "small", "footnotesize", "scriptsize"):
        s = re.sub(r"\\" + c + r"(?![a-zA-Z])(\[[^]]*\])?", "", s)
    s = re.sub(r"\\vspace\*?\{[^}]*\}", "", s)
    s = s.replace("\\textperiodcentered", "·")
    # siunitx
    s = replace_siunitx(s)
    # chapter lead, figure credits, TODO
    s = re.sub(r"\\chapterlead\{", r"\\leadpara{", s)
    def figsrc(m):
        return ""
    # boxes: give every box an explicit title div
    def boxes(s):
        out, i = [], 0
        pat = re.compile(r"\\begin\{(keyeq|example|insight|pitfall|tryit|derivation|specnote|objectives|takeaways)\}")
        exn = 0
        while True:
            m = pat.search(s, i)
            if not m:
                out.append(s[i:]); break
            out.append(s[i:m.start()])
            name, j = m.group(1), m.end()
            title = None
            if name == "example":
                title, j = brace(s, skip_ws(s, j))
                exn += 1
                lab = re.match(r"\s*\\label\{([^}]*)\}", s[j:])
                n = f"P.{exn}" if chap_num == "P" else f"{chap_num}.{exn}"
                if lab:
                    t, n2 = refs.labels.get(lab.group(1), ("wexample", n))
                    if n2 != n:
                        warn(f"example numbering mismatch {lab.group(1)}: {n} vs {n2}")
                        n = n2
                title = f"Worked Example {n} · {title}"
            else:
                jj = skip_ws(s, j)
                if jj < len(s) and s[jj] == "[":
                    title, j = bracket(s, jj)
                if name == "keyeq":
                    title = "Key equation" + (" · " + title if title else "")
                elif not title:
                    title = BOX_DEFAULT[name]
            out.append("\\begin{box%s}\\begin{boxtitle}%s\\end{boxtitle}" % (name, title))
            i = j
        s = "".join(out)
        for n in BOX_DEFAULT.keys() | {"example"}:
            s = s.replace("\\end{%s}" % n, "\\end{box%s}" % n)
        return s
    s = boxes(s)
    # minipages -> width-tagged divs
    def minip(m):
        w = float(m.group(2) or 1.0)
        return "\\begin{mpcolW%d}" % round(w * 100)
    s = re.sub(r"\\begin\{minipage\}(?:\[[^]]*\])*\{([0-9.]*)\\(?:line|text)width\}", lambda m: "\\begin{mpcolW%d}" % round(float(m.group(1) or 1) * 100), s)
    widths = iter(re.findall(r"\\begin\{mpcolW(\d+)\}", s))
    # match the end tags in order (minipages are not nested in our sources)
    s = re.sub(r"\\end\{minipage\}", lambda m: "\\end{mpcolW%s}" % next(widths), s)
    # center env -> plain
    s = s.replace("\\begin{center}", "").replace("\\end{center}", "")
    # table column specs: pandoc 3.1 does not know the style's custom L/C columns, and >{..}, <{..},
    # @{..}, !{..} decorations make it give up on the whole table -> reduce to plain l/c/r/p/X columns
    def colspec(m):
        head, spec_start = m.group(0), m.end()
        spec, j = brace(s_ref[0], spec_start - 1)
        spec2 = re.sub(r"[<>@!]\{(?:[^{}]|\{[^{}]*\})*\}", "", spec)
        # p{..}/X/L/C -> l: pandoc 3.1.3 mis-parses p{..} columns when a page has two such tables,
        # and the browser sizes HTML table columns from their content anyway
        spec2 = re.sub(r"[pmb]\{[^{}]*\}", "l", spec2)
        spec2 = re.sub(r"\b[LCX]\b", "l", spec2)
        spec2 = re.sub(r"\s+", " ", spec2).strip()
        return head[:-1] + "{" + spec2 + "}", j
    s_ref = [s]
    out, i = [], 0
    for m in re.finditer(r"\\begin\{tabularx\}\{[^}]*\}\{|\\begin\{tabular\*?\}(?:\[[^]]*\])?\{", s):
        if m.start() < i:
            continue
        rep, j = colspec(m)
        out.append(s[i:m.start()]); out.append(rep); i = j
    out.append(s[i:]); s = "".join(out)
    # tables: pandoc does not always keep the label as an id -> add explicit anchors
    def tab_targets(m):
        labs = re.findall(r"\\label\{([^}]*)\}", m.group(0))
        return "".join("\\hypertarget{%s}{}" % l for l in labs) + m.group(0)
    s = re.sub(r"\\begin\{(table|figure)\*?\}.*?\\end\{\1\*?\}", tab_targets, s, flags=re.S)
    # numbering: chapter title, sections, figures, tables, equations
    s = number_things(s, chap_num, refs)
    # cross references and citations
    s = replace_refs(s, refs)
    # restore listings (Python by default, shell style -> bash)
    def restore(m):
        v = verb[int(m.group(1))]
        opt = re.match(r"\\begin\{lstlisting\}(\[[^]]*\])?", v)
        o = opt.group(1) or ""
        lang = "bash" if "shell" in o else ("text" if "language=" not in o and "style=plain" in o else "Python")
        lab = re.search(r"label=\{?([^,\]}]*)", o)
        cap = re.search(r"caption=\{([^}]*)\}", o)
        body = v[opt.end():]
        head = ""
        if lab:
            n, _ = refs.num(lab.group(1))
            head = "\\hypertarget{%s}{}" % lab.group(1)
            if cap:
                head += "\\begin{lstcaption}@@LST:Listing %s.@@ %s\\end{lstcaption}" % (n, cap.group(1))
        return head + "\\begin{lstlisting}[language=%s]" % lang + body
    s = re.sub(r"@@VERB(\d+)@@", restore, s)
    return s


def number_things(s, chap_num, refs):
    """Insert chapter/section numbers, caption numbers and equation tags.

    Mirrors LaTeX's counters: \\caption steps the counter of the enclosing float,
    \\captionof{k} steps counter k, subfigure captions get (a), (b), ... Every number is
    cross-checked against the .aux file through the label that follows the caption."""
    out, i = [], 0
    sec = sub = 0
    cnt = {"figure": 0, "table": 0}
    float_kind, in_sub, subn = None, False, 0
    tok = re.compile(r"\\(chapter|section|subsection)(\*?)(?=\s*[\[{])"
                     r"|\\begin\{(equation|align|gather)\}"
                     r"|\\(begin|end)\{(figure\*?|table\*?|subfigure)\}"
                     r"|\\captionof\{(figure|table)\}|\\caption(?![a-zA-Z])")

    def check(kind, n, after):
        m = re.match(r"\s*(?:\\end\{[a-z]+\}\s*)?\\label\{([^}]*)\}", after) or \
            re.search(r"\\label\{([^}]*)\}", after[:400].split("\\caption")[0])
        if m:
            t, n2 = refs.labels.get(m.group(1), (kind, n))
            if t in ("figure", "table") and n2 != n:
                warn(f"{kind} number mismatch for {m.group(1)}: computed {n}, aux {n2}")
                return n2, True
        return n, False

    while True:
        m = tok.search(s, i)
        if not m:
            out.append(s[i:]); break
        out.append(s[i:m.start()])
        if m.group(1):
            cmd, star = m.group(1), m.group(2)
            j = skip_ws(s, m.end())
            if s[j] == "[":
                _, j = bracket(s, j)
            title, j = brace(s, skip_ws(s, j))
            if cmd == "chapter":
                title = title.replace("\\newline", "\\\\")   # pandoc drops \newline here, gluing the words
                if chap_num == "P":
                    out.append("\\chapter{%s}" % title)
                else:
                    lab = f"Appendix {chap_num}" if chap_num.isalpha() else f"Chapter {chap_num}"
                    out.append("\\chapter{@@CHAP:%s@@ %s}" % (lab, title))
            elif not star and chap_num != "P":
                if cmd == "section":
                    sec += 1; sub = 0; n = f"{chap_num}.{sec}"
                else:
                    sub += 1; n = f"{chap_num}.{sec}.{sub}"
                out.append("\\%s{@@SEC:%s@@ %s}" % (cmd, n, title))
            else:
                out.append("\\%s%s{%s}" % (cmd, star, title))
            i = j
        elif m.group(3):                      # numbered display maths -> starred + \\tag
            env = m.group(3)
            end_idx, end_after = find_env_end(s, env, m.end())
            body = s[m.end():end_idx]
            labs = re.findall(r"\\label\{([^}]*)\}", body)
            anchors = "".join("\\hypertarget{%s}{}" % l for l in labs)
            pieces = re.split(r"(\\\\)", body) if env != "equation" else [body]
            new = []
            for pc in pieces:
                lm = re.search(r"\\label\{([^}]*)\}", pc)
                if lm:
                    pc = re.sub(r"\s*\\label\{[^}]*\}", "", pc).rstrip() + " \\tag{%s}" % refs.num(lm.group(1))[0]
                new.append(pc)
            out.append(anchors + "\\begin{%s*}" % env + "".join(new) + "\\end{%s*}" % env)
            i = end_after
        elif m.group(4):                      # float begin/end
            be, env = m.group(4), m.group(5)
            if env == "subfigure":
                in_sub = (be == "begin")
            elif be == "begin":
                float_kind = "figure" if env.startswith("figure") else "table"; subn = 0
            else:
                float_kind = None
            out.append(m.group(0)); i = m.end()
        else:                                 # \\caption or \\captionof{k}
            kind = m.group(6)
            j = skip_ws(s, m.end())
            if j < len(s) and s[j] == "[":
                _, j = bracket(s, j)
            cap, j = brace(s, skip_ws(s, j))
            if kind is None and in_sub:
                subn += 1
                out.append("\\caption{@@SUB:(%s)@@ %s}" % ("abcdefghij"[subn - 1], cap))
            else:
                k = kind or float_kind or "figure"
                cnt[k] += 1
                n = f"{cnt[k]}" if chap_num == "P" else f"{chap_num}.{cnt[k]}"
                n, fixed = check(k, n, s[j:])
                if fixed:
                    cnt[k] = int(n.split(".")[-1])
                tag = ("FIG:Figure " if k == "figure" else "TAB:Table ") + n + "."
                if kind:  # \\captionof -> stand-alone caption block
                    out.append("\\begin{captionblock}@@%s@@ %s\\end{captionblock}" % (tag, cap))
                else:
                    out.append("\\caption{@@%s@@ %s}" % (tag, cap))
            i = j
    return "".join(out)


# ----------------------------------------------------------------------------- pandoc
PRELUDE = r"""
\newcommand{\OB}{Open-BioAFE}\newcommand{\sgx}{SG13G2}\newcommand{\ie}{i.e., }\newcommand{\eg}{e.g., }
\newcommand{\dB}{\,\mathrm{dB}}\newcommand{\SNR}{\mathrm{SNR}}\newcommand{\CMRR}{\mathrm{CMRR}}
\newcommand{\ENOB}{\mathrm{ENOB}}\newcommand{\NEF}{\mathrm{NEF}}\newcommand{\PEF}{\mathrm{PEF}}
\newcommand{\Vdd}{V_\mathrm{DD}}\newcommand{\Vcm}{V_\mathrm{cm}}\newcommand{\Vdm}{V_\mathrm{dm}}
\newcommand{\Zin}{Z_\mathrm{in}}\newcommand{\Zcm}{Z_\mathrm{cm}}\newcommand{\Ze}{Z_\mathrm{e}}
\newcommand{\Ehc}{E_\mathrm{hc}}\newcommand{\vn}{v_\mathrm{n}}\newcommand{\fs}{f_\mathrm{s}}
\newcommand{\fc}{f_\mathrm{c}}\newcommand{\gm}{g_\mathrm{m}}\newcommand{\RL}{R_\mathrm{L}}
\newcommand{\CL}{C_\mathrm{L}}\newcommand{\sgn}{\operatorname{sgn}}\newcommand{\erfc}{\operatorname{erfc}}
\newcommand{\code}[1]{\texttt{#1}}\newcommand{\tool}[1]{\textbf{#1}}\newcommand{\Ohm}{\ensuremath{\Omega}}
\newcommand{\leadpara}[1]{\begin{chapterlead}#1\end{chapterlead}}
\newcommand{\figsrc}[1]{\begin{figcredit}#1\end{figcredit}}
\newcommand{\TODO}[1]{\textbf{[TODO: #1]}}
\newcommand{\ignoredarg}[1]{}
\newcommand{\textcolor}[2]{#2}
"""


def run_pandoc(tex):
    r = subprocess.run(["pandoc", "-f", "latex", "-t", "html5", "--mathjax", "--wrap=none",
                        "--top-level-division=chapter", "--highlight-style=pygments"],
                       input=PRELUDE + tex, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)
    for line in r.stderr.splitlines():
        if line.strip() and "Could not convert TeX math" in line or "Skipped" in line:
            warn("pandoc: " + line.strip()[:200])
    return r.stdout


# ----------------------------------------------------------------------------- figures
def convert_figures(names):
    """names: set of graphic names as written in the LaTeX (e.g. 'ch03_loss', 'tikzext/03_channel-2')."""
    FIGOUT.mkdir(parents=True, exist_ok=True)
    info = {}
    for nm in sorted(names):
        base = nm.split("/")[-1]
        cands = [SRC / "tikzext" / (base + ".pdf")] if nm.startswith("tikzext/") else \
                [SRC / "figs" / (base + ".pdf"), SRC / "figs" / (base + ".png"), SRC / "canva" / (base + ".png"),
                 SRC / "slides" / (base + ".png")]
        src = next((c for c in cands if c.exists()), None)
        if src is None:
            warn(f"figure not found: {nm}"); continue
        sub = "tikz" if nm.startswith("tikzext/") else ""
        dst_dir = FIGOUT / sub if sub else FIGOUT
        dst_dir.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".png":
            dst = dst_dir / (base + ".png")
            shutil.copy(src, dst)
            from struct import unpack
            with open(src, "rb") as f:
                head = f.read(24)
            w = unpack(">I", head[16:20])[0]
            width_px = min(800, round(w / 2))       # PNG sources are drawn at about 2x
        else:
            pi = subprocess.run(["pdfinfo", str(src)], capture_output=True, text=True).stdout
            mm = re.search(r"Page size:\s*([\d.]+) x ([\d.]+)", pi)
            wpt = float(mm.group(1))
            width_px = round(min(800, wpt * 96 / 72 * 1.25))
            svg = dst_dir / (base + ".svg")
            dst = svg
            stale = not svg.exists() or svg.stat().st_mtime < src.stat().st_mtime
            if stale:
                subprocess.run(["pdftocairo", "-svg", str(src), str(svg)], check=True)
            if svg.stat().st_size > 700_000:      # dense rasters / many traces -> PNG is smaller
                png = dst_dir / (base + ".png")
                if not png.exists() or png.stat().st_mtime < src.stat().st_mtime:
                    dpi = max(150, min(300, round(width_px * 2 / (wpt / 72))))
                    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", str(src),
                                    str(png.with_suffix(""))], check=True)
                svg.unlink(); dst = png
        info[nm] = ("/assets/figs/" + (sub + "/" if sub else "") + dst.name, width_px)
    return info


# ----------------------------------------------------------------------------- pages
def url_for(page):
    return page["permalink"]


def liquid_url(path):
    return "{% endraw %}{{ '" + path + "' | relative_url }}{% raw %}"


def postprocess(htmltxt, page, label_page, fig_info, pages_by_slug):
    h = htmltxt
    # sentinels
    h = re.sub(r"@@CHAP:([^@]*)@@\s*", r'<span class="chapnum">\1</span>', h)
    h = re.sub(r"@@SEC:([^@]*)@@\s*", r'<span class="secnum">\1</span>', h)
    h = re.sub(r"@@(FIG|TAB|LST):([^@]*)@@\s*", r'<span class="capnum">\2</span> ', h)
    h = re.sub(r"@@SUB:([^@]*)@@\s*", r'<span class="capnum">\1</span> ', h)
    # boxes / divs produced from environments
    h = re.sub(r'<div class="box(keyeq|example|insight|pitfall|tryit|derivation|specnote|objectives|takeaways)">',
               r'<div class="tbox tbox-\1">', h)
    h = h.replace('<div class="boxtitle">', '<div class="tbox-title">')
    h = re.sub(r'<div class="mpcolW(\d+)">', lambda m: '<div class="mpcol" style="--w:%d%%">' % int(m.group(1)), h)
    # images
    def img(m):
        nm = html.unescape(m.group(1))
        if nm not in fig_info:
            return m.group(0)
        path, w = fig_info[nm]
        return '<img src="%s" style="width:%dpx" alt="" loading="lazy"' % (liquid_url(path), w)
    h = re.sub(r'<img src="([^"]*)"', img, h)
    h = re.sub(r'(<img [^>]*?) style="width:[0-9.]+%"', r"\1", h)      # pandoc's own width
    # alt text = first sentence (bold part) of the figure caption
    def alt(m):
        fig = m.group(0)
        cap = re.search(r"<figcaption>(.*?)</figcaption>", fig, re.S)
        txt = ""
        if cap:
            strong = re.search(r"<strong>(.*?)</strong>", cap.group(1), re.S)
            txt = re.sub(r"<[^>]+>", "", (strong or cap).group(1))
            txt = re.sub(r"\\[()\[\]]", "", txt)
            txt = html.escape(html.unescape(re.sub(r"\s+", " ", txt)).strip()[:180], quote=True)
        return fig.replace('alt=""', 'alt="%s"' % txt)
    h = re.sub(r"<figure[^>]*>.*?</figure>", alt, h, flags=re.S)
    # links
    def link(m):
        target = html.unescape(m.group(1))
        if target.startswith("cite:"):
            return 'href="%s#ref-%s"' % (liquid_url("/references/"), target[5:])
        pg = label_page.get(target)
        if pg is None:
            warn(f"label without page: {target}"); return 'href="#"'
        anchor = "" if target.startswith(("ch:", "app:")) and pg["anchor_is_page"].get(target) else "#" + target
        if pg is page:
            return 'href="%s"' % (anchor or "#")
        return 'href="%s%s"' % (liquid_url(pg["permalink"]), anchor)
    h = re.sub(r'href="REF:([^"]*)"', link, h)
    # KaTeX has no \ensuremath / \scalebox
    h = re.sub(r"\\ensuremath\{([^{}]*)\}", r"\1", h)
    h = re.sub(r"\\scalebox\{[^}]*\}\{\$?([^}$]*)\$?\}", r"\\large \1", h)
    # pandoc writes gather*/align* as gathered/aligned; KaTeX needs gather/align for per-row \tag
    def multitag(m):
        env, inner = m.group(1), m.group(2)
        if "\\tag" not in inner:
            return m.group(0)
        e2 = {"gathered": "gather", "aligned": "align"}[env]
        return "\\begin{%s}%s\\end{%s}" % (e2, inner, e2)
    h = re.sub(r"\\begin\{(gathered|aligned)\}(.*?)\\end\{\1\}", multitag, h, flags=re.S)
    # drop duplicate ids (keep the first)
    seen = set()
    def dedup(m):
        if m.group(1) in seen:
            return ""
        seen.add(m.group(1)); return m.group(0)
    h = re.sub(r' id="([^"]+)"', dedup, h)
    # strip pandoc's leftover data attributes on spans
    h = re.sub(r' label="[^"]*"', "", h)
    return h


def front_matter(**kw):
    lines = ["---"]
    for k, v in kw.items():
        if v is None:
            continue
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def nav_footer(prev, nxt, page=None):
    def a(p, cls, arrow):
        if not p:
            return '<span></span>'
        return '<a class="pn-link %s" href="%s"><small>%s</small>%s</a>' % (
            cls, liquid_url(p["permalink"]), arrow, html.escape(p["title"]))
    src = ""
    if page and page.get("file"):
        src = ('<p class="page-source">Generated from <a href="https://github.com/bricd-org/biomedical-ic-design/blob/main/'
               'book/tutorial/chapters/%s.tex">book/tutorial/chapters/%s.tex</a>. Figure, table and equation '
               'numbers match the <a href="%s">PDF edition</a>.</p>\n' %
               (page["file"], page["file"], liquid_url("/assets/pdf/" + PDF_NAME)))
    return ('\n<nav class="prev-next" aria-label="Chapter navigation">%s%s</nav>\n%s' %
            (a(prev, "prev", "← Previous"), a(nxt, "next", "Next →"), src))


def references_page(cites):
    bbl = (BUILD / "tutorial.bbl").read_text(errors="replace")
    body = bbl.split("\\begin{thebibliography}", 1)[1].rsplit("\\end{thebibliography}", 1)[0]
    body = body.split("\n", 1)[1]
    entries = re.split(r"\\bibitem\[", body)[1:]
    items = []
    for e in entries:
        _, j = bracket("[" + e, 0)
        rest = ("[" + e)[j:]
        key, k = brace(rest, 0)
        text = rest[k:]
        text = re.sub(r"\\newblock\s*", " ", text)
        text = re.sub(r"\\providecommand.*", "", text)
        text = text.replace("\\urlprefix", "").replace("\\natexlab", "")
        items.append((cites.get(key, 0), key, text.strip()))
    items.sort()
    tex = "\\begin{enumerate}\n" + "\n".join("\\item \\hypertarget{ref-%s}{}%s" % (k, t) for _, k, t in items) + "\n\\end{enumerate}"
    h = run_pandoc(tex)
    h = h.replace("<ol>", '<ol class="references">', 1)
    h = re.sub(r'<li><div id="(ref-[^"]*)">\s*</div>\s*', r'<li id="\1">', h)
    return h


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-latex", action="store_true", help="reuse book/_build instead of compiling")
    args = ap.parse_args()
    if not args.no_latex or not (BUILD / "tutorial.aux").exists():
        build_latex()
    labels, cites = read_aux()
    refs = Refs(labels, cites)
    print(f"{len(labels)} labels, {len(cites)} citations")
    tikz_names = {p.stem for p in (SRC / "tikzext").glob("*.pdf")}

    # ---- pages in reading order
    items = book_structure()
    pages, parts = [], []
    pages.append(dict(file="00_preface", kind="preface", num="P", title="Preface", slug="preface",
                      permalink="/preface/", part=None))
    in_app, chap_counter, app_letter = False, 0, 0
    for it in items:
        if it[0] == "part":
            parts.append(dict(n=it[1], title=it[2], blurb=it[3]))
        elif it[0] == "appendix":
            in_app = True
        elif it[0] == "file":
            fname, partno = it[1], it[2]
            src = (SRC / "chapters" / (fname + ".tex")).read_text()
            # split files that hold several \chapter (the appendices)
            chunks = re.split(r"(?=\\chapter[\[{])", src)
            head = chunks[0] if not chunks[0].lstrip().startswith("\\chapter") else ""
            for ch in [c for c in chunks if c.lstrip().startswith("\\chapter")]:
                j = len("\\chapter")
                short = None
                if ch[j] == "[":
                    short, j = bracket(ch, j)
                title = short or brace(ch, j)[0]
                if in_app:
                    app_letter += 1; num = "ABCDEFGH"[app_letter - 1]
                    slug = num.lower() + "-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
                    pages.append(dict(file=fname, src=head + ch, kind="appendix", num=num, title=title,
                                      slug=slug, permalink=f"/appendix/{num.lower()}/", part="app"))
                else:
                    chap_counter += 1; num = str(chap_counter)
                    slug = f"{chap_counter:02d}-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
                    pages.append(dict(file=fname, src=head + ch, kind="chapter", num=num, title=title,
                                      slug=slug, permalink=f"/part-{partno}/ch{chap_counter:02d}/", part=partno))
    pages[0]["src"] = (SRC / "chapters" / "00_preface.tex").read_text()

    # ---- labels -> pages
    label_page = {}
    for p in pages:
        p["anchor_is_page"] = {}
        for l in re.findall(r"\\label\{([^}]*)\}", strip_comments(p["src"])):
            label_page[l] = p
        for l in re.findall(r"\\begin\{lstlisting\}\[[^]]*label=\{?([^,\]}]+)", p["src"]):
            label_page[l.strip()] = p
        m = re.search(r"\\chapter\{[^\n]*?\}\s*\\label\{([^}]*)\}", p["src"])
        if m:
            p["anchor_is_page"][m.group(1)] = True
    for l in labels:
        if l not in label_page and not l.startswith("part"):
            pass

    # ---- preprocess + pandoc
    graphics = set()
    for p in pages:
        tex = preprocess(p["src"], p["num"], refs, tikz_names, label_page)
        graphics |= set(re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]*)\}", tex))
        p["html"] = run_pandoc(tex)
        print(f"  converted {p['permalink']}")
    fig_info = convert_figures(graphics)
    print(f"{len(fig_info)} figures")

    # ---- write pages
    for d in ("chapters", "appendices", "parts"):
        out = ROOT / d
        if out.exists():
            shutil.rmtree(out)
        out.mkdir()
    order = 0
    for idx, p in enumerate(pages):
        body = postprocess(p["html"], p, label_page, fig_info, None)
        prev = pages[idx - 1] if idx > 0 else None
        nxt = pages[idx + 1] if idx + 1 < len(pages) else None
        body = "{% raw %}\n" + body + nav_footer(prev, nxt, p) + "{% endraw %}\n"
        if p["kind"] == "preface":
            fm = front_matter(title="Preface", nav_order=1, permalink=p["permalink"])
            path = ROOT / "preface.html"
        elif p["kind"] == "chapter":
            pt = parts[p["part"] - 1]
            fm = front_matter(title=f"{p['num']}. {p['title']}", parent=f"Part {ROMAN[pt['n'] - 1]} · {pt['title']}",
                              nav_order=int(p["num"]), permalink=p["permalink"])
            path = ROOT / "chapters" / (p["slug"] + ".html")
        else:
            fm = front_matter(title=f"{p['num']}. {p['title']}", parent="Appendices",
                              nav_order=ord(p["num"]) - 64, permalink=p["permalink"])
            path = ROOT / "appendices" / (p["slug"] + ".html")
        p["title_full"] = p["title"]
        path.write_text(fm + body)
    for pt in parts:
        chs = [p for p in pages if p["kind"] == "chapter" and p["part"] == pt["n"]]
        lst = "\n".join("- [%s. %s](%s)" % (c["num"], c["title"], "{{ '%s' | relative_url }}" % c["permalink"]) for c in chs)
        txt = front_matter(title=f"Part {ROMAN[pt['n'] - 1]} · {pt['title']}", nav_order=pt["n"] + 1,
                           has_children=True, has_toc=False, permalink=f"/part-{pt['n']}/")
        txt += f'\n<p class="part-label">Part {ROMAN[pt["n"] - 1]}</p>\n\n# {pt["title"]}\n{{: .part-title }}\n\n{pt["blurb"]}\n{{: .part-blurb }}\n\n## Chapters in this part\n\n{lst}\n'
        (ROOT / "parts" / f"part-{pt['n']}.md").write_text(txt)
    apps = [p for p in pages if p["kind"] == "appendix"]
    lst = "\n".join("- [%s. %s](%s)" % (a["num"], a["title"], "{{ '%s' | relative_url }}" % a["permalink"]) for a in apps)
    (ROOT / "appendices" / "index.md").write_text(
        front_matter(title="Appendices", nav_order=len(parts) + 3, has_children=True, has_toc=False,
                     permalink="/appendix/") +
        "\n# Appendices\n\nFormula sheet, biosignal reference tables, design-review checklists, a glossary and further reading.\n\n" + lst + "\n")
    # references
    refs_html = references_page(cites)
    (ROOT / "references.html").write_text(
        front_matter(title="References", nav_order=len(parts) + 4, permalink="/references/") +
        "{% raw %}\n<h1>References</h1>\n<p>Numbered as in the PDF edition.</p>\n" +
        postprocess(refs_html, {}, label_page, fig_info, None) + "{% endraw %}\n")
    # the PDF
    (ROOT / "assets" / "pdf").mkdir(parents=True, exist_ok=True)
    shutil.copy(BUILD / "tutorial.pdf", ROOT / "assets" / "pdf" / PDF_NAME)
    # cover image for the home page
    cover = ROOT / "assets" / "images" / "cover.png"
    cover.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-png", "-r", "60", "-f", "1", "-l", "1", "-singlefile",
                    str(BUILD / "tutorial.pdf"), str(cover.with_suffix(""))], check=True)
    print(f"done: {len(pages)} pages, {len(WARN)} warnings")
    (ROOT / "tools" / "last_build_warnings.txt").write_text("\n".join(WARN) + "\n")


if __name__ == "__main__":
    main()
