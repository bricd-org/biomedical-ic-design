---
title: 31. Signal Quality and Motion Artefacts
parent: "Part VI · Wearable Systems"
nav_order: 31
permalink: /part-6/ch31/
chapter: 31
---

# <span class="chapnum">Chapter 31</span>Signal Quality and Motion Artefacts

On a moving person the hardest question is not how small a signal the chip can resolve, but whether the sample it just produced can be trusted.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain the mechanisms by which motion turns into voltage at the electrodes;
- measure contact quality during a recording, with impedance tracking and with other indicators the chip already has;
- cancel an artefact adaptively from reference signals with the NLMS algorithm, and choose its references, length, step size and regularisation;
- predict how fast the canceller learns, and line the references and the recording up in time;
- build a signal-quality index that travels with the data, and budget its bits;
- budget the hardware and computation that all of this costs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which references, measured by the same chip on the same clock, let a wearable remove motion artefacts it cannot filter, and tell the user when it cannot?

</div>

Everything in Parts I to V assumed a still subject. A wearable is worn by someone who walks, talks, chews and turns their head, and every movement disturbs the electrodes. The resulting **motion artefacts** are often larger than the signal and, worse, they fall in the same band: from a fraction of a hertz to tens of hertz, exactly where the ECG, EEG and EMG live. No filter can separate what shares a band. This chapter shows how to recognise motion artefacts, how to measure the electrode contact while recording, and how to subtract the artefact using signals that are correlated with it but not with the biosignal.

## <span class="secnum">31.1</span>How motion becomes voltage

Four mechanisms dominate {% include cite.html keys="webster" %}.

- **The interface itself.** Moving an electrode relative to its gel disturbs the double layer of [Chapter 3]({% link chapters/03_electrodes.md %}) and so its half-cell potential. Floating electrodes, gel, and Ag/AgCl's non-polarisable surface reduce it.
- **The skin.** Stretching the skin changes the potential across its outer layer by millivolts. Light abrasion of the skin reduces it.
- **Currents through a changing impedance.** Any current through the electrode turns its impedance change into a voltage. The DC lead-off current of [Chapter 12]({% link chapters/12_cmcontrol.md %}) is one such current; the common-mode current from the mains is another, through the divider $$\Delta Z / Z_\mathrm{cm}$$ of [Chapter 4]({% link chapters/04_interference.md %}), whose imbalance $$\Delta Z$$ now moves with every step.
- **The cables.** Flexing leads generates triboelectric charge, and moving leads change their capacitance to the body and to the mains. Short, light, shielded leads, or digitising close to the electrodes, reduce it.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.1 · A lead-off current meets a moving electrode</div>

The DC lead-off detector of [Chapter 12]({% link chapters/12_cmcontrol.md %}) passes 6 nA through each electrode. A dry electrode whose impedance swings by 20 kΩ as the wearer walks then produces $$6\ \text{nA} \times 20\ \text{k}\Omega = 120$$ µV of artefact, at the walking rhythm: six times a typical EEG. An AC impedance measurement at tens of kilohertz ([Chapter 28]({% link chapters/28_bioz.md %})) moves its own artefact out of band, and turning the DC lead-off current off while recording removes this term altogether.

</div>

## <span class="secnum">31.2</span>Measuring contact quality while recording

The contact cannot be judged once at the start: it changes as the gel dries, as the wearer sweats, and with every movement. A wearable needs indicators that it can read *continuously*, on the same clock as the signal.

