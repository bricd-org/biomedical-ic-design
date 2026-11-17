---
title: 32. Signal Quality and Motion Artefacts
parent: "Part VI · Wearable Systems"
nav_order: 32
permalink: /part-6/ch32/
chapter: 32
---

# <span class="chapnum">Chapter 32</span>Signal Quality and Motion Artefacts

On a moving person the hardest question is not how small a signal the chip can resolve, but whether the sample it just produced can be trusted.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain the mechanisms by which motion turns into voltage at the electrodes;
- measure contact quality during a recording, with impedance tracking and with other indicators the chip already has;
- cancel an artefact adaptively from reference signals with the NLMS algorithm, and choose its references, length and step size;
- build a signal-quality index that travels with the data;
- budget the hardware and computation that all of this costs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which references, measured by the same chip on the same clock, let a wearable remove motion artefacts it cannot filter, and tell the user when it cannot?

</div>

Everything in Parts I to V assumed a still subject. A wearable is worn by someone who walks, talks, chews and turns their head, and every movement disturbs the electrodes. The resulting **motion artefacts** are often larger than the signal and, worse, they fall in the same band: from a fraction of a hertz to tens of hertz, exactly where the ECG, EEG and EMG live. No filter can separate what shares a band. This chapter shows how to recognise motion artefacts, how to measure the electrode contact while recording, and how to subtract the artefact using signals that are correlated with it but not with the biosignal.

## <span class="secnum">32.1</span>How motion becomes voltage

Four mechanisms dominate {% include cite.html keys="webster" %}.

- **The interface itself.** Moving an electrode relative to its gel disturbs the double layer of [Chapter 3]({% link chapters/03_electrodes.md %}) and so its half-cell potential. Floating electrodes, gel, and Ag/AgCl's non-polarisable surface reduce it.
- **The skin.** Stretching the skin changes the potential across its outer layer by millivolts. Light abrasion of the skin reduces it.
- **Currents through a changing impedance.** Any current through the electrode turns its impedance change into a voltage. The DC lead-off current of [Chapter 12]({% link chapters/12_cmcontrol.md %}) is one such current; the common-mode current from the mains is another, through the divider $$\Delta Z / Z_\mathrm{cm}$$ of [Chapter 4]({% link chapters/04_interference.md %}), whose imbalance $$\Delta Z$$ now moves with every step.
- **The cables.** Flexing leads generates triboelectric charge, and moving leads change their capacitance to the body and to the mains. Short, light, shielded leads, or digitising close to the electrodes, reduce it.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.1 · A lead-off current meets a moving electrode</div>

The DC lead-off detector of [Chapter 12]({% link chapters/12_cmcontrol.md %}) passes 6 nA through each electrode. A dry electrode whose impedance swings by 20 kΩ as the wearer walks then produces $$6\ \text{nA} \times 20\ \text{k}\Omega = 120$$ µV of artefact, at the walking rhythm: six times a typical EEG. An AC impedance measurement at tens of kilohertz ([Chapter 28]({% link chapters/28_bioz.md %})) moves its own artefact out of band, and turning the DC lead-off current off while recording removes this term altogether.

</div>

## <span class="secnum">32.2</span>Measuring contact quality while recording

The contact cannot be judged once at the start: it changes as the gel dries, as the wearer sweats, and with every movement. A wearable needs indicators that it can read *continuously*, on the same clock as the signal.

- **Electrode impedance**, by the out-of-band tone and IQ demodulation of [Chapter 28]({% link chapters/28_bioz.md %}). Its magnitude says how good the contact is, its phase how much of it is capacitive, its imbalance between electrodes how much mains will convert to differential mode, and its rate of change how much the contact is moving. A tone injected through the right-leg drive reaches every electrode at once, so one source can track all channels.
- **The DC servo's output** ([Chapter 10]({% link chapters/10_dsl.md %})), which follows the electrode offset: a step means the interface was disturbed.
- **Mains power in the signal**, a free measure of the impedance imbalance: the 50 Hz line rises when one contact degrades.
- **Saturation and clipping counters** in the converter path.
- **Motion itself**, from an accelerometer next to the electrodes.

Each indicator costs little. The impedance channel costs a few microwatts ([Chapter 29]({% link chapters/29_arch.md %})); the rest are numbers the chip already computes.

## <span class="secnum">32.3</span>Adaptive cancellation

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

