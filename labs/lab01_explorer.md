---
title: "Lab 1. Biosignal explorer"
parent: Hands-On Labs
nav_order: 1
permalink: /labs/lab-01/
---

# <span class="chapnum">Lab 1 · Python</span>Biosignal explorer

**Goal.** Measure real biosignals and check the amplitude and bandwidth ranges of [Table 2.1]({% link chapters/02_signals.md %}#tab-2-1), which set every specification of the front-end. Goes with [Chapter 2]({% link chapters/02_signals.md %}).

**Data.** MIT-BIH Arrhythmia Database record 100, lead MLII, 360 S/s {% include cite.html keys="mitbih" %}; a CHB-MIT scalp EEG recording such as `chb01_03.edf` (256 S/s, about 40 MB) {% include cite.html keys="chbmit" %}; a NinaPro EMG file (2 kS/s; NinaPro asks you to register before downloading) {% include cite.html keys="ninapro" %}.

**Run.**

```bash
cd labs/python
python lab1_biosignal_explorer.py                                  # streams ECG and EEG
python lab1_biosignal_explorer.py --chbmit chb01_03.edf --ninapro S1_E1_A1.mat
python lab1_biosignal_explorer.py --offline                        # synthetic signals only
```

The script high-passes each signal at the lower edge of its band to remove baseline wander and electrode drift, then measures:

- the **amplitude** as a robust peak-to-peak value, between the 0.5th and 99.5th percentiles, and the RMS (`biosig.amplitude_stats`);
- the **power bandwidth**, the band that holds 95 % of the signal's power, from a Welch spectrum (`biosig.psd`, `biosig.band_edges`).

It plots five seconds of each trace next to its spectrum (`out/lab1_explorer.png`) and writes your version of Table 2.1 to `out/lab1_table.md`.

**Expected results.** With the synthetic signals (`--offline`) the script prints:

| Signal | p-p | RMS | 95 % power band | Table 2.1 |
|---|---|---|---|---|
| ECG | 1.21 mV | 168 µV | 1.2–21.5 Hz | 0.5–4 mV, 0.05–150 Hz |
| EEG | 105 µV | 19.7 µV | 0.5–21.8 Hz | 5–300 µV, 0.5–100 Hz |
| EMG (bursts) | 1.38 mV | 216 µV | 30–441 Hz | 0.05–5 mV, 10–500 Hz |

With the real recordings (`--chbmit data/physionet/chbmit/chb01_03.edf`), the first two rows become:

| Signal | p-p | RMS | 95 % power band | Table 2.1 |
|---|---|---|---|---|
| ECG, MIT-BIH 100, MLII | 1.41 mV | 180 µV | 1–37 Hz | 0.5–4 mV, 0.05–150 Hz |
| EEG, CHB-MIT chb01_03, FP1-F7 | 149 µV | 26 µV | 0.5–18 Hz | 5–300 µV, 0.5–100 Hz |

Both fall inside the Chapter 2 ranges. The EMG row stays synthetic until you download a NinaPro file.

**Questions.**

1. Does each measured amplitude fall inside the Table 2.1 range? Which recording comes closest to an edge of its range, and what does that mean for the gain plan of [Chapter 11]({% link chapters/11_filters.md %})?
2. The ECG's 95 % power band ends near 20–40 Hz, yet diagnostic ECG needs 150 Hz. Which features of the waveform live in the last few per cent of the power? (Hint: look at the QRS complex and at pacemaker spikes, [Chapter 24]({% link chapters/24_ecg.md %}).)
3. Find the mains line in the real ECG and EEG spectra. How large is it in microvolts, and how does it compare with the 1.5 µVrms noise target?
4. Change the high-pass corner from 0.05 Hz to 0.5 Hz for the ECG. What happens to the amplitude, and why does the standard ask for 0.05 Hz in diagnostic mode?
5. From your table, which signal sets the input-referred noise, which sets the input range, and which sets the sample rate?

**Deliverable.** Your version of Table 2.1 with the source of each row, and one paragraph on where your numbers differ from the chapter's and why.

[All labs]({% link labs.md %}) · Previous: [Setting up]({% link labs.md %}#setup) · Next: [Lab 2. Electrodes and interference]({% link labs/lab02_interference.md %})
