---
title: 6. Noise and the Noise–Power Trade-off
parent: "Part II · The Analog Front-End"
nav_order: 6
permalink: /part-2/ch06/
chapter: 6
---

# <span class="chapnum">Chapter 6</span>Noise and the Noise–Power Trade-off

Every microvolt of noise you remove costs current. The noise efficiency factor tells you how close a design is to the physical limit.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compute thermal, flicker, shot and $$kT/C$$ noise and refer them to the amplifier input;
- integrate a noise spectrum over the signal band with the right noise bandwidth;
- derive the noise efficiency factor (NEF) and the power efficiency factor (PEF) and use them to compare designs;
- explain why a weak-inversion differential pair cannot do better than $$\mathrm{NEF} = \sqrt2\,n$$, and what current reuse buys;
- set a current budget per channel from the 1.5 µVrms noise target.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What is the minimum supply current that can meet the EEG-mode noise target, and how close to it can a real amplifier get?

</div>

[Chapter 5]({% link chapters/05_devices.md %}) measured the noise of single SG13G2 transistors. This chapter turns those numbers into a budget: how much noise each source adds, how to add them over the signal band, and how much current a given noise level costs. The budget starts from [Chapter 3]({% link chapters/03_electrodes.md %}): of the 1.5 µVrms allowed from 0.5 to 100 Hz, the electrodes take 0.34 µVrms (wet) or 1.20 µVrms (dry), leaving the amplifier **1.46 µVrms** or **0.9 µVrms**.

## <span class="secnum">6.1</span>Noise sources

Four kinds of noise appear in a biopotential front-end.

**Thermal noise.** Any resistance $$R$$ at temperature $$T$$ produces a white voltage noise of density $$4kTR$$ (V²/Hz). The electrode's real part is one such resistance ([Chapter 3]({% link chapters/03_electrodes.md %})); bias resistors and the channel of a MOSFET are others.

**Shot noise.** A current made of independent charges crossing a barrier fluctuates with density $$2qI$$ (A²/Hz). The base current of a bipolar transistor carries it ([Chapter 5]({% link chapters/05_devices.md %})), as does the leakage of a protection diode. In weak inversion, a MOSFET's channel current is itself a diffusion current over a barrier, so its "thermal" noise *is* shot noise. Refer $$2qI_\mathrm{D}$$ to the gate through $$g_\mathrm{m} = I_\mathrm{D}/(nU_T)$$:

$$\overline{v_n^2} = \frac{2qI_\mathrm{D}}{g_\mathrm{m}^2} = \frac{2n^2 kT\,U_T}{I_\mathrm{D}} = \frac{2nkT}{g_\mathrm{m}},$$

the expression [Chapter 5]({% link chapters/05_devices.md %}) checked against the SG13G2 simulation (18.4 against 18.5 nV/√Hz at 1 µA). In strong inversion the factor $$n/2$$ becomes about $$2/3$$.

**Flicker noise.** The $$1/f$$ noise of MOSFETs, $$K/(WLf)$$, with $$K = 1.6\times10^{-10}$$ V²·µm² for the SG13G2 low-voltage NMOS and $$5.4\times10^{-10}$$ for the PMOS.

**kT/C noise.** A capacitor sampled through a switch keeps the switch's thermal noise as a frozen voltage of variance $$kT/C$$, whatever the switch resistance. On 1 pF that is 64 µVrms, spread from DC to half the sample rate. It sets the capacitor sizes of the converters ([Chapter 14]({% link chapters/14_adcspecs.md %}), [Chapter 15]({% link chapters/15_switches.md %})) and of switched-capacitor filters ([Chapter 11]({% link chapters/11_filters.md %})); oversampling divides its in-band part by the OSR.

## <span class="secnum">6.2</span>Input-referred noise and noise bandwidth

Noise is measured at the output but compared with the signal at the input. Divide the output noise density by the squared gain at each frequency to get the **input-referred** density, and integrate that over the band:

$$V_\mathrm{ni,rms}^2 = \int_0^\infty \overline{v_{ni}^2}(f)\,\lvert H(f)\rvert^2\,df,$$

where $$H$$ is the normalised shape of the band. For white noise only the area under $$\lvert H\rvert^2$$ matters. That area is the **noise bandwidth** $$B_n$$:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Noise bandwidth and 1/f integration</div>

