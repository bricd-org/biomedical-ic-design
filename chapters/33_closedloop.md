---
title: 33. Closed-Loop Systems
parent: "Part VI · Wearable Systems"
nav_order: 33
permalink: /part-6/ch33/
chapter: 33
---

# <span class="chapnum">Chapter 33</span>Closed-Loop Systems

A device that only records can be slow; a device that acts on what it records must decide in time, and timing becomes part of the specification.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- describe closed-loop biomedical systems: sense, decide, act;
- build a latency budget from the electrodes to the stimulus, with its jitter, and turn it into a phase error;
- decide where the loop closes, on the chip or through a phone, from its latency, jitter and energy;
- estimate the phase of a brain rhythm in real time, despite the delay of every causal filter;
- time stimuli to samples, and size how long the front-end is blind after a stimulus or an overload;
- size the averaging time of an evoked response from the input noise.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Where must the loop close, on the device or beyond the radio, for the stimulus to land at the right moment of the rhythm it targets?

</div>

Up to now the chip has listened. A **closed-loop** system also acts: it detects a state in the signal and responds within a fixed time, by stimulating a nerve, playing a sound, vibrating, or changing a therapy. Responsive neurostimulators detect the onset of a seizure and stimulate to stop it ([Chapter 27]({% link chapters/27_soc.md %})). Sleep studies play short bursts of sound timed to the slow oscillations of deep sleep and enhance them {% include cite.html keys="ngo2013" %}. Brain-stimulation studies time each pulse to the phase of an ongoing rhythm, because the brain's response depends on it {% include cite.html keys="zrenner2018" %}. Hearing tests at the ear play sounds and measure the brain's response to them. All share one requirement that open-loop recording never had: a deadline.

## <span class="secnum">33.1</span>Sense, decide, act

A closed loop has four stages: **acquisition** (electrodes, front-end, converter and decimation), **decision** (filtering, detection, phase estimation), **actuation** (a sound, a current, a vibration) and the body's own response. Each stage adds delay, and the decision stage must work only with the past: every filter it uses is causal, and every causal filter delays the signal.

The decision can run in three places: in the chip's own logic, next to the converter; in the processor of the device's radio, behind the SPI port of [Chapter 27]({% link chapters/27_soc.md %}); or on a phone, beyond the radio link. Worked Example 33.1 compares the first and the last.

## <span class="secnum">33.2</span>The latency budget

Add up the delay from the electrodes to the stimulus:

- **The front-end.** The ΔΣ path has one pole at a few kilohertz ([Chapter 11]({% link chapters/11_filters.md %})): less than 0.1 ms.
- **Conversion.** An incremental ΔΣ delivers its word at the end of its cycle, 2 ms at 500 S/s ([Chapter 20]({% link chapters/20_dscircuits.md %})). Its cascade-of-integrators decimator weights the cycle's input by a falling ramp, so the word describes the input on average 1.33 ms before it appears. A SAR samples in microseconds.
- **Digital filters.** A linear-phase FIR filter of $$N$$ taps delays every frequency by $$(N-1)/2$$ samples ([Chapter 23]({% link chapters/23_dsp.md %})); a band-pass that isolates a 1 Hz rhythm needs a long filter, and so a long delay. A causal IIR band-pass keeps the phase at its centre frequency, but not around it (section 33.3).
- **The link.** Over BLE, a sample waits in a buffer for the next connection event, the phone decides, and its command waits for a later event to come back ([Chapter 27]({% link chapters/27_soc.md %})): tens of milliseconds, with a jitter of the same order.
- **The actuator.** An audio codec's output buffer, a stimulator's ramp-up: a few milliseconds.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Phase error from latency</div>

$$\Delta\varphi = 360^\circ \cdot f \cdot \tau$$

A latency $$\tau$$ that is not compensated becomes a phase error $$\Delta\varphi$$ at the rhythm's frequency $$f$$; a jitter in $$\tau$$ becomes a phase jitter by the same rule, and a latency compensated with a frequency that is wrong by $$\delta f$$ leaves $$360^\circ \cdot \delta f \cdot \tau$$.

</div>

