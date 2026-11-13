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

Part II ends with an amplified, filtered biosignal of a few hundred millivolts. Part III turns it into numbers. This chapter treats the converter as an ideal black box that samples and rounds, and asks only what those two operations cost. Every real converter in Chapters 15–21 adds errors on top of the ones found here, so these are the best numbers you can hope for.

## <span class="secnum">13.1</span>Sampling and aliasing with ExG examples

Sampling at a rate $$f_\mathrm{s}$$ keeps one value every $$1/f_\mathrm{s}$$ seconds. In the frequency domain it copies the input spectrum to every multiple of $$f_\mathrm{s}$$, so after sampling there is no way to tell a tone at $$f$$ from one at $$f + kf_\mathrm{s}$$ or $$kf_\mathrm{s} - f$$. Only the band from 0 to $$f_\mathrm{s}/2$$, the **Nyquist band**, is unambiguous, and any input above it folds back into it:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Where a tone lands after sampling</div>

$$
f_\mathrm{alias} = \bigl\lvert f - k f_\mathrm{s} \bigr\rvert, \qquad k = \mathrm{round}\!\left(\frac{f}{f_\mathrm{s}}\right), \qquad 0 \le f_\mathrm{alias} \le \frac{f_\mathrm{s}}{2}
$$

</div>

The Nyquist theorem says that a signal confined to $$0 \ldots f_\mathrm{B}$$ survives sampling if $$f_\mathrm{s} > 2f_\mathrm{B}$$. The signal is rarely the problem. The trouble comes from everything else at the input that is *not* confined to the band: mains harmonics, EMG on an ECG lead, chopper ripple ([Chapter 9]({% link chapters/09_chopper.md %})), and the amplifier's own wide-band noise. Each of these folds somewhere into the band, and once folded it cannot be filtered out.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.1 · Mains harmonics in an EEG sampled at 256 S/s</div>