- **Electrode impedance**, by the out-of-band tone and IQ demodulation of [Chapter 28]({% link chapters/28_bioz.md %}). At tens of kilohertz the tone sees a contact through its series resistance and the interface's capacitance: the quadrature part follows that capacitance and so the contact's area, its imbalance between electrodes hints at how much mains will convert to differential mode, and its rate of change shows how much the contact is moving. The interface's own resistance, which rises as a dry contact dries, is nearly invisible at the tone's frequency ([Chapter 32]({% link chapters/32_ear.md %})): the mains level below catches it while recording, and a DC lead-off check before recording. A tone injected through the right-leg drive reaches every electrode at once, so one source can track all channels.
- **The DC servo's output** ([Chapter 10]({% link chapters/10_dsl.md %})), which follows the electrode offset: a step means the interface was disturbed.
- **Mains power in the signal**, a free measure of the impedance imbalance: the 50 Hz line rises when one contact degrades.
- **Saturation and clipping counters** in the converter path.
- **Motion itself**, from an accelerometer next to the electrodes.

Each indicator costs little. The impedance channel costs a few microwatts ([Chapter 29]({% link chapters/29_arch.md %})); the rest are numbers the chip already computes.

## <span class="secnum">31.3</span>Adaptive cancellation

When a measured signal $$x$$ is correlated with the artefact but not with the biosignal, the artefact can be *predicted* from $$x$$ and subtracted. This is **adaptive noise cancelling** {% include cite.html keys="widrow1975" %}. The recorded signal is $$d = s + a$$, biosignal plus artefact. An adaptive FIR filter with weights $$\mathbf{w}$$ turns the last $$L$$ samples of each reference into an estimate $$y = \mathbf{w}^\mathsf{T}\mathbf{x}$$ of the artefact, and the output is $$e = d - y$$. Because $$s$$ is uncorrelated with $$\mathbf{x}$$, minimising the power of $$e$$ can only remove the part of $$d$$ that the references explain: the artefact.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Normalised LMS</div>

$$e[n] = d[n] - \mathbf{w}^\mathsf{T}\mathbf{x}[n], \qquad \mathbf{w} \leftarrow \mathbf{w} + \frac{\mu\, e[n]\, \mathbf{x}[n]}{\delta + \mathbf{x}^\mathsf{T}[n]\,\mathbf{x}[n]}$$

$$\mathbf{x}$$ holds the last $$L$$ samples of every reference, $$0 < \mu < 2$$ is the step size and $$\delta$$ regularises the division.

</div>

The **normalised LMS** (NLMS) update makes the step independent of the reference's level {% include cite.html keys="haykin2014" %}. Three choices set its performance:

- **The step size** $$\mu$$ trades tracking speed against *misadjustment*: the biosignal itself jitters the weights, and that jitter appears as added noise. Values from 0.001 to 0.05 are typical.
- **The length** $$L$$ must cover the delay and the shape of the path from reference to artefact: a few samples for an impedance trace, tens for an accelerometer whose effect lags through the mechanics of the skin.
- **The regularisation** $$\delta$$ matters more than it looks. Motion references are bursty, nearly zero between movements; dividing by a tiny $$\mathbf{x}^\mathsf{T}\mathbf{x}$$ then turns the EEG into huge weight jumps that ruin the next movement. Set $$\delta$$ of the order of the references' typical power.

