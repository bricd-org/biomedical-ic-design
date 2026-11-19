---
title: Hands-On Labs
layout: default
nav_order: 7.5
has_children: true
has_toc: false
permalink: /labs/
---

Labs
{: .part-label }

# Hands-On Labs
{: .part-title }

Fifteen labs in three tracks, and a capstone: Python models first, then SG13G2 circuits, then the whole chain on real recordings.
{: .part-blurb }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Lab status</div>

All fifteen labs are written, each with its script: the Python labs in `labs/python/`, and the SG13G2 labs in `labs/spice/`, which need Docker and the IIC-OSIC-TOOLS container. Every expected result in these labs comes from running those scripts. Several of them corrected the chapters: thin-oxide gate leakage limits teraohm biasing (Lab 4), the SAR needs seven low-noise comparator decisions (Labs 7 and 8), and the smallest MIM capacitor is 1.95 fF (Lab 14).

</div>

The labs use only free tools. **Track A** (Python) models signals, interference and converters with NumPy, SciPy, wfdb and python-deltasigma {% include cite.html keys="pydeltasigma" %}. **Track B** (SG13G2) designs transistor-level circuits with Xschem and ngspice in the IHP open PDK {% include cite.html keys="ihppdk" %}. **Track C** (systems) runs the whole chain on real recordings and takes blocks to layout. The Python labs live in [`labs/python/`](https://github.com/bricd-org/biomedical-ic-design/tree/main/labs/python) and share one module, `biosig.py`.

**Table L.1. The fifteen labs.**
{: .tabcaption #tab-l-1 }

| Lab | Track | Chapters | What you do | Deliverable |
|---|---|---|---|---|
| 1 [Biosignal explorer]({% link labs/lab01_explorer.md %}) | A | 2 | Load MIT-BIH, CHB-MIT and NinaPro recordings; plot traces and spectra; measure amplitude and bandwidth | Your version of the Chapter 2 amplitude-versus-bandwidth table |
| 2 [Electrodes and interference]({% link labs/lab02_interference.md %}) | A | 3–4, 12 | Model the body, Randles electrodes and a 51 kΩ‖47 nF imbalance; inject 10 Vrms of mains common mode; sweep CMRR and input impedance; add right-leg drive | Interference versus CMRR and imbalance; the required CMRR |
| 3 [Devices in weak inversion]({% link labs/lab03_devices.md %}) | B | 5–6 | gm/ID curves, flicker noise versus W·L, HBT versus MOS input noise | Lookup tables and noise plots, reused in Labs 4 and 5 |
| 4 [The Harrison LNA]({% link labs/lab04_lna.md %}) | B | 6, 8 | Capacitive-feedback amplifier with pseudo-resistors; AC, noise and transient simulations; NEF | An LNA that meets the spec; NEF versus bias current |
| 5 [Chopper amplifier]({% link labs/lab05_chopper.md %}) | B | 9–10 | Input and output choppers and a DC servo loop; 1/f noise removal, ripple, input impedance; ±300 mV offset | Noise spectra before and after chopping, ripple and input-impedance plots |
| 6 [Ideal ADC and spectral testing]({% link labs/lab06_adctest.md %}) | A | 13–14, 22 | Quantise sine waves; coherent sampling and windows; SNDR, SFDR and ENOB; histogram DNL and INL with capacitor mismatch | A reusable `adctest.py` |
| 7 [StrongARM comparator]({% link labs/lab07_comparator.md %}) | B | 16 | Design; Monte Carlo offset; transient-noise input noise; energy per decision | A comparator with offset and noise numbers |
| 8 [SAR ADC]({% link labs/lab08_sar.md %}) | B | 15, 17–18 | Bootstrapped sample-and-hold, monotonic CDAC, Verilog SAR logic; mixed-signal simulation; `adctest.py` | A 10- to 12-bit SAR with its ENOB and figure of merit |
| 9 [ΔΣ by design]({% link labs/lab09_deltasigma.md %}) | A | 19–20 | First-, second- and third-order NTFs; SQNR versus OSR; incremental mode; fixed-point CIC filter | NTF, coefficients and decimator for the ECG/EEG channel |
| 10 [Switched-capacitor ΔΣ]({% link labs/lab10_scdeltasigma.md %}) | B | 20 | The Lab 9 loop with switched-capacitor integrators and a 1-bit quantiser, compared with the ideal model | Transistor-level spectrum and SQNR |
| 11 [ECG chain end to end]({% link labs/lab11_ecg.md %}) | C | 24, 29 | MIT-BIH and the Noise Stress Test through a behavioural front-end and ADC; Pan–Tompkins QRS detection | QRS sensitivity and positive predictive value versus ADC bits and input noise |
| 12 [EEG seizure detection]({% link labs/lab12_seizure.md %}) | C | 25, 27 | Band-power features on CHB-MIT; a simple classifier; reduced word length and sample rate | Latency and accuracy versus bits and a power proxy |
| 13 [EMG gesture recognition]({% link labs/lab13_gestures.md %}) | C | 26 | MAV, WL, ZC and SSC features on NinaPro; LDA or SVM; fixed point | Accuracy versus channels, sample rate and resolution |
| 14 [Layout to GDS]({% link labs/lab14_layout.md %}) | C | 30 | Comparator and CDAC in KLayout; DRC, LVS and extraction with the JKU template; post-layout simulation | Clean DRC and LVS; post-layout versus schematic |
| 15 [Bioimpedance IQ readout]({% link labs/lab15_bioz.md %}) | B | 28 | Cole tissue model, tetrapolar measurement and digital IQ in Python; then an SG13G2 current source and square-wave IQ demodulator | Cole plot, ΔZ resolution versus current, analog versus digital IQ error |

Each lab has its own page, linked from the table; the [capstone]({% link labs/capstone.md %}) puts the circuit labs together into one Open-BioAFE channel.

## Setting up {#setup}

**Track A and C (Python).** Any Python 3.9 or newer works. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r labs/python/requirements.txt
```

This installs NumPy, SciPy, Matplotlib and wfdb, which streams PhysioNet records {% include cite.html keys="mitbih,chbmit" %} without a manual download. Every lab imports `labs/python/biosig.py`, the same module that computes the numbers and figures in the chapters, and writes its plots and tables to `labs/python/out/`. Each lab also runs offline: a recording that cannot be loaded is replaced by the synthetic signal of `biosig.py`, and the output says which was used. PhysioNet is sometimes slow or briefly down, so the scripts first look for a local copy in `data/physionet/<database>/` (git-ignored) and stream the record only when there is none. To make local copies of everything the labs use:

```bash
mkdir -p data/physionet/mitdb data/physionet/nstdb data/physionet/chbmit
for r in 100 105 119; do for e in hea dat atr; do curl -sSL -o data/physionet/mitdb/$r.$e https://physionet.org/files/mitdb/1.0.0/$r.$e; done; done
for r in em ma bw; do for e in hea dat; do curl -sSL -o data/physionet/nstdb/$r.$e https://physionet.org/files/nstdb/1.0.0/$r.$e; done; done
curl -sSL -o data/physionet/chbmit/chb01_03.edf https://physionet.org/files/chbmit/1.0.0/chb01/chb01_03.edf
```

**Track B and Lab 14 (SG13G2).** Install Docker and pull the IIC-OSIC-TOOLS container {% include cite.html keys="iicosic" %}, which includes the IHP-Open-PDK {% include cite.html keys="ihppdk" %}, Xschem, ngspice and KLayout:

```bash
docker pull hpretl/iic-osic-tools:2026.10
```

The scripts in `labs/spice/` start the container themselves, write a `.spiceinit` that loads the PSP and resistor models, run ngspice in batch mode and parse the results ([Chapter 30]({% link chapters/30_flow.md %})). Run `python labs/spice/sg13_char.py` once: if it reproduces the gm/ID curves of [Chapter 5]({% link chapters/05_devices.md %}), your set-up is complete. For interactive work with Xschem and KLayout, start the container with its desktop as described in its documentation.