256 S/s is a common EEG rate ([Table 2.1]({% link chapters/02_signals.md %}#tab-2-1)), and its Nyquist band ends at 128 Hz. The 50 Hz fundamental and its 100 Hz harmonic are already in band and must be handled by CMRR and a digital notch. The higher harmonics fold:

- 150 Hz lands at $$\lvert 150 - 256\rvert = 106$$ Hz, just above the EEG band;
- 200 Hz lands at 56 Hz, in the gamma band;
- **250 Hz lands at $$\lvert 250 - 256\rvert = 6$$ Hz, in the theta band**;
- 350 Hz lands at 94 Hz, and 500 Hz at 12 Hz, in the alpha band.

With 60 Hz mains, 240 Hz lands at 16 Hz and 300 Hz at 44 Hz. A 50 Hz notch filter after the converter removes none of these, and a reader of the EEG would see a narrow 6 Hz rhythm that the brain never produced.

</div>

<figure id="fig-13-1">
  <img src="{{ '/assets/figs/ch13_alias.svg' | relative_url }}" style="width:720px" alt="Mains harmonics folded into the 0 to 128 Hz band by sampling at 256 S/s, and Butterworth filter responses against the 56 dB needed at 350 Hz">
  <figcaption><span class="capnum">Figure 13.1.</span> <strong>Out-of-band interference decides the anti-alias filter.</strong> (a) Where the first ten 50 Hz harmonics land after sampling at 256 S/s. Only 50 and 100 Hz (blue) belong there; the rest (red) fold into the EEG band, the 250 Hz harmonic onto 6 Hz. (b) An ECG channel sampled at 500 S/s with a 150 Hz band: anything at 350 Hz folds onto the band edge. Pushing a 1 mVrms interferer below the 1.5 µVrms floor takes 56 dB, which only the 8th-order Butterworth filter reaches. Computed with <code>biosig.alias_freq()</code> and <code>biosig.butter_atten_db()</code>.</figcaption>
</figure>

An **anti-alias filter** in front of the sampler must therefore attenuate every interferer that could fold into the band until it is below the noise floor. The first frequency that folds into the band is $$f_\mathrm{s} - f_\mathrm{B}$$, so that is where the filter has to be steep.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.2 · Anti-alias filter for a Nyquist-rate ECG channel</div>

Sample an ECG with a 150 Hz band at 500 S/s. A tone at $$f_\mathrm{s} - f_\mathrm{B} = 350$$ Hz folds onto 150 Hz. Suppose the worst interferer there is 1 mVrms, a strong EMG burst from the chest muscles. To bring it below the 1.5 µVrms noise floor the filter needs

$$A \ge 20\log_{10}\frac{1\ \text{mV}}{1.5\ \text{µV}} \approx 56\ \text{dB at 350 Hz}.$$

A Butterworth low-pass with its corner at 150 Hz gives $$10\log_{10}\!\left[1 + (350/150)^{2n}\right]$$: 15 dB for order 2, 29 dB for order 4, 44 dB for order 6 and **59 dB for order 8** ([Figure 13.1](#fig-13-1)b). An 8th-order filter with a corner set this precisely is a large analog block.

Sample at 2 kS/s instead and the first folding frequency moves to 1850 Hz, more than twelve times the band edge. A 3rd-order filter now gives 65 dB, and a digital filter after the converter removes everything between 150 Hz and 1 kHz before the rate is reduced to 500 S/s. This trade, a faster converter for a simpler analog filter, is the start of oversampling.

</div>

The lesson for a biomedical chip is that the anti-alias filter is set by the interferers, not by the signal. The ΔΣ converter of [Chapter 19]({% link chapters/19_dstheory.md %}) samples so fast that its first folding frequency is tens of kilohertz away, where a single pole and the front-end's own roll-off suffice; the SAR, running near the Nyquist rate, needs the filter that [Chapter 11]({% link chapters/11_filters.md %}) designs.

## <span class="secnum">13.2</span>The quantisation-noise model

A converter with $$N$$ bits divides its full-scale range $$V_\mathrm{FS}$$ (peak to peak) into $$2^N$$ steps of one **LSB** (least significant bit):

$$\Delta = \frac{V_\mathrm{FS}}{2^N}.$$

Rounding the input to the nearest level leaves an error between $$-\Delta/2$$ and $$+\Delta/2$$ ([Figure 13.2](#fig-13-2)a). If the input is busy, crossing many levels in a way unrelated to the sampling, the error behaves like a random variable spread evenly over that interval, with a mean of zero and a power of

$$\overline{e^2} = \frac{1}{\Delta}\int_{-\Delta/2}^{\Delta/2} e^2\,de = \frac{\Delta^2}{12}.$$

This is the **quantisation-noise model**: the quantiser is replaced by an adder that injects white noise of power $$\Delta^2/12$$, spread evenly from 0 to $$f_\mathrm{s}/2$$. Compare it with a full-scale sine, whose amplitude is $$V_\mathrm{FS}/2 = 2^{N-1}\Delta$$ and whose power is $$(2^{N-1}\Delta)^2/2$$:

$$\mathrm{SQNR} = 10\log_{10}\frac{2^{2N-2}\Delta^2/2}{\Delta^2/12} = 10\log_{10}\!\left(1.5 \cdot 2^{2N}\right).$$

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Quantisation-limited SNR and effective number of bits</div>

$$
\mathrm{SQNR} = 6.02N + 1.76\ \mathrm{dB}, \qquad \mathrm{ENOB} = \frac{\mathrm{SNDR} - 1.76}{6.02}
$$

</div>

Each bit adds 6 dB. The same relation, read backwards, defines the **effective number of bits** (ENOB) of a real converter: measure its signal-to-noise-and-distortion ratio and ask how many ideal bits would give the same number. A 12-bit converter with 68 dB of SNDR is an 11.0-bit converter. [Chapter 14]({% link chapters/14_adcspecs.md %}) measures SNDR properly; `biosig.tone_metrics()` already does it for the figures here, and quantising a near-full-scale sine with `biosig.quantize()` gives 74.2 dB at 12 bits and 98.4 dB at 16 bits, matching the formula.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.3 · Bits for the EMG channel</div>

In EMG mode the programmable gain ([Chapter 11]({% link chapters/11_filters.md %})) is set so that ±5 mV at the electrodes fills the SAR's range. Referred to the input, $$V_\mathrm{FS} = 10$$ mV and a 12-bit LSB is

$$\Delta = \frac{10\ \text{mV}}{4096} = 2.44\ \text{µV}, \qquad \frac{\Delta}{\sqrt{12}} = 0.70\ \text{µVrms}.$$

The analog noise in the EMG band (10–500 Hz) is about $$1.5\sqrt{490/99.5} \approx 3.3$$ µVrms ([Worked Example 2.3]({% link chapters/02_signals.md %})). Adding the two in power gives $$\sqrt{3.33^2 + 0.70^2} = 3.40$$ µVrms: quantisation costs 2 %. A 10-bit converter would give 2.8 µVrms of quantisation noise and raise the total to 4.4 µVrms, about 30 % worse.

</div>

A useful rule follows: keep the quantisation noise **at most a third of the analog noise** at the converter input. Then it adds about 5 % ($$\sqrt{1 + 1/9} = 1.054$$), and more bits buy nothing.

<figure id="fig-13-2">
  <img src="{{ '/assets/figs/ch13_quant.svg' | relative_url }}" style="width:720px" alt="A 3-bit quantiser staircase with its sawtooth error, and spectra of a small sine quantised with and without dither">
  <figcaption><span class="capnum">Figure 13.2.</span> <strong>The noise model holds only when the error is busy.</strong> (a) A 3-bit quantiser: the output (blue) follows the input in steps, and the error (red, shifted down by 6 LSB) is a sawtooth between −½ and +½ LSB, then grows without bound once the input leaves the range. (b) A sine of 1.3 LSB amplitude on a 12-bit quantiser. Without dither (red) the error is a deterministic function of the input and appears as harmonics up to −83 dBFS; with triangular dither (blue) the harmonics vanish into a flat floor that is a little higher. Computed with <code>biosig.quantize()</code>.</figcaption>
</figure>

The model fails whenever the error is *not* busy:

- **Small signals.** An input that spans only a few LSB crosses the same few levels in a regular pattern, so the error is a function of the input and repeats with it. It shows up as harmonics, not noise ([Figure 13.2](#fig-13-2)b).
- **DC and slow signals.** A constant input gives a constant error, up to half an LSB of offset that no averaging removes. An ECG baseline or a slow EEG drift spends a long time near a few codes.
- **Overload.** Beyond full scale the error is no longer bounded at all. With an electrode offset or a motion artefact this is a real case, which is why [Chapter 10]({% link chapters/10_dsl.md %}) removes the offset before the converter.

## <span class="secnum">13.3</span>Dither and oversampling

The cure for a quantiser whose error is not busy is to make it busy. Adding a small random signal, **dither**, before the quantiser moves the input across levels at random, so the error decorrelates from the signal. Triangular dither of 1 LSB peak to peak removes the dependence of the error's mean and power on the input entirely; Gaussian dither of about half an LSB rms or more does nearly as well. The price is the dither's own noise, visible in [Figure 13.2](#fig-13-2)b as a higher floor.

A biomedical front-end usually gets dither for free. In Worked Example 13.3 the analog noise at the converter is 3.3 µVrms, which is 1.4 LSB rms. That is more than enough to keep the error white, as long as the gain stages are designed so that the amplifier's noise, and not the quantiser, sets the floor. Choose the LSB by the one-third rule and the quantiser behaves like the model.

Once the error is white, its power $$\Delta^2/12$$ is spread evenly over $$0 \ldots f_\mathrm{s}/2$$. Sample faster than Nyquist and the same power is spread thinner. If the signal occupies only $$0 \ldots f_\mathrm{B}$$, a digital low-pass filter after the converter keeps only the fraction $$2f_\mathrm{B}/f_\mathrm{s}$$ of it. Define the **oversampling ratio**

$$\mathrm{OSR} = \frac{f_\mathrm{s}}{2f_\mathrm{B}}, \qquad \mathrm{SQNR} = 6.02N + 1.76 + 10\log_{10}\mathrm{OSR}\ \text{dB}.$$

Every doubling of the sample rate buys 3 dB, half a bit.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.4 · Plain oversampling versus noise shaping for EEG</div>

A 12-bit converter samples an EEG with a 100 Hz band. At 256 S/s its SQNR is 74 dB. Run it at 25.6 kS/s instead, an OSR of 128, filter digitally and decimate back down:

$$\mathrm{SQNR} = 74.0 + 10\log_{10}128 = 74.0 + 21.1 = 95.1\ \text{dB} \;\approx\; 15.5\ \text{bits}.$$

Four extra bits, but at a hundred times as many conversions, and so roughly a hundred times the converter energy. And it works only if the error is white: the simulated points in [Figure 13.3](#fig-13-3)a fall up to 3 dB short at high OSR because a pure sine's quantisation error has harmonics that stay in band.

A **noise-shaping** loop does far better at the same OSR. [Chapter 19]({% link chapters/19_dstheory.md %}) shows that a second-order loop with a *1-bit* quantiser reaches about 100 dB at an OSR of 128, because it pushes the quantisation noise out of the band instead of only spreading it.

</div>

<figure id="fig-13-3">
  <img src="{{ '/assets/figs/ch13_os_jitter.svg' | relative_url }}" style="width:720px" alt="SQNR versus oversampling ratio for plain oversampling and for first- and second-order noise shaping, and jitter-limited SNR versus input frequency">
  <figcaption><span class="capnum">Figure 13.3.</span> <strong>Oversampling is weak alone; jitter is harmless at ExG rates.</strong> (a) In-band SQNR of an 8-bit quantiser versus OSR: plain oversampling gains 3 dB per octave (line, and simulated points with an ideal decimation filter), while first- and second-order noise shaping gain 9 and 15 dB per octave (dashed, from Chapter 19). (b) The SNR limit set by sampling-clock jitter. Even 10 ns of jitter stays above the ideal 16-bit line up to about 200 Hz, and 1 ns stays above it across the whole ExG band. Computed with <code>biosig.sqnr_os_db()</code> and <code>biosig.jitter_snr_db()</code>.</figcaption>
</figure>

## <span class="secnum">13.4</span>Clock jitter

A sampling clock whose edges wander by $$\sigma_t$$ rms samples the input at slightly wrong instants. For a sine of amplitude $$A$$ at $$f_\mathrm{in}$$ the error is the slope times the timing error, at most $$2\pi f_\mathrm{in} A\,\sigma_t$$, and comparing its rms value with the signal's gives

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Jitter-limited SNR</div>

$$
\mathrm{SNR}_\mathrm{jitter} = -20\log_{10}\!\left(2\pi f_\mathrm{in}\,\sigma_t\right)
$$

</div>

The limit depends on the input frequency, and biosignals are slow.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.5 · How much jitter can Open-BioAFE tolerate?</div>

For the 16-bit ΔΣ channel, 98 dB at the top of the ECG band (150 Hz) needs

$$\sigma_t < \frac{1}{2\pi \cdot 150\ \text{Hz} \cdot 10^{98/20}} \approx 13\ \text{ns}.$$

For the 12-bit SAR in spike mode, 74 dB at 7 kHz needs $$\sigma_t < 4.5$$ ns. In EMG mode, 1 ns of jitter at 500 Hz limits the SNR to 110 dB, far above anything the channel can use.

</div>

Nanoseconds of jitter are easy: an on-chip relaxation or ring oscillator with period jitter far below a nanosecond costs microwatts. This is the opposite of the SerDes world, where femtoseconds matter {% include cite.html keys="serdestut" %}. A biomedical converter worries about energy per conversion instead, which is the subject of [Chapter 14]({% link chapters/14_adcspecs.md %}). The one exception is the continuous-time ΔΣ modulator, whose feedback DAC turns clock jitter into a noise source of its own ([Chapter 20]({% link chapters/20_dscircuits.md %})).

## <span class="secnum">13.5</span>Rates and bits for each mode

The answer to the design question combines the bands of [Chapter 2]({% link chapters/02_signals.md %}), the dynamic range of Worked Examples 2.2 and 2.3 and the anti-alias trade of this chapter.

**Table 13.1. Output rate and resolution for each Open-BioAFE mode.** The output rate is after any decimation. "Bits needed" comes from the dynamic range over the analog noise in the mode's band.
{: .tabcaption #tab-13-1 }

| Mode | Band | Converter | Output rate | Bits needed | Why |
|---|---|---|---|---|---|
| ECG | 0.05–150 Hz | Incremental ΔΣ | 500 S/s | 16 (up to 17 DC-coupled) | 103 dB with the full ±300 mV offset; less after the DC servo loop |
| EEG | 0.5–100 Hz | Incremental ΔΣ | 256–500 S/s | 16 | Same offset problem, smallest signals |
| EMG | 10–500 Hz | SAR | 2 kS/s | 10–11 (12 built) | 60–67 dB AC-coupled; the one-third rule gives 12 |
| Spikes (optional) | 0.3–7 kHz | SAR | 20–30 kS/s | 8–10 | About 30 dB of spike over wide-band noise, plus margin for LFP and artefacts |

The two Nyquist-rate SAR modes run at three to four times their band edge, so the analog filter of [Chapter 11]({% link chapters/11_filters.md %}) can be of modest order. The ΔΣ modes run their modulator far faster, at an OSR that [Chapter 19]({% link chapters/19_dstheory.md %}) chooses, and decimate down to the rates in the table.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Choose the sample rate from the interferers you must keep out of the band, not from the signal: the faster you sample, the simpler the analog filter and the more the digital filter does. Choose the bits so that quantisation noise is at most a third of the analog noise; beyond that, bits are wasted energy. Jitter is not a concern at ExG rates, so the clock can be a cheap on-chip oscillator.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

ECG and EEG: 16-bit incremental ΔΣ, 256–500 S/s output. EMG: 12-bit SAR at 2 kS/s. Spikes (optional): the same SAR at 20–30 kS/s. Sampling-clock jitter below 1 ns rms.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

A 50 Hz notch filter after the converter does not remove mains interference that has already aliased. If a mains harmonic folds into the band, it appears at a frequency the notch does not touch, such as 6 Hz in Worked Example 13.1. Filter before sampling, or sample fast enough that the harmonics have somewhere harmless to fold.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 6]({% link chapters/31_labs.md %}#lab-6) quantises sine waves, applies coherent sampling and windows, and builds the `adctest.py` module every later converter lab uses. Start from `biosig.quantize()` and `biosig.tone_metrics()`, then reproduce [Figure 13.2](#fig-13-2) and the 6.02N + 1.76 dB line.

</div>

**Read with this chapter.** Pelgrom {% include cite.html keys="pelgrom" %} for sampling, quantisation and jitter, Schreier, Temes and Pavan {% include cite.html keys="schreier" %} for oversampling and the noise model.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Sampling folds everything above $$f_\mathrm{s}/2$$ into the band; the anti-alias filter is set by the interferers, which fold to frequencies no later filter can reach.
- At 256 S/s the 250 Hz mains harmonic lands at 6 Hz; a Nyquist-rate ECG channel at 500 S/s needs an 8th-order filter for a 1 mVrms interferer, while 2 kS/s needs only 3rd order.
- An ideal $$N$$-bit quantiser gives $$6.02N + 1.76$$ dB with a full-scale sine; the white-noise model fails for small, slow or overloading inputs, and dither (often the front-end's own noise) restores it.
- Keep quantisation noise at most a third of the analog noise; for EMG that means 12 bits over ±5 mV.
- Plain oversampling buys only 3 dB per octave; noise shaping (Chapter 19) does much better.
- Jitter of a few nanoseconds is harmless at ExG frequencies.

</div>
