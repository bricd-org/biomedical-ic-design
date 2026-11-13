---
title: 23. A DSP Toolkit for Biosignals
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 23
permalink: /part-4/ch23/
chapter: 23
---

# <span class="chapnum">Chapter 23</span>A DSP Toolkit for Biosignals

Most of what a clinician sees has been filtered, decimated and cleaned after the ADC. The filters must not distort the waveform features they are meant to reveal.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- choose sample rates for each biosignal;
- compare FIR and IIR filters and use zero-phase filtering;
- remove baseline wander and mains interference with adaptive and comb notch filters;
- use wavelets for denoising and feature extraction;
- predict fixed-point effects and choose word lengths.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which filters, at what word length, clean each biosignal without distorting it, and how much do they cost on chip?

</div>

Part III ends with numbers: 16-bit samples at 500 S/s for ECG and EEG, 12-bit samples at 2 kS/s for EMG. Part IV turns them into information, a heartbeat, a seizure, a gesture, either on the chip or after a radio link. This chapter collects the tools the later chapters share. Tompkins's book {% include cite.html keys="tompkins" %} is the classic reference for all of them.

## <span class="secnum">23.1</span>Sample-rate choices

The converters deliver fixed rates ([Table 13.1]({% link chapters/13_sampling.md %}#tab-13-1)). Each application then keeps only what it needs:

- **diagnostic ECG**: 500 S/s for 0.05–150 Hz; morphology (ST segments, QRS width) needs the full band and the low corner;
- **monitoring ECG**: 125–250 S/s for 0.5–40 Hz; heart rate and rhythm survive heavy filtering;
- **EEG**: 256 S/s for 0.5–100 Hz; seizure features live below 30 Hz;
- **EMG**: 1–2 kS/s for 10–500 Hz; gesture features are computed over windows of 100–250 ms;
- **spikes**: 20–30 kS/s for 0.3–7 kHz, reduced to spike times and waveforms before transmission.

Reducing the rate after filtering, **decimation**, is the cheapest data reduction there is, and it comes before any other processing on chip.

## <span class="secnum">23.2</span>FIR, IIR and zero-phase filtering

**FIR** filters can have exactly linear phase, so every frequency is delayed by the same time and the waveform's shape survives, but they need many taps for sharp responses at low frequencies. **IIR** filters reach the same sharpness with a handful of coefficients, but their phase is nonlinear, and they distort waveforms.

The classic example is the ST segment, the stretch between the QRS complex and the T wave whose level a cardiologist reads for ischaemia. A causal high-pass filter strong enough to remove baseline wander also tilts the ST segment.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 23.1 · What a 0.5 Hz high-pass does to the ST segment</div>

Add a 0.15 mV ST elevation to the synthetic ECG and measure it, relative to the PR baseline, after a first-order high-pass ([Figure 23.1](#fig-23-1)a):

- causal, 0.5 Hz: **0.107 mV**, 29 % low;
- zero-phase (forward and backward), 0.5 Hz: 0.131 mV, 13 % low;
- causal, 0.05 Hz: 0.146 mV, within 3 %.

The 0.05 Hz corner that the diagnostic ECG standards specify exists for this reason. Monitoring ECG can use 0.5 Hz because it needs only the beats.

</div>

**Zero-phase** filtering runs the same IIR filter forwards and then backwards over the record, cancelling its phase. It needs the whole record, or at least a block of it, so it works offline or with a delay, not in a real-time loop.

## <span class="secnum">23.3</span>Baseline wander and mains interference

**Baseline wander**, from breathing and electrode motion, sits below about 0.5 Hz. Besides a high-pass filter, two nonlinear methods remove it without touching the ST segment: fit a spline through the PR segments of successive beats and subtract it, or subtract a median-filtered version of the signal over a window longer than a beat. Both need the beats to be found first ([Chapter 24]({% link chapters/24_ecg.md %})).

**Mains interference** at 50 or 60 Hz and its harmonics is what remains after the analog chain's CMRR and right-leg drive ([Chapter 12]({% link chapters/12_cmcontrol.md %})). A fixed notch drifts off the mains frequency, which varies by a few tenths of a hertz, and rings after artefacts. An **adaptive notch** instead synthesises a sine at the measured mains frequency, adjusts its amplitude and phase with a least-mean-squares loop to match the interference, and subtracts it, tracking slow changes. A **comb filter**, a delay of one mains period subtracted from the signal, removes all the harmonics at once, at the price of notches at every multiple of 50 Hz, including some in the EMG band.

## <span class="secnum">23.4</span>Wavelets

A wavelet transform splits a signal into octave bands with good time resolution at high frequencies and good frequency resolution at low frequencies, which suits biosignals made of short events on slow backgrounds. Two uses dominate. **Denoising**: transform, shrink the small coefficients that are mostly noise, and transform back, which removes noise without the blurring of a low-pass filter. **Feature extraction**: the QRS complex concentrates in the scales around 10–40 Hz, so a QRS detector can work on those coefficients alone. On chip, a lifting implementation of a short wavelet needs only additions and shifts.

## <span class="secnum">23.5</span>Fixed-point effects

On-chip filters run in fixed point, and three effects set the word length.

- **Coefficient quantisation** moves the poles. A filter whose poles sit very close to the unit circle, such as a high-pass at 0.5 Hz with 500 S/s (poles at 0.994), is extremely sensitive.
- **Round-off noise** is added at every multiplication and grows with the filter's internal gain.
- **Limit cycles**: small oscillations that a recursive filter sustains with zero input because of rounding.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Why narrow filters need long words</div>

$$
\text{pole radius } r \approx 1 - \frac{2\pi f_\mathrm{c}}{f_\mathrm{s}} \quad\Rightarrow\quad \text{coefficients must resolve } 1 - r \approx 6\times10^{-3}\ (f_\mathrm{c} = 0.5\ \text{Hz},\ f_\mathrm{s} = 500\ \text{S/s})
$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 23.2 · Word length of a baseline high-pass</div>

A 4th-order Butterworth high-pass at 0.5 Hz, at 500 S/s, implemented in fixed point ([Figure 23.1](#fig-23-1)b):

- in **direct form**, its expanded polynomial coefficients are so sensitive that it is unstable at every word length up to 30 bits;
- as **second-order sections**, it reaches 71 dB, the level of a 12-bit converter, at 26 bits, and 97 dB at 30 bits.

Decimating to 125 S/s first, then filtering, moves the poles away from $$z = 1$$ by a factor of four and saves several bits. Better still, let the analog DC servo loop ([Chapter 10]({% link chapters/10_dsl.md %})) do the sub-hertz high-pass and keep the digital filters for corners well above 1 Hz.

</div>

<figure id="fig-23-1">
  <img src="{{ '/assets/figs/ch23_dsp.svg' | relative_url }}" style="width:720px" alt="An ECG beat with ST elevation after causal and zero-phase high-pass filtering, and output SNR of a fixed-point high-pass filter versus word length for direct form and second-order sections">
  <figcaption><span class="capnum">Figure 23.1.</span> <strong>Phase and word length are where biosignal filters go wrong.</strong> (a) A synthetic ECG with a 0.15 mV ST elevation (grey) after a causal first-order high-pass at 0.5 Hz (red), which pulls the ST segment down, and the same filter run forward and backward (blue dashed). (b) Output SNR, against floating point, of a fixed-point 4th-order Butterworth high-pass at 0.5 Hz and 500 S/s: the direct form is unstable below 32 bits; second-order sections reach 12-bit quality at 26 bits. Computed in <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Decimate first, to the lowest rate each application needs. Use zero-phase or linear-phase filtering wherever waveform shape matters, and keep diagnostic high-pass corners at 0.05 Hz. Remove mains interference with an adaptive notch that tracks the mains frequency, not with a fixed one. Implement every recursive filter as second-order sections, and leave sub-hertz corners to the analog servo loop, because at 500 S/s they cost more than 26 bits in fixed point.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

On-chip DSP: decimation to the application rate, second-order-section IIR filters above 1 Hz in 24-bit fixed point, an adaptive 50/60 Hz notch, and feature extraction ([Chapters 24–26]({% link chapters/24_ecg.md %})). Sub-hertz high-pass in the analog servo loop. Diagnostic-quality raw data available at 500 S/s with no on-chip high-pass beyond 0.05 Hz.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Designing an IIR filter in floating point with `scipy.signal.butter()` and porting its `b, a` coefficients directly to hardware. For low corner frequencies the direct form is unstable in any practical word length. Always design with `output="sos"`, simulate the fixed-point version, and check stability and limit cycles before committing it to silicon.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

In `figsrc/ch23_figs.py`, decimate the input to 125 S/s before the high-pass and repeat the word-length sweep. Then replace the first-order high-pass of panel (a) with a median-filter baseline removal and measure the ST level again.

</div>

**Read with this chapter.** Tompkins {% include cite.html keys="tompkins" %}.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Decimate to the application's rate first: 500 S/s for diagnostic ECG, 125–250 S/s for monitoring, 256 S/s for EEG.
- A causal 0.5 Hz high-pass reads a 0.15 mV ST elevation as 0.107 mV; zero-phase filtering or a 0.05 Hz corner preserves it.
- Adaptive notches track the mains frequency; comb filters remove all harmonics at the cost of extra notches.
- Wavelets denoise without blurring and isolate the QRS scales.
- Narrow recursive filters need second-order sections and long words: 26 bits for 12-bit quality at 0.5 Hz and 500 S/s.

</div>
