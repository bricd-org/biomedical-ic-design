# HANDOFF — Open-BioAFE Tutorial (pick up here)

Last session: 10 November 2026. Last commit on `main`: `fe63f09` (pushed to
`git@github.com:bricd-org/biomedical-ic-design.git`). This file is not committed yet.

## 1. The goal

Build a course website + PDF book like the Open-SERDES tutorial
(`/Users/kithminrw/SerDes Project/serdes-tutorial`, live at https://www.thebricd.org/serdes-tutorial/),
following the curriculum document *"Biomedical IC Design Tutorial — Curriculum & Labs"*
(10 Nov 2026, Kithmin Wickremasinghe). That PDF was in `~/Downloads` and has since been moved;
everything needed from it is captured in this file (section 8) and in the outline chapters.

- Title: **Open-BioAFE: Designing a Biopotential Acquisition Chip from Scratch**
- 5 parts, 31 chapters, 15 labs, appendices A–E. One reference chip: 8-channel ECG/EEG/EMG
  front-end + 12-bit async SAR + 2nd-order incremental ΔΣ in IHP SG13G2.
- Formula per concept (same as SerDes): short derivation → worked example with the project's real
  numbers → *what this means for your design* box.
- Optional content source: `/Users/kithminrw/SkillSurf/art_of_aicd` (https://www.skillsurf.org/art_of_aicd/)
  — cross-link its Part II (transistor, gm/ID) from Ch 5 rather than repeating it.

**The user's current scope (first release):** finish the full outline + the basic chapters
(Part I), push, then pause. The user works directly on `main`.

## 2. Where we stopped

| Item | State |
|---|---|
| Site scaffold (Jekyll just-the-docs, BRICD theme, dark mode, KaTeX) | done, copied from SerDes and rebranded |
| `tools/build_site.py` (LaTeX → pandoc → Jekyll pages) | adapted, **never run** (pandoc missing) |
| `book/tutorial.tex` (title page, 5 parts, all 31 `\include`s, appendix, bib) | done |
| `book/tutorial/biotut.sty` (house style) | done (renamed macros, rms units added) |
| `book/tutorial/bib/core.bib` | done (46 entries) |
| Preface `00_preface.tex` | **written** (incl. reading-paths TikZ figure) |
| Ch 1–4 (Part I) | **NOT written** — figures and numbers ready (section 4) |
| Ch 5–30 | written as **outlines** (generated, now hand-editable) |
| Ch 31 `31_labs.tex` | **missing** |
| Appendices `A_appendices.tex` | **missing** |
| `labs/python/biosig.py` (shared model) | done, tested |
| Lab 1 and Lab 2 scripts | **missing** |
| Figure scripts + PDFs for Ch 1–4 (13 plots) | done, **not visually reviewed yet** |
| Home page `index.md`, labs page `labs.md` | **missing** |
| Book compiled with latexmk | **never** (would fail on missing includes) |
| Website built / previewed | **never** |
| Pages deploy | workflow switched to **manual trigger** so a half-built site is not published |

## 3. Decisions already made (do not re-litigate)

- **Pipeline:** same as SerDes — LaTeX book is the single source of truth; `tools/build_site.py`
  generates `chapters/`, `appendices/`, `parts/`, `preface.html`, `references.html`, figures and the
  PDF. Never hand-edit generated pages.
- **Permalinks follow the curriculum's site map:** chapters `/part-N/chNN/`, appendices
  `/appendix/a/`…`/e/`, appendix index `/appendix/`, plus `/preface/`, `/references/`, and a
  hand-written `/labs/` page (nav_order 7; appendices 8, references 9 — set in `build_site.py`).
- **Repository layout from the curriculum:** labs in `labs/python/` (later `labs/xschem/`,
  `labs/verilog/`, `labs/layout/`), `data/` holds download scripts only. Figure scripts stay in
  `book/tutorial/figsrc/` (Overleaf compatibility, like SerDes) and import `labs/python/biosig.py`.
- **Outline chapters** carry a `specnote[Chapter status: outline]` box naming their build stage.
- **Branch:** work on `main` (user's choice). Remote switched from HTTPS to SSH (other BRICD
  repos use SSH; HTTPS had no credentials).
- **Honesty line:** AI-assistance disclaimer says the draft *may contain mistakes*; it does not
  claim human review. Standards are summarised, never reproduced.

## 4. Next steps, in order

### Step 1 — Write Chapters 1–4 (`book/tutorial/chapters/0N_*.tex`)

Use SerDes `01_intro.tex` as the style model. Every chapter: `\tikzsetfigurename{NN_name-}` first
line if it has TikZ, `\chapter{..}\label{ch:..}`, `\chapterlead{..}`, `objectives` box, sections
with `\label{sec:..}`, worked examples (`\begin{example}{Title}\label{we:..}`), `keyeq`,
`insight`, `pitfall`, `tryit` (pointing to `\cref{sec:lab1}` etc.), `specnote`, and a closing
`takeaways` box. **Labels below are already referenced by other chapters and must exist.**

**Ch 1 `01_why.tex` — Why Biomedical ICs** — `\label{ch:why}`
- Sections: applications (wearable ECG patch, Holter, EEG headset, sEMG prosthetics, neural
  implants/BCIs) with a table (channels / signal & band / what limits the design); why integrate
  (channel count, power, size); the signal chain; the Open-BioAFE spec sheet; the design question
  *"what does each application demand in channels, noise, power and lifetime?"*
- **Must define** `fig:ch1-chain` (TikZ, 9 blocks — see section 8) and `tab:ch1-spec`
  (spec sheet — see section 8).
- Figure `ch01_lifetime` (battery lifetime vs average power).
- Worked examples: battery life — 8 ch × 10 µW = 80 µW on a CR2032 (≈2430 J) ≈ **352 days**;
  8 × 100 µW ≈ 35 days; discrete-class 8 × ~1 mW ≈ **3.5 days** (energy only; radio excluded,
  coin cells cannot supply high peaks). Data rates: ECG/EEG 8 × 500 S/s × 16 b = 64 kb/s; EMG
  8 × 2 kS/s × 12 b = 192 kb/s; spike mode 8 × 20 kS/s × 12 b = 1.92 Mb/s; at an *illustrative*
  ~10 nJ/bit radio, 64 kb/s costs ≈0.64 mW = 8× the whole AFE budget → motivates Ch 27.
- Key equation: lifetime `T = E_batt / (N·P_ch + P_dig + P_radio)`.
- Say "commercial discrete AFEs are of the order of 1 mW per channel" — avoid quoting exact
  datasheet numbers unless verified.
- SG13G2 facts safe to state: 130 nm SiGe BiCMOS, HBT fT/fmax ≈ 350/450 GHz, 1.2 V core and
  3.3 V I/O MOS, MIM capacitors. HBTs: low 1/f noise but base current through the electrode.

**Ch 2 `02_signals.tex` — Bioelectric Signals** — `\label{ch:signals}`
- Action potentials (Hodgkin–Huxley, cite `hodgkin1952`), ECG (P-QRS-T, leads, Einthoven),
  EEG (δ 0.5–4, θ 4–8, α 8–13, β 13–30, γ 30–100 Hz; 10–20 system), EMG (motor units, surface
  vs needle), spikes and LFPs, ECoG (cite `buzsaki2012`). The master amplitude-vs-bandwidth table
  (`SIGNALS` in `biosig.py`). Design question: dynamic range and bandwidth of the chain.
- Figures: `ch02_ap` (HH: peak ≈ +39 mV, rest −65 mV, AHP ≈ −76 mV), `ch02_ecg` (synthetic,
  cite `mcsharry2003`), `ch02_eeg` (trace + PSD with bands), `ch02_emg_spikes`, `ch02_map`
  (the key figure).
- Worked example — dynamic range: DC-coupled, ±300 mV offset (212 mV rms full-scale sine) over
  1.5 µVrms → **103 dB ≈ 16.8 bits** (motivates 16-b ΔΣ); AC-coupled, 5 mV peak EMG over
  1.5 µVrms → **67 dB ≈ 10.9 bits** (motivates 12-b SAR). Note EMG mode has more bandwidth, so
  its noise floor is higher.
- `tryit` → Lab 1.

**Ch 3 `03_electrodes.tex` — Electrodes and the Body as a Circuit** — `\label{ch:electrodes}`
- Ag/AgCl wet vs dry vs implanted; half-cell potential (Ag/AgCl ≈ +0.222 V vs SHE) and DC
  offset; Randles model (cite `randles1947`); electrode thermal noise; motion artefacts; source
  impedance mismatch (cite `chi2010` for dry electrodes). TikZ: electrode–skin equivalent circuit
  (circuitikz: Ehc, Rd‖Cd, gel Rs, skin potential, epidermis Re‖Ce, dermis Ru).
- Models (`ELECTRODES` in `biosig.py`): wet = 1 kΩ + 51 kΩ‖47 nF (the standards' network);
  dry = 5 kΩ + 1 MΩ‖4.7 nF; implanted micro = 10 kΩ + CPE (n = 0.85, |Z| = 500 kΩ at 1 kHz).
- Numbers (T = 310 K, one electrode, 0.5–100 Hz thermal noise): wet **0.24 µVrms**, dry
  **0.85 µVrms**, micro 2.3 µVrms (micro 300 Hz–7 kHz: 2.8 µVrms). |Z| wet: 52 k (0.67 Hz),
  41.5 k (50 Hz); dry: 1.0 M (0.67 Hz), 564 k (50 Hz). Real electrodes add excess noise above
  thermal (pitfall box).
- Input-impedance worked example: the standards' test uses 620 kΩ‖4.7 nF at 0.67 Hz and 40 Hz
  with ±300 mV offsets, ≤20 % drop allowed → Zin ≥ 4·|Zs| = **2.48 MΩ at 0.67 Hz** (this is
  the 2.5 MΩ rule), 2.0 MΩ at 40 Hz (cite `medteqzin`, `iec60601-2-25`).
- Figures: `ch03_impedance`, `ch03_noise`, `ch03_loading`, `ch03_offset`.
- `tryit` → Lab 2.

**Ch 4 `04_interference.tex` — Interference, Safety and Standards** — `\label{ch:interference}`
- Mains coupling (cite `huhta1973`): 230 V/50 Hz, Cpow = 3 pF, Cbody = 200 pF → displacement
  current **0.22 µA**; floating body Vcm = **3.4 V**; with a 51 kΩ‖47 nF ground electrode
  Vcm ≈ **9 mV**. TikZ (circuitikz): mains → Cpow → body → Cbody → earth; electrodes Z1, Z2, Z3 to
  amplifier inputs with Zcm to amplifier ground; Ciso to earth.
- CM→DM by imbalance (cite `pallas1991`): with Vcm = 9 mV and ΔZ = 40.7 kΩ: Zcm 10 MΩ →
  36.6 µV, 100 MΩ → **3.7 µV**, 1 GΩ → 0.37 µV, 10 GΩ → 0.037 µV of mains.
- CMRR test (cite `medteqcmrr`, `iec60601-2-25`, `-2-27`): standard's 20 Vrms via 100 pF
  divider ≡ 10 Vrms behind 200 pF; 51 kΩ‖47 nF in one lead (40.7 kΩ at 50 Hz, 37.8 kΩ at 60 Hz);
  300 mV DC; indication must stay below 1 mV (10 mm at 10 mm/mV). 10 Vrms = 28.3 Vpp →
  **89.0 dB**. Worst-case bound if all 10 V reached the electrodes: Zcm ≥ **1.15 GΩ at 50 Hz
  (≤ 2.76 pF)**, 1.07 GΩ at 60 Hz (≤ 2.48 pF). Typical ECGs measure ~95 dB; claims of 120 dB are
  usually without the imbalance network. -2-47 (ambulatory) uses only 2.8 Vrms.
- Effective CMRR: `1/CMRR_eff = 1/CMRR_amp + ΔZ/Zcm` (figure `ch04_cmdm` b).
- Safety (cite `iec60601-1`; summarise, hedge): patient/auxiliary current, normal condition:
  BF 100 µA, CF 10 µA a.c.; single fault 500 / 50 µA; d.c. 10 µA; above 1 kHz × f/1 kHz up to
  100 kHz, never above 10 mA. Isolation, defibrillation (survive several kV, recover quickly),
  ESD (system ±8 kV contact / ±15 kV air per 60601-1-2; on-chip HBM). Implant heating: keep
  tissue rise ≈ 1 °C; power density limit of tens of mW/cm² — cite `kim2007` and hedge.
- Figures: `ch04_cmdm`, `ch04_mains_eeg`, `ch04_limits`.

### Step 2 — Chapter 31 `31_labs.tex` — Hands-on Labs — `\label{ch:labs}`
Model on SerDes `16_labs.tex`. Must define `sec:lab1` … `sec:lab15` (and ideally
`sec:capstone`). Write Lab 0 (set-up), Lab 1 and Lab 2 in full (goal, code, expected figure and
numbers, questions); Labs 3–15 as short planned sections from the table in section 8. Add a lab
table with tracks A/B/C.

### Step 3 — Lab scripts in `labs/python/`
- `lab1_biosignal_explorer.py`: load MIT-BIH record 100 (`wfdb.rdrecord('100', pn_dir='mitdb')`),
  a CHB-MIT EDF (e.g. `chb01/chb01_03.edf`, ~40 MB) and NinaPro (needs a manual download → accept
  a local `.mat` path); **fall back to `biosig.py` synthetic signals** if offline; plot traces and
  Welch PSDs; measure amplitude (`amplitude_stats`) and bandwidth (`band_edges`); write the
  student's version of the Ch 2 table to `labs/python/out/` (git-ignored).
- `lab2_electrodes_interference.py`: phasor model of body + electrodes + amplifier
  (`body_cm_voltage`, `cm_to_dm`, `required_cmrr_db`); inject 10 Vrms CM; sweep CMRR, Zcm and
  imbalance; add a behavioural right-leg drive (Vcm reduced by 1 + loop gain); plot interference vs
  CMRR and imbalance; print the required CMRR. Optional: `labs/spice/lab2_body.cir` for ngspice
  (ngspice-47 is installed via Homebrew).
- `data/fetch_data.py`: download helpers only.

### Step 4 — Appendices `A_appendices.tex` (one file, five `\chapter`s, like SerDes)
A Formula sheet (NEF/PEF, kT/C, CMRR with imbalance, SQNR/ENOB, Walden/Schreier FoM, ΔΣ SQNR,
IQ |Z| and φ — the equations are already in the outline chapters); B Biosignal reference tables
(`SIGNALS` + electrode impedances); C Design-review checklists (AFE: noise, CMRR, offset, Zin,
protection; ADC: kT/C, matching, comparator noise, reference; layout: common centroid, guard
rings, shielding of high-impedance nodes); D Glossary (ExG, NEF, DRL, DSL, CCIA, NTF, OSR, ENOB…);
E Further reading (section 2 of the curriculum + AI-assistance disclaimer and corrections contact).

### Step 5 — Home page and labs page (hand-written)
- `index.md`: copy SerDes `index.md` structure. Hero kicker *OPEN-BIOAFE · IHP SG13G2 · 8-CHANNEL
  ExG FRONT-END*, title, subtitle (section 8), buttons *Start reading · Go to the labs · Source
  on GitHub*; key-numbers strip (7 tiles, section 8); signal-chain figure
  (`assets/figs/tikz/01_why-0.svg` once built, class `chain-figure`); "What is inside" cards per
  part with `<span class="status status-written">` / `status-outline` badges (CSS already added
  at the end of `_sass/custom/custom.scss`); labs; about + AI disclaimer.
- `labs.md` (permalink `/labs/`, nav_order 7): the 15-lab table (class `lab-table`), tool
  setup (Python venv; IIC-OSIC-TOOLS container), links to Ch 31 sections and scripts.

### Step 6 — Build, check, publish
1. Tools: `pandoc` ≥ 3 and `poppler` (pdftocairo, pdftoppm, pdfinfo). See section 6.
2. `python3 tools/build_site.py` (compiles with `latexmk -pdf -shell-escape`; TikZ is externalised
   to `book/tutorial/tikzext/`). Fix warnings in `tools/last_build_warnings.txt`.
3. Preview: `bundle install && bundle exec jekyll serve` → http://localhost:4000/biomedical-ic-design/
   (needs Ruby ≥ 3.1; system Ruby is 2.6).
4. Check every page in the browser (light + dark, phone width), the PDF, and that the outline
   chapters render.
5. Re-enable `push` in `.github/workflows/pages.yml`; in GitHub settings set
   Pages → Source → GitHub Actions; tag v0.1 when the first release is ready.

## 5. Conventions and gotchas

- **Macros** (in `biotut.sty`; any new one must also go in `PRELUDE` in `tools/build_site.py`):
  `\OB` (Open-BioAFE), `\sgx`, `\SNR`, `\CMRR`, `\ENOB`, `\NEF`, `\PEF`, `\Vdd`, `\Vcm`, `\Vdm`,
  `\Zin`, `\Zcm`, `\Ze`, `\Ehc`, `\vn`, `\fs`, `\fc`, `\gm`, `\code{}`, `\tool{}`, `\ie`, `\eg`.
- **Units:** siunitx `\qty{..}{..}`; custom units `\Vrms`, `\mVrms`, `\uVrms`, `\uVpp`, `\Vpp`
  (also mapped in the builder's `UNIT` table — keep both in sync). `\uVrms` = `\micro V_{rms}`
  has not been compiled yet; check it on the first LaTeX build.
- **Citations:** the builder renders `\citet` as a bare number, so write `Name~\cite{key}`
  (the outline generator already does this).
- **Boxes the builder knows:** keyeq, example, insight, pitfall, tryit (default title "Try it in
  Python"), derivation, specnote (default "Open-BioAFE target"), objectives, takeaways. Adding a
  new box type needs changes in `biotut.sty`, `build_site.py` (`BOX_DEFAULT` + regexes) and CSS.
- **Figures:** draw at final size with `bricdstyle.py` (`FULL`, `FULL2`, `HALF`…), include
  with `\includegraphics{name}` (no scaling). Redraw: `cd book/tutorial/figsrc && python chNN_figs.py`.
- **Python:** use `~/opt/anaconda3/bin/python` (3.9, numpy 1.22, scipy 1.7, matplotlib 3.5).
  Homebrew pythons have no numpy. `wfdb` is not installed yet: make a venv with
  `--system-site-packages` from the anaconda python and `pip install wfdb` (and later
  `python-deltasigma`, `mne` if used).
- **Title page and part pages** use `\tikzexternaldisable`; everything else is externalised.

## 6. Environment status (this Mac)

- TeX Live: `pdflatex`, `latexmk` present.
- **pandoc / poppler: not installed yet.** A `brew install pandoc poppler ruby` was left running
  in the background; Homebrew had no bottle for this macOS and was **compiling pandoc from
  source with GHC/cabal** (slow; may take a long time). If it fails or is stopped, install the
  official pandoc macOS arm64 package from https://github.com/jgm/pandoc/releases instead, then
  `brew install poppler` separately. Check with `which pandoc pdftocairo` and
  `brew list --versions pandoc poppler ruby`.
- Ruby: system 2.6 (too old for Jekyll 4.4). Homebrew `ruby` was in the same install command;
  use `/opt/homebrew/opt/ruby/bin` on PATH for `bundle`.
- ngspice-47 installed (Homebrew).
- The curriculum PDF is no longer at `~/Downloads/Biomedical IC Design Tutorial — Curriculum & Labs.pdf`.

## 7. Known issues to clean up

- The 13 figures were generated but **not visually reviewed** (label overlaps likely in
  `ch02_eeg` band labels, `ch02_map` text positions, `ch03_offset` annotations). Render to PNG
  (`sips -s format png in.pdf --out out.png`) and inspect.
- `tutorial.tex` includes `01_why`, `02_signals`, `03_electrodes`, `04_interference`, `31_labs`,
  `A_appendices` which do not exist yet.
- 21 labels are referenced but not defined: `ch:signals ch:electrodes ch:interference ch:labs
  fig:ch1-chain tab:ch1-spec sec:lab1`…`sec:lab15`.
- Not yet cited (fine for now, use them in Part I): `buzsaki2012 hodgkin1952 iec60601-1
  iec60601-2-25 iec60601-2-27 iec60601-2-47 kim2007 mcsharry2003 medteqcmrr medteqzin
  randles1947 wfdb`.
- Outline polish: key equations are placed after each outline chapter's first section (Ch 6's NEF
  box sits under "Noise sources" and repeats the formula in section 6.3); Ch 6 reading list says
  "Razavi (Chapter on noise)". The generator lives only in the old session scratchpad, so edit the
  `.tex` files directly from now on.
- `bricdstyle.py` still carries SerDes eye-diagram helpers (harmless).
- `tools/build_site.py` has not been run since adaptation; expect small fixes.

## 8. Reference data from the curriculum (the PDF is gone — this is the record)

**Hero:** kicker *OPEN-BIOAFE · IHP SG13G2 · 8-CHANNEL ExG FRONT-END*; title *Designing a
Biopotential Acquisition Chip from Scratch*; subtitle *A design tutorial for undergraduate and
early-graduate engineers building an open-source biomedical analog front-end and data converters
in 130 nm SiGe BiCMOS. Bioelectric signals, electrodes and safety, low-noise amplifiers, chopping,
SAR and ΔΣ ADCs, bioimpedance sensing, biosignal processing, the open-source flow, and hands-on
labs.*

**Key numbers (targets, to be confirmed by the Part II/III budgets):** 8 channels (ECG, EEG or
EMG, selectable bandwidth) · 0.5 Hz–1 kHz ExG band (spike mode to 7 kHz optional) · < 1.5 µVrms
input-referred noise, 0.5–100 Hz (EEG mode) · > 90 dB CMRR (above the ~89 dB the IEC ECG CMRR
test implies) · ±300 mV electrode DC offset tolerated · 12 b SAR / 16 b ΔΣ · < 10 µW/ch front-end
power. (`SPEC` in `biosig.py` holds the same numbers.)

**Spec sheet for `tab:ch1-spec`** (parameter · target · chapter): channels 8 selectable (1);
band 0.5 Hz–1 kHz, spikes to 7 kHz optional (2); noise < 1.5 µVrms 0.5–100 Hz EEG mode (2, 3, 6);
CMRR > 90 dB at 50/60 Hz (4); offset ±300 mV (3, 10); input impedance ≥ 2.5 MΩ per input,
common-mode goal > 1 GΩ at 50 Hz (3, 4); converters 12-b SAR for EMG/spikes and 16-b incremental
ΔΣ for ECG/EEG (13–20); front-end power < 10 µW/ch (6, 29); supply 1.2 V (5); process IHP SG13G2
130 nm SiGe BiCMOS (5, 30); optional bioimpedance (respiration) channel (28); data out SPI (27).

**Signal chain for `fig:ch1-chain` (9 blocks):** Electrodes, body (Ch 2–4) → ESD + lead-off
(Ch 12) → Chopper LNA + DSL (Ch 5–10) → PGA + anti-alias (Ch 11) → splits to **12-bit SAR ADC**
(Ch 15–18 · EMG, spikes) and **Incremental ΔΣ ADC** (Ch 19–20 · ECG, EEG) → Decimation + feature
DSP (Ch 20, 23–27) → Data out (SPI/BLE · Ch 27). Right-leg drive (Ch 12 · CM feedback) loops from
the LNA back to the electrodes. Highlight the two converters (Part III). Use the `blk`/`blkb`/`sig`
TikZ styles from `biotut.sty`.

**Reading paths:** circuit = Part I → II → III → V; signal = Part I → IV → Ch 13–14 → V;
converter-only = Ch 13–22 + Labs 6–10 (already in the Preface figure).

**Labs (15, three tracks + capstone):**

| Lab | Track | Chapters | What you do | Deliverable |
|---|---|---|---|---|
| 1 Biosignal explorer | A Python | 2 | Load MIT-BIH, CHB-MIT, NinaPro with wfdb/MNE; plot traces and PSDs; measure amplitude and bandwidth | Your version of the Ch 2 amplitude-vs-bandwidth table |
| 2 Electrodes and interference | A | 3–4, 12 | Netlist body, Randles electrodes, 51 kΩ‖47 nF imbalance; inject 10 Vrms mains CM; sweep CMRR and Zin; add right-leg drive | Interference vs CMRR and imbalance; required CMRR |
| 6 Ideal ADC and spectral testing | A | 13–14, 22 | Quantise sines; coherent sampling, windows; SNDR, SFDR, ENOB; histogram DNL/INL with cap mismatch | Reusable `adctest.py` |
| 9 ΔΣ by design | A | 19–20 | 1st/2nd/3rd-order NTFs with python-deltasigma; SQNR vs OSR; incremental mode; fixed-point CIC | NTF, coefficients and decimator for the ECG/EEG channel |
| 3 Devices in weak inversion | B SG13G2 | 5–6 | gm/ID, flicker noise vs W·L, HBT vs MOS input noise | Lookup tables and noise plots (reused in 4–5) |
| 4 The Harrison LNA | B | 6, 8 | Capacitive-feedback OTA amp with pseudo-resistors; AC, noise, transient; NEF | LNA meeting spec; NEF vs bias current |
| 5 Chopper amplifier | B | 9–10 | Input/output choppers + DC servo loop; 1/f removal, ripple, Zin loss; ±300 mV offset | Before/after noise PSD, ripple, Zin plots |
| 7 StrongARM comparator | B | 16 | Design; Monte Carlo offset; transient-noise input noise; energy/decision | Comparator with offset and noise numbers |
| 8 SAR ADC | B | 15, 17–18 | Bootstrapped S/H, monotonic CDAC, Verilog SAR logic; mixed-signal sim; `adctest.py` | 10–12-b SAR with ENOB and FoM |
| 10 Switched-capacitor ΔΣ | B | 20 | Lab 9 loop with SC integrators and 1-bit quantiser vs ideal | Transistor-level spectrum and SQNR |
| 15 Bioimpedance IQ readout | B | 28 | Python: Cole tissue, tetrapolar, digital IQ, |Z|/φ vs f, respiration ΔZ on ECG; then SG13G2 OTA current source + square-wave IQ demodulator | Cole plot, ΔZ resolution vs current, analog vs digital IQ error |
| 11 ECG chain end-to-end | C Python | 24, 29 | MIT-BIH + Noise Stress Test through behavioural AFE+ADC; Pan–Tompkins | QRS sensitivity/PPV vs ADC bits and input noise |
| 12 EEG seizure detection | C | 25, 27 | Band-power features on CHB-MIT; simple classifier; reduced word length and rate | Latency/accuracy vs bits and power proxy |
| 13 EMG gesture recognition | C | 26 | MAV/WL/ZC/SSC on NinaPro; LDA/SVM; fixed point | Accuracy vs channels, rate, resolution |
| 14 Layout to GDS | C* | 30 | Comparator and CDAC in KLayout; DRC/LVS/PEX with JKU template; post-layout sim | Clean DRC/LVS, post-layout vs schematic |

(*The curriculum lists Lab 14 under Track C; it is a layout lab.) **Capstone — one Open-BioAFE
channel:** Lab 5 + PGA + Lab 8 (SAR) or Lab 10 (ΔΣ), optionally Lab 15; verify across corners;
feed real ECG/EEG through the transistor-level chain via ngspice PWL sources; report against the
key numbers. Best designs → IHP OpenMPW submission.

**Build order (stages; stage 1 is the current release):**
1. Home, Preface, Part I with Labs 1–2. 2. Ch 13–14, 19 with Labs 6, 9. 3. Part II with Labs 3–5.
4. Rest of Part III with Labs 7, 8, 10. 5. Part IV incl. bioimpedance with Labs 11–13, 15.
6. Part V, Lab 14, capstone, appendices; tag v0.1.

**Resource URLs (verified):** IHP-Open-PDK github.com/IHP-GmbH/IHP-Open-PDK · JKU template
github.com/iic-jku/ihp-sg13g2-ams-chip-template · IHP Analog Academy
github.com/IHP-GmbH/IHP-AnalogAcademy (8-bit synchronous SAR, starts from a dynamic comparator) ·
JKU SKY130 12-b SAR github.com/iic-jku/SKY130_SAR-ADC1 · TWEPP 2024 talk
indico.cern.ch/event/1381495/contributions/5988502/ · MEDTEQ CMRR and Zin articles (in
`core.bib`). Datasets: physionet.org/content/mitdb, /nstdb, /chbmit; ninapro.hevs.ch.

## 9. Open questions for the user

- Keep Lab 14 in Track C as the curriculum says, or move it to Track B?
- NinaPro downloads may need registration: is a "bring your own file + synthetic fallback"
  approach acceptable for Lab 1/13?
- When should the Pages deploy go live — after stage 1 (Part I) or later?
- Should `HANDOFF.md` be committed, or kept local?
