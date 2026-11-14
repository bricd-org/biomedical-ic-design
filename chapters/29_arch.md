---
title: 29. The Full Architecture and Its Budgets
parent: "Part V · Putting It Together"
nav_order: 29
permalink: /part-5/ch29/
chapter: 29
---

# <span class="chapnum">Chapter 29</span>The Full Architecture and Its Budgets

Every chapter so far has answered one budget question. This chapter puts the answers together on one chip.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- assemble the noise, CMRR, power, area and data-rate budgets of Open-BioAFE;
- choose SAR or ΔΣ per mode;
- add the optional bioimpedance channel;
- clock the whole chip from one reference;
- draw the top-level floorplan, the test chip and its pinout.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Does the assembled Open-BioAFE chip meet every number of its specification ([Table 1.2]({% link chapters/01_why.md %}#tab-1-2)), and where is the margin?

</div>

[Figure 1.1]({% link chapters/01_why.md %}#fig-1-1) drew the signal chain before any block was designed. Twenty-seven chapters later every block has a design, a number and a reason. This chapter adds the numbers up. The figure script `figsrc/ch29_figs.py` holds the budgets in two tables, so they can be updated as the lab results replace the chapter estimates. [Figure 29.1](#fig-29-1) shows the chip that the budgets describe.

<figure id="fig-29-1">
  <img src="{{ '/assets/figs/ch29_chip.svg' | relative_url }}" style="width:720px" alt="Block diagram of the complete chip: eight channel strips with protection, chopped LNA, PGA, Gm-C filter and incremental delta-sigma converter; a shared multiplexer and SAR; shared right-leg drive, references, LDOs, clocks and bioimpedance excitation; and a digital back end with decimators, features, coding and SPI">
  <figcaption><span class="capnum">Figure 29.1.</span> <strong>The complete Open-BioAFE chip.</strong> Each of the eight channels runs from its protected input pads through the chopped LNA with its servo and boosting loops, the PGA and the fourth-order filter to its own 16-bit incremental ΔΣ converter (ECG and EEG). An 8:1 multiplexer shares one 12-bit SAR among the channels (EMG). The right-leg drive, references, regulators, clocks and the optional impedance excitation are shared, and the digital back end turns the samples into features and sends them over SPI. Each block is labelled with the chapter that designs it.</figcaption>
</figure>

## <span class="secnum">29.1</span>Noise budget

Noise sources add in power. Over the 0.5–100 Hz EEG band, referred to the electrodes:

- the electrodes' own thermal noise: 0.34 µVrms (wet) or 1.20 µVrms (dry) for the pair ([Chapter 3]({% link chapters/03_electrodes.md %}));
- the chopped LNA, including the noise gain of its input, feedback, gate and servo capacitors: 0.36 µVrms ([Chapter 10]({% link chapters/10_dsl.md %}));
- two 5 kΩ input-protection resistors: 0.13 µVrms ([Chapter 12]({% link chapters/12_cmcontrol.md %}));
- the anti-alias filter's $$kT/C$$, divided by the gain of 800 in front of it: 0.05 µVrms ([Chapter 11]({% link chapters/11_filters.md %}));
- the PGA, divided by the LNA's gain: 0.02 µVrms;
- the 16-bit ΔΣ converter, divided by the total gain: 0.006 µVrms ([Chapter 20]({% link chapters/20_dscircuits.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 29.1 · The channel's noise</div>

With wet electrodes: $$\sqrt{0.34^2 + 0.36^2 + 0.13^2 + 0.05^2 + 0.02^2} = $$ **0.51 µVrms**, a third of the 1.5 µVrms target. With dry electrodes: **1.26 µVrms**, 16 % below the target ([Figure 29.3](#fig-29-3)a).

With dry electrodes the electrodes themselves take 91 % of the noise power, and the electronics only 9 %. Further front-end current would buy almost nothing; the excess noise of real dry electrodes ([Chapter 3]({% link chapters/03_electrodes.md %})) is the real risk to the margin.

</div>

[Figure 29.2](#fig-29-2) follows the largest signal and the noise through the chain. Each mode's gain brings its largest signal close to the converter's 0.5 V full scale: 4 mV of ECG through a gain of 100 and 5 mV of EMG through 80 both reach 0.4 V, and 300 µV of EEG through 800 reaches 0.24 V, 6 dB below full scale. The EEG noise rises with the signal, so their ratio is fixed at the electrodes and the LNA and never improves afterwards. By the converter the 0.51 µVrms has become about 0.41 mVrms, 39 dB above the 16-bit converter's quantisation noise of 4.4 µVrms: the stages after the LNA, the converter included, add almost nothing. That is what the gain plan of [Chapter 11]({% link chapters/11_filters.md %}) was for.

<figure id="fig-29-2">
  <img src="{{ '/assets/figs/ch29_levels.svg' | relative_url }}" style="width:720px" alt="Level diagram in dBV across electrodes, LNA, PGA, filter and converter for the largest ECG, EEG and EMG signals and for the EEG noise, with the converter full scale and the 16-bit and 12-bit quantisation noise">
  <figcaption><span class="capnum">Figure 29.2.</span> <strong>Gain brings every mode near full scale, and the noise stays far above the quantisation.</strong> Peak level of the largest signal at each node for ECG (4 mV, gain 100), EEG (300 µV, gain 800) and EMG (5 mV, gain 80), the EEG noise over 0.5–100 Hz with wet electrodes, the 0.5 V full scale, and the quantisation noise of the 16-bit ΔΣ (4.4 µVrms) and the 12-bit SAR (70 µVrms). EEG keeps 6 dB of headroom, and its noise reaches the converter 39 dB above the 16-bit quantisation noise. From <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.2</span>CMRR budget

The channel's CMRR has an intrinsic part and a part lost to the source ([Chapter 7]({% link chapters/07_ia.md %})). Chopping lifts the intrinsic CMRR of the capacitively coupled LNA above 100 dB ([Chapter 9]({% link chapters/09_chopper.md %})). Positive-feedback boosting raises the input impedance to about 200 MΩ ([Chapter 10]({% link chapters/10_dsl.md %})). The right-leg drive, with a loop gain of 100 at 50 Hz, divides the common mode at the electrodes by 101 ([Chapter 12]({% link chapters/12_cmcontrol.md %})). In the 10 Vrms CMRR test of the ECG standards ([Chapter 4]({% link chapters/04_interference.md %})) the residual is 0.06 mVpp, **24 dB inside** the 1 mVpp limit. The common-mode input impedance the test requires falls from 1.15 GΩ without the right-leg drive to about 12 MΩ with it, which closes the open design point of Chapter 4. [Table 1.2]({% link chapters/01_why.md %}#tab-1-2) now states the requirement in that form.

## <span class="secnum">29.3</span>Power, area and data rate

**Power.** Per channel ([Figure 29.3](#fig-29-3)b): the LNA's 2 µA (2.4 µW), the ΔΣ converter (1.9 µW, in ECG/EEG mode), the PGA (0.6 µW), a share of the right-leg drive, bias and LDOs (0.6 µW), the 3.3 V servo integrator (0.33 µW), choppers and ripple loop (0.3 µW), impedance boosting (0.3 µW), feature extraction and decimation (0.3 µW), and the filter and SAR shares. That totals **6.8 µW in ECG/EEG mode** and **4.9 µW in EMG mode**, against the 10 µW target: about 3 µW of margin, all of it estimate until the labs measure the blocks.

**Area.** The input capacitors dominate: two 20 pF MIM capacitors per channel (0.027 mm²), the anti-alias filter's capacitors (about 0.03 mm²), the servo and boosting capacitors, the LNA, PGA and ΔΣ transistors. With routing, about 0.14 mm² per channel, 1.15 mm² for eight. The SAR, references, bias, LDOs and right-leg drive add about 0.2 mm², the digital back end about 0.3 mm²: **about 1.7 mm² of core**, plus the pad ring.

**Data rate.** Features, 0.3–7 kb/s; raw data on demand up to 192 kb/s (eight channels of EMG), both well within an SPI link at a few megahertz ([Chapter 27]({% link chapters/27_soc.md %})).

<figure id="fig-29-3">
  <img src="{{ '/assets/figs/ch29_budgets.svg' | relative_url }}" style="width:720px" alt="Stacked noise-power budget of one channel with wet and dry electrodes against the 1.5 microvolt target, and stacked power per channel by block in ECG/EEG and EMG modes against 10 microwatts">
  <figcaption><span class="capnum">Figure 29.3.</span> <strong>The chip meets its noise and power targets; dry electrodes use most of the noise budget.</strong> (a) Noise power over 0.5–100 Hz of one channel, by source, with wet and dry electrodes, against the 1.5 µVrms target (2.25 µV²). (b) Power per channel by block in ECG/EEG mode (with the ΔΣ converter) and EMG mode (with a share of the SAR), against the 10 µW target. From the chapter numbers collected in <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.4</span>SAR or ΔΣ per mode

**Table 29.1. The Open-BioAFE specification against the designed chain.**
{: .tabcaption #tab-29-1 }

| Parameter | Target ([Table 1.2]({% link chapters/01_why.md %}#tab-1-2)) | Designed | Chapters |
|---|---|---|---|
| Input noise, 0.5–100 Hz | < 1.5 µVrms | 0.51 µVrms (wet), 1.26 µVrms (dry) | 3, 6, 9–12 |
| CMRR test residual | < 1 mVpp (≈ 89 dB) | 0.06 mVpp (24 dB margin) | 4, 7, 10, 12 |
| Electrode offset | ±300 mV | ±300 mV with the 4 pF, 3.3 V servo loop | 10 |
| Input impedance | ≥ 2.5 MΩ; ≥ 100 MΩ for dry | 6.25 MΩ chopped; about 200 MΩ boosted | 9, 10 |
| ECG/EEG converter | 16 bits | incremental ΔΣ, 16.5 bits at 500 S/s | 13, 19, 20 |
| EMG/spike converter | 12 bits | asynchronous SAR, ENOB ≥ 11, 16 kS/s shared | 13–18 |
| Power per channel | < 10 µW | 6.8 µW (ECG/EEG), 4.9 µW (EMG) | 6, 14, 18, 20, 29 |
| Supply, process | 1.2 V, SG13G2 | 1.2 V core, 3.3 V servo, IHP SG13G2 | 5, 10, 30 |
| Data out | SPI | features 0.3–7 kb/s; raw ≤ 192 kb/s | 27 |

The converter routing of [Figure 1.1]({% link chapters/01_why.md %}#fig-1-1) follows from Part III. **ECG and EEG** go to the incremental ΔΣ: their dynamic range, set by the residual electrode offset and artefacts, needs 16 bits, and at that resolution the oversampled converter's 1.1 pF sampling capacitor beats the 150 pF a Nyquist converter would need ([Chapter 14]({% link chapters/14_adcspecs.md %})). **EMG and spikes** go to the SAR: 12 bits suffice ([Chapter 13]({% link chapters/13_sampling.md %})), and at those bandwidths a shared Nyquist converter at about 12 pJ per conversion is almost free. A heart-rate-only mode could go further, with the ΔΣ at about 8 bits and the front-end bias halved ([Chapter 24]({% link chapters/24_ecg.md %})).

## <span class="secnum">29.5</span>The bioimpedance channel

The optional impedance channel of [Chapter 28]({% link chapters/28_bioz.md %}) adds a balanced current source at about 50 kHz (10–50 µA into the body, from a few microamperes of supply current), square-wave IQ demodulators on the recording channels, and two slow outputs per channel for the SAR. It shares the electrodes with the ECG by frequency separation, and its clock is derived from the same source as the chopper's. It adds of the order of 5 µW to the chip when running, and is duty-cycled while the contacts are stable.

## <span class="secnum">29.6</span>One clock

Every clock on the chip comes from one 1.024 MHz reference, an external clock or a trimmed RC oscillator, through dividers ([Figure 29.4](#fig-29-4)). Divided by two, it runs the ΔΣ loops, the decimators and the features at 512 kHz; 1024 of those cycles make one incremental conversion, so each channel delivers a 16-bit word every 2 ms, 500 S/s ([Chapter 20]({% link chapters/20_dscircuits.md %})). Divided by 256, it gives the 4 kHz chopper clock ([Chapter 9]({% link chapters/09_chopper.md %})): a whole number of chopper periods, eight, fits in each ΔΣ conversion. Divided by 64, it starts a SAR conversion every 62.5 µs; the 8:1 multiplexer visits each channel every 500 µs, 2 kS/s per channel, while the SAR times its own bit cycles ([Chapter 18]({% link chapters/18_sar.md %})). The impedance excitation, 51.2 kHz in I and Q phases, falls between the chopper's odd harmonics, as [Chapter 28]({% link chapters/28_bioz.md %}) requires. Only the SPI port runs on the host's clock.

Locking every clock to one reference is what makes the chopper harmless to the converters. Each channel is sampled at the same point of every chopper period, so the residual ripple aliases to a small constant offset instead of a beat tone inside the signal band. A separate oscillator for any one block would bring the beat back, at a frequency that drifts with temperature.

<figure id="fig-29-4">
  <img src="{{ '/assets/figs/ch29_clocks.svg' | relative_url }}" style="width:720px" alt="Clock tree from a 1.024 MHz reference through dividers to the delta-sigma loop, output word, choppers, SAR start of conversion and impedance excitation, and a timing diagram of one 2 ms frame showing the conversion, the chopper, 32 SAR slots and the channel-1 samples">
  <figcaption><span class="capnum">Figure 29.4.</span> <strong>One reference clocks the whole chip, so every sampling instant keeps a fixed phase to the chopper.</strong> Top: the dividers and what each clock drives. Bottom: one 2 ms frame, with the incremental ΔΣ reset and its 1024 cycles, eight chopper periods, 32 SAR slots cycling through the eight channels, and the four samples of channel 1, each at the same chopper phase.</figcaption>
</figure>

## <span class="secnum">29.7</span>Floorplan

Signal flow decides the floorplan. The eight channels form a row along the edge with the input pads, each channel a strip running from its pads inward: protection, LNA, PGA and filter, then its ΔΣ converter. The input pads and their routing are short and guarded ([Chapter 12]({% link chapters/12_cmcontrol.md %}#shielding)). The SAR, the bandgap, bias, references and LDOs sit in the middle. The digital back end, which holds the decimators, features and SPI, sits at the opposite edge on its own supply and substrate ties, with a guard ring and a wide gap between it and the analog row. The verdict of the Verma et al. SoC {% include cite.html keys="verma2010" %} and of the readout architectures in Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %} is the same: keep the clocks and the digital switching currents physically and electrically away from the microvolt inputs.

[Figure 29.5](#fig-29-5) draws the floorplan with the core to scale. The eight strips take two thirds of the 1.7 mm², and the two input capacitors alone a fifth of each strip, which is why the capacitor sizes of [Chapter 10]({% link chapters/10_dsl.md %}) set the chip's area.

<figure id="fig-29-5">
  <img src="{{ '/assets/figs/ch29_floorplan.svg' | relative_url }}" style="width:720px" alt="Floorplan concept: sixteen input pads along the top edge feed eight vertical channel strips with protection, LNA and input capacitors, PGA and filter, and delta-sigma converter; a middle row holds the RLD, SAR, bandgap, references, LDOs and bioimpedance source; the digital blocks sit at the bottom inside a guard ring next to the SPI pads">
  <figcaption><span class="capnum">Figure 29.5.</span> <strong>The microvolt inputs and the digital clocks sit at opposite edges.</strong> Sixteen input pads along one edge feed eight channel strips of 0.2 × 0.7 mm: protection, the LNA with its two 20 pF input capacitors, PGA and filter, ΔΣ. The SAR, bandgap, references, LDOs, right-leg drive and impedance source share the middle; the digital back end sits at the far edge inside a guard ring, on its own supply, next to the SPI pads. A concept: the core, about 1.6 × 1.06 mm, is to scale; the pads are illustrative.</figcaption>
</figure>

## <span class="secnum">29.8</span>Test chip and package

The first silicon is a test chip: the product's blocks plus the access needed to measure each one ([Figure 29.6](#fig-29-6)). An analog test multiplexer brings any LNA, PGA or filter output of any channel to two test pads, so the analog chain can be measured without the converters. Test modes over SPI stream the raw ΔΣ bit streams and SAR codes past the decimators and features, so the converters can be measured without the digital filters, and an on-chip resistor calibrates the impedance channel ([Chapter 28]({% link chapters/28_bioz.md %})). A test-signal generator and the lead-off currents of [Chapter 12]({% link chapters/12_cmcontrol.md %}) let the chip check its own channels. The bench of [Chapter 22]({% link chapters/22_adctest.md %}) supplies the rest: an electrode simulator with its offset, a precision DAC that plays recorded biosignals into the inputs, the CMRR fixture, an FPGA on the SPI port and a separately measured current on every supply.

<figure id="fig-29-6">
  <img src="{{ '/assets/figs/ch29_testchip.svg' | relative_url }}" style="width:720px" alt="Test chip concept: the eight channels, delta-sigma converters, digital back end, MUX and SAR, right-leg drive, bioimpedance source, clocks and references, with dashed test features (test-signal generator, analog test multiplexer to two test pads, raw-data test modes over SPI) and a test PCB with electrode simulator, precision DAC, CMRR fixture, FPGA and supplies">
  <figcaption><span class="capnum">Figure 29.6.</span> <strong>A test chip measures every block on its own.</strong> The product's signal path (blue and gold) with the test access added (dashed): a test-signal generator and lead-off currents at the inputs, an analog test multiplexer from any LNA, PGA or filter output to the TESTA and TESTB pads, and SPI test modes that return the raw ΔΣ bit streams and SAR codes. The test board plays simulated electrodes and recorded biosignals into the inputs and captures everything over SPI.</figcaption>
</figure>

[Figure 29.7](#fig-29-7) puts the test chip's 40 signals into a 6 × 6 mm QFN-40 package with the floorplan's rule. The sixteen inputs, two shield pins and the right-leg drive wrap round one corner; SPI, clock and reset sit in the opposite corner on their own I/O supply; the analog supplies separate the two groups, and the exposed pad is the analog ground. On the test board the input corner faces the electrode connector and the digital corner the FPGA, so no microvolt trace runs beside a clock. Plan the pins with the bench, before tape-out ([Chapter 30]({% link chapters/30_flow.md %})).

<figure id="fig-29-7">
  <img src="{{ '/assets/figs/ch29_package.svg' | relative_url }}" style="width:720px" alt="QFN-40 pinout concept, top view: inputs IN1 to IN8, two shield pins and RLD on the top and left sides, SPI, clock, reset and DRDY on the bottom-right corner, supplies and analog pins between, die on a VSSA exposed pad">
  <figcaption><span class="capnum">Figure 29.7.</span> <strong>The package keeps the floorplan's separation.</strong> A QFN-40 concept, 6 × 6 mm with 0.5 mm pitch, top view: electrode inputs, shields and right-leg drive (dark blue) round the top-left corner, SPI, clock, reset and data-ready (gold) round the bottom-right corner, supplies (grey) and the impedance, reference and test pins (light blue) between them. The die sits on an exposed pad tied to VSSA.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

On paper the assembled chain meets every target. Noise is 0.51 µVrms with wet electrodes and 1.26 µVrms with dry ones, the CMRR test passes with 24 dB of margin, and the power is 6.8 µW per channel. The margins sit in different places: noise is tight only with dry electrodes, and there the electrodes dominate; CMRR has plenty; power has 3 µW, all of it estimate. Replace each estimate with a lab measurement as the labs are done, and keep the budget tables in `figsrc/ch29_figs.py` up to date.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

Eight channels, each: protected inputs, chopped capacitively coupled LNA with servo loop and impedance boosting, PGA, fourth-order Gm-C filter, second-order incremental ΔΣ. Shared: 12-bit asynchronous SAR, right-leg drive, bandgap, references with an off-chip reservoir capacitor, three LDOs, optional impedance excitation, digital features and SPI. About 1.7 mm² of core in IHP SG13G2.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Treating a budget built from estimates as a result. Every number in [Figure 29.3](#fig-29-3) comes from a chapter's model, not from a measured circuit; the labs exist to replace them. Keep the source of every entry next to its value, and expect the first silicon to move several of them.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

Edit the `NOISE` and `POWER` tables in `figsrc/ch29_figs.py` with your own lab results (Labs 4, 5, 7, 8 and 10) and regenerate [Figure 29.3](#fig-29-3). Then try a heart-rate-only mode: halve the LNA current, drop the ΔΣ, and recompute the noise and power.

</div>

**Read with this chapter.** Verma et al. {% include cite.html keys="verma2010" %}, Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %}.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Noise: 0.51 µVrms (wet) and 1.26 µVrms (dry) against 1.5 µVrms; with dry electrodes the electrodes take 91 % of the noise power.
- CMRR: chopping, boosting and a right-leg drive of loop gain 100 pass the ECG test with 24 dB of margin; the common-mode impedance requirement is about 12 MΩ with the right-leg drive.
- Power: 6.8 µW per channel in ECG/EEG mode and 4.9 µW in EMG mode, against 10 µW.
- About 1.7 mm² of core; features 0.3–7 kb/s over SPI.
- One 1.024 MHz reference clocks everything, so the chopper ripple aliases to a constant; floorplan and pinout keep the inputs and the digital at opposite edges.
- ECG/EEG to the incremental ΔΣ, EMG/spikes to the shared SAR, as Part III's budgets require.

</div>
