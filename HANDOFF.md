# HANDOFF — Open-BioAFE Tutorial (pick up here)

Last updated: 12 November 2026, evening (Ch 13 written; outline review against lecture
material, section 2a). On
10 November the tutorial was switched from a LaTeX book (with a generated website) to **a website
written directly in Markdown**. There is no LaTeX book and no PDF any more; `book/` and
`tools/build_site.py` were removed.

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
| Ch 1–4 (Part I) | **written** (11 Nov 2026): full text, 15 figures (incl. diagrams `ch03_electrode_model.svg`, `ch04_mains_coupling.svg`), 5 tables, worked examples; every number checked against `biosig.py` |
| Ch 13 | **written** (12 Nov 2026): aliasing of mains harmonics (250 Hz → 6 Hz at 256 S/s), anti-alias order (8th at 500 S/s vs 3rd at 2 kS/s), quantisation model and its failures, dither, oversampling, jitter, Table 13.1 (rate and bits per mode); 3 figures from `figsrc/ch13_figs.py` |
| Ch 14 | **written** (13 Nov 2026): spectral metrics, coherent sampling, DNL/INL by ramp histogram; behavioural 12-b SAR with 1 % unit mismatch (SNDR 69.5 dB, DNL −0.42…+1.45, σ_u < 0.26 % needed); Walden/Schreier FoM (SAR ≈ 41 nW/ch at 10 fJ/step; ΔΣ 3.0 µW/ch at 175 dB, 0.95 µW at 180 dB); kT/C (0.58 pF 12 b, 150 pF 16 b, 1.2 pF at OSR 128); thermal bound 8kT·SNR ≈ FoM_S 192 dB; Table 14.1 kept; 2 figures from `figsrc/ch14_figs.py` |
| Ch 19 | **written** (13 Nov 2026): NTF/STF, linear-model SQNR vs simulation (1-bit 2nd order at OSR 128: 100.2 dB formula FS, 84.9 dB simulated at −6 dBFS; effective quantiser gain ≈ 0.63), Table 19.1 (SQNR vs order 1–4 and OSR 16–256), Lee criterion and max stable amplitude, idle tones (DC 0.002 → lines at 38/77/115 Hz at 38.4 kHz), NTF synthesis (Legendre zeros, Butterworth poles, H∞ = 1.5), incremental: 2nd order M = 1024 → 16.6 b worst case, 512 kHz at 500 S/s vs free-running 3rd order OSR 128 at 38.4 kHz; 3 figures from `figsrc/ch19_figs.py` (~70 s to run) |
| Ch 5 | **written** (13 Nov 2026, title kept "Devices for Microwatt Design"): IC/EKV, gm/ID from SG13G2 sims (n ≈ 1.22, ceiling 31.7 V⁻¹, I_spec ≈ 0.78 µA/□ NMOS, 0.20 µA/□ PMOS), thermal noise 18.5 nV/√Hz at 1 µA (PMOS floor ~40 % above 2nkT/gm in the models), flicker K = 1.6e-10 (NMOS) / 5.4e-10 (PMOS) V²µm² — **NMOS quieter in these models**; unchopped pair needs ~1800 µm²/device (NMOS) for 1 µVrms; HBT npn13G2 gm/IC 37.7, β ≈ 680, e_n 15.1 nV/√Hz flat, base shot noise beats MOS only below ~6 MΩ, r_π 18 MΩ; Pelgrom from PDK mismatch libs: A_VT 3.9/2.2 mV·µm, A_β 0.5/0.33 %·µm, MIM 1 %·µm, HBT IS 3.8 %; 3 figures from `figsrc/ch05_figs.py` |
| Ch 6 | **written** (13 Nov 2026): noise sources (MOS weak-inversion channel noise = shot noise, 2nkT/gm), noise bandwidth (π/2, 1.11, ln fH/fL), chopped vs unchopped pair (0.26–0.33 vs ~1.0 µVrms), e_n/i_n with source; NEF/PEF with the **bandwidth convention made explicit** (brick-wall band: I_tot = NEF²·4kT·U_T·B_n/V², 4kTU_T·99.5 Hz = 4.26e-20 A·V²); limits: BJT pair √2, weak-inversion MOS pair √2·n = 1.73 (SG13G2 sim 1.72–2.05), current reuse → n; EEG target costs 60–840 nA; first stage 2 µA at NEF 3 → 0.44 µVrms; 2 figures from `figsrc/ch06_figs.py`. (The old outline's "single BJT NEF = 1" claim was dropped: with Steyaert's definition a single BJT gives 1/√2.) |
| Ch 7 | **written** (13 Nov 2026): 3-op-amp IA (first stage multiplies CMRR; 0.1 % resistors: worst 54 dB, MC median 67.7 dB; ±300 mV at 1.2 V limits DC-coupled G1 to 1.5), current-feedback IA (no resistor matching, tens-of-mV input range), CCIA (G = Cin/Cfb, offset blocked; **SG13G2 MIM = 1.5 fF/µm²**, 20 pF = 13 300 µm²; unchopped CMRR from MIM matching 78 dB 1σ / 69 dB 3σ → chopping needed), RC-mismatch CMRR falls 20 dB/dec, effective CMRR needs Zcm (Ch 4: ~1.9 GΩ) or RLD; choice: chopped CCIA, Cin 20 pF, Cfb 200 fF; 2 figures from `figsrc/ch07_figs.py` |
| Ch 8–12, 15–18, 20–30 | outlines. **Next: Ch 8 → 12** (rest of build stage 3), then Ch 15–18, 20–22 (stage 4), Part IV 23–28 (stage 5), Part V 29–30 (stage 6). User (13 Nov): "continue working until all the missing chapters are done" |
| Ch 31 `chapters/31_labs.md` | outline: lab table + one short section per lab (anchors `#lab-1`…`#lab-15`, `#setup`, `#capstone`) |
| Appendices | **missing** (no pages yet, not in the menu) |
| `references.md` + `_data/references.yml` (48 entries; `rich1983`, `ott2009` added 12 Nov) | done |
| `labs/python/biosig.py` (shared model) | done, tested; converter helpers added 12 Nov: `quantize`, `sqnr_ideal_db`, `enob`, `alias_freq`, `butter_atten_db`, `sqnr_os_db(N, osr, L)`, `jitter_snr_db`, `coherent_tone`, `tone_metrics` (SNDR/SNR/THD/SFDR, optional in-band limit); 13 Nov: `cdac_weights`, `sar_convert`, `code_to_volts`, `dnl_inl`, `ktc_cap`, `e_thermal_min`, `fom_walden`, `fom_schreier`; ΔΣ: `ntf_pure`, `synth_ntf(order, osr, h_inf, opt_zeros)`, `ntf_response`, `simulate_dsm(u, b, a, dither=)` (1-bit error-feedback loop, dither shaped), `dsm_sqnr` (Hann² window — plain Hann caps 3rd/4th order near 100 dB), `incremental2(u_dc, M)` |
| SG13G2 device data | `labs/spice/sg13_char.py` runs ngspice in `hpretl/iic-osic-tools:2026.10` (12 s; writes its own `.spiceinit` loading psp103/r3_cmc OSDI; models `cornerMOSlv.lib mos_tt`, `cornerHBT.lib hbt_typ`; devices `sg13_lv_nmos/pmos d g s b w= l=`, `npn13G2 c b e bn Nx=`) → `figsrc/data/sg13_gmid.csv`, `sg13_noise.csv`, `sg13_hbt.csv`, `sg13_hbt_noise.csv` (committed, so figures need no Docker). Working files in `labs/spice/char/` (git-ignored). Extend it for Ch 6–12 (e.g. OTA, pseudo-resistor, switch sims) |
| Lab 1 and Lab 2 scripts | **missing** |
| Figure scripts `figsrc/` → `assets/figs/*.svg` (16 plots) | done, reviewed at page size; used in Ch 1–4 and 13 |
| Pages deploy | `.github/workflows/pages.yml` deploys on every push to `main` |
| Local preview | `preview_start bioafe` (Docker, port 4005; entry in `~/SkillSurf/.claude/launch.json`) → http://localhost:4005/biomedical-ic-design/ |
| BRICD home page | Open-BioAFE is Project 01 (*to be commenced*) on www.thebricd.org (`bricd-org.github.io`, pushed 12 Nov, `a2cf7ac`), linking this tutorial; keep its numbers in step with `SPEC`. Preview: `preview_start bricd-site` (port 4006) |

