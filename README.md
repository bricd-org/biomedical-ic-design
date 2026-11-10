# Open-BioAFE Tutorial — *Designing a Biopotential Acquisition Chip from Scratch*

A design tutorial for undergraduate and early-graduate engineers building an open-source
8-channel ECG/EEG/EMG analog front-end with a 12-bit SAR and a 16-bit incremental ΔΣ ADC in the
IHP SG13G2 130 nm SiGe BiCMOS open PDK, written for [BRICD](https://www.thebricd.org). It follows
the same format as the [Open-SERDES Tutorial](https://www.thebricd.org/serdes-tutorial/): a LaTeX
book that is also published as a website.

**Status: work in progress (draft v0.1, November 2026).** The site is not published yet.

| Part | Chapters | State |
|---|---|---|
| Preface | audience, reading paths, how the labs work | written |
| I. Foundations | 1–4: why biomedical ICs, bioelectric signals, electrodes, interference and safety | figures and models done, text in progress |
| II. The analog front-end | 5–12 | outline |
| III. Data converters | 13–22 | outline |
| IV. Biosignal processing and systems | 23–28 | outline |
| V. Putting it together | 29–31 (architecture, open-source flow, 15 labs) | outline (29–30); 31 to do |
| Appendices | A–E | to do |

Each outline chapter lists its topics, the design question it answers, its labs and its reading.

## Repository layout

```
book/                   LaTeX source of the book (single source of truth)
  tutorial.tex            main file (pdfLaTeX + BibTeX)
  tutorial/biotut.sty     house style (from the Open-SERDES tutorial)
  tutorial/chapters/      one .tex file per chapter
  tutorial/figsrc/        Python scripts that draw every plot (house style: bricdstyle.py)
  tutorial/figs/          the generated plots (PDF)
  tutorial/bib/core.bib   references
labs/python/            lab scripts; biosig.py is shared by the labs and the figure scripts
data/                   download scripts only; datasets stay on PhysioNet/NinaPro
tools/build_site.py     converts book/ into the website pages (needs TeX Live, pandoc >= 3, poppler)
_config.yml, _sass/, _includes/   Jekyll + just-the-docs theme settings (BRICD colours and fonts)
.github/workflows/pages.yml       builds and deploys the site (manual trigger until v0.1 is ready)
```

To redraw the figures (NumPy, SciPy, Matplotlib):

```bash
cd book/tutorial/figsrc && for f in ch0*_figs.py; do python "$f"; done
```

## Next steps

1. Write Chapters 1–4, Chapter 31 (labs index, Labs 1–2 in full) and the appendices.
2. Write `labs/python/lab1_biosignal_explorer.py` and `lab2_electrodes_interference.py`.
3. Write the home page (`index.md`) and the labs page, run `tools/build_site.py`, preview with
   `bundle exec jekyll serve`, then switch the Pages workflow back to deploy on push.

## AI assistance and corrections

This tutorial is being developed with the help of AI tools and may contain mistakes. If you spot
one, please email [bricd.org@gmail.com](mailto:bricd.org@gmail.com) or open an issue.

## Licence

© 2026 the Open-BioAFE Tutorial authors, BRICD. Content (text, figures, PDFs, website pages) is
licensed under [CC BY 4.0](LICENSE); code (lab scripts, figure scripts, build tools, site
configuration) under the [MIT licence](LICENSE-CODE). Neither covers the BRICD name and logo, or
the works the tutorial cites.
