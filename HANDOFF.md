# HANDOFF — Open-BioAFE Tutorial (pick up here)

Last updated: 10 November 2026. On that day the tutorial was switched from a LaTeX book (with a
generated website) to **a website written directly in Markdown**. There is no LaTeX book and no
PDF any more; `book/` and `tools/build_site.py` were removed.

## 1. The goal

Build a course website like the Open-SERDES tutorial (live at https://www.thebricd.org/serdes-tutorial/),
following the curriculum document *"Biomedical IC Design Tutorial — Curriculum & Labs"*
(10 Nov 2026). That PDF has since been moved; everything needed from it is captured in this file
(section 8) and in the outline chapters. Unlike Open-SERDES, **no LaTeX book or PDF**.

- Title: **Open-BioAFE: Designing a Biopotential Acquisition Chip from Scratch**
- 5 parts, 31 chapters, 15 labs, appendices A–E. One reference chip: 8-channel ECG/EEG/EMG
  front-end + 12-bit async SAR + 2nd-order incremental ΔΣ in IHP SG13G2.
- Formula per concept (same as SerDes): short derivation → worked example with the project's real
  numbers → *what this means for your design* box.
- Optional content source: https://www.skillsurf.org/art_of_aicd/ — cross-link its Part II
  (transistor, gm/ID) from Ch 5 rather than repeating it.

**Scope of the first release:** the full outline + the basic chapters (Part I), then pause. The
user works directly on `main`.

## 2. Where we stopped

| Item | State |
|---|---|
| Site (Jekyll 4.4 + just-the-docs 0.10.1, BRICD theme, dark mode, KaTeX) | done; builds cleanly |
| Home page `index.md` (hero, key numbers, signal chain, part cards) | done |
| Preface `preface.md` (incl. reading-paths figure `assets/figs/reading-paths.svg`) | **written** |
| Ch 1–4 (Part I) | **outlines** (Ch 1 has the spec table and signal-chain figure); text NOT written — figures and numbers ready (section 4) |
| Ch 5–30 | outlines |
| Ch 31 `chapters/31_labs.md` | outline: lab table + one short section per lab (anchors `#lab-1`…`#lab-15`, `#setup`, `#capstone`) |
| Appendices | **missing** (no pages yet, not in the menu) |
| `references.md` + `_data/references.yml` (46 entries) | done |
| `labs/python/biosig.py` (shared model) | done, tested |
| Lab 1 and Lab 2 scripts | **missing** |
| Figure scripts `figsrc/` → `assets/figs/*.svg` (13 plots) | done, reviewed once (see section 7); not yet used on any page |
| Pages deploy | `.github/workflows/pages.yml` deploys on every push to `main` |

## 3. Decisions already made (do not re-litigate)

- **No LaTeX book, no PDF.** The Markdown pages are the source; edit them directly.
- **Permalinks follow the curriculum's site map:** chapters `/part-N/chNN/`, parts `/part-N/`,
  plus `/preface/` and `/references/`. Appendices, when written: `/appendix/a/`…`/e/` and an
  index at `/appendix/` (parent "Appendices").
- **Menu order** (`nav_order`): Home 0, Preface 1, Parts 2–6, References 7; chapters sit under
  their part (`parent: "Part I · Foundations"` etc.) with `nav_order` = chapter number.
  Appendices, when added, go between the parts and References.
- **No separate labs page:** Chapter 31 is the lab hub; the home page's "Go to the labs" button
  and every `tryit` box link into it.
- **Repository layout from the curriculum:** labs in `labs/python/` (later `labs/xschem/`,
  `labs/verilog/`, `labs/layout/`), `data/` holds download scripts only. Figure scripts live in
  `figsrc/`, import `labs/python/biosig.py`, and write SVGs to `assets/figs/`.
- **Outline chapters** carry a `specnote` box titled *Chapter status: outline* naming their
  build stage.
- **Branch:** work on `main` (user's choice). Remote uses SSH (HTTPS had no credentials).
- **Honesty line:** AI-assistance disclaimer says the draft *may contain mistakes*; it does not
  claim human review. Standards are summarised, never reproduced.

## 4. Next steps, in order

### Step 1 — Write Chapters 1–4 (`chapters/0N_*.md`)

Each page already exists as an outline: replace the outline with the full text, keeping the front
matter. Use a SerDes chapter page as the style model for content. Every chapter: lead paragraph
(`{: .chapterlead }`), `objectives` box, numbered sections (`## <span class="secnum">2.1</span>Title`),
worked examples (`tbox-example`, titled *Worked Example 2.1 · Title*), `keyeq`, `insight`,
`pitfall`, `tryit` (linking to `{% link chapters/31_labs.md %}#lab-1` etc.), `specnote`, and a
closing `takeaways` box. Figures: `<figure id="fig-2-1">` with an `<img>` from `assets/figs/` and
a `<figcaption>` starting `<span class="capnum">Figure 2.1.</span> <strong>…</strong>`. Other
pages already link to `01_why.md#tab-1-1` and `#fig-1-1`; keep those ids. Circuit diagrams
(planned below) are hand-drawn SVGs, like
`assets/figs/signal-chain.svg`.

**Ch 1 `01_why.md` — Why Biomedical ICs?**
- Sections: applications (wearable ECG patch, Holter, EEG headset, sEMG prosthetics, neural
  implants/BCIs) with a table (channels / signal & band / what limits the design); why integrate
  (channel count, power, size); the signal chain; the Open-BioAFE spec sheet; the design question
  *"what does each application demand in channels, noise, power and lifetime?"*
- Figure 1.1 (signal chain) and Table 1.1 (spec sheet) are already on the page.
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

**Ch 2 `02_signals.md` — Bioelectric Signals**
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

**Ch 3 `03_electrodes.md` — Electrodes and the Body as a Circuit**
- Ag/AgCl wet vs dry vs implanted; half-cell potential (Ag/AgCl ≈ +0.222 V vs SHE) and DC
  offset; Randles model (cite `randles1947`); electrode thermal noise; motion artefacts; source
  impedance mismatch (cite `chi2010` for dry electrodes). Diagram (SVG): electrode–skin equivalent circuit
  ( Ehc, Rd‖Cd, gel Rs, skin potential, epidermis Re‖Ce, dermis Ru).
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

**Ch 4 `04_interference.md` — Interference, Safety and Standards**
- Mains coupling (cite `huhta1973`): 230 V/50 Hz, Cpow = 3 pF, Cbody = 200 pF → displacement
  current **0.22 µA**; floating body Vcm = **3.4 V**; with a 51 kΩ‖47 nF ground electrode
  Vcm ≈ **9 mV**. Diagram (SVG): mains → Cpow → body → Cbody → earth; electrodes Z1, Z2, Z3 to
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

### Step 2 — Chapter 31 `chapters/31_labs.md` — Hands-on Labs
The outline has the lab table and a short section per lab. Write the set-up section, Lab 1 and
Lab 2 in full (goal, code, expected figure and numbers, questions); keep the anchors
(`{#lab-1}` … `{#lab-15}`, `{#setup}`, `{#capstone}`) because other pages link to them.

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

### Step 4 — Appendices (`appendices/a_formulas.md` … `e_reading.md` + `appendices/index.md`)
Each page `parent: "Appendices"`; the index `has_children: true`, permalink `/appendix/`, and a
`nav_order` between the parts and References (move References to 8). Content:
A Formula sheet (NEF/PEF, kT/C, CMRR with imbalance, SQNR/ENOB, Walden/Schreier FoM, ΔΣ SQNR,
IQ |Z| and φ — the equations are already in the outline chapters); B Biosignal reference tables
(`SIGNALS` + electrode impedances); C Design-review checklists (AFE: noise, CMRR, offset, Zin,
protection; ADC: kT/C, matching, comparator noise, reference; layout: common centroid, guard
rings, shielding of high-impedance nodes); D Glossary (ExG, NEF, DRL, DSL, CCIA, NTF, OSR, ENOB…);
E Further reading (section 2 of the curriculum + AI-assistance disclaimer and corrections contact).
Add `appendices` to the `defaults` layout scope in `_config.yml`, and an Appendices card on the
home page.

### Step 5 — Check and publish
1. Preview (section 6), check every page in light and dark mode and at phone width.
2. Push to `main`; the Pages workflow deploys. In the repository settings, Pages → Source must be
   **GitHub Actions**. Tag v0.1 when the first release is ready.

## 5. Conventions and gotchas

- **Maths:** `$$...$$` (kramdown) inline or as its own paragraph; KaTeX renders the `\( \)` /
  `\[ \]` that kramdown writes. In tables, avoid `|` inside maths (use `\lvert \rvert`). Write
  ΔΣ, µV, Ω as Unicode in text and in front-matter titles (the menu cannot render maths).
- **Units:** plain text with a space: `1.5 µVrms`, `±300 mV`, `0.5–100 Hz`.
- **Boxes:** `<div class="tbox tbox-NAME" markdown="1">`, then `<div class="tbox-title">Title</div>`,
  a blank line, the Markdown content, a blank line, `</div>`. Names: keyeq, example, insight,
  pitfall, tryit, derivation, specnote, objectives, takeaways. Default titles: keyeq "Key
  equation · …", insight "What this means for your design", pitfall "Common pitfall", tryit "Try
  it in Python", specnote "Open-BioAFE target", objectives "In this chapter you will learn",
  takeaways "Key takeaways". Box titles are raw HTML: use `\(...\)` there for maths.
- **Links:** `[Chapter 6]({% link chapters/06_noise.md %})`, with `#anchor` after the tag for a
  section; the build fails on a missing file. Headings get automatic ids; add `{#id}` at the end
  of a heading for a stable one.
- **Citations:** `Name {% include cite.html keys="key1,key2" %}`. New references go at the **end**
  of `_data/references.yml` (numbers are positions in that file); the text field is Markdown.
- **Prev/next links** come from the `chapter:` number in each page's front matter (preface 0).
- **Figures:** draw with `figsrc/bricdstyle.py` (`FULL`, `FULL2`, `HALF`…); redraw with
  `cd figsrc && python chNN_figs.py`. Diagrams are hand-written SVG in `assets/figs/`.
- **Python:** use `~/opt/anaconda3/bin/python` (3.9, numpy 1.22, scipy 1.7, matplotlib 3.5).
  Homebrew pythons have no numpy. `wfdb` is not installed yet: make a venv with
  `--system-site-packages` from the anaconda python and `pip install wfdb` (and later
  `python-deltasigma`, `mne` if used).

## 6. Environment status (this Mac)

- No Ruby ≥ 3.1 on the Mac (system Ruby is 2.6), so preview in Docker (the `ruby:3.3` image is
  pulled; gems are cached in the `bioafe-gems` volume):
  `docker run --rm -p 4000:4000 -v "$PWD":/site -v bioafe-gems:/usr/local/bundle -w /site ruby:3.3 bash -c "bundle install && bundle exec jekyll serve --host 0.0.0.0 --force_polling"`
  → http://localhost:4000/biomedical-ic-design/. In an arm64 container bundler adds an
  `aarch64-linux` platform to `Gemfile.lock`; revert that (`git checkout Gemfile.lock`) before
  committing unless it is wanted.
- `gh` (GitHub CLI) is not installed.
- ngspice-47 installed (Homebrew).

## 7. Known issues to clean up

- Figures reviewed once at small size: `ch02_map` labels crowd each other (ECoG / EEG (scalp) /
  LFP), and in `ch03_noise` (b) the green curve crosses the "EEG-mode target" label. Fix before
  using them on a page.
- Not yet cited anywhere (fine for now, use them when Part I is written): check with a search of
  `chapters/` for each key in `_data/references.yml`.
- Outline polish: key equations are placed after each outline chapter's first section (Ch 6's NEF
  box sits under "Noise sources" and repeats the formula in section 6.3); Ch 6 reading list says
  "Razavi (Chapter on noise)".
- `figsrc/bricdstyle.py` still carries SerDes eye-diagram helpers (harmless).

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

**Spec sheet (Table 1.1)** (parameter · target · chapter): channels 8 selectable (1);
band 0.5 Hz–1 kHz, spikes to 7 kHz optional (2); noise < 1.5 µVrms 0.5–100 Hz EEG mode (2, 3, 6);
CMRR > 90 dB at 50/60 Hz (4); offset ±300 mV (3, 10); input impedance ≥ 2.5 MΩ per input,
common-mode goal > 1 GΩ at 50 Hz (3, 4); converters 12-b SAR for EMG/spikes and 16-b incremental
ΔΣ for ECG/EEG (13–20); front-end power < 10 µW/ch (6, 29); supply 1.2 V (5); process IHP SG13G2
130 nm SiGe BiCMOS (5, 30); optional bioimpedance (respiration) channel (28); data out SPI (27).

**Signal chain (Figure 1.1, 9 blocks):** Electrodes, body (Ch 2–4) → ESD + lead-off
(Ch 12) → Chopper LNA + DSL (Ch 5–10) → PGA + anti-alias (Ch 11) → splits to **12-bit SAR ADC**
(Ch 15–18 · EMG, spikes) and **Incremental ΔΣ ADC** (Ch 19–20 · ECG, EEG) → Decimation + feature
DSP (Ch 20, 23–27) → Data out (SPI/BLE · Ch 27). Right-leg drive (Ch 12 · CM feedback) loops from
the LNA back to the electrodes. Highlight the two converters (Part III). Drawn as
`assets/figs/signal-chain.svg` (Figure 1.1, also on the home page).

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