[Figure 33.1](#fig-33-1)a draws the rule for three rhythms. For the slow oscillation of deep sleep, about 0.75 Hz, a 60 ms loop over BLE costs 16°, inside a ±30° tolerance. For theta at 6 Hz it costs 130°, and for alpha at 10 Hz 216°: the stimulus lands on the opposite phase. A loop that closes on the device, within about 5 ms, keeps alpha within 18°. Fast rhythms need the loop on the device; slow ones can tolerate the radio, if its jitter is controlled.

<figure id="fig-33-1">
  <img src="{{ '/assets/figs/ch33_loop.svg' | relative_url }}" style="width:720px" alt="Phase error against loop latency for a 0.75 Hz slow oscillation, 6 Hz theta and 10 Hz alpha, with a 30 degree tolerance band and markers at 5 ms on the device and 60 ms over BLE; and the SNR of an auditory steady-state response against the number of averaged one-second epochs for three response amplitudes, against a 10 dB detection line">
  <figcaption><span class="capnum">Figure 33.1.</span> <strong>Fast rhythms need the loop on the device; small responses need many sweeps.</strong> (a) Phase error 360°·f·τ for three rhythms against loop latency, with a ±30° tolerance; markers at 5 ms (loop on the device) and 60 ms (through a BLE link). (b) SNR of an auditory steady-state response in its FFT bin against the number of averaged 1 s epochs, at the noise of the dry ear-EEG contacts of Chapter 32 (0.12 µV/√Hz over 1–40 Hz): 0.3, 0.1 and 0.05 µV responses need 2, 15 and 58 epochs for 10 dB. From <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 33.1 · On the chip or through the phone</div>

Close the loop on the chip, with the decision in its own logic and the actuator clocked from its reference, or through a phone over BLE, at the 30 ms connection interval that Chapter 27 uses for raw ECG. Take the actuator, an audio DAC's frame buffer and interpolation filter, as 1.5 ms (an assumption).

- **On the chip.** 0.08 ms in the front-end's pole (taken at 2 kHz), 1.33 ms in the conversion, 0.02 ms for a decision of ten operations at 512 kHz, 1.5 ms in the actuator: **2.9 ms**, fixed. That is 0.8° of a 0.75 Hz slow oscillation and 10.6° of 10 Hz alpha, and a fixed delay can be compensated entirely. The only jitter is the sample grid: an event is seen at the next word, up to 2 ms late, ±3.6° at 10 Hz, unless its time is interpolated between samples, as the demo of section 33.3 does.
- **Through the phone.** The word waits 0–30 ms for the next connection event. The phone's command, however fast the phone decides, waits for the following event, 30 ms later, then takes 0.33 ms on air (a 20-byte notification at 1 Mb/s). With the same front-end, conversion and actuator, the loop takes **33–63 ms**, 48 ms on average, spread evenly over ±15 ms. At 0.75 Hz that is 13° ± 4°; at 10 Hz, 174° ± 54°. A phone that misses an event, or a packet sent again, adds another 30 ms.
- **Acting on the sample counter.** Let the phone answer with the sample number at which to act, and let the device act on its own clock. The jitter disappears, but the forecast must now reach the worst case, 64 ms ahead: 17° of the slow oscillation and 230° of alpha to be aimed around. If the rhythm's frequency is known to 5 %, 0.9° and 11.5° remain.
- **Energy.** The phone needs the raw samples of at least one channel: 8.3 kb/s with framing, 42 µW in bits and 333 µW in connection events at Chapter 27's 5 nJ per bit and 10 µJ per event, **375 µW** in all, seven times the 54 µW of the eight channels. On the chip, two second-order sections per sample at Chapter 23's 10 pJ per MAC cost 0.05 µW, and the radio can wake once a second to send a log, for about 10 µW.

The slow oscillation tolerates the phone; alpha does not, unless the loop forecasts 64 ms ahead and acts on its own clock. Either way the link costs more than the whole front-end, so a loop that runs all night belongs on the chip.

</div>

## <span class="secnum">33.3</span>Estimating the phase in real time

The textbook way to find the phase of a rhythm, a zero-phase band-pass filter and the Hilbert transform, needs the future: it filters forwards and backwards. A real-time system has only the past. Three practical approaches:

- **Filter and predict.** Band-pass the recent signal causally, fit a short **autoregressive model** to it, and forecast the next fraction of a second; take the phase from the forecast at the present moment. This compensates the filter's delay and is the approach behind phase-locked brain stimulation {% include cite.html keys="zrenner2018" %}.
- **Track the rhythm with a phase-locked loop**: an oscillator whose phase is pulled towards the band-passed signal, updated every sample, cheap enough for a small datapath.
- **Detect events and extrapolate**: for the slow oscillation, detect the negative half-wave when it crosses a threshold and schedule the sound for the expected up-phase a fixed time later {% include cite.html keys="ngo2013" %}.

All three start with a causal band-pass, and a causal band-pass gives the true phase only at its centre frequency $$f_0$$. Around it, the phase moves with the rhythm's frequency $$f$$ at a rate set by the filter's group delay $$\tau_\mathrm{g}$$, the same rule again:

$$\Delta\varphi \approx -360^\circ \cdot \tau_\mathrm{g}\,(f - f_0), \qquad \tau_\mathrm{g} = \frac{Q}{\pi f_0}\ \text{for a second-order band-pass of quality factor } Q.$$

The demo's filter, one second-order section with $$Q = 1.5$$, delays the envelope by 48 ms at 10 Hz and by 637 ms at 0.75 Hz, and at 10 Hz turns each hertz of detuning into 17° of phase. Because $$\tau_\mathrm{g}(f - f_0)$$ depends only on the relative detuning, a rhythm that wanders ±8 % around the centre, as the demo's does, comes out with up to +14° and −13° of error at either frequency. A narrower filter rejects more of the background and errs more off centre; a broader one errs less and lets the background move the zero crossings.

All three approaches degrade when the rhythm is weak or irregular. A good loop measures its own accuracy, by logging the true phase afterwards with a zero-phase filter, and acts only when the rhythm is present and the signal-quality index of [Chapter 31]({% link chapters/31_quality.md %}) says the data can be trusted.

The demo below runs the simplest real-time scheme, event detection: a causal band-pass at the target frequency, an upward zero crossing as the event, and a stimulus aimed at the next peak a quarter period later, delivered after the loop's latency and jitter. The true phase of each stimulus is found afterwards with a zero-phase filter and the Hilbert transform. It samples at the chip's 500 S/s and interpolates each zero crossing between samples, so the loop's latency is the only delay. It starts at a 0.75 Hz slow oscillation and 60 ms through a radio link; move the frequency to alpha.

{::nomarkdown}
{% include demos/phase.html %}
{:/}

## <span class="secnum">33.4</span>Acting without corrupting the recording

The stimulus must be timed by the same clock as the samples. An audio codec clocked from the front-end's reference ([Chapter 29]({% link chapters/29_arch.md %})) plays its sounds on known samples, so every stimulus can be placed exactly in the recording; a codec on its own crystal drifts against the EEG by a sample every few tens of seconds.

The stimulus must also stay out of the recording, or the loop responds to its own output. Electrical stimulation couples directly into the electrodes ([Chapter 27]({% link chapters/27_soc.md %})): the front-end must survive it without saturating, and the samples during each pulse are blanked or flagged. Sound reaches the EEG through the speaker's magnetic field, the drive currents and the mechanics of the earpiece: separate grounds, a speaker driver away from the inputs, and stimulus timing logged with the data keep it identifiable.

A stimulus also leaves something behind. Even a charge-balanced pulse leaves a residual polarisation on the electrodes, and an overload from motion or a lost contact shifts the electrode offset ([Chapter 31]({% link chapters/31_quality.md %})); both reach the front-end as a step. The DC servo loop of [Chapter 10]({% link chapters/10_dsl.md %}) removes a step with its time constant, but only as fast as the LNA lets it. While the step exceeds the LNA's linear input range, the LNA clips, the servo's integrator sees only the clipped output, and the loop corrects at most that range per time constant. That is the pessimistic case of a linear integrator resistor: if the clipped output appears across a pseudo-resistor, which conducts tens of times more with nearly half a volt across it ([Chapter 8]({% link chapters/08_lna.md %})), the correction runs faster and the slewing ends sooner. Until the step is back inside the converter's range the channel is blind, and until its tail falls below the noise the record is corrupted:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Recovery after a step at the input</div>

$$
t_\mathrm{rec} = \tau \ln\frac{V_0}{V_\mathrm{ok}}\ \ (V_0 \le V_\mathrm{lin}), \qquad t_\mathrm{rec} = \tau\left(\frac{V_0}{V_\mathrm{lin}} - 1 + \ln\frac{V_\mathrm{lin}}{V_\mathrm{ok}}\right)\ \ (V_0 > V_\mathrm{lin}), \qquad \tau = \frac{1}{2\pi f_\mathrm{HP}}
$$

$$V_0$$ is the step at the input, $$V_\mathrm{lin}$$ the LNA's linear input range, $$f_\mathrm{HP}$$ the servo's high-pass corner and $$V_\mathrm{ok}$$ the residual you accept: the converter's range for the end of the blind time, the input noise for a clean record. Stimuli at a rate $$f_\mathrm{stim}$$ lose a fraction $$f_\mathrm{stim}\,t_\mathrm{rec}$$ of the recording.

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 33.2 · How long the channel is blind</div>

In EEG mode, the LNA's ±0.45 V output swing at a gain of 100 makes $$V_\mathrm{lin}$$ = 4.5 mV ([Chapter 8]({% link chapters/08_lna.md %})), and the total gain of 800 maps the converter's range to ±0.625 mV at the input ([Chapter 11]({% link chapters/11_filters.md %})). Take the 1.5 µV noise target as $$V_\mathrm{ok}$$ for a clean record. A simulation of the loop with a clipping LNA, on synthetic EEG at 20 kS/s, confirms these numbers to within 1 % ([Figure 33.2](#fig-33-2)).

- **A 4.5 mV step**, the largest the LNA passes unclipped. At the 0.5 Hz corner ($$\tau$$ = 0.32 s): back in range after 0.63 s, clean after 2.5 s. At the 0.05 Hz corner of diagnostic recordings: 6.3 s and 25 s. In the fast-settle mode (50 Hz, $$\tau$$ = 3.2 ms): 6.3 ms and 25 ms.
- **The fast-settle duration.** Five time constants, the 16 ms of Worked Example 10.2, bring the step well inside the converter's range but leave 4.5 mV × e⁻⁵ = 30 µV. 20 ms (6.3 time constants) leaves 8.4 µV, which the 0.5 Hz loop takes another 0.55 s to remove; 26 ms, a little over eight time constants, leaves 1.3 µV, under the noise. That is why [Table 29.1]({% link chapters/29_arch.md %}#tab-29-1) holds the fast-settle mode while the LNA is clipped and for 26 ms after.
- **A 50 mV step** clips the LNA, and the loop first slews for ten time constants: blind for 3.8 s and corrupted for 5.8 s at 0.5 Hz; in fast-settle mode, 38 ms and 58 ms, of which 32 ms are slewing.
- **Stimuli once a second.** With 26 ms of fast-settle after each, 2.6 % of the recording is lost (5.8 % after 50 mV steps); at 0.5 Hz alone each step needs 2.5 s, and the record is never clean.
- **Not during the pulse.** A 1 ms pulse that clips the LNA moves the loop's correction by 1.4 mV in fast-settle mode, a new step of its own, but by only 14 µV at 0.5 Hz. Hold the loop during the pulse, then settle fast.

The fast-settle mode turns seconds into tens of milliseconds, which is what lets a device stimulate and record on the same body. Trigger it from the stimulus schedule or from a clipping detector, and hold it while the LNA is clipped and for eight time constants after, so that its length follows the step.

</div>

<figure id="fig-33-2">
  <img src="{{ '/assets/figs/ch33_recovery.svg' | relative_url }}" style="width:720px" alt="Residual of a 50 mV and a 4.5 mV input step against time for servo corners of 0.05 Hz, 0.5 Hz and 50 Hz fast-settle; and a 50 mV step on synthetic EEG, pinned at the converter limit for 3.8 s at 0.5 Hz and back within 40 ms with fast-settle">
  <figcaption><span class="capnum">Figure 33.2.</span> <strong>A step at the input blinds the channel for seconds, or for milliseconds in fast-settle mode.</strong> (a) Residual of a step at the input against time, for the servo's 0.05 and 0.5 Hz corners and its 50 Hz fast-settle mode, for a 50 mV step (solid), which first clips the LNA and slews, and a 4.5 mV step (dashed); dotted, the LNA's linear range (±4.5 mV), the converter's range in EEG mode (±0.625 mV) and the 1.5 µV noise target. (b) A 50 mV step on synthetic EEG, as the converter sees it: with the 0.5 Hz servo the channel is pinned at the converter's limit for 3.8 s; with 60 ms of fast-settle it is back in range within 40 ms. Servo loop with a clipping LNA, simulated at 20 kS/s in <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

A blanking scheme therefore has three parts: hold the servo loop through each pulse, settle fast for as long as the step needs, and flag every sample in between. The flags travel with the data as part of the signal-quality index of [Chapter 31]({% link chapters/31_quality.md %}), and the decision ignores flagged samples, or the loop would respond to its own stimulus.

## <span class="secnum">33.5</span>Evoked responses: hearing tests at the ear

A closed loop can also *test*. Play a sound and measure the brain's response: an **auditory brainstem response** (ABR) to clicks, a few milliseconds long, or an **auditory steady-state response** (ASSR) to a tone modulated at, typically, 40 or 80–100 Hz {% include cite.html keys="picton2003" %}. Both are far smaller than the background EEG, so they are measured by **averaging**: the response repeats with every stimulus while the EEG does not, and the noise falls as $$1/\sqrt{N}$$ over $$N$$ repetitions. An ASSR appears as a peak at its modulation frequency in the averaged spectrum, detected when it stands far enough above the neighbouring bins. At the ear the responses are smaller still {% include cite.html keys="kidmose2013" %}: [Figure 33.1](#fig-33-1)b shows that a 0.1 µV response needs about 15 averaged seconds at the noise of dry ear-EEG contacts, and a 0.05 µV one about a minute.

Why $$\sqrt N$$: the response is the same in every epoch, so averaging $$N$$ epochs keeps its amplitude $$A$$, while the noise, independent from one epoch to the next, adds in power, and its average falls to $$1/\sqrt N$$ of one epoch's. In the spectrum of an epoch of length $$T_\mathrm{ep}$$ that holds a whole number of modulation cycles, the response sits in one bin of width $$1/T_\mathrm{ep}$$, which holds a noise power $$e_\mathrm{n}^2/T_\mathrm{ep}$$ for a noise density $$e_\mathrm{n}$$:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · The averaging gain</div>

$$
\sigma_N = \frac{\sigma_1}{\sqrt N}, \qquad \mathrm{SNR}_N = N\,\frac{A^2\,T_\mathrm{ep}}{e_\mathrm{n}^2}, \qquad T = N\,T_\mathrm{ep} = \mathrm{SNR}_\mathrm{req}\,\frac{e_\mathrm{n}^2}{A^2}
$$

$$A$$ is the response's rms amplitude, $$e_\mathrm{n}$$ the noise density at its frequency and $$\mathrm{SNR}_\mathrm{req}$$ the power ratio a detection needs.

</div>

The recording time depends only on the noise density and the response, not on how the record is cut into epochs. It is the steady-state line of [Chapter 25]({% link chapters/25_eeg.md %}) with a rectangular window: 3 dB per doubling of the time.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 33.3 · How long a hearing test at the ear takes</div>

Ask for 10 dB ($$\mathrm{SNR}_\mathrm{req}$$ = 10) with 1 s epochs, 1 Hz bins, and count only the front-end's noise, taken as white. The brain's own background and muscle activity at the modulation frequency add to it, so these times are lower limits.

- **Dry contacts.** The contacts alone give 0.75 µVrms over 1–40 Hz ([Chapter 32]({% link chapters/32_ear.md %})), 0.12 µV/√Hz. A 0.3 µV response then needs 1.6 s (2 epochs), 0.1 µV 14 s (15 epochs) and 0.05 µV 58 s (58 epochs), as [Figure 33.1](#fig-33-1)b shows. The amplifier's share brings the channel to 0.79 µVrms and adds 11 % to each time: 16 s and 64 s.
- **Wet contacts.** At 0.32 µVrms, the whole wet channel, 0.1 µV needs 2.6 s and 0.05 µV 10.5 s: six times faster than dry, the ratio of the noise powers. The contact, not the chip, sets the length of the test.
- **The threshold.** Chapter 25's F-test at 1 % false alarms fires when the bin stands 5.85 times above its neighbours, an expected SNR of 4.85 (6.9 dB). A 0.1 µV response reaches that in 7.0 s, but is then found in only about half the trials; the 10 dB of the figure buys a reliable detection for twice the time.
- **The clock.** A stimulus on its own crystal, 50 ppm off the converter's, lets an 80 Hz response drift 84° against the epochs over 58 s, and the average loses 0.8 dB; on a 1 % RC oscillator the response drifts a whole cycle every 1.25 s and averages away. Derived from the converter's reference, it cannot drift.

</div>

The requirements differ from those of continuous EEG. An ASSR at 80–100 Hz needs bandwidth well above the sleep and alpha bands; an ABR needs tens of kilosamples per second and stimulus timing accurate to tens of microseconds. For Open-BioAFE, that is the SAR path of [Chapter 18]({% link chapters/18_sar.md %}), which samples one channel at 25 kS/s in spike mode, not the 500 S/s ΔΣ path, with the stimulus clocked from the same reference as the converter.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Write the latency budget, with its jitter, before the architecture: on the chip a loop takes about 3 ms and does not jitter; through a phone it takes tens of milliseconds, jitters by ±15 ms and costs more radio power than the whole front-end. Fast rhythms need the decision next to the converter; a loop through a phone should act on the sample counter, not on arrival. Clock and log every stimulus with the samples, hold the servo through each pulse, settle fast for as long as the step needs, and act only when the signal-quality index allows. For evoked responses, budget the averaging time from the input noise, and give the converter the bandwidth and the timing accuracy the response needs.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Quoting a closed loop's mean latency and forgetting its jitter. A loop through a phone that averages 40 ms but varies by ±20 ms spreads its stimuli over ±72° of a 10 Hz rhythm, even if the mean has been compensated. Measure the latency distribution end to end, from a test signal at the electrodes to the stimulus at the actuator.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

Generate a slow oscillation with `biosig.eeg()` plus a 0.75 Hz component, band-pass it causally, and schedule a "sound" a fixed delay after each negative half-wave crosses −40 µV. Measure the true phase of each stimulus afterwards with a zero-phase filter and the Hilbert transform, and plot its spread against the noise level and the delay. Then run `python figsrc/ch33_figs.py report`, which prints every number of Worked Examples 33.1–33.3, and change the connection interval, the actuator's delay, the fast-settle duration or the noise and response amplitude to your own.

</div>

**Read with this chapter.** Ngo et al. {% include cite.html keys="ngo2013" %}, Zrenner et al. {% include cite.html keys="zrenner2018" %}, Picton et al. {% include cite.html keys="picton2003" %}, Kidmose et al. {% include cite.html keys="kidmose2013" %}.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A closed loop senses, decides and acts within a deadline; every causal filter and every buffer in it adds delay.
- A latency τ is a phase error 360°·f·τ: 60 ms over BLE costs 16° of a 0.75 Hz slow oscillation but 216° of 10 Hz alpha. Jitter, and the frequency error left in a compensated delay, follow the same rule.
- On the chip a loop takes about 3 ms and does not jitter; through a phone at a 30 ms interval, 33–63 ms (±54° of alpha) and 375 µW of radio, seven times the front-end.
- Real-time phase needs prediction, a phase-locked loop or event detection, and a check of its own accuracy; a causal band-pass is phase-true only at its centre.
- Clock and log every stimulus with the samples, and keep its artefacts out of the decision. A 4.5 mV step blinds the channel for 0.63 s and corrupts it for 2.5 s at 0.5 Hz, for 6.3 and 25 ms in fast-settle mode; a step that clips the LNA adds time in proportion to its size.
- Averaging $$N$$ epochs divides the noise by $$\sqrt N$$; the time needed, $$\mathrm{SNR}_\mathrm{req}\,e_\mathrm{n}^2/A^2$$, does not depend on the epoch. With dry ear-EEG contacts a 0.1 µV ASSR needs about 15 s, about six times longer than with wet ones. ABRs need the fast SAR path and microsecond timing.

</div>
