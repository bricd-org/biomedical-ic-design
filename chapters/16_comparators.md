---
title: 16. Comparators
parent: "Part III · Data Converters"
nav_order: 16
permalink: /part-3/ch16/
chapter: 16
---

# <span class="chapnum">Chapter 16</span>Comparators

A SAR converter makes one comparator decision per bit; its offset, noise and energy set much of the converter's performance.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compare static preamplifier-plus-latch, dynamic StrongARM and double-tail comparators;
- predict offset from Pelgrom coefficients and calibrate it;
- measure input-referred noise with transient-noise simulation;
- control kickback and metastability;
- estimate energy per decision.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which comparator gives 12-bit decisions at the lowest energy, and how do you verify its offset and noise?

</div>

The comparator of the Open-BioAFE SAR must resolve the 244 µV LSB of [Chapter 15]({% link chapters/15_switches.md %}), twelve times per conversion, 16 000 conversions per second. Speed is no issue at that rate. What matters is that its noise stays well below an LSB and that it spends little energy doing so.

## <span class="secnum">16.1</span>Comparator architectures

**Static preamplifier plus latch.** A continuous-time preamplifier gains up the input difference, and a latch regenerates it to logic levels when clocked. The preamplifier draws current all the time, which a microwatt converter cannot afford, but it shields the input from the latch's kickback and can be auto-zeroed.

