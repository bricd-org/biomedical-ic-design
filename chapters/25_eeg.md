---
title: 25. EEG Processing and Brain–Computer Interfaces
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 25
permalink: /part-4/ch25/
chapter: 25
---

# <span class="chapnum">Chapter 25</span>EEG Processing and Brain–Computer Interfaces

EEG carries information in rhythms and their changes; most of the processing estimates power in frequency bands.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compute band power and spectral features;
- remove EOG and EMG artefacts, including with ICA;
- detect seizure onset on the CHB-MIT database;
- explain the basics of SSVEP and motor-imagery BCIs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which EEG features need which resolution and sample rate, and what does that save on chip?

</div>

The EEG is the most demanding signal of the chip: it sets the 1.5 µVrms noise target and, with the electrode offset, the 16-bit converter ([Chapter 2]({% link chapters/02_signals.md %})). What the applications extract from it, however, is mostly coarse: the power in a few frequency bands, its changes over seconds, and its spatial pattern across electrodes. This chapter asks how much of the front-end's precision those features actually use, with a synthetic EEG whose seizure-like segments are known exactly; Lab 12 repeats the study on real recordings from CHB-MIT {% include cite.html keys="chbmit" %}.

## <span class="secnum">25.1</span>Band power and spectral features

EEG rhythms fall into bands: delta (0.5–4 Hz), theta (4–8 Hz), alpha (8–13 Hz), beta (13–30 Hz) and gamma (30–100 Hz). The workhorse feature is the **power in each band** over a window of one to a few seconds, estimated with Welch's method (averaged FFTs of overlapping, windowed segments) or with a bank of band-pass filters and a squarer, which is cheaper on chip. Ratios between bands, relative power (band power over total power) and the **spectral edge** (the frequency below which 90 % of the power lies) follow from the same numbers. Time-domain features such as **line length**, the sum of absolute sample-to-sample differences, are cheaper still, but, as section 25.3 shows, they respond to noise as well as to rhythms.

## <span class="secnum">25.2</span>Artefact removal

The eyes and muscles produce larger signals than the brain. **Eye movements and blinks** (EOG) add slow, large deflections at the frontal electrodes, below about 4 Hz. **Muscle activity** (EMG) from the jaw, forehead and neck adds broadband noise above about 20 Hz. Three methods deal with them:

- **filtering**, which removes the out-of-band part but also the EEG in the same band;
- **regression** against dedicated EOG electrodes, which subtracts a scaled copy of the eye signal;
- **independent component analysis** (ICA), which unmixes a multichannel recording into statistically independent sources; components that look like blinks or muscle are removed and the rest are mixed back.

ICA needs many channels and offline computation. On chip, the practical approach is to detect artefacts, by amplitude, slope or the DC servo's offset monitor ([Chapter 10]({% link chapters/10_dsl.md %})), and flag or discard the affected windows rather than repair them.

## <span class="secnum">25.3</span>Seizure-onset detection

An epileptic seizure typically shows as a rhythmic discharge, often in the theta range, with a large amplitude, building up over seconds. Detectors compute features per window, two seconds in this example, and classify each window. The SoC of Verma et al. {% include cite.html keys="verma2010" %} computed spectral energy features on chip for exactly this purpose, so that only detections, not raw EEG, had to leave the device.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 25.1 · How many bits does seizure detection need?</div>