**References.** An accelerometer measures the cause of the artefact, not its electrical path: it sees the movement, but not how each electrode responds to it. The electrode impedance measures the interface itself, but not the parts of the artefact that bypass it, such as cable motion. The two are complementary. [Figure 31.1](#fig-31-1) cancels a synthetic artefact, built from an impedance-driven part (a lead-off current through the moving contact) and a part that follows acceleration directly, with each reference and with both.

<figure id="fig-31-1">
  <img src="{{ '/assets/figs/ch31_nlms.svg' | relative_url }}" style="width:720px" alt="Synthetic motion artefact during walking compared with the residual after NLMS cancellation using impedance and accelerometer references, and a bar chart of artefact reduction: 7.5 dB with the accelerometer, 5.7 dB with impedance and 12.2 dB with both">
  <figcaption><span class="capnum">Figure 31.1.</span> <strong>Two references remove more than either alone.</strong> (a) A synthetic walking artefact on a 256 S/s EEG, and what is left after NLMS with both references (8 taps each, μ = 0.01, δ = one per tap), both against the clean EEG, all in the 0.5–40 Hz band. (b) Artefact power removed after convergence: 7.5 dB with the accelerometer alone, 5.7 dB with the electrode impedance alone, 12.2 dB with both; a least-squares fit, the ceiling for these references, reaches 18 dB. The model and its numbers are illustrative, not measured. From <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

How quickly the filter learns, and how much it disturbs the signal once it has learnt, follow from the step size {% include cite.html keys="haykin2014" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · How fast NLMS learns, and what it costs</div>

$$\tau \approx \frac{L}{2\mu_\mathrm{eff}}\ \text{samples}, \qquad \mathcal{M} \approx \frac{\mu_\mathrm{eff}}{2 - \mu_\mathrm{eff}}, \qquad \mu_\mathrm{eff} = \mu\,\frac{\mathbf{x}^\mathsf{T}\mathbf{x}}{\delta + \mathbf{x}^\mathsf{T}\mathbf{x}}$$

$$\tau$$ is the time constant of the output's mean-square error, $$L$$ the total number of weights, and $$\mathcal{M}$$ the misadjustment: the excess output power, as a fraction of the power the filter cannot remove, mostly the biosignal itself. Both hold for white references; narrowband, bursty references learn their slowest components more slowly.

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.2 · Choosing the step size</div>

With both references and eight taps each, the filter of Figure 31.1 has $$L = 16$$ weights and $$\delta = 16$$. The references are scaled to unit power over the minute, but they carry that power during the walks, where each tap holds 2.1, so $$\mathbf{x}^\mathsf{T}\mathbf{x} \approx 34$$ and the regularisation trims the step to $$\mu_\mathrm{eff} \approx 0.68\,\mu$$. At $$\mu = 0.01$$ the key equation gives $$\tau \approx 16/(2 \times 0.0068) \approx 1170$$ samples, **4.6 s** at 256 S/s, and a misadjustment of 0.3 %.

[Figure 31.2](#fig-31-2)a shows what that means on the recording. Five seconds into the first walk the canceller removes 14 dB. At $$\mu = 0.003$$ ($$\tau \approx 15$$ s) it needs about nine seconds to get there, but once it has learnt it removes the most: 14.8 dB on the last walk, against 12.9 dB at $$\mu = 0.01$$. At $$\mu = 0.1$$ ($$\tau \approx 0.5$$ s) it learns within four seconds but seldom removes more than 10 dB: the EEG, 19 µVrms here and larger than the 17 µVrms artefact, keeps jolting the weights, and with narrowband, bursty references that costs far more than the 3.5 % the key equation predicts for white ones. Over the whole minute the reduction is 10.3, 12.2, 10.5, 7.2 and 5.0 dB for $$\mu$$ = 0.003, 0.01, 0.03, 0.1 and 0.3.

**What it means:** pick $$\mu$$ so that $$\tau$$ is a fraction of a typical movement, here walks of 8 to 12 s, and check the choice on recordings rather than trusting the white-reference numbers. The regularisation leaves the weights almost untouched between movements, so what the filter learnt carries over: the first walk is the worst one for every step size.

</div>

Three conditions make it work on real data. The references must be sampled on the same clock as the signal, or their delay changes and the filter chases it; this is one more argument for measuring impedance on the recording chip. The references must not contain the biosignal: an impedance trace demodulated out of band is clean, but an accelerometer on the head picks up the ballistocardiogram, the tiny motion of each heartbeat, and can cancel part of a cardiac signal. And the filter must be stopped from adapting when there is no movement, or reset after a large one, or it drifts.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.3 · Line the references up</div>

The first condition is easy to break without noticing. The impedance trace leaves the demodulator through a low-pass filter; with the 10 Hz bandwidth of Worked Example 28.1 ([Chapter 28]({% link chapters/28_bioz.md %})) and a second-order Butterworth response, it arrives 23 ms late at the walking rhythm, six samples at 256 S/s. A causal filter cannot look ahead, so it must predict an impedance it has not yet seen: with both references the reduction falls from 12.2 to **10.6 dB**, and with a 2 Hz output filter (123 ms late) to 7.6 dB ([Figure 31.2](#fig-31-2)b). Impedance alone falls from 5.7 to 4.7 dB.

Delaying the recording and the accelerometer by the same six samples, so that all three streams line up, restores **12.2 dB** (13.0 dB with the 2 Hz trace, whose smoothing helps a little). Delaying the recording alone is not enough when there are two references: it makes the accelerometer early instead, and the reduction drops to 9.4 dB.

**What it means:** know the delay of every path from the body to the canceller, the decimation filters, the impedance demodulator and the accelerometer's own filters, and align all streams to the slowest. Lining up costs latency, 23 ms here, which is harmless for a recording but matters in the closed loops of [Chapter 33]({% link chapters/33_closedloop.md %}).

</div>

<figure id="fig-31-2">
  <img src="{{ '/assets/figs/ch31_learning.svg' | relative_url }}" style="width:720px" alt="Artefact reduction in two-second windows during three walks for step sizes 0.003, 0.01 and 0.1, and artefact reduction against the lag of the impedance trace, falling from 12.2 dB to 7.2 dB at 125 ms unless all streams are lined up">
  <figcaption><span class="capnum">Figure 31.2.</span> <strong>Learn fast enough, but not too fast; and line the streams up.</strong> (a) Artefact removed in 2 s windows during the three walks of Figure 31.1's recording, both references, for three step sizes: 0.003 learns slowly and then removes the most, 0.01 learns within the first walk, 0.1 learns at once but the EEG keeps jolting its weights. (b) Artefact removed against the lag of the impedance trace behind the recording: 12.2 dB on time, 10.6 dB at 23 ms, 7.2 dB at 125 ms; triangles mark the trace through a 10 Hz and a 2 Hz output low-pass. Delaying the recording and the accelerometer to match restores 12.2 dB at every lag. Synthetic, as Figure 31.1. From <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

Try it below on the same kind of synthetic recording, with Figure 31.1's settings: 256 S/s, 8 taps per reference, μ = 0.01 and δ of one per tap. The recording is generated in your browser, so its numbers differ a little from the figure's. Change the references, the step size and the number of taps, slide how much of the artefact comes through the impedance, and switch the regularisation off to see the filter fail between movements.

{::nomarkdown}
{% include demos/nlms.html %}
{:/}

## <span class="secnum">31.4</span>A signal-quality index

Cancellation reduces artefacts; it does not abolish them. A wearable should therefore say, for each window of data, how far it can be trusted. A **signal-quality index** combines the indicators of section 31.2 into a number or a few classes: good, usable with care, unusable. The simplest version is a set of thresholds (impedance above a limit, servo step, clipping, mains power, acceleration above a limit); a better one is a classifier trained on recordings labelled by experts, with the indicators as its features.

The index belongs *with* the data, sample by sample or window by window, in the same packets ([Chapter 27]({% link chapters/27_soc.md %})). Downstream, it gates what the algorithms may conclude: a seizure detector ([Chapter 25]({% link chapters/25_eeg.md %})) should not alarm on a window flagged unusable, a sleep scorer should mark it, and an analysis of many nights can weight each window by its quality instead of throwing whole nights away.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.4 · What the quality record costs on the link</div>

Take a record for each channel and each 250 ms window: a 2-bit class and three 1-bit flags, for lead-off, saturation and a servo step. For eight channels that is $$8 \times 5\ \text{bits} \times 4\ \text{s}^{-1} = 160$$ b/s. Add each channel's impedance magnitude and phase, 12 bits each, once a second: 192 b/s. The record is **352 b/s**.

Next to raw EEG, 32.8 kb/s for eight channels at 256 S/s and 16 bits ([Chapter 27]({% link chapters/27_soc.md %})), that is 1.1 %, and at 5 nJ/b it costs 1.8 µW in the radio. Next to the band-power features of Chapter 27, 384 b/s, it nearly doubles the stream. Send the impedance only when it moves by more than a set step and the flags only when they change, and a still recording costs only the classes: 64 b/s.

**What it means:** the record is cheap beside raw data and expensive beside features, so code it by change when the chip sends features.

</div>

## <span class="secnum">31.5</span>What it costs the chip

The hardware is mostly already there. The impedance channel of [Chapter 28]({% link chapters/28_bioz.md %}) adds of the order of 5 µW when running; an accelerometer adds tens of microwatts; the servo outputs, clipping counters and mains-power estimate are by-products. The computation is small: eight channels, two references of eight taps and 500 S/s need $$8 \times 16 \times 500 = 64\,000$$ multiply-accumulates per second for the filters and as many for the updates, 128 000 in all, well within a microcontroller and within reach of a small on-chip datapath. What matters more is *time*: impedance, motion and signal must share one sample clock, and the sample counter must travel with every packet.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Plan for motion from the start. Keep currents through the electrodes small or out of band, measure the electrode impedance continuously on the recording chip and its clock, add a motion sensor, and send a quality flag with every window. Cancel what the references explain with a regularised NLMS filter, and flag what they do not.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

A quality record on the chip's own frame clock: for each channel and 250 ms window, lead-off, saturation and servo-step flags and a 2-bit class from programmable thresholds; for each channel, impedance magnitude and phase from the impedance channel ([Chapter 28]({% link chapters/28_bioz.md %})) once a second or on change; sent over SPI with the samples it describes, about 0.35 kb/s ([Chapter 27]({% link chapters/27_soc.md %})). DC lead-off off while recording. Adaptive cancellation runs off chip in the first revision, on streams lined up by the sample counter.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Judging an artefact remover by how clean the output looks. A filter that removes "too much" removes signal: if the reference contains the biosignal, as a head-mounted accelerometer contains the heartbeat, the canceller subtracts it. Test on recordings with a known clean reference, or on synthetic artefacts added to clean data, and report what was removed from the signal as well as from the artefact.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

Run `figsrc/ch31_figs.py`, then change the artefact model in `scene()`: make it depend only on acceleration, or only on impedance, and watch which reference wins. Set δ back to a tiny number and see the filter blow up between movements. `report()` prints every number in this chapter; change `MUS` or `LAGS` to explore the step size and the reference lag.

</div>

**Read with this chapter.** Widrow et al. {% include cite.html keys="widrow1975" %}, Haykin {% include cite.html keys="haykin2014" %}, Webster {% include cite.html keys="webster" %} (motion artefacts).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Motion artefacts come from the electrode interface, the skin, currents through a changing impedance and the cables; they share the signal's band, so filters cannot remove them.
- A 6 nA lead-off current through a 20 kΩ impedance swing is 120 µV of artefact: keep electrode currents small or out of band.
- Measure contact quality continuously: impedance by IQ demodulation, servo steps, mains power, clipping and acceleration.
- NLMS cancels what correlated references explain; regularise it against bursty references, and keep references free of the biosignal and on the signal's clock.
- In the synthetic example, the accelerometer and the impedance remove 7.5 and 5.7 dB alone and 12.2 dB together.
- NLMS learns with a time constant of about $$L/2\mu_\mathrm{eff}$$ samples: μ = 0.01 learns within a walk and removes 12.2 dB over the minute, 0.003 learns too slowly and 0.1 lets the EEG jolt the weights (7.2 dB).
- Line every stream up in time: an impedance trace 23 ms late costs 1.6 dB, and delaying the recording and the accelerometer to match gets it back.
- A quality record of flags, a class and the impedance costs about 0.35 kb/s, 1 % of raw EEG; code it by change when the chip sends features.
- Send a signal-quality index with the data and let it gate what downstream algorithms conclude.

</div>
