# Open-BioAFE Tutorial — *Designing a Biopotential Acquisition Chip from Scratch*

A design tutorial for undergraduate and early-graduate engineers building an open-source
8-channel ECG/EEG/EMG analog front-end with a 12-bit SAR and a 16-bit incremental ΔΣ ADC in the
IHP SG13G2 130 nm SiGe BiCMOS open PDK, written for [BRICD](https://www.thebricd.org).

The tutorial is a website made of Markdown pages, built with Jekyll and the just-the-docs theme,
and published at <https://www.thebricd.org/biomedical-ic-design/>.

**Status: work in progress (draft v0.1, November 2026).**

| Part | Chapters | State |
|---|---|---|
| Preface | audience, reading paths, how the labs work | written |
| I. Foundations | 1–4: why biomedical ICs, bioelectric signals, electrodes, interference and safety | written |
| II. The analog front-end | 5–12 | outline |
| III. Data converters | 13–22 | outline |
| IV. Biosignal processing and systems | 23–28 | outline |
| V. Putting it together | 29–31 (architecture, open-source flow, 15 labs) | outline |
| Appendices | A–E | to do |

Each outline chapter lists its topics, the design question it answers, its labs and its reading.

## Repository layout

```
index.md                home page
preface.md              preface
chapters/NN_name.md     one page per chapter (front matter sets its menu place and URL)
parts/part-N.md         one page per part (the chapter list in the menu)
references.md           the reference list, drawn from _data/references.yml
_data/references.yml    every reference; a citation's number is its position in this file
_includes/cite.html     numbered citations: {% include cite.html keys="harrison2003" %}
_includes/prev-next.html  previous/next links, from the `chapter:` number in the front matter
assets/figs/            figures (SVG)
figsrc/                 Python scripts that draw the plots into assets/figs/ (house style: bricdstyle.py)
labs/python/            lab scripts; biosig.py is shared by the labs and the figure scripts
data/                   download scripts only; datasets stay on PhysioNet/NinaPro
_config.yml, _sass/, _includes/   Jekyll + just-the-docs theme settings (BRICD colours and fonts)
.github/workflows/pages.yml       builds and deploys the site on every push to main
```

## Writing a page

Pages are kramdown (GitHub-flavoured Markdown). Copy the structure of an existing chapter:

- **Maths:** `$$...$$`, inline in a sentence or as its own paragraph for a display equation;
  KaTeX renders it. Write `ΔΣ`, `µV` and similar as plain Unicode in text.
- **Boxes:** `<div class="tbox tbox-insight" markdown="1">`, a `<div class="tbox-title">` line, a
  blank line, the content, and `</div>`. Box types: `keyeq`, `example`, `insight`, `pitfall`,
  `tryit`, `derivation`, `specnote`, `objectives`, `takeaways`.
- **Links between pages:** `[Chapter 6]({% link chapters/06_noise.md %})`. The build fails if the
  file does not exist, so broken links are caught.
- **Citations:** `{% include cite.html keys="key1,key2" %}`. Add new references at the end of
  `_data/references.yml` so existing numbers do not change.
- **Figures:** `<figure id="fig-2-1"><img src="{{ '/assets/figs/NAME.svg' | relative_url }}" alt="...">`
  with a `<figcaption>`; tables get a caption paragraph followed by `{: .tabcaption #tab-2-1 }`.

## Previewing

Jekyll 4.4 needs Ruby 3.1 or newer. With Ruby installed:

```bash
bundle install && bundle exec jekyll serve
```

Or, without a local Ruby, in Docker:

```bash
docker run --rm -p 4000:4000 -v "$PWD":/site -v bioafe-gems:/usr/local/bundle -w /site ruby:3.3 bash -c "bundle install && bundle exec jekyll serve --host 0.0.0.0"
```

Then open <http://localhost:4000/biomedical-ic-design/>.

To redraw the figures (NumPy, SciPy, Matplotlib):

```bash
cd figsrc && for f in ch0*_figs.py; do python "$f"; done
```

## Next steps

1. Write Chapter 31 Labs 1–2 in full, and the appendices.
2. Write `labs/python/lab1_biosignal_explorer.py` and `lab2_electrodes_interference.py`.

## AI assistance and corrections

This tutorial is being developed with the help of AI tools and may contain mistakes. If you spot
one, please email [bricd.org@gmail.com](mailto:bricd.org@gmail.com) or open an issue.

## Licence

© 2026 the Open-BioAFE Tutorial authors, BRICD. Content (text, figures, website pages) is
licensed under [CC BY 4.0](LICENSE); code (lab scripts, figure scripts, site configuration) under
the [MIT licence](LICENSE-CODE). Neither covers the BRICD name and logo, or the works the tutorial
cites.
