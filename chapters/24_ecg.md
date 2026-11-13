---
title: 24. ECG Processing
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 24
permalink: /part-4/ch24/
chapter: 24
---

# <span class="chapnum">Chapter 24</span>ECG Processing

Detecting heartbeats is the oldest biomedical DSP problem, and the best way to see how ADC bits and amplifier noise reach a clinical result.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- implement the Pan–Tompkins QRS detector;
- compute heart rate and heart-rate variability metrics;
- classify beats on the MIT-BIH Arrhythmia Database;
- test robustness with the MIT-BIH Noise Stress Test Database;
- show how ADC bits and AFE noise move detection sensitivity.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How many bits and how much input noise can the ECG chain afford before QRS detection degrades?

</div>

Everything an ECG system reports, heart rate, rhythm, arrhythmia alarms, starts with finding each QRS complex. This chapter builds the standard detector, uses it to answer the design question with a behavioural model of the Open-BioAFE chain, and sketches what comes after detection. The figures use the synthetic ECG of `biosig.ecg()`, whose beat times are known exactly; Lab 11 repeats the study on real recordings.

## <span class="secnum">24.1</span>Pan–Tompkins QRS detection

The detector of Pan and Tompkins {% include cite.html keys="pantompkins1985" %} has stayed the reference for four decades because each of its stages has a clear job:

1. a **band-pass filter** at 5–15 Hz keeps the QRS energy and rejects baseline wander, P and T waves, and muscle noise;
2. a **derivative** emphasises the QRS's steep slopes;
3. **squaring** makes everything positive and stresses large slopes over small ones;
4. a **moving-window integrator** of about 150 ms, the width of a wide QRS, turns each complex into one smooth pulse;
5. **adaptive thresholds**, which track running estimates of the signal-peak and noise-peak levels, decide which pulses are beats, with a 200 ms refractory period after each one.