`figsrc/ch25_figs.py` adds three 10 s rhythmic discharges (3–6 Hz, 60 µV) to two minutes of synthetic EEG (20 µVrms background) and detects them per 2 s window ([Figure 25.1](#fig-25-1)). In EEG mode the total gain of 800 maps ±0.625 mV at the electrodes onto the converter ([Chapter 11]({% link chapters/11_filters.md %})).

- **Line length** fails: noise inflates it as much as the discharges do, and a threshold on it does no better than always answering "no seizure" (75 % of windows).
- **Theta power** (3–8 Hz) with a threshold at three times its median reaches **99 % window accuracy with 6–7 bits** (an LSB of 19.5 µV at 6 bits), with input noise from 1.5 up to 15 µVrms. With 4 bits it still reaches 92–95 %.

</div>

<figure id="fig-25-1">
  <img src="{{ '/assets/figs/ch25_eeg.svg' | relative_url }}" style="width:720px" alt="A synthetic EEG with seizure-like segments and its line-length and theta-power features, and window accuracy of a theta-power detector versus ADC bits for three noise levels">
  <figcaption><span class="capnum">Figure 25.1.</span> <strong>The right feature matters more than the bits.</strong> (a) Two minutes of synthetic EEG with rhythmic discharges (shaded), its line length and its theta power per 2 s window: theta power stands out, line length barely. (b) Window accuracy of a theta-power threshold against ADC bits over the EEG-mode range of ±0.625 mV, for three levels of input noise, averaged over four records; the dotted line is the 75 % of always answering "no seizure". Computed in <code>figsrc/ch25_figs.py</code>.</figcaption>
</figure>

Real seizures are less clean than these. On CHB-MIT, patient-specific detectors that combine band powers from several channels perform far better than generic ones, and the useful figures are sensitivity per seizure, detection latency from onset, and false detections per hour. The synthetic study still makes the design point: the detector's features need far less resolution than the raw recording.

## <span class="secnum">25.4</span>BCI basics

Brain–computer interfaces turn EEG features into commands. Two paradigms dominate non-invasive BCIs:

- **SSVEP** (steady-state visually evoked potentials): the user looks at one of several targets flickering at different frequencies, and the visual cortex responds at the attended frequency and its harmonics. A narrow-band detector at each flicker frequency, over occipital electrodes, picks the target within a second or two.
- **Motor imagery**: imagining a movement of the left or right hand suppresses the mu (8–13 Hz) and beta rhythms over the opposite motor cortex. Band power over the left and right motor areas, combined with spatial filtering such as common spatial patterns, classifies the imagined movement.

Both rely on band power, not on microvolt waveform detail, and both benefit more from more channels and better electrode contact than from more bits.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Keep the full 16-bit, 1.5 µVrms chain for clinical recording, where the raw EEG is read by a person. For on-chip detection, compute band powers, which in this example need only 6–7 bits; that lets the chip send detections and features instead of raw data, which is where the power savings are ([Chapter 27]({% link chapters/27_soc.md %})). Choose features by testing them against noise: line length looks cheap but responds to noise as strongly as to rhythms. Detect artefacts on chip and flag them; leave ICA to offline analysis.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

On-chip EEG features per channel: band powers (delta to gamma) from a filter bank and squarer over 1–2 s windows, computed on the decimated 256 S/s data with 8-bit inputs to the feature path; a threshold or linear detector with per-patient thresholds; artefact flags from amplitude, slope and the DC servo monitor. Raw 16-bit data available on demand.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Reporting window accuracy on data where most windows are negative. With 75 % of windows free of seizures, a detector that never fires is 75 % accurate. Report sensitivity per seizure, detection latency and false detections per hour, and always compare with the trivial detector.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 12]({% link chapters/31_labs.md %}#lab-12) computes band-power features on CHB-MIT, trains a simple classifier, and plots latency and accuracy against word length and sample rate. Start by running `figsrc/ch25_figs.py` on a CHB-MIT record instead of the synthetic EEG, and replace window accuracy with per-seizure sensitivity and false detections per hour.

</div>

**Read with this chapter.** The CHB-MIT Scalp EEG Database {% include cite.html keys="chbmit" %}, Verma et al. {% include cite.html keys="verma2010" %}, Buzsáki, Anastassiou and Koch {% include cite.html keys="buzsaki2012" %} (the origin of the EEG rhythms).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- EEG features are mostly band powers over 1–2 s windows, from Welch spectra or filter banks.
- Artefacts (EOG, EMG) are larger than the EEG; ICA removes them offline, on chip they are flagged.
- In a synthetic study, theta power detects seizure-like discharges at 99 % window accuracy with 6–7 bits; line length fails against noise.
- SSVEP and motor-imagery BCIs rely on band power too; channels and contact quality matter more than bits.
- The 16-bit chain is for raw clinical EEG; on-chip detection can run on far fewer bits and send far less data.

</div>
