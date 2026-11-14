# HANDOFF — Open-BioAFE Tutorial (pick up here)

Last updated: 14 November 2026 (**all chapters 1–30 written**; Ch 31 set-up + all Python labs (1, 2, 6,
9, 11, 12, 13, 15 part 1) and Lab 3 written with scripts; next: the other labs, appendices; outline review against lecture material, section 2a). On
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
| Ch 19 | **written** (13 Nov 2026): NTF/STF, linear-model SQNR vs simulation (1-bit 2nd order at OSR 128: 100.2 dB formula FS, 84.9 dB simulated at −6 dBFS; effective quantiser gain ≈ 0.63), Table 19.1 (SQNR vs order 1–4 and OSR 16–256), Lee criterion and max stable amplitude, idle tones (DC 0.002 → lines at 38/77/115 Hz at 38.4 kHz), NTF synthesis (Legendre zeros, Butterworth poles, H∞ = 1.5), incremental: 2nd order M = 1024 → 16.5 b worst case (was 16.6; corrected 14 Nov, error 1.04e-5), 512 kHz at 500 S/s vs free-running 3rd order OSR 128 at 38.4 kHz; 3 figures from `figsrc/ch19_figs.py` (~70 s to run) |
| Ch 5 | **written** (13 Nov 2026, title kept "Devices for Microwatt Design"): IC/EKV, gm/ID from SG13G2 sims (n ≈ 1.22, ceiling 31.7 V⁻¹, I_spec ≈ 0.78 µA/□ NMOS, 0.20 µA/□ PMOS), thermal noise 18.5 nV/√Hz at 1 µA (PMOS floor ~40 % above 2nkT/gm in the models), flicker K = 1.6e-10 (NMOS) / 5.4e-10 (PMOS) V²µm² — **NMOS quieter in these models**; unchopped pair needs ~1800 µm²/device (NMOS) for 1 µVrms; HBT npn13G2 gm/IC 37.7, β ≈ 680, e_n 15.1 nV/√Hz flat, base shot noise beats MOS only below ~6 MΩ, r_π 18 MΩ; Pelgrom from PDK mismatch libs: A_VT 3.9/2.2 mV·µm, A_β 0.5/0.33 %·µm, MIM 1 %·µm, HBT IS 3.8 %; 3 figures from `figsrc/ch05_figs.py` |
| Ch 6 | **written** (13 Nov 2026): noise sources (MOS weak-inversion channel noise = shot noise, 2nkT/gm), noise bandwidth (π/2, 1.11, ln fH/fL), chopped vs unchopped pair (0.26–0.33 vs ~1.0 µVrms), e_n/i_n with source; NEF/PEF with the **bandwidth convention made explicit** (brick-wall band: I_tot = NEF²·4kT·U_T·B_n/V², 4kTU_T·99.5 Hz = 4.26e-20 A·V²); limits: BJT pair √2, weak-inversion MOS pair √2·n = 1.73 (SG13G2 sim 1.72–2.05), current reuse → n; EEG target costs 60–840 nA; first stage 2 µA at NEF 3 → 0.44 µVrms; 2 figures from `figsrc/ch06_figs.py`. (The old outline's "single BJT NEF = 1" claim was dropped: with Steyaert's definition a single BJT gives 1/√2.) |
| Ch 7 | **written** (13 Nov 2026): 3-op-amp IA (first stage multiplies CMRR; 0.1 % resistors: worst 54 dB, MC median 67.7 dB; ±300 mV at 1.2 V limits DC-coupled G1 to 1.5), current-feedback IA (no resistor matching, tens-of-mV input range), CCIA (G = Cin/Cfb, offset blocked; **SG13G2 MIM = 1.5 fF/µm²**, 20 pF = 13 300 µm²; unchopped CMRR from MIM matching 78 dB 1σ / 69 dB 3σ → chopping needed), RC-mismatch CMRR falls 20 dB/dec, effective CMRR needs Zcm (Ch 4: ~1.9 GΩ) or RLD; choice: chopped CCIA, Cin 20 pF, Cfb 200 fF; 2 figures from `figsrc/ch07_figs.py` |
| Ch 8 | **written** (13 Nov 2026): Harrison LNA (A_M = 20 pF/200 fF = 40 dB; f_H = gm/(2πA_M C_L) = 24 kHz at 2 pF, 4.8 kHz at 10 pF); **pseudo-resistors simulated** (`labs/spice/sg13_lna.py`, gmin 1e-15 — default gmin caps at 2/gmin!): thin-oxide 1 pair 2e11 Ω (4.1 Hz), 4 pairs 7.6e11 (1.05 Hz), thick-oxide pair 5.6e13 Ω (0.014 Hz 27 °C, 0.032 Hz 37 °C, 1.0 Hz 85 °C); Cgg ≈ 2.2 fF/µm²; capacitive noise gain: unchopped optimum 6200 µm²/0.98 µVrms (C1 20 pF), chopped 0.27–0.29 µVrms with 100–1000 µm²; EMG mode C2 → 2 pF; LNA wideband noise ~5 µVrms must be filtered before sampling; 2 figures from `figsrc/ch08_figs.py` |
| Ch 9 | **written** (13 Nov 2026): chopping as modulation (baseband ≈ S_white(1 + 0.85 f_c/f_ch)); 1000 µm² NMOS pair corner 460 Hz → 0.273 µVrms at 4 kHz (100 µm²: corner 4.6 kHz, 0.367 µV at 4 kHz); ripple = offset × gain (±39 mV for 100 µm², 0.39 mV σ); residual offset 2·f_ch·Δq·R_s (1 fC, 4 kHz: 0.4 µV wet, 8 µV dry); RRL (Yazicioglu 2007); auto-zero folding ~2f_n/f_s; Zin = 1/(2 f_ch C_in) = 6.25 MΩ at 4 kHz with 20 pF; **choice f_ch = 4 kHz, input devices 1000 µm²**; 2 figures from `figsrc/ch09_figs.py` |
| Ch 10 | **written** (13 Nov 2026): chopped Zin 1/(2 f_ch C_in) = 6.25 MΩ flat vs unchopped 2/(jωC_in); pads 5 pF = 640 MΩ@50 Hz/32 MΩ@1 kHz; PF boosting Z/ε (dry needs ε < 6 %; 3 % → 208 MΩ@10 Hz); **input chopper defeats CCIA DC blocking → DSL required**: C_DSL ≥ (V_off/V_DSL)·C_in → 12 pF (1.2 V, noise gain 1.72) or **4 pF with a 3.3 V integrator (noise gain 1.32, chosen)**; f_HP = (C_DSL/C_fb)/(2πτ) → τ = 6.4 s for 0.5 Hz; DSL integrator output sampled by SAR as electrode-offset monitor; chopped LNA noise ≈ 0.36 µVrms; 1 figure from `figsrc/ch10_figs.py` |
| Ch 11 | **written** (13 Nov 2026): Gm-C (100 Hz on 10 pF = 6.3 nS = 0.25 nA; 0.5 Hz = 1.3 pA ≈ leakage → sub-Hz corner by the DSL), Gm-C noise ξkT/C (41 µVrms on 10 pF → filters after gain), SC corner (C2/C1 = 6.4 for 100 Hz at 4 kHz); **gain plan Table 11.1** (ADC range ±0.5 V diff.: ECG 100×1, EEG 100×8, EMG 10×8, spikes 100×8); anti-alias: SAR EMG 2 kS/s → 4th-order Butterworth at 600 Hz (32 dB at 1.5 kHz), chopper ripple 4 kHz = 2·f_s aliases to DC (−66 dB); ΔΣ 512 kHz → one pole, 4 kHz in sinc notch (8 × 500 S/s); mains notch digital (Ch 23); 1 figure from `figsrc/ch11_figs.py` |
| Ch 12 | **written** (13 Nov 2026): RLD divides CM by 1+A → CMRR test needs Zcm 11.4 MΩ at A = 100 (vs 1.15 GΩ); boosted 200 MΩ front-end leaves 0.06 mVpp (24 dB margin); RLD stability with C_body 200 pF and safety resistor R_o (≥ 120 kΩ for 10 µA at 1.2 V; **150 kΩ → 53° PM at 5 kHz crossover**, 45° at 300 pF); CMFB; lead-off DC (nA) / AC (→ Ch 28); ESD (sg13g2_esd, series R noise 0.13 µV for 5 kΩ), RF filter matching; 12.5 shielding/guarding/active electrodes kept (`#shielding`); anchor `#lead-off-detection`; 1 figure `figsrc/ch12_figs.py` |
| Ch 15 | **written** (13 Nov 2026): SAR range ±0.5 V diff → LSB 244 µV; kT/C diff C ≥ 24kT/Δ² = 1.7 pF/side; settling trivial (boot NMOS 1.5–2 kΩ, τ 8 ns on 4 pF); **SG13G2 switch sims** (`labs/spice/sg13_switch.py`): NMOS 0.5/0.13 off above ~0.8 V, TG peak 11 kΩ, Cgg 0.98 fF → ~0.9 fC injection (1.8 LSB on 1 pF); off leakage 6.5/10.8/95 pA at 27/37/85 °C, 2 stacked 2.0/3.3/30 pA → **4 pF/side, stacked off devices** (0.17 LSB droop in 50 µs at 37 °C); 1 figure `figsrc/ch15_figs.py` |
| Ch 16 | **written** (13 Nov 2026): dynamic comparators chosen; SAR comparator offset = static converter offset (4 µm² NMOS pair 2.0 mV σ) → calibrate; **integrating-comparator noise σ = 2nU_T√(q/Q_int)** (weak inversion): LSB/4 at 12 b → 171 fC/device, C_L 342 fF, ~1 pJ/decision (10 b: 62 fJ); low-noise mode only for last bits (~4 pJ/conversion); kickback 1 fF×1.2 V/4 pF = 0.3 mV; metastability negligible (3.7 ns for 1e-9 at τ 200 ps vs 4.8 µs per bit); 1 figure `figsrc/ch16_figs.py` |
| Ch 17 | **written** (13 Nov 2026): CDAC energy by charge conservation (`figsrc/ch17_figs.py` `energy()`): 10 b conventional 1193 / monotonic 256 (matches the quoted 255.5) / Vcm 213 C_uV²; 12 b 4777/1024/853 → 0.84 pJ per conversion with 0.98 fF units (Vcm); 12-b MIM matching needs 22 fF units = 91 pF/side vs kT/C 1.7–4 pF → small array (σ_DNL,mid 0.79 LSB) + redundancy/calibration (Ch 18); MIM vs MOM, common centroid; reference: on-chip 4 µA buffer would cost ~300 pJ/conversion → **off-chip 1 µF on a reference pin** (2 µV droop, 13 nA average buffer current); 1 figure |
| Ch 18 | **written** (13 Nov 2026): binary search, sync vs async (async chosen, burst + sleep), Verilog SAR core; behavioural MC (`figsrc/ch18_figs.py`) with 0.98 fF units σ_u 1.24 %: binary 11.5 b uncal / 11.8 cal, radix-1.8 14 cycles 11.3 uncal / 11.8 cal (redundancy: gap-free for every die + noisy early decisions); energy ≈ 7.6 pJ/conversion (comparator 3.9, logic 1.5 est., CDAC 0.84, ref 0.84, sampler 0.5 est.) → 3.7 fJ/step, 0.12 µW for 8 ch at 16 kS/s; case study Verma 2010 kept qualitative (no unverified numbers); 1 figure |
| Ch 20 | **written** (13 Nov 2026): SC integrators; C_s ≥ 16kT/(3Mσ²) = 1.1 pF (CoI ramp averages noise by 3M/4); OTA settles only to 1 % (1-bit loop) → GBW 1.2 MHz, ~1 µA; integrator swings (a1 = a2 = 0.5, ±0.8): |x1| 1.7, |x2| 2.25 × ref → a2 = 0.25; CT vs DT, ELD; one modulator per channel; **CoI decimator has no exact notches: −28 dB at 4 kHz, 0.9 dB droop at 150 Hz** (Ch 11 corrected: ripple → DC via synchronous clocks + 28 dB); Table 20.1 ≈ 1.9 µW/ch; 1 figure `figsrc/ch20_figs.py` |
| Ch 21 | **written** (13 Nov 2026): direct digitisation (range vs noise), VCO ADCs, **level-crossing ECG sim** (`figsrc/ch21_figs.py`: δ 27 µV → 156 S/s, 9.5 µVrms ≈ 1 % of R; δ 7.6 µV → 562 S/s), compressive sensing, reading ISSCC designs with the tutorial's budgets; Open-BioAFE keeps the classic partition; 1 figure |
| Ch 22 | **written** (13 Nov 2026): coherent sampling and windows (leakage figure), processing gain (4096-pt 12-b floor ≈ −107 dBc/bin), aliased harmonics, sine-histogram DNL with arcsine correction (2^20 samples → 160 hits/code → 0.07–0.08 LSB error vs ramp), ~2.6 M samples for 0.05 LSB, models vs transistors, returned-die test plan; 1 figure `figsrc/ch22_figs.py` |
| Ch 23 | **written** (13 Nov 2026): sample rates per application; ST distortion (0.15 mV ST: causal 0.5 Hz HP → 0.107 mV, zero-phase 0.131, causal 0.05 Hz 0.146); baseline (spline/median), adaptive & comb notch; wavelets; **fixed point: 4th-order 0.5 Hz HP at 500 S/s — direct form unstable ≤ 30 bits, SOS 71 dB at 26 bits** → decimate first / leave sub-Hz HP to the analog DSL; 1 figure `figsrc/ch23_figs.py` |
| Ch 24 | **written** (13 Nov 2026): Pan–Tompkins (compact version in `figsrc/ch24_figs.py`), HRV, beat classification (patient-independent), NSTDB; **behavioural sweep on synthetic ECG: Se = PPV = 100 % with ≥ 5 bits over ±5 mV and ≤ 100 µVrms noise; 98.6–100 % at 200 µVrms; 4 bits 85–96 %** → spec set by EEG/morphology, monitoring mode could be far cheaper (Ch 29); 1 figure |
| Ch 25 | **written** (13 Nov 2026): band power & spectral features, artefacts (ICA offline, flag on chip), seizure detection on synthetic EEG (`figsrc/ch25_figs.py`, 3 rhythmic 60 µV discharges, 2 s windows, EEG range ±0.625 mV): **line length fails (= 75 % trivial), theta power 99 % at 6–7 bits even with 15 µVrms noise**; SSVEP & motor imagery; 1 figure |
| Ch 26 | **written** (13 Nov 2026): EMG envelope & MAV/WL/ZC/SSC; synthetic 8-ch 5-gesture LDA (`figsrc/ch26_figs.py`): 100 % with ≥ 5 bits over ±5 mV at 500–2000 S/s, 4 bits 98–99.5 %, 3 bits 57–66 % (synthetic = easy; NinaPro harder, depends on channels/placement); NEO spike detector; spike sorting off-implant, send spike times/snippets (3 Mb/s raw for 10 ch); 1 figure |
| Ch 27 | **written** (14 Nov 2026): data rates raw vs features (8 ch: ECG 64 vs 0.34 kb/s, EEG 33 vs 0.38, EMG 192 vs 2.6, 1 spike ch 360 vs 6.7 → 54–190×); radio at ~5 nJ/b: raw EMG 960 µW (12× the 80 µW AFE), features 2–13 µW; Verma 2010 qualitative; compression; LDO/PSRR (80 dB: 30 µV → 3 nV); BLE/backscatter/inductive; stimulation & charge balance; spec: features out over SPI, raw on demand; 1 figure `figsrc/ch27_figs.py` (energy/bit values are order-of-magnitude assumptions) |
| Ch 28 | **written** (14 Nov 2026): applications; Cole model (example R0 60, R∞ 30, fc 30 kHz, α 0.7 → 42 Ω −12° at 50 kHz); bipolar adds 2Z_e (≈2 kΩ wet, 10 kΩ dry at 50 kHz) → tetrapolar; excitation options; CF limit 500 µA at 50 kHz; IQ demod, resolution 50 nV/√Hz·√10 Hz/I → 16 mΩ at 10 µA, 3.2 mΩ at 50 µA; square-wave demod odd harmonics; ECG+Z frequency separation; impedance-aware mode spec; 1 figure `figsrc/ch28_figs.py` |
| Ch 29 | **written** (14 Nov 2026): noise budget 0.51 µVrms wet / 1.26 dry (electrodes 91 % of dry noise power); CMRR test 0.06 mVpp (24 dB margin), Z_cm need ≈ 12 MΩ with RLD; power 6.8 µW/ch ECG/EEG, 4.9 EMG; ~1.7 mm² core; Table 29.1 spec vs designed; bioZ channel ~5 µW; floorplan; budgets live in `figsrc/ch29_figs.py` (NOISE/POWER tables). **Table 1.2 Z_cm row updated; Ch 3 and Ch 4 sentences aligned** |
| Ch 30 | **written** (14 Nov 2026): Table 30.1 tool set (Xschem, ngspice/Xyce, Python, Verilog/Icarus/Verilator, Yosys/OpenROAD, KLayout, JKU template); `.spiceinit` OSDI + corner lib + subcircuits; gmin/abstol/time-varying traps from this tutorial; XSPICE+Verilator co-sim; corners (tt/ss/ff/sf/fs, ±10 % supply, 0–45 °C use, −20–85 °C qual) + mismatch MC; DRC/LVS/PEX; tape-out checklist; no figure. **All outline chapters 1–30 are now written. Next: Step 2 (Ch 31 labs), Step 3 (lab scripts), appendices** |
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