The original paper reported detecting 99.3 % of the beats in the MIT-BIH Arrhythmia Database {% include cite.html keys="mitbih" %}. `figsrc/ch24_figs.py` contains a compact version, and [Figure 24.1](#fig-24-1)a shows its stages.

## <span class="secnum">24.2</span>Heart rate and HRV

The intervals between successive R peaks, the **RR intervals**, give the instantaneous heart rate. Their variation, **heart-rate variability**, reflects the autonomic nervous system. Time-domain metrics are SDNN (the standard deviation of normal RR intervals) and RMSSD (the rms of successive differences). Frequency-domain metrics are the power in the low-frequency (0.04–0.15 Hz) and high-frequency (0.15–0.4 Hz) bands of the RR series, after resampling it to a uniform rate. HRV needs R-peak times accurate to a few milliseconds, which 500 S/s and a peak refinement on the band-passed signal provide; 125 S/s with parabolic interpolation of the peak is almost as good.

## <span class="secnum">24.3</span>Beat classification

Once beats are found, each can be described by a handful of features: RR intervals before and after, QRS width, amplitudes, and a few coefficients of its shape. A simple classifier, from thresholds to linear discriminants, separates normal beats from ventricular ectopic beats with high accuracy on the MIT-BIH database. Two precautions keep the results honest. Train and test on *different patients*, because beats from the same patient look alike. And report sensitivity and positive predictivity per class, not overall accuracy, because normal beats dominate the database.

## <span class="secnum">24.4</span>Noise stress testing

Real recordings carry baseline wander, muscle noise and electrode motion. The MIT-BIH Noise Stress Test Database {% include cite.html keys="nstdb" %} provides calibrated recordings of each noise type, to be added to clean ECG at chosen signal-to-noise ratios. Electrode-motion noise is the hardest, because its spectrum overlaps the QRS's. A detector, or a front-end, is characterised by how its sensitivity and positive predictivity fall as the SNR drops.

## <span class="secnum">24.5</span>Co-design: bits and noise versus sensitivity

A behavioural chain answers the design question: synthetic ECG (1 mV R wave, 75 beats per minute with 5 % variability), plus white input noise, plus 200 µV of baseline wander, through a converter whose ±5 mV input range is quantised to $$B$$ bits (a gain of 100 into the ±0.5 V converter of Part III), then the detector.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 24.1 · How much does QRS detection need?</div>

Over 70 beats ([Figure 24.1](#fig-24-1)b):

- with **5 bits or more** and up to 100 µVrms of input noise, sensitivity and positive predictivity are both **100 %**;
- with 200 µVrms of noise they stay at 98.6–100 %;
- with 4 bits, sensitivity falls to 85–96 %, and with 3 bits to about 50–60 %.

QRS detection is extraordinarily tolerant: five bits over ±5 mV is an LSB of 312 µV, and 100 µVrms is sixty-seven times the EEG noise target.

</div>

<figure id="fig-24-1">
  <img src="{{ '/assets/figs/ch24_qrs.svg' | relative_url }}" style="width:720px" alt="Stages of a Pan-Tompkins QRS detector on a noisy quantised ECG, and QRS detection sensitivity versus ADC bits for four input noise levels">
  <figcaption><span class="capnum">Figure 24.1.</span> <strong>Heartbeat detection needs only a few bits.</strong> (a) Stages of the Pan–Tompkins detector on a synthetic ECG quantised to 8 bits with 50 µVrms of noise: the signal, the 5–15 Hz band-pass output and the moving-window integral, with the detected beats (dotted). (b) QRS sensitivity against ADC bits over a ±5 mV input range for four levels of input noise, averaged over three noise seeds. Computed in <code>figsrc/ch24_figs.py</code>.</figcaption>
</figure>

The lesson is not that the Open-BioAFE specification is too strict. Its 16 bits and 1.5 µVrms are set by EEG and by diagnostic ECG morphology, ST levels of tenths of a millivolt and P waves of a few tens of microvolts ([Chapter 2]({% link chapters/02_signals.md %})). The lesson is that a heart-rate monitor could run the same chip in a much cheaper mode: a few bits, a relaxed front-end bias, a lower sample rate. That trade belongs in the system budget of [Chapter 29]({% link chapters/29_arch.md %}).

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Size the chain for the most demanding use of the signal, not for the easiest. QRS detection works with 5 bits and 100 µVrms of noise, so a monitoring mode can save a great deal of power; diagnostic morphology and EEG set the full specification. Validate every claim on real recordings with noise added from the Noise Stress Test Database, and report sensitivity and positive predictivity, per class, on patients the detector was not tuned on.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

On-chip QRS detection (Pan–Tompkins at 250 S/s) for heart rate and RR intervals in a low-power monitoring mode; full 16-bit, 500 S/s raw ECG in diagnostic mode. A monitoring mode with the ΔΣ reduced to about 8 bits and the front-end bias halved is a candidate for the budgets of [Chapter 29]({% link chapters/29_arch.md %}).

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Scoring a detector on a different time window from the reference annotations. Detections in a stretch the reference does not cover count as false positives and lower the positive predictivity for no real reason; an early version of this chapter's script did exactly that and reported 92 %. Score detections and annotations over the same window, with a fixed tolerance (75–150 ms).

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 11]({% link chapters/31_labs.md %}#lab-11) runs MIT-BIH records and the Noise Stress Test through a behavioural front-end and ADC with Pan–Tompkins detection, and plots sensitivity and positive predictivity against ADC bits and input noise. Start from `figsrc/ch24_figs.py`, replace `biosig.ecg()` with a record loaded by `wfdb`, and add electrode-motion noise at 6, 0 and −6 dB SNR.

</div>

**Read with this chapter.** Pan and Tompkins {% include cite.html keys="pantompkins1985" %}, Tompkins {% include cite.html keys="tompkins" %}, the MIT-BIH Arrhythmia Database {% include cite.html keys="mitbih" %} and Noise Stress Test Database {% include cite.html keys="nstdb" %}.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Pan–Tompkins: 5–15 Hz band-pass, derivative, squaring, 150 ms integration, adaptive thresholds with a refractory period.
- RR intervals give heart rate and HRV (SDNN, RMSSD, LF/HF power); HRV needs millisecond R-peak timing.
- Classify beats with patient-independent training and per-class metrics.
- In a behavioural chain, QRS detection stays at 100 % with 5 bits over ±5 mV and up to 100 µVrms of noise.
- The chip's specification is set by EEG and diagnostic morphology; heart-rate monitoring could run in a far cheaper mode.

</div>