## 2a. Outline review against lecture material (12 Nov 2026)

The user asked whether the course material in `~/Downloads/Courses/Biomedical IC Design` could
improve the outline, "only if required". That folder holds university lecture slides
(biopotential electrodes, operational amplifiers, biopotential amplifiers, signal conditioning,
built on Webster). Most of it was already covered by Ch 2–4 and the outlines. The gaps found and
filled:

- **Ch 4 (written):** new pitfall box at the end of 4.1, *The body is not the only antenna*:
  magnetic loop pickup (1 µT, 50 Hz, 100 cm² → about 3 µV, already differential; twist the
  leads), capacitive pickup on the leads and the grounded shield's ~100 pF/m that drops Z_cm to
  ~30 MΩ at 50 Hz for a one-metre lead (hence driven shields), and RF rectification in the
  input pair. Links to `ch12/#shielding`.
- **Ch 12 (outline):** 12.1 adds RLD saturation safety (series resistor limits patient current;
  loop gain keeps the effective resistance low); 12.4 is now *Input protection, ESD and RF
  filtering* (RC mismatch between inputs costs CMRR); new **12.5 Shielding, guarding and active
  electrodes** `{#shielding}`; two new objectives; reading list adds Rich and Ott.
- **Ch 7 (outline):** 7.1 adds why first-stage gain multiplies the second stage's CMRR (0.1 %
  resistors: 54 dB at unity gain, 94 dB behind a gain of 100); 7.4 adds the worst-case
  (1+G)/(4t) resistor-mismatch CMRR, op-amp CMRR in combination, and CMRR versus frequency.
