---
title: "Lab 13. EMG gesture recognition"
parent: Hands-On Labs
nav_order: 13
permalink: /labs/lab-13/
---

# <span class="chapnum">Lab 13 · Systems</span>EMG gesture recognition

**Goal.** Find what a gesture classifier needs from the front-end (channels, sample rate, bits), and whether the classifier itself fits in a few hundred gates of fixed-point logic. Goes with [Chapter 26]({% link chapters/26_emg.md %}).

**Data.** Offline, the synthetic 8-channel EMG of Worked Example 26.1: five gestures, each a fixed pattern of channel amplitudes with trial-to-trial variation. For real data, download a NinaPro subject's `.mat` file {% include cite.html keys="ninapro" %} (registration required) and pass it with `--ninapro`; the script uses repetitions 2 and 5 as the test set, as the NinaPro papers do.

**Run.**

```bash
cd labs/python
python lab13_emg_gestures.py                        # about a minute
python lab13_emg_gestures.py --ninapro S1_E1_A1.mat
```

The converter is modelled as signed integer codes over the ±5 mV range of the EMG gain setting. The four features of Chapter 26 (MAV, WL, ZC and SSC) are computed from the integer codes over 200 ms windows. A linear discriminant with a shared covariance, on standardised features, classifies them. The script works through three steps:

1. accuracy against 2, 4 and 8 channels, 500 to 2000 S/s and 3 to 12 bits;
2. the classifier in **fixed point**: integer features, a Mitchell approximation of log₂ (the position of the leading one plus the remaining bits as a fraction, a shift and a priority encoder in hardware), and weights quantised to 8, 6 and 4 bits;
3. an **electrode shift** between training and use, modelled by mixing each channel with its neighbour.

**Expected results.** Offline:

| Channels | 3 bits | 4 bits | 5 bits | 8 bits | 12 bits |
|---|---|---|---|---|---|
| 2 (1 kS/s) | 42 % | 66 % | 84 % | 89 % | 91 % |
| 4 (1 kS/s) | 45 % | 88 % | 96 % | 98.5 % | 99.5 % |
| 8 (500 / 1000 / 2000 S/s) | 48–51 % | 96–98.5 % | 100 % | 100 % | 100 % |

In fixed point, with 8 channels at 1 kS/s and 8 bits, accuracy stays at 100 % with 8-bit and 6-bit weights and 99.5 % with 4-bit weights. A shift that mixes 20 % of the neighbouring channel costs 1 %, but 40 % costs 15 % and 60 % leaves 40 %. The converter needs 5 bits and 500 S/s, as [Worked Example 26.1]({% link chapters/26_emg.md %}) found. The number of channels and the electrode placement matter far more than the converter, and the classifier fits in small integer logic. Standardising the features before quantising the weights is essential: without it the log features' large common offset swamps the differences between classes, and 8-bit weights fall to chance.

**Questions.**

1. Why do two channels stop at about 90 % however many bits you give them? Which gestures do they confuse? (Print a confusion matrix.)
2. Drop one feature at a time. Which feature carries the most information at 4 bits, and which at 12 bits?
3. Retrain after the electrode shift with only five trials per gesture. How much accuracy does a short recalibration recover?
4. Run NinaPro. How does the accuracy compare with the synthetic data, and does it still saturate at 5 bits?
5. Count the additions, comparisons and multiplications per window of the fixed-point classifier for 8 channels and 5 gestures, and estimate its energy with the figures of [Chapter 27]({% link chapters/27_soc.md %}).

**Deliverable.** Accuracy against channels, sample rate and resolution, the fixed-point classifier with its word lengths, and a recommendation for the EMG mode of the chip.

[All labs]({% link labs.md %}) · Previous: [Lab 12. EEG seizure detection]({% link labs/lab12_seizure.md %}) · Next: [Lab 14. Layout to GDS]({% link labs/lab14_layout.md %})
