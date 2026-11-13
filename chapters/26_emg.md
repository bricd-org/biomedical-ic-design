---
title: 26. EMG and Neural Spike Processing
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 26
permalink: /part-4/ch26/
chapter: 26
---

# <span class="chapnum">Chapter 26</span>EMG and Neural Spike Processing

Muscle signals are read through their envelope; neural signals through the timing of individual spikes.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compute EMG envelopes and the time-domain features MAV, WL, ZC and SSC;
- classify hand gestures on NinaPro;
- detect neural spikes with the nonlinear energy operator (NEO);
- explain spike sorting and why implants compress before transmitting.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much resolution, sample rate and channel count does gesture recognition or spike detection actually need?

</div>

Surface EMG is the summed activity of many motor units: a noise-like signal whose *amplitude* follows the force of the contraction. Neural spikes are the opposite: brief, stereotyped events whose *timing* carries the information. Both are handled by the SAR path of Open-BioAFE, EMG at 2 kS/s per channel and spikes at 20–30 kS/s ([Chapter 13]({% link chapters/13_sampling.md %})), and both are reduced to a few numbers per window long before they leave the chip.

## <span class="secnum">26.1</span>EMG envelopes and features

The **envelope** of the EMG, its rectified and smoothed amplitude, tracks muscle force. Over windows of 100–250 ms, four time-domain features, cheap enough for any microcontroller or a few hundred gates, describe each channel:

- **MAV**, the mean absolute value: the envelope itself;
- **WL**, the waveform length: the sum of absolute differences, combining amplitude and frequency;
- **ZC**, the number of zero crossings above a small threshold: a frequency estimate;
- **SSC**, the number of slope sign changes above a threshold: another frequency estimate, more robust to offsets.

Frequency-domain features (median and mean frequency of the spectrum) track muscle fatigue, which shifts the spectrum downwards during a sustained contraction.

## <span class="secnum">26.2</span>Gesture classification

Each hand gesture activates a different combination of forearm muscles, so the pattern of features across several electrode channels identifies the gesture. A linear discriminant on MAV, WL, ZC and SSC from eight channels is the classic baseline, and the NinaPro database {% include cite.html keys="ninapro" %} the standard benchmark.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 26.1 · How many bits does gesture recognition need?</div>

`figsrc/ch26_figs.py` generates synthetic 8-channel EMG for five gestures, each a fixed pattern of channel amplitudes (0.03–0.6 mVrms) with trial-to-trial variation of ±25 % per channel and ±30 % overall, plus 3 µVrms of noise. It computes the four features per channel over 200 ms and trains a linear discriminant on 40 trials per gesture ([Figure 26.1](#fig-26-1)). Over the EMG-mode range of ±5 mV:

- with **5 bits or more**, accuracy is 100 % at 500, 1000 and 2000 S/s;
- with 4 bits, 98–99.5 %; with 3 bits, 57–66 %, against 20 % chance.

The synthetic gestures are well separated by construction. Real recordings, with dozens of gestures, electrode shift and fatigue, are much harder, and NinaPro results depend more on the number of channels, the electrode placement and the training data than on the converter. The design point stands: gesture recognition uses only a handful of bits, and sample rates well below 2 kS/s.

</div>

<figure id="fig-26-1">
  <img src="{{ '/assets/figs/ch26_emg.svg' | relative_url }}" style="width:720px" alt="Synthetic surface EMG for three gestures with its mean-absolute-value envelope, and gesture classification accuracy versus ADC bits for three sample rates">
  <figcaption><span class="capnum">Figure 26.1.</span> <strong>Gesture recognition reads amplitude patterns, not fine detail.</strong> (a) One channel of synthetic surface EMG for three successive gestures and its mean absolute value over 200 ms windows. (b) Accuracy of a linear discriminant on MAV, WL, ZC and SSC from eight channels against ADC bits over ±5 mV, at three sample rates, for five synthetic gestures. Computed in <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">26.3</span>Spike detection

An extracellular spike is 50–500 µV tall and about a millisecond long, riding on background noise and on slower local field potentials ([Chapter 2]({% link chapters/02_signals.md %})). A simple amplitude threshold, typically four to five times the noise's standard deviation estimated robustly from the median absolute value, works when the spikes are large. The **nonlinear energy operator** works better for small, sharp spikes:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Nonlinear energy operator</div>

$$
\psi[n] = x[n]^2 - x[n-1]\,x[n+1]
$$

</div>

$$\psi$$ is large where the signal is both large *and* changing quickly, so it emphasises spikes over slower, equally large background fluctuations. A threshold on a smoothed $$\psi$$, at a multiple of its mean, detects the spikes. It costs two multiplications per sample, which suits an implant.

## <span class="secnum">26.4</span>Spike sorting and compression

Each electrode records several neurons, whose spikes differ in shape. **Spike sorting** extracts each detected spike's waveform, reduces it to a few features (principal components or wavelet coefficients), and clusters them, one cluster per neuron. The full process is computationally heavy and is normally done off the implant.

Implants compress because their radio, not their front-end, limits them. Ten channels at 30 kS/s and 10 bits are 3 Mb/s of raw data, more than an implantable link can sustain within its heat budget. Sending only the spike times (a few bytes per spike, at tens of spikes per second per channel) reduces that by two to three orders of magnitude. Sending short waveform snippets around each spike, so that sorting can be done outside, sits in between. [Chapter 27]({% link chapters/27_soc.md %}) budgets the radio.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

For EMG, compute the time-domain features on chip over 100–250 ms windows; they need only a few bits and modest sample rates, and they reduce the data by hundreds. More channels and good electrode placement improve gesture recognition far more than more bits. For spikes, detect on chip with an amplitude or NEO threshold and send spike times or short snippets, never the raw 30 kS/s stream.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

EMG mode: MAV, WL, ZC and SSC per channel over 200 ms windows from the 2 kS/s, 12-bit SAR data (features computed on 8-bit inputs), streamed at 5–10 windows per second. Spike mode (one channel, optional): NEO detector with an adaptive threshold, spike times and 1.6 ms snippets.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Testing a gesture classifier on trials recorded in the same session as its training data. Electrode position, skin condition and fatigue change from session to session, and accuracy measured within a session overstates what a user will see. Train and test on different sessions, or different days, and report both.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 13]({% link chapters/31_labs.md %}#lab-13) computes MAV, WL, ZC and SSC on NinaPro, trains LDA or SVM classifiers in fixed point, and plots accuracy against channels, sample rate and resolution. Run `figsrc/ch26_figs.py` first, then replace its synthetic windows with NinaPro recordings; if NinaPro needs registration, provide a local file or keep the synthetic fallback.

</div>

**Read with this chapter.** The NinaPro database {% include cite.html keys="ninapro" %}, Buzsáki, Anastassiou and Koch {% include cite.html keys="buzsaki2012" %} (extracellular signals and spikes).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- EMG is read through its envelope: MAV, WL, ZC and SSC over 100–250 ms windows.
- In a synthetic five-gesture study a linear discriminant reaches 100 % with 5 bits over ±5 mV at 500–2000 S/s; real recordings depend more on channels and placement than on bits.
- The nonlinear energy operator $$x[n]^2 - x[n-1]x[n+1]$$ detects small, sharp spikes for two multiplications per sample.
- Implants send spike times or snippets, not raw data: the radio, not the front-end, sets the limit.

</div>
