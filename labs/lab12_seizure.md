---
title: "Lab 12. EEG seizure detection"
parent: Hands-On Labs
nav_order: 12
permalink: /labs/lab-12/
---

# <span class="chapnum">Lab 12 · Systems</span>EEG seizure detection

**Goal.** Detect seizures from band-power features, and find how far the converter's word length and sample rate can fall before the detector suffers, as a first step towards on-chip detection. Goes with Chapters [25]({% link chapters/25_eeg.md %}) and [27]({% link chapters/27_soc.md %}).

**Data.** Offline, the synthetic EEG of Worked Example 25.1: two-minute records of 20 µVrms background with three 10 s rhythmic discharges (3–6 Hz, 60 µV) each. For real data, download a CHB-MIT record with a seizure {% include cite.html keys="chbmit" %} (the record's summary file on PhysioNet gives the seizure's onset and end) and pass it with `--chbmit`.

**Run.**

```bash
cd labs/python
python lab12_eeg_seizure.py
python lab12_eeg_seizure.py --noise 15e-6
python lab12_eeg_seizure.py --chbmit chb01_03.edf --seizure 2996 3036
```

Each record passes through input noise, an optional decimation (the converter at 128 or 64 S/s instead of 256), and an N-bit converter over the ±0.625 mV range of the EEG gain setting. Per 2 s window the script computes line length and the power in the delta, theta, alpha and beta bands. Two detectors run on the features:

- a **threshold** on theta power at three times its median, as in Chapter 25;
- a **linear discriminant** on the four log band powers, trained on two records at full resolution and tested on four others.

For each detector the script reports window accuracy, event sensitivity, the mean detection latency after onset and the false detections per hour. The power proxy, $$(f_\mathrm{s}/256) \times 2^{N-12}$$, assumes the converter's energy per conversion doubles per bit ([Chapter 14]({% link chapters/14_adcspecs.md %})).

**Expected results.** Offline, at 1.5 µVrms of input noise:

| Bits, rate | Power proxy | Theta threshold: accuracy, latency | LDA: accuracy, latency |
|---|---|---|---|
| 12 b, 256 S/s | 1 | 99.6 %, 2.0 s | 99.2 %, 2.2 s |
| 6 b, 256 S/s | 0.016 | 99.6 %, 2.0 s | 97.9 %, 2.5 s |
| 4 b, 256 S/s | 0.004 | 91.2 %, 3.8 s | 94.6 %, 2.5 s, 30 false detections per hour |
| 12 b, 64 S/s | 0.25 | 99.6 %, 2.0 s | 99.2 %, 2.2 s |
| 6 b, 64 S/s | 0.004 | 99.2 %, 2.0 s | 95.4 %, 3.0 s |

Every discharge is found in every case. Line length stays at 75 % window accuracy, no better than always answering "no seizure", as [Worked Example 25.1]({% link chapters/25_eeg.md %}) found. Theta power needs only 6 bits and 64 S/s: a detection-only mode could run the converter at a fraction of a per cent of the diagnostic mode's energy. The latency of 2 s is set by the window length.

The real recording turns the picture round. On `chb01_03.edf` (one hour of FP1-F7 with one 40 s seizure; the discriminant is trained and tested on the same record, which flatters it):

| Detector, 12 bits, 256 S/s | Window accuracy | Seizure found | Latency | False detections per hour |
|---|---|---|---|---|
| Theta power, 3 × median | 92.2 % | yes | 6 s | 101 |
| LDA on log band powers | 95.6 % | yes | 6 s | 58 |
| Line length, 3 × median | 98.2 % | yes | — | 12 |

Real EEG has far more theta outside seizures than the synthetic background, so the theta threshold fires a hundred times an hour; line length, useless on the synthetic data, is the best of the three here. Word length still barely matters down to 6 bits, but at 4 bits most of the background quantises to zero and the threshold's false detections drop for the wrong reason. Synthetic data shows what a circuit does; only real recordings show whether a detector works.

**Questions.**

1. Why does a single threshold on theta power do as well as the discriminant here? Construct a case where it would not, for example a record with strong alpha or eye-movement artefacts.
2. Halve the window to 1 s. What happens to latency, accuracy and false detections?
3. Raise the input noise to 15 µVrms, ten times the EEG target. Which detector degrades first, and why does band power tolerate noise better than line length?
4. Run a real CHB-MIT seizure. Train on one record of a patient and test on another of the same patient, then on a different patient. What happens to the false detections per hour, the number that decides whether a wearable detector is usable?
5. Count the operations per window of the theta-power detector at 64 S/s and 6 bits, and estimate its energy with the picojoule-per-operation figures of [Chapter 27]({% link chapters/27_soc.md %}).

**Deliverable.** Latency and accuracy against bits and sample rate, with the power proxy, for both detectors, and a proposed detection mode for the chip.

[All labs]({% link labs.md %}) · Previous: [Lab 11. ECG chain end to end]({% link labs/lab11_ecg.md %}) · Next: [Lab 13. EMG gesture recognition]({% link labs/lab13_gestures.md %})
