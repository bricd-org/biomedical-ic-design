---
title: 27. On-Chip Processing and System Integration
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 27
permalink: /part-4/ch27/
chapter: 27
---

# <span class="chapnum">Chapter 27</span>On-Chip Processing and System Integration

On a wearable or implant, the radio usually costs more energy than the sensing; computing on chip is how you spend less of it.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- place feature extraction and small machine-learning models in silicon;
- use the seizure-detection SoC of Verma et al. {% include cite.html keys="verma2010" %} as a case study;
- compress biosignal data before transmission;
- design power management with LDOs and energy harvesting;
- compare BLE, backscatter and inductive data links;
- introduce stimulation: current DACs and charge balance.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which processing belongs on the Open-BioAFE chip, and which data must leave it?

</div>

Chapters [24]({% link chapters/24_ecg.md %})–[26]({% link chapters/26_emg.md %}) found that heartbeats, seizures and gestures can be recognised from a few numbers per window. This chapter asks what that is worth in a system, where the front-end is only one consumer among several, and adds the remaining pieces of a complete biosignal chip: power management, the data link and, briefly, stimulation ([Figure 27.1](#fig-27-1)).

<figure id="fig-27-1">
  <img src="{{ '/assets/figs/ch27_system.svg' | relative_url }}" style="width:720px" alt="System partition: electrodes, the analog front-end and converters, on-chip processing, an external radio link and phone, with power management from a battery or harvester and an optional stimulator">
  <figcaption><span class="capnum">Figure 27.1.</span> <strong>The system around the front-end.</strong> On chip, the front-end and converters feed a processing block that computes features, runs small classifiers and compresses raw data; three regulators supply the analog, converter and digital sections from a battery or harvester; an optional stimulator drives current back into the electrodes. Off chip, a radio carries the data at a cost of nanojoules per bit, which is why features (solid) rather than raw samples (dashed) should cross the link by default.</figcaption>
</figure>

## <span class="secnum">27.1</span>Feature extraction and edge ML in silicon

Every bit that leaves the chip costs energy in the radio; every operation on chip costs energy in the logic. The comparison decides the partition.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 27.1 · What raw data costs in the radio</div>

Eight channels of raw samples need 64 kb/s for ECG (500 S/s, 16 bits), 33 kb/s for EEG (256 S/s, 16 bits) and 192 kb/s for EMG (2 kS/s, 12 bits); one spike channel at 30 kS/s and 12 bits needs 360 kb/s. The features of the previous chapters need 0.3 kb/s (RR intervals and rhythm flags), 0.4 kb/s (six band powers per 2 s window and channel), 2.6 kb/s (four features per channel at five windows per second) and 6.7 kb/s (spike times and 16-sample snippets): **54 to 190 times less** ([Figure 27.2](#fig-27-2)a).

A Bluetooth-Low-Energy-class radio costs of the order of 5 nJ per transmitted bit, all overheads included. Raw EMG then costs 960 µW in the radio, twelve times the 80 µW of the whole eight-channel front-end; raw ECG 320 µW; the features 2–13 µW ([Figure 27.2](#fig-27-2)b).

</div>

The features cost little to compute. Band power is a filter, a squarer and an accumulator per band; MAV, WL, ZC and SSC are additions and comparisons; Pan–Tompkins is a few filters and a threshold. In a 130 nm process these operations cost picojoules each, and the feature path runs on the decimated, reduced-word-length data of Part IV. Small classifiers, such as a linear discriminant, a decision tree or a support-vector machine with a handful of support vectors, fit as well, especially with per-patient training done offline and only the parameters loaded on chip.

<figure id="fig-27-2">
  <img src="{{ '/assets/figs/ch27_soc.svg' | relative_url }}" style="width:720px" alt="Data rate per mode for raw samples and on-chip features, and radio power versus energy per bit for raw and feature data compared with the analog front-end power">
  <figcaption><span class="capnum">Figure 27.2.</span> <strong>Features cut the data by 50 to 200 times, and the radio power with it.</strong> (a) Data rate of eight channels of raw samples and of the on-chip features of Chapters 24–26 for each mode (spikes: one channel). (b) Radio power against the radio's energy per transmitted bit for raw data (solid) and features (dashed), with the 80 µW of the eight-channel analog front-end; the dotted lines mark a BLE-class radio and a backscatter link. Computed in <code>figsrc/ch27_figs.py</code>; the energy-per-bit values are order-of-magnitude assumptions.</figcaption>
</figure>

## <span class="secnum">27.2</span>Case study: an EEG seizure-detection SoC

The SoC of Verma et al. {% include cite.html keys="verma2010" %} is the reference design for this partition: chopper-stabilised instrumentation amplifiers, a multiplexed SAR converter and a feature processor that computes spectral energy features on chip, so that a seizure detector can run on the features rather than on raw EEG streamed off the device. Reading it after Part IV, look for three numbers: the energy of the analog front-end per channel, the energy of the feature computation per channel, and the data rate the chip would need without the features. The pattern of this chapter, in which features cost far less than transmission, is what made the design worthwhile.

## <span class="secnum">27.3</span>Compression

When raw data must leave the chip, for clinical review or for training a classifier, compression reduces the cost. **Lossless** coding of the differences between successive samples, with a variable-length code such as a Huffman or Rice code, typically halves to thirds the data for ECG and EEG, because successive samples are close. **Lossy** methods, such as transform coding with wavelets, level-crossing sampling ([Chapter 21]({% link chapters/21_bioadc.md %})) or compressive sensing, go further at a controlled loss of fidelity. Spikes are compressed by detection itself, as [Chapter 26]({% link chapters/26_emg.md %}) showed. Lossless difference coding is cheap enough for any chip and should be the default for raw streams.

## <span class="secnum">27.4</span>Power management

A microvolt front-end needs a quiet supply. A low-dropout regulator (LDO) between the battery and the analog circuits suppresses the battery's and the digital circuits' noise, but adds its own: an LDO's output noise of a few tens of microvolts across the band is common, and it reaches the signal through the front-end's limited power-supply rejection. With 80 dB of PSRR, 30 µVrms becomes 3 nVrms at the input, which is harmless; with 40 dB it becomes 0.3 µVrms, a fifth of the EEG budget. Separate LDOs for the analog front-end, the converters and the digital logic, and a fully differential front-end, keep the PSRR high. Clock edges and digital switching currents must stay off the analog supply and substrate.

Wearables run from small batteries, typically tens to hundreds of milliampere-hours. At 1.2 V and 100 µW for the whole chip, a 100 mAh cell lasts about 50 days. **Energy harvesting** (thermoelectric from body heat, photovoltaic, or radio-frequency power) delivers tens of microwatts at best on the body, which a feature-transmitting chip can live on and a raw-streaming one cannot.

## <span class="secnum">27.5</span>Data links

Three kinds of link dominate:

- **Active radios** such as BLE: standard, interoperable with phones, of the order of nanojoules per bit, and duty-cycled to save power at low data rates.
- **Backscatter**: the chip modulates the reflection of a carrier sent by a reader, instead of generating its own; tens to hundreds of picojoules per bit on the chip side, but the reader must be close and powered.
- **Inductive links** for implants: a coil pair carries both power and data through the skin, with data rates from tens of kilobits to megabits per second.

The link chooses itself once the data rate is known: features fit any of them; raw spikes or raw multichannel EMG need a capable, power-hungry link or a wire.

## <span class="secnum">27.6</span>Stimulation

Closed-loop devices, such as responsive neurostimulators and functional electrical stimulation, also *deliver* current through electrodes. A stimulator is a current-steering DAC that drives biphasic pulses: a cathodic phase that excites the tissue and an anodic phase that returns the charge. **Charge balance** is the safety requirement: any net charge left on the electrode drives electrochemical reactions that corrode the electrode and damage tissue. Matched current sources, passive shorting of the electrodes between pulses, and series DC-blocking capacitors keep the residual charge near zero. The recording front-end must also survive the stimulation artefact, volts at the electrode for milliseconds, which is where the large input range of direct-digitising front-ends ([Chapter 21]({% link chapters/21_bioadc.md %})) and the fast recovery of the servo loop ([Chapter 10]({% link chapters/10_dsl.md %})) matter. Sarpeshkar {% include cite.html keys="sarpeshkar" %} treats both the energy-efficient electronics and the systems around them.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Compute the features on chip and send them, with raw data only on demand and losslessly compressed: at nanojoules per radio bit, raw multichannel data costs ten times the front-end, features a small fraction of it. Give the analog front-end its own quiet LDO and keep its PSRR high. Choose the link from the data rate, not the other way round. If the device stimulates, design charge balance in from the start.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

On chip: decimation, the feature paths of [Chapters 24–26]({% link chapters/24_ecg.md %}) (RR intervals, band powers, EMG features, spike times) and lossless difference coding for raw streams. Out: an SPI interface to an external BLE or backscatter radio, features by default (0.3–7 kb/s), raw data on demand. Separate analog, converter and digital LDOs; front-end PSRR ≥ 80 dB. No stimulator in the first revision.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Quoting a microwatt front-end and leaving out the radio. A wearable's battery life is set by the whole system, and with raw streaming the radio usually dominates by an order of magnitude. Budget the link with the front-end from the first page ([Chapter 29]({% link chapters/29_arch.md %})).

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

Add a lossless Rice coder to `figsrc/ch27_figs.py` and measure its compression ratio on `biosig.ecg()` and `biosig.eeg()` samples quantised to 16 bits; then recompute the raw-data radio power with the compressed rate.

</div>

**Read with this chapter.** Verma et al. {% include cite.html keys="verma2010" %}, Sarpeshkar {% include cite.html keys="sarpeshkar" %} (ultra-low-power bioelectronics).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- On-chip features cut the data by 54 to 190 times (ECG, EEG, EMG, spikes).
- At about 5 nJ per radio bit, raw EMG from eight channels costs 960 µW, twelve times the front-end; features cost 2–13 µW.
- Lossless difference coding halves to thirds raw ECG and EEG; spikes are compressed by detection.
- The front-end needs its own LDO and high PSRR: 80 dB turns 30 µV of supply noise into 3 nV.
- Links: BLE (nanojoules per bit), backscatter (tens of picojoules), inductive for implants; the data rate chooses.
- Stimulators must be charge-balanced; the recording front-end must survive their artefacts.

</div>