**StrongARM latch.** A single clocked stage: when the clock rises, a tail switch lets the input pair discharge two precharged nodes at rates set by the input difference, and a cross-coupled inverter pair then regenerates the difference to full logic levels. It draws no static current, only the charge of each decision, and it is the standard comparator of low-power SARs ([Figure 16.1](#fig-16-1)).

<figure id="fig-16-1">
  <img src="{{ '/assets/figs/ch16_strongarm.svg' | relative_url }}" style="width:720px" alt="Transistor schematic of the StrongARM latch: clocked tail transistor, input pair, cross-coupled NMOS and PMOS pairs, and four clocked reset transistors">
  <figcaption><span class="capnum">Figure 16.1.</span> <strong>The StrongARM latch.</strong> While CLK is low, four PMOS switches precharge the internal nodes P and Q and the outputs to \(V_\mathrm{DD}\), and the tail M0 is off. When CLK rises, M0 turns on and the input pair M1–M2 discharges P and Q at rates set by \(v_\mathrm{in+}\) and \(v_\mathrm{in-}\). Once the outputs have fallen by about a threshold, the cross-coupled pairs M3–M6 take over and regenerate the difference to full logic levels. Only the charge of the nodes is drawn per decision; an SR latch (not drawn) holds the result while the comparator resets.</figcaption>
</figure>

**Double-tail.** The integrating input stage and the regenerating latch get separate tails and clocks. The input stage can integrate longer and with a lower common mode, which improves noise and works at low supplies, at the price of a second clock phase.

For a 1.2 V, 16 kS/s, 12-bit converter, a dynamic comparator, StrongARM or double-tail, is the clear choice. The rest of the chapter sizes it.

## <span class="secnum">16.2</span>Offset and calibration

The comparator's offset is the input-pair mismatch of Pelgrom's law, plus the latch's mismatch divided by the gain of the integration phase. With the SG13G2 coefficients ([Chapter 5]({% link chapters/05_devices.md %})), a 4 µm² input pair has $$\sigma(V_\mathrm{os}) = 3.9/\sqrt4 = 2.0$$ mV (NMOS) or 1.1 mV (PMOS), eight and four LSBs ([Figure 16.2](#fig-16-2)b).

In a SAR this matters much less than it seems. The comparator compares every bit against the *same* threshold, so its offset shifts the whole transfer curve. It is a converter offset, not a nonlinearity, and [Chapter 14]({% link chapters/14_adcspecs.md %}) showed that offset is harmless in a biomedical channel whose DC level is removed anyway. Two cases still need care. A pipelined or two-comparator scheme compares against two thresholds, and there the offsets must match. And a large offset eats into the input range. A foreground calibration at power-up, shorting the inputs and trimming a small capacitor DAC on the comparator's internal nodes until the output toggles, brings it below an LSB.

## <span class="secnum">16.3</span>Noise

Comparator noise does not shift the curve; it blurs every decision. For an integrating comparator with a weak-inversion input pair, the noise and signal can be compared as charges. During the integration phase each input device delivers a charge $$Q_\mathrm{int}$$ with shot-noise variance $$2qQ_\mathrm{int}$$, while the input difference changes the charges by $$g_\mathrm{m}V_\mathrm{in}T = V_\mathrm{in}Q_\mathrm{int}/(nU_T)$$. Comparing the two:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Input-referred noise of an integrating comparator (weak inversion)</div>

$$
\sigma_v = 2\,nU_T\sqrt{\frac{q}{Q_\mathrm{int}}} = \sqrt{\frac{kT}{C_\mathrm{L}}\cdot\frac{4n^2U_T}{\Delta V}}, \qquad Q_\mathrm{int} = C_\mathrm{L}\Delta V
$$

</div>

The second form uses the load capacitance $$C_\mathrm{L}$$ that the input pair discharges by $$\Delta V$$. The noise is a $$kT/C$$ term, scaled by $$4n^2U_T/\Delta V$$. Lower noise means more charge per decision, which means more energy.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 16.1 · Noise and energy of the 12-bit comparator</div>

Aim for $$\sigma_v \le$$ LSB/4 = 61 µV, so that noise adds less than 0.1 bit of error. With $$n = 1.22$$, the input pair must integrate $$Q_\mathrm{int} = q(2nU_T/\sigma_v)^2 = 171$$ fC per device ([Figure 16.2](#fig-16-2)a). Discharging the integration nodes by 0.5 V, that is $$C_\mathrm{L} = 342$$ fF.

The energy per decision is about $$2C_\mathrm{L}V_\mathrm{DD}^2 = 0.99$$ pJ, or 11.8 pJ for twelve decisions, 0.19 µW at 16 kS/s. That is more than half of the 20 pJ budget of a 10 fJ/step SAR ([Chapter 14]({% link chapters/14_adcspecs.md %})). A 10-bit comparator needs sixteen times less: 10.7 fC, 21 fF and 62 fJ per decision.

</div>

The example points to the standard trick. Only the last few decisions of a conversion need the full noise performance; the first bits decide between voltages hundreds of LSBs apart. A SAR that uses a fast, noisy comparator mode for the early bits and the low-noise mode only for the last two or three, or that repeats and averages only the final decision, saves most of the comparator's energy ([Chapter 18]({% link chapters/18_sar.md %})).

Verify noise with a **transient-noise** simulation: apply a small DC input, run many comparisons with noise enabled, and fit the fraction of "1" decisions against the input to a Gaussian error function. Its standard deviation is the input-referred noise. An AC noise analysis cannot do this, because the comparator is a time-varying, regenerative circuit.

<figure id="fig-16-2">
  <img src="{{ '/assets/figs/ch16_comparator.svg' | relative_url }}" style="width:720px" alt="Input-referred noise of an integrating comparator versus integrated charge, and comparator offset versus input-device area for SG13G2 NMOS and PMOS pairs">
  <figcaption><span class="capnum">Figure 16.2.</span> <strong>Noise is bought with charge; offset is bought with area.</strong> (a) Input-referred noise of an integrating comparator with a weak-inversion input pair (n = 1.22) against the charge each input device integrates per decision; 12 bits at LSB/4 needs about 170 fC, 10 bits about 11 fC. (b) Offset standard deviation of an SG13G2 input pair against device area, with one 12-bit LSB. In a SAR the offset is a static converter offset and can be calibrated. Computed in <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">16.4</span>Kickback and metastability

**Kickback.** When the latch regenerates, its internal nodes swing by the full supply in a fraction of a nanosecond, and the input devices' gate–drain capacitance couples part of that swing back to the inputs. In a SAR the inputs are the CDAC's top plates, which are floating, so the kickback charge changes the held voltage. A 1 fF gate–drain capacitance swinging 1.2 V onto 4 pF is 0.3 mV, an LSB. Symmetric layout makes most of it common mode, a large CDAC dilutes it, and a small preamplifier or cascode isolates it.

**Metastability.** An input very close to the threshold produces a tiny initial difference, and the latch needs a long time to regenerate it. With regeneration time constant $$\tau = C/g_\mathrm{m}$$ and an integration gain $$A$$, the probability that a decision is still unresolved after a time $$t$$ is about $$(V_\mathrm{DD}/(A\,V_\mathrm{FS}))e^{-t/\tau}$$. For a low-power latch with $$\tau = 200$$ ps and $$A = 10$$, an error probability of $$10^{-9}$$ needs 3.7 ns. Each bit of the 16 kS/s SAR has about 4.8 µs, so at biosignal rates metastability is a matter of design hygiene, not of speed. An asynchronous SAR, which triggers the next bit on the comparator's ready signal, still needs a timeout so that a metastable decision cannot stall the conversion ([Chapter 18]({% link chapters/18_sar.md %})).

## <span class="secnum">16.5</span>Energy per decision

The comparator's energy is almost all charge drawn from the supply: the integration nodes precharged and discharged each decision ($$C_\mathrm{L}V_\mathrm{DD}\Delta V$$ per node), the latch's regeneration, and the clock drivers. The noise requirement fixes $$C_\mathrm{L}$$, so the energy per decision scales as $$1/\sigma_v^2$$: four times per bit of resolution, the thermal-noise rule of [Chapter 14]({% link chapters/14_adcspecs.md %}) again. At 12 bits the comparator is no longer a small part of the SAR's energy. Spend its low-noise energy only on the decisions that need it.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Use a dynamic comparator, StrongARM or double-tail, with no static current. Size its input pair for kickback and common-mode range, not for offset, which in a SAR is a static converter offset and can be calibrated. Size its integration capacitance for noise: LSB/4 at 12 bits needs about 340 fF and about 1 pJ per decision. Then cut the average by using the low-noise mode only for the last bits. Verify with transient-noise and Monte Carlo simulation; the AC analysis cannot see either property.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

Comparator: double-tail dynamic latch, weak-inversion NMOS input pair, noise ≤ 61 µVrms (LSB/4) in the final-bit mode, offset calibrated at power-up to below 1 LSB, about 1 pJ per low-noise decision and about 0.1 pJ in the fast mode: three low-noise and nine fast decisions give about 4 pJ per conversion.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Measuring comparator noise with a single transient run. One run gives one decision per clock and needs thousands of decisions per input level to estimate a probability. Sweep five to ten input levels across ±3σ, run a few thousand clocks at each with transient noise on, and fit the error function. Fewer points give a number, but not a trustworthy one.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 7]({% link chapters/31_labs.md %}#lab-7) designs the StrongARM comparator in SG13G2, finds its offset with Monte Carlo and its input-referred noise with transient noise, and measures its energy per decision. Compare your noise with [Figure 16.2](#fig-16-2)a at the charge your design integrates.

</div>

**Read with this chapter.** Razavi {% include cite.html keys="razavi" %}, Pelgrom {% include cite.html keys="pelgrom" %} (comparators), the IHP Analog Academy, whose SAR module starts from a dynamic comparator {% include cite.html keys="ihpacademy" %}.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Dynamic comparators (StrongARM, double-tail) draw only the charge of each decision; they suit a microwatt SAR.
- Comparator offset is a static converter offset in a SAR (2 mV for a 4 µm² NMOS pair) and can be calibrated.
- Integrating-comparator noise is $$2nU_T\sqrt{q/Q_\mathrm{int}}$$: LSB/4 at 12 bits needs about 170 fC per device and about 1 pJ per decision.
- Kickback onto the floating CDAC must be made common mode or isolated; metastability is negligible at biosignal rates but needs a timeout in asynchronous SARs.
- Energy per decision grows four times per bit; use the low-noise mode only for the last bits.

</div>
