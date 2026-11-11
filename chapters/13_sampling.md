---
title: 13. Sampling and Quantisation
parent: "Part III · Data Converters"
nav_order: 13
permalink: /part-3/ch13/
chapter: 13
---

# <span class="chapnum">Chapter 13</span>Sampling and Quantisation

An ADC does two things to a biosignal: it looks at it only at discrete instants, and it rounds every look to one of $$2^N$$ levels.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 2 (the Python-only converter core: Chapters 13, 14 and 19 with Labs 6 and 9). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- apply the Nyquist theorem to ExG signals and predict what aliases where;
- derive the quantisation-noise model, its $$6.02N + 1.76$$ dB result and its limits;
- use dither and oversampling to trade rate for resolution;
- estimate the jitter limit and see why it is minor at biosignal rates.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What sample rate and how many bits does each Open-BioAFE mode need, before any circuit is chosen?

</div>

## <span class="secnum">13.1</span>Sampling and aliasing with ExG examples

Mains harmonics and out-of-band EMG folding into the ECG band; anti-aliasing requirements set by real interferers rather than by the signal.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Quantisation-limited SNR and effective number of bits</div>

$$
\mathrm{SQNR} = 6.02N + 1.76\ \mathrm{dB}, \qquad \mathrm{ENOB} = \frac{\mathrm{SNDR} - 1.76}{6.02}
$$

</div>

## <span class="secnum">13.2</span>The quantisation-noise model

Uniform error of $$\pm\,\mathrm{LSB}/2$$, its $$\mathrm{LSB}^2/12$$ power, and when the white-noise model fails (low-amplitude and DC signals).

## <span class="secnum">13.3</span>Dither and oversampling

Adding noise to linearise the quantiser; each doubling of the sample rate buys 3 dB of SQNR, setting up the noise shaping of [Chapter 19]({% link chapters/19_dstheory.md %}).

## <span class="secnum">13.4</span>Clock jitter

$$\mathrm{SNR}_\mathrm{jitter} = -20\log_{10}(2\pi f_\mathrm{in}\sigma_t)$$; at a few kilohertz, even nanoseconds of jitter are harmless, which is why biomedical ADCs worry about energy instead.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 6]({% link chapters/31_labs.md %}#lab-6) quantises sine waves, applies coherent sampling and windows, and builds the `adctest.py` module every later converter lab uses.

</div>

**Read with this chapter.** Pelgrom {% include cite.html keys="pelgrom" %}, Schreier, Temes and Pavan {% include cite.html keys="schreier" %}.