- **Ch 6 (outline):** 6.2 adds noise with a source, e_n² + i_n²|Z_e|² + 4kT Re{Z_e}, and the
  e_n/i_n crossover (ties to the HBT base-current point in 5.4 and to dry electrodes).
- **Ch 9 (outline):** 9.2 adds residual offset ∝ f_ch (so f_ch just above the 1/f corner),
  duty-cycle and non-overlap errors, and syncing the chopper clock with the ADC.

Not used (already covered, or op-amp basics that *The Art of Analog IC Design* covers): ideal
op-amp circuits, slew rate, offset trimming, electrode chemistry details, electrode catalogue.

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
- **Lecture slides are a private checklist only.** The slides in
  `~/Downloads/Courses/Biomedical IC Design` are never cited, linked, named or copied on the
  public site. Cite the public sources they build on instead (Webster, Pallàs-Areny and Webster,
  Winter and Webster, Rich, Chi et al.).

## 4. Next steps, in order

### Step 1 — Chapters 1–4: DONE (11 Nov 2026)

Written from the plan that was here (the numbers are also in section 8 and in `biosig.py`). Use
them as the style model for later chapters: lead, objectives, design question, numbered sections,
key equations, worked examples with the project's numbers, insight/pitfall/specnote/tryit boxes,
"Read with this chapter", closing takeaways. Figure ids are `fig-N-M` in reading order; table
captions use `{: .tabcaption #tab-N-M }`. Maths inside a `<figure>` caption or a box title must be
written `\( ... \)`, not `$$...$$` (kramdown does not convert maths inside raw HTML).

### Step 1b — Write the outline chapters (user's request, 12 Nov 2026)