**References.** An accelerometer measures the cause of the artefact, not its electrical path: it sees the movement, but not how each electrode responds to it. The electrode impedance measures the interface itself, but not the parts of the artefact that bypass it, such as cable motion. The two are complementary. [Figure 32.1](#fig-32-1) cancels a synthetic artefact, built from an impedance-driven part (a lead-off current through the moving contact) and a part that follows acceleration directly, with each reference and with both.

<figure id="fig-32-1">
  <img src="{{ '/assets/figs/ch32_nlms.svg' | relative_url }}" style="width:720px" alt="Synthetic motion artefact during walking compared with the residual after NLMS cancellation using impedance and accelerometer references, and a bar chart of artefact reduction: 7.5 dB with the accelerometer, 5.7 dB with impedance and 12.2 dB with both">
  <figcaption><span class="capnum">Figure 32.1.</span> <strong>Two references remove more than either alone.</strong> (a) A synthetic walking artefact on a 256 S/s EEG, and what is left after NLMS with both references (8 taps each, μ = 0.01, δ = one per tap), both against the clean EEG, all in the 0.5–40 Hz band. (b) Artefact power removed after convergence: 7.5 dB with the accelerometer alone, 5.7 dB with the electrode impedance alone, 12.2 dB with both; a least-squares fit, the ceiling for these references, reaches 18 dB. The model and its numbers are illustrative, not measured. From <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

Three conditions make it work on real data. The references must be sampled on the same clock as the signal, or their delay changes and the filter chases it; this is one more argument for measuring impedance on the recording chip. The references must not contain the biosignal: an impedance trace demodulated out of band is clean, but an accelerometer on the head picks up the ballistocardiogram, the tiny motion of each heartbeat, and can cancel part of a cardiac signal. And the filter must be stopped from adapting when there is no movement, or reset after a large one, or it drifts.

Try it below on the same kind of synthetic recording. Change the references, the step size and the number of taps, slide how much of the artefact comes through the impedance, and switch the regularisation off to see the filter fail between movements.

{::nomarkdown}
{% include demos/nlms.html %}
{:/}

## <span class="secnum">32.4</span>A signal-quality index

Cancellation reduces artefacts; it does not abolish them. A wearable should therefore say, for each window of data, how far it can be trusted. A **signal-quality index** combines the indicators of section 32.2 into a number or a few classes: good, usable with care, unusable. The simplest version is a set of thresholds (impedance above a limit, servo step, clipping, mains power, acceleration above a limit); a better one is a classifier trained on recordings labelled by experts, with the indicators as its features.

The index belongs *with* the data, sample by sample or window by window, in the same packets ([Chapter 27]({% link chapters/27_soc.md %})). Downstream, it gates what the algorithms may conclude: a seizure detector ([Chapter 25]({% link chapters/25_eeg.md %})) should not alarm on a window flagged unusable, a sleep scorer should mark it, and an analysis of many nights can weight each window by its quality instead of throwing whole nights away.

## <span class="secnum">32.5</span>What it costs the chip

The hardware is mostly already there. The impedance channel of [Chapter 28]({% link chapters/28_bioz.md %}) adds of the order of 5 µW when running; an accelerometer adds tens of microwatts; the servo outputs, clipping counters and mains-power estimate are by-products. The computation is small: eight channels, two references of eight taps and 500 S/s need $$8 \times 16 \times 500 \times 2 = 128\,000$$ multiply-accumulates per second for the filter and as many for the update, well within a microcontroller and within reach of a small on-chip datapath. What matters more is *time*: impedance, motion and signal must share one sample clock, and the sample counter must travel with every packet.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Plan for motion from the start. Keep currents through the electrodes small or out of band, measure the electrode impedance continuously on the recording chip and its clock, add a motion sensor, and send a quality flag with every window. Cancel what the references explain with a regularised NLMS filter, and flag what they do not.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Judging an artefact remover by how clean the output looks. A filter that removes "too much" removes signal: if the reference contains the biosignal, as a head-mounted accelerometer contains the heartbeat, the canceller subtracts it. Test on recordings with a known clean reference, or on synthetic artefacts added to clean data, and report what was removed from the signal as well as from the artefact.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

Run `figsrc/ch32_figs.py`, then change the artefact model in `scene()`: make it depend only on acceleration, or only on impedance, and watch which reference wins. Set δ back to a tiny number and see the filter blow up between movements.

</div>

**Read with this chapter.** Widrow et al. {% include cite.html keys="widrow1975" %}, Haykin {% include cite.html keys="haykin2014" %}, Webster {% include cite.html keys="webster" %} (motion artefacts).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Motion artefacts come from the electrode interface, the skin, currents through a changing impedance and the cables; they share the signal's band, so filters cannot remove them.
- A 6 nA lead-off current through a 20 kΩ impedance swing is 120 µV of artefact: keep electrode currents small or out of band.
- Measure contact quality continuously: impedance by IQ demodulation, servo steps, mains power, clipping and acceleration.
- NLMS cancels what correlated references explain; regularise it against bursty references, and keep references free of the biosignal and on the signal's clock.
- In the synthetic example, the accelerometer and the impedance remove 7.5 and 5.7 dB alone and 12.2 dB together.
- Send a signal-quality index with the data and let it gate what downstream algorithms conclude.

</div>