$$
B_n = \frac{\pi}{2} f_\mathrm{c}\ \text{(1st order)}, \qquad B_n = \frac{\pi}{2\sqrt2} f_\mathrm{c} = 1.11 f_\mathrm{c}\ \text{(2nd-order Butterworth)}, \qquad \int_{f_\mathrm{L}}^{f_\mathrm{H}} \frac{K}{WL\,f}\,df = \frac{K}{WL}\ln\frac{f_\mathrm{H}}{f_\mathrm{L}}
$$

</div>

A first-order roll-off at 100 Hz lets through 57 % more white-noise power than an ideal brick wall at 100 Hz. Flicker noise behaves differently: each decade of frequency contributes the same power, so the *ratio* of the band edges decides it, and the shape of the roll-off hardly matters.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 6.1 · The same input pair, chopped and unchopped</div>

Take the NMOS pair of [Chapter 5]({% link chapters/05_devices.md %}): 1800 µm² per device, 1 µA each, thermal floor $$\sqrt2 \times 18.5 = 26$$ nV/√Hz.

**Chopped** (flicker noise removed, thermal only): a brick wall from 0.5 to 100 Hz gives $$26\ \text{nV} \times \sqrt{99.5} = 0.26$$ µVrms; a first-order low-pass at 100 Hz gives 0.33 µVrms; a second-order Butterworth 0.28 µVrms ([Figure 6.1](#fig-6-1)b).

**Unchopped**: the flicker noise of the pair, $$\sqrt{2K\ln(200)/1800\ \text{µm}^2}$$, dominates, and all three filter shapes give 1.00–1.02 µVrms. Moving the high-pass corner instead matters: the diagnostic ECG band of 0.05–150 Hz has $$\ln(3000) = 8.0$$ instead of $$\ln(200) = 5.3$$, which raises the flicker noise by 23 %.

</div>

<figure id="fig-6-1">
  <img src="{{ '/assets/figs/ch06_bw.svg' | relative_url }}" style="width:720px" alt="Noise density of an NMOS input pair with its flicker and thermal parts, and integrated noise versus upper frequency for chopped and unchopped cases and three filter shapes">
  <figcaption><span class="capnum">Figure 6.1.</span> <strong>Flicker noise piles up per decade; white noise depends on the filter shape.</strong> (a) Input-referred noise of an SG13G2 NMOS pair, 1800 µm² and 1 µA per device: flicker noise dominates the EEG band (shaded), the 26 nV/√Hz thermal floor dominates above a few hundred hertz. (b) Noise integrated from 0.5 Hz up to the frequency on the axis, for the unchopped pair (solid, about 1 µVrms for every filter) and the chopped, thermal-only pair (dashed, 0.26–0.33 µVrms depending on the filter). Computed from the Chapter 5 device data.</figcaption>
</figure>

With a real electrode the amplifier's noise is not the whole story. An amplifier has a voltage noise $$e_n$$ and a current noise $$i_n$$, and the current noise flows through the electrode impedance. Together with the electrode's own thermal noise the input sees

$$\overline{v_\mathrm{total}^2} = e_n^2 + i_n^2\,\lvert Z_\mathrm{e}\rvert^2 + 4kT\,\mathrm{Re}\{Z_\mathrm{e}\} \ \text{per hertz}.$$

Above $$\lvert Z_\mathrm{e}\rvert = e_n/i_n$$ the current noise dominates. For the SG13G2 HBT at 1 µA that crossover is $$15.1\ \text{nV}/21.6\ \text{fA} = 0.7$$ MΩ, between a wet and a dry electrode, which is the trade-off of [Figure 5.3]({% link chapters/05_devices.md %}#fig-5-3). A MOSFET's gate current is so small that its current noise matters only for implanted microelectrodes.

## <span class="secnum">6.3</span>Noise efficiency factor and power efficiency factor

Noise can always be lowered by spending more current, so a noise number alone says little about a design. Steyaert and Sansen {% include cite.html keys="steyaert1987" %} normalised it by the current with the **noise efficiency factor**, and Harrison and Charles {% include cite.html keys="harrison2003" %} made it the standard yardstick for neural and biopotential amplifiers:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Noise efficiency factor and power efficiency factor</div>

$$
\mathrm{NEF} = V_\mathrm{ni,rms}\sqrt{\frac{2\,I_\mathrm{tot}}{\pi\, U_T\, 4kT\, \mathrm{BW}}}, \qquad \mathrm{PEF} = \mathrm{NEF}^2\,V_\mathrm{DD}
$$

</div>

$$I_\mathrm{tot}$$ is the total supply current of the amplifier and BW its −3 dB bandwidth; the $$\pi/2$$ inside assumes the noise rolls off with one pole, so that $$B_n = (\pi/2)\,\mathrm{BW}$$. For a band that is cut sharply by a digital filter afterwards, as in Open-BioAFE, use $$\mathrm{BW} = 2B_n/\pi$$. The definition can then be turned around into a current budget:

$$I_\mathrm{tot} = \mathrm{NEF}^2\,\frac{4kT\,U_T\,B_n}{V_\mathrm{ni,rms}^2}.$$

The **power efficiency factor** multiplies by the supply voltage, so that a design at 1.2 V and one at 3.3 V can be compared on power rather than current.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 6.2 · The current the EEG target costs</div>

With $$B_n = 99.5$$ Hz, $$4kT\,U_T\,B_n = 4.26\times10^{-20}$$ A·V². For the wet-electrode budget of 1.46 µVrms:

- an amplifier at the weak-inversion limit, $$\mathrm{NEF} = 1.73$$ (section 6.4), needs **60 nA**;
- a good real amplifier at NEF 3 needs 180 nA, and one at NEF 4 needs 320 nA.

For the dry-electrode budget of 0.9 µVrms the same amplifiers need 157 nA, 474 nA and 842 nA ([Figure 6.2](#fig-6-2)a). At 1.2 V, NEF 3 is a PEF of 10.8.

</div>

These currents are tiny next to the 8 µA a 10 µW channel can draw. Thermal noise alone does not explain why biopotential amplifiers spend microamperes. [Figure 6.2](#fig-6-2)b shows the first reason: without chopping, the flicker noise of a realistically sized pair is a floor that no current can push down. A 1000 µm² pair stays at 1.3 µVrms however much current it gets. The others are bandwidth (a chopped amplifier must amplify at the chopping frequency, kilohertz rather than hertz), the noise of every device after the input pair, and the extra stages that set gain, offset rejection and input impedance.

<figure id="fig-6-2">
  <img src="{{ '/assets/figs/ch06_nef.svg' | relative_url }}" style="width:720px" alt="Total current needed versus noise budget for several NEF values, and input noise of an SG13G2 NMOS pair versus current with and without flicker noise">
  <figcaption><span class="capnum">Figure 6.2.</span> <strong>Thermal noise is cheap; flicker noise is not for sale.</strong> (a) Total current needed to reach an amplifier noise budget over 0.5–100 Hz, for NEF from √2 to 6, with the wet- and dry-electrode budgets marked. (b) Input noise of an SG13G2 NMOS pair (W/L = 100/10 µm per device) against its total current: thermal noise alone follows the weak-inversion limit until the devices leave weak inversion; with the flicker noise of an unchopped 1000 or 1800 µm² pair, the noise flattens at 1.3 and 1.0 µVrms. Computed from the Chapter 5 device data.</figcaption>
</figure>

## <span class="secnum">6.4</span>The physical limit

How low can the NEF go? Consider a differential pair whose only noise is that of its two input transistors, each carrying half of $$I_\mathrm{tot}$$. For ideal bipolar transistors, each contributes $$2kT/g_\mathrm{m}$$ with $$g_\mathrm{m} = I_\mathrm{tot}/(2U_T)$$, and the pair's input noise is the sum of the two:

$$\overline{v_{ni}^2} = 2 \times \frac{2kT \cdot 2U_T}{I_\mathrm{tot}} = \frac{8kT\,U_T}{I_\mathrm{tot}}.$$

Put this into the current-budget form of the NEF and the pair gives $$\mathrm{NEF}^2 = 8/4 = 2$$, or **NEF = √2**. A weak-inversion MOS pair has $$n$$ times less $$g_\mathrm{m}$$ per microampere, which multiplies the noise power by $$n^2$$:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · NEF limit of a weak-inversion MOS pair</div>

$$
\mathrm{NEF}_\mathrm{min} = \sqrt2\,n \approx 1.73 \quad \text{for SG13G2 } (n = 1.22)
$$

</div>

The SG13G2 NMOS pair of [Figure 6.2](#fig-6-2)b reaches 1.72 at 100 nA, and 2.05 at 10 µA where its devices drift into moderate inversion. A real amplifier adds the noise of its other transistors. In a simple OTA the current-mirror load adds power in proportion to $$g_\mathrm{m,load}/g_\mathrm{m,in}$$: with loads in strong inversion at 5 V⁻¹ and inputs at 30 V⁻¹ that is 17 % more power, or 8 % more NEF. Cascodes, folding branches and bias circuits add more. Published capacitive-feedback amplifiers sit around NEF 2–4; the original design of Harrison and Charles reached 4.0 {% include cite.html keys="harrison2003" %}.

One trick goes below $$\sqrt2\,n$$. If the same current flows through an NMOS and a PMOS that both see the input, as in an inverter-based or complementary input stage, the two transconductances add while the current is spent once. The input noise power halves, and the limit falls to about $$n \approx 1.2$$. This **current reuse** comes at a price in SG13G2: the PMOS adds its larger flicker noise and its excess thermal noise ([Chapter 5]({% link chapters/05_devices.md %})), so it pays off only in a chopped amplifier at a supply high enough to stack the two devices.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 6.3 · A current budget for the Open-BioAFE first stage</div>

Give the first stage 2 µA, a quarter of the channel's budget. At NEF 3, its thermal noise over 0.5–100 Hz is

$$V_\mathrm{ni} = 3\sqrt{\frac{4.26\times10^{-20}}{2\ \text{µA}}} = 0.44\ \text{µVrms},$$

half the dry-electrode budget, provided chopping removes the flicker noise. Added in power to the dry electrodes' 1.20 µVrms, the channel totals $$\sqrt{1.20^2 + 0.44^2} = 1.28$$ µVrms, within the 1.5 µVrms target with room for the later stages.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

The thermal-noise floor costs well under a microampere at the EEG target; a weak-inversion MOS pair cannot beat NEF 1.73, and a good amplifier reaches 3. Spend the rest of the budget on what thermal-noise arithmetic ignores: removing flicker noise (chopping), amplifying at the chopping frequency, and the later stages. Judge every design by its NEF and PEF, compute noise over the real band edges, and remember that a first-order roll-off adds 57 % of white-noise power.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

First stage: about 2 µA from 1.2 V, NEF ≤ 3 (PEF ≤ 11), thermal noise ≤ 0.45 µVrms over 0.5–100 Hz, flicker noise removed by chopping ([Chapter 9]({% link chapters/09_chopper.md %})). Whole channel with dry electrodes: about 1.3 µVrms against the 1.5 µVrms target.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

NEF values are only comparable when they use the same bandwidth convention. The definition assumes a first-order roll-off with BW its −3 dB frequency; quoting the NEF of a brick-wall band with BW set to the band width makes an amplifier look $$\sqrt{\pi/2} = 1.25$$ times better than it is. Also check that $$I_\mathrm{tot}$$ includes the bias circuits and, for chopped amplifiers, the clock drivers.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 4]({% link chapters/31_labs.md %}#lab-4) computes the NEF of your Harrison LNA versus bias current. Before building it, reproduce [Figure 6.2](#fig-6-2)b from `figsrc/data/sg13_gmid.csv`: it tells you the best NEF your input pair can reach at each current.

</div>

**Read with this chapter.** Steyaert and Sansen {% include cite.html keys="steyaert1987" %}, Harrison and Charles {% include cite.html keys="harrison2003" %}, Sarpeshkar {% include cite.html keys="sarpeshkar" %} (noise in subthreshold circuits), Razavi {% include cite.html keys="razavi" %} (the chapter on noise).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Thermal noise $$4kTR$$, shot noise $$2qI$$, flicker noise $$K/(WLf)$$ and $$kT/C$$; in weak inversion a MOSFET's channel noise is the shot noise of its current, $$2nkT/g_\mathrm{m}$$ at the gate.
- White noise integrates over the noise bandwidth ($$\pi/2$$ times the corner for one pole); flicker noise over $$\ln(f_\mathrm{H}/f_\mathrm{L})$$, so only the band edges matter.
- NEF normalises noise by current; with a brick-wall band, $$I_\mathrm{tot} = \mathrm{NEF}^2\,4kTU_TB_n/V_\mathrm{ni}^2$$.
- A weak-inversion MOS pair cannot beat NEF $$\sqrt2\,n = 1.73$$ in SG13G2; current reuse can approach $$n$$.
- The EEG target needs only 60–840 nA of thermal-noise current; flicker noise, chopping bandwidth and later stages are what cost microamperes.

</div>
