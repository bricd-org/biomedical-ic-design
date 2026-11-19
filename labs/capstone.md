---
title: "Capstone. One Open-BioAFE channel"
parent: Hands-On Labs
nav_order: 16
permalink: /labs/capstone/
---

# <span class="chapnum">Capstone</span>One Open-BioAFE channel

Combine Lab 5, a PGA and Lab 8 (SAR) or Lab 10 (ΔΣ), and optionally Lab 15; verify across corners; feed real ECG and EEG through the transistor-level chain with ngspice PWL sources; and report against the specification of [Table 1.2]({% link chapters/01_why.md %}#tab-1-2). The best designs go to an IHP OpenMPW submission.

**A reference run.** `.venv/bin/python labs/spice/capstone_chain.py` (five ngspice runs; Docker's 7.75 GB allows about three long transients at a time) does a first version of the capstone with the Lab 5 front-end: SG13G2 transmission-gate choppers, a behavioural OTA and the 300 mV electrode offset. It runs that front-end at three MOS corners, then drives it with real recordings as ngspice PWL sources and passes its output through the PGA, decimation to 500 S/s and a 16-bit quantiser:

| Run | Result |
|---|---|
| Corners tt / ss / ff, 1 mV at 37 Hz | gain 91.7 / 91.7 / 91.8; output offset 2.7 / 2.9 / 2.4 mV; ripple 1.2 mV; input impedance 6.5 MΩ |
| MIT-BIH record 100, 3 s, PGA ×1 | chain gain 96, SNR 28.5 dB over 3–40 Hz (6.2 µVrms of error referred to the input); Lab 11's detector finds 3 of 3 R peaks, no extra detections |
| CHB-MIT chb01_03, FP1-F7, 2 s from the seizure onset, PGA ×8 | chain gain 772, SNR 31.1 dB over 3–40 Hz (1.06 µVrms of error on a 37.8 µVrms signal) |

<figure id="fig-lc-1">
  <img src="{{ '/assets/figs/lab_capstone.svg' | relative_url }}" style="width:720px" alt="Two panels: three seconds of MIT-BIH record 100 and two seconds of seizure-onset EEG, each showing the input and the chain output divided by its gain lying on top of each other">
  <figcaption><span class="capnum">Figure LC.1.</span> <strong>Real recordings through the simulated front-end come out intact.</strong> (a) MIT-BIH record 100 and (b) CHB-MIT chb01_03 at the seizure onset, each through the chopped LNA with transistor-level SG13G2 choppers, the PGA, decimation to 500 S/s and a 16-bit quantiser (blue, divided by the chain's gain), over the input passed through the designed 2 Hz servo response (grey), both band-limited to 3–40 Hz. From <code>labs/spice/capstone_chain.py</code> and <code>figsrc/labs_figs.py</code>.</figcaption>
</figure>

[Figure LC.1](#fig-lc-1) shows the two recordings. The comparison passes the input through the designed response first, the lab netlist's 2 Hz servo high-pass (four times the chip's 0.5 Hz, so that a few seconds of simulation settle), because at 3–8 Hz that high-pass alone shifts the phase by 10–30° and would otherwise read as error. What remains, a few microvolts, is chopper residue and the servo's settling within a short record; a longer run, the transistor-level OTA of `labs/spice/sg13_ota.py` and the converter of Lab 8 or 10 are the next steps toward the full capstone.

[All labs]({% link labs.md %}) · Previous: [Lab 15. Bioimpedance IQ readout]({% link labs/lab15_bioz.md %})