### Step 1c — Architecture and circuit diagrams (user's request, 14 Nov 2026)

The user asked for more figures that explain the chapters, "a lot of architecture diagrams are missing in
the data converter section". Every Part III figure so far is a data plot. Draw diagrams as **hand-written
SVG** in `assets/figs/` like `ch04_mains_coupling.svg` (viewBox 720 wide, Libre Franklin, palette from
`figsrc/bricdstyle.py`: strokes #1D2A30, analog boxes #E4EEF8, digital boxes #FBF1DF, clocks #9A6212,
secondary text #56656B). Insert with the placeholder number NEW (id fig-N-NEW, "Figure N.NEW") and run
`python tools/renumber_figs.py N`, which renumbers ids, captions and cross-links in all chapters. Planned, in order of value:
- Ch 18: SAR architecture (S/H, differential CDAC, comparator, async logic, self-timed clock, output) — **DONE** (Fig 18.1, `ch18_sar_arch.svg`; old 18.1 → 18.2)
- Ch 20: incremental ΔΣ with reset and CoI decimator — **DONE** (Fig 20.1, `ch20_incr_arch.svg`; old 20.1 → 20.2);
  SC integrator — **DONE** (Fig 20.2, `ch20_scint.svg`)
- Ch 19: ΔΣ loop and its linear model — **DONE** (Fig 19.1, `ch19_loop.svg`)
- Ch 17: binary vs split CDAC — **DONE** (Fig 17.1, `ch17_arrays.svg`)
- Ch 16: StrongARM latch schematic with its phases — **DONE** (Fig 16.1, `ch16_strongarm.svg`)
- Ch 15: sampling switch + bootstrapped switch — **DONE** (Fig 15.1, `ch15_switches.svg`)
- Ch 13: sampling chain — **DONE** (Fig 13.1, `ch13_chain.svg`)
- Ch 21: direct digitisation, VCO ADC — **DONE** (Fig 21.1, `ch21_arch.svg`); Ch 22: test bench — **DONE** (Fig 22.2, `ch22_bench.svg`)
- Part II (all current figures are data plots): Ch 8 Harrison LNA — **DONE** (Fig 8.1); Ch 9 chopper
  amplifier with spectra — **DONE** (Fig 9.1);
  Ch 10 CCIA with DC-servo and impedance-boosting loops — **DONE** (Fig 10.1); Ch 12 RLD loop — **DONE**
  (Fig 12.1); Ch 7 IA topologies — **DONE** (Fig 7.1); Ch 11 gain plan and two paths — **DONE** (Fig 11.1)
- Ch 29 full-chip block diagram (Fig 29.1), Ch 28 tetrapolar + IQ readout (Fig 28.2), Ch 24 Pan–Tompkins
  pipeline (Fig 24.1), Ch 27 system partition (Fig 27.1) — **DONE**; still to draw: Ch 14 architecture map

### Step 1 — Chapters 1–4: DONE (11 Nov 2026)

Written from the plan that was here (the numbers are also in section 8 and in `biosig.py`). Use
them as the style model for later chapters: lead, objectives, design question, numbered sections,
key equations, worked examples with the project's numbers, insight/pitfall/specnote/tryit boxes,
"Read with this chapter", closing takeaways. Figure ids are `fig-N-M` in reading order; table
captions use `{: .tabcaption #tab-N-M }`. Maths inside a `<figure>` caption or a box title must be
written `\( ... \)`, not `$$...$$` (kramdown does not convert maths inside raw HTML).

### Step 1b — Write the outline chapters: DONE (12–14 Nov 2026)

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

### Step 2 — Chapter 31 `chapters/31_labs.md` — Hands-on Labs: set-up, Lab 1, Lab 2 DONE (14 Nov 2026)
Done: set-up (venv + `labs/python/requirements.txt`, container pull), Lab 1 and Lab 2 in full with
expected-results tables (synthetic numbers for Lab 1; Lab 2 matches WE 4.1–4.4 and Ch 12 exactly),
questions and deliverables; "Lab status" box replaces the outline box.
**Lab 6** (`labs/python/adctest.py`, module + lab: sine_test with rect/hann/bh4 and `half` lobe width,
ramp and sine histograms with amplitude/offset estimated from end codes; reproduces WE 14.1 exactly)
and **Lab 9** (`labs/python/lab9_deltasigma.py`: NTFs, SQNR vs OSR formula vs sim, incremental with
a2 = 0.25, bit-true CoI, −28 dB at 4 kHz) also DONE. Side fixes: Ch 22 now warns that Hann's near
skirt (−41 dBc) caps SNDR at ~41 dB unless ~30 bins are excluded; the incremental converter is
**16.5 bits** worst case (error 1.04e-5), corrected from 16.6 in Ch 19, 20, 29.
**Lab 11** (`lab11_ecg_chain.py`: Pan–Tompkins, Se/PPV vs bits × noise matches WE 24.1; NSTDB em
noise stress, SNR from QRS p-p²/8) and **Lab 15 Python part** (`lab15_bioz.py`: Cole, bipolar vs
tetrapolar, time-domain digital IQ confirms WE 28.1 16/3.2/0.32 mΩ with rms currents; square-wave
excitation+demod reads 3.6 % low) also DONE (14 Nov).
**Lab 12** (`lab12_eeg_seizure.py`: theta threshold vs LDA on log band powers, bits × decimation,
latency, false detections/h, power proxy (fs/256)·2^(N-12); theta 99.6 % down to 6 b and 64 S/s;
line length 75 %, as WE 25.1) DONE (14 Nov).
**Lab 13** (`lab13_emg_gestures.py`, ~1 min: integer-code features, LDA on standardised features,
channels × fs × bits; fixed point with Mitchell log2 keeps 100 % at 6-b weights (standardising is
essential, else 8-b weights fall to chance); electrode shift 0.4 → 84.5 %) DONE (14 Nov).
All Python labs are now written (1, 2, 6, 9, 11, 12, 13, 15 part 1). The NinaPro and CHB-MIT code
paths are untested here (no wfdb, no data downloaded): test them first when wfdb is installed.
**Lab 3** written from the existing `labs/spice/sg13_char.py` and its CSVs (expected numbers = Ch 5);
watch out: a literal `|` in a list item (|V<sub>DS</sub>|) makes kramdown build a table, use `&#124;`.
**Lab 4** written (14 Nov): Part 1 = `sg13_lna.py` pseudo-resistor table (Ch 8 numbers), Part 2 =
student-built LNA with Ch 8 targets (C1 20 pF, C2 200 fF, 40 dB, f_H ≈ 24 kHz at 2 pF, 6200 µm²
unchopped optimum, NEF limit 1.73). No full-LNA testbench script exists yet: adding
`labs/spice/lab4_lna.py` (OTA + caps + pseudo-R, AC/noise/tran/NEF sweep) would make it complete.
**Next: the SG13G2 labs 5, 7, 8, 10, 14 and Lab 15 part 2** (need Docker), then the appendices.
Original plan:
The outline has the lab table and a short section per lab. Write the set-up section, Lab 1 and
Lab 2 in full (goal, code, expected figure and numbers, questions); keep the anchors
(`{#lab-1}` … `{#lab-15}`, `{#setup}`, `{#capstone}`) because other pages link to them.

### Step 3 — Lab scripts in `labs/python/`: lab1 + lab2 DONE (14 Nov 2026)
`lab1_biosignal_explorer.py` (wfdb optional, falls back to synthetic; CHB-MIT via `wfdb.rdrecord`
on the EDF — not tested here because wfdb is not installed in the anaconda env and nothing was
downloaded) and `lab2_electrodes_interference.py` (verified). Original plan:
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

- **Resolved in Ch 12 (keep Table 1.2 in step in Ch 29):** the RLD (loop gain 100) cuts the Z_cm need to 11.4 MΩ. Original note — **Open design point from Ch 4:** with the standards' 40.7 kΩ imbalance and a 100 dB amplifier,
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