The user asked to "continue writing the empty chapters". Order: the curriculum's build stages
(section 8), because stage 2 needs only Python: **Ch 13 (done) → Ch 14 → Ch 19**, then Part II
(Ch 5–12, which needs SG13G2 device numbers from simulation), then the rest of Part III, Part IV,
Part V. For each chapter: follow the Ch 2–4 / Ch 13 style, put every number through `biosig.py`
(add helpers there), draw figures with `figsrc/chNN_figs.py`, remove the *Chapter status: outline*
box, keep the outline's objectives/design question/section titles unless there is a reason, build
and check the page (no `.katex-error`, images load), then update this file.

Notes for the next chapters:
- **Ch 14:** SNDR/SFDR/THD from `tone_metrics`; histogram DNL/INL with capacitor mismatch
  (Pelgrom); Walden and Schreier FoM worked with the Ch 13 numbers (12-b SAR at 2 kS/s, 16-b ΔΣ
  at 500 S/s); kT/C sizing (×4 per bit) vs CV² (×2 per bit); Murmann survey (cite, do not copy
  data); keep Table 14.1.
- **Ch 19:** NTF/STF of 1st/2nd order, `sqnr_os_db(N, osr, L)` already gives the key equation
  (1-bit, L = 2, OSR 128 → 100.2 dB, quoted in Ch 13); simulate a 1st/2nd-order loop in plain
  numpy (python-deltasigma is not installed; install in a venv or write a small `simulate_dsm`
  in `biosig.py`); Lee criterion; idle tones with a DC input (ECG baseline); answer "order and OSR
  for 16 b" at the lowest clock.
- Ch 13 figure 13.3a: plain-oversampling simulation falls ~3 dB under the line at high OSR
  (pure-sine quantisation error is not white); the text says so — keep it if redrawing.

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
  CMRR and imbalance; print the required CMRR. Include a grounded-shield case in the Z_cm sweep
  (~100 pF/m of lead, about 30 MΩ at 50 Hz) against a driven shield, to match the Ch 4 pitfall
  box. Optional: `labs/spice/lab2_body.cir` for ngspice
  (ngspice-47 is installed via Homebrew).
- `data/fetch_data.py`: download helpers only.

### Step 4 — Appendices (`appendices/a_formulas.md` … `e_reading.md` + `appendices/index.md`)
Each page `parent: "Appendices"`; the index `has_children: true`, permalink `/appendix/`, and a
`nav_order` between the parts and References (move References to 8). Content:
A Formula sheet (NEF/PEF, kT/C, CMRR with imbalance, SQNR/ENOB, Walden/Schreier FoM, ΔΣ SQNR,
IQ |Z| and φ — the equations are already in the outline chapters); B Biosignal reference tables
(`SIGNALS` + electrode impedances); C Design-review checklists (AFE: noise incl. current noise × electrode impedance, CMRR incl. vs
frequency, offset, Zin, protection, RF-filter matching, RLD current limit, shield drive; ADC:
kT/C, matching, comparator noise, reference; layout: common centroid, guard rings, shielding of
high-impedance nodes); D Glossary (ExG, NEF, DRL, DSL, CCIA, NTF, OSR, ENOB, driven shield,
guard, active electrode, RF rectification…);
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

- **Open design point from Ch 4:** with the standards' 40.7 kΩ imbalance and a 100 dB amplifier,
  90 dB effective CMRR needs Z_cm ≈ 1.9 GΩ at 50 Hz, about twice the "> 1 GΩ" goal in Table 1.2
  (Ch 1) and `SPEC`. Ch 4 says so in its specnote; settle it in the Ch 29 budgets and then update
  Table 1.2.
- Figure scripts find TeX Gyre Heros through `kpsewhich`; `bricdstyle.py` now also looks in
  `/Library/TeX/texbin`, because a non-login shell may not have it on PATH (plots otherwise fall
  back to DejaVu Sans).
- Some references in `_data/references.yml` are still uncited (they belong to later chapters);
  search `chapters/` for a key before assuming it is used.
- Outline polish (remaining outlines): key equations are placed after each outline chapter's first section (Ch 6 fixed when written; NEF
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
