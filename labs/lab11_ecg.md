---
title: "Lab 11. ECG chain end to end"
parent: Hands-On Labs
nav_order: 11
permalink: /labs/lab-11/
---

# <span class="chapnum">Lab 11 · Systems</span>ECG chain end to end

**Goal.** Find how many bits and how much input noise a heartbeat detector tolerates, and how it fails under electrode motion, so that a monitoring mode can be specified from evidence. Goes with Chapters [24]({% link chapters/24_ecg.md %}) and [29]({% link chapters/29_arch.md %}).

**Data.** MIT-BIH record 100 with its beat annotations {% include cite.html keys="mitbih" %}, and the electrode-motion record `em` of the Noise Stress Test Database {% include cite.html keys="nstdb" %}, streamed by wfdb or read from local copies (see the [set-up]({% link labs.md %}#setup)). Offline, the script uses the synthetic ECG of Chapter 24 and band-limited (1–20 Hz) noise in place of electrode motion.

**Run.**

```bash
cd labs/python
python lab11_ecg_chain.py                          # record 100, first 5 minutes
python lab11_ecg_chain.py --record 105 --seconds 600
python lab11_ecg_chain.py --offline
```

The chain adds white input noise and 200 µV of baseline wander, quantises over the ±5 mV range of the ECG gain setting ([Table 11.1]({% link chapters/11_filters.md %}#tab-11-1)), and runs the simplified Pan–Tompkins detector of Chapter 24 {% include cite.html keys="pantompkins1985" %}. A detection within ±75 ms of an annotated beat is a true positive. The script then adds electrode-motion noise at the Noise Stress Test's signal-to-noise ratios, with the signal power taken from the QRS amplitude as in that database, (QRS peak-to-peak)²/8.

**Expected results.** Offline (70 synthetic beats), Se/PPV in per cent:

| Input noise | 3 bits | 4 bits | 5 bits | 8 bits | 12 bits |
|---|---|---|---|---|---|
| 0 | 49 / 31 | 84 / 78 | 100 / 100 | 100 / 100 | 100 / 100 |
| 100 µVrms | 56 / 56 | 96 / 96 | 100 / 100 | 100 / 100 | 100 / 100 |
| 200 µVrms | 62 / 46 | 94 / 94 | 99 / 99 | 99.5 / 99.5 | 99.5 / 99.5 |

With electrode motion at 12 bits: 100 % at 24 dB SNR, 98.6 % at 18 dB, 87 % at 12 dB, and below 65 % at 6 dB. These agree with [Worked Example 24.3]({% link chapters/24_ecg.md %}): five bits and 100 µVrms suffice for detection. Electrode motion, which shares the QRS band, breaks the detector long before the converter or the input noise does. Record 105, which is noisy, and records with many ectopic beats (for example 119 or 208) are harder than record 100.

On the real recordings (first five minutes, 371 and 417 beats), Se/PPV in per cent at 100 µVrms of input noise:

| Record | 3 bits | 4 bits | 5 bits | 8 bits | 12 bits | Electrode motion at 6 / 0 dB SNR (12 bits) |
|---|---|---|---|---|---|---|
| 100 | 99.9 / 90.3 | 100 / 99.6 | 100 / 100 | 100 / 100 | 100 / 100 | 99.7 / 98.4, 96.8 / 75.9 |
| 105 | 97.0 / 81.7 | 92.1 / 92.1 | 98.6 / 98.6 | 99.0 / 99.0 | 98.9 / 98.9 | 93.3 / 93.1, 80.3 / 72.0 |

Real QRS complexes are sharper than the synthetic ones, so record 100 survives even 3 bits and electrode motion down to 6 dB. Record 105 saturates near 99 % whatever the converter does: its noise and artefacts, not the bits, limit the detector.

**Questions.**

1. What is the smallest number of bits, at 100 µVrms of noise, that keeps Se and PPV above 99.5 % on record 100? On record 105?
2. Five bits over ±5 mV is an LSB of 312 µV, larger than the input noise. Why does the detector still work? Which stage of Pan–Tompkins is most sensitive to quantisation?
3. Replace electrode motion by NSTDB muscle noise (`ma`) and baseline wander (`bw`). Rank the three by how much they hurt the detector, and explain the ranking from their spectra.
4. A monitoring mode could run the converter at 6 bits and 250 S/s. Using the converter energy of [Chapter 18]({% link chapters/18_sar.md %}), estimate the power saved per channel against the diagnostic mode.
5. Is a sensitivity of 99 % good enough for an arrhythmia monitor that runs for a day? How many missed beats is that?

**Deliverable.** The Se/PPV table against bits and noise for at least two MIT-BIH records, the noise-stress curve, and a specification for an ECG monitoring mode (bits, noise, sample rate) with its evidence.

[All labs]({% link labs.md %}) · Previous: [Lab 10. Switched-capacitor ΔΣ]({% link labs/lab10_scdeltasigma.md %}) · Next: [Lab 12. EEG seizure detection]({% link labs/lab12_seizure.md %})
