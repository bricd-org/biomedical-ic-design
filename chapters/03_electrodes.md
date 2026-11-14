---
title: 3. Electrodes and the Body as a Circuit
parent: "Part I · Foundations"
nav_order: 3
permalink: /part-1/ch03/
chapter: 3
---

# <span class="chapnum">Chapter 3</span>Electrodes and the Body as a Circuit

The electrode is the first component of the circuit: before the amplifier sees anything, it adds an offset of hundreds of millivolts, a frequency-dependent impedance and its own noise.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compare wet Ag/AgCl, dry and implanted electrodes;
- explain half-cell potentials and the DC offset they leave between two electrodes;
- model the electrode–skin interface with the Randles circuit;
- compute the thermal noise of an electrode;
- derive the input impedance the amplifier needs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What input impedance, offset tolerance and noise floor does the electrode force on the amplifier?

</div>

## <span class="secnum">3.1</span>Electrode types

In the body, current is carried by ions; in the wire, by electrons. An electrode is where one becomes the other, through a chemical reaction at its surface. How easily that reaction runs decides almost everything about the electrode as a circuit element.

- **Wet Ag/AgCl electrodes** are the clinical standard. A silver disc coated with silver chloride sits in a chloride gel, and the reaction $$\mathrm{Ag} + \mathrm{Cl^-} \rightleftharpoons \mathrm{AgCl} + e^-$$ runs freely in both directions. Such an electrode is called **non-polarisable**: current passes with little change in its voltage, so its potential is stable and its noise is low. The gel wets the outer layer of the skin and lowers its impedance.
- **Dry electrodes** (metal, conductive polymer, or spiked contacts) touch the skin directly, which suits long-term wearables and EEG headsets. Without gel the contact impedance is ten to a hundred times higher, it varies between electrodes, and it is more sensitive to motion {% include cite.html keys="chi2010" %}.
- **Implanted microelectrodes** are tens of micrometres across and sit in the tissue, where there is no skin. Their tiny area makes them strongly capacitive, with impedances of hundreds of kilohms at 1 kHz.

## <span class="secnum">3.2</span>Half-cell potential and DC offset

Every electrode in an electrolyte develops a **half-cell potential** $$E_\mathrm{hc}$$, the voltage across its surface reaction. For Ag/AgCl it is about +0.222 V against the standard hydrogen electrode. Two identical electrodes would cancel, but in practice they never are identical: the skin under each one, the gel, the chloride concentration and the pressure all differ. The skin itself adds a potential of its own, $$E_\mathrm{se}$$, across its outer layer, which changes when the skin is stretched.

The difference between two electrodes is a **DC offset** of tens to hundreds of millivolts, much larger than any biopotential and slowly drifting. The ECG standards require an electrocardiograph to work with ±300 mV of offset at its input {% include cite.html keys="iec60601-2-25" %}. [Figure 3.1](#fig-3-1) shows what that looks like: an offset of about 120 mV on which the 1 mV ECG is invisible, plus baseline wander and a motion artefact.

<figure id="fig-3-1">
  <img src="{{ '/assets/figs/ch03_offset.svg' | relative_url }}" style="width:720px" alt="An ECG on a 120 mV electrode offset, and the same signal after removing the offset, with baseline wander and a motion artefact">
  <figcaption><span class="capnum">Figure 3.1.</span> <strong>The offset is a hundred times larger than the signal.</strong> (a) Ten seconds at an electrode pair: about 120 mV of offset with the ECG invisible on top. (b) The same signal after subtracting 120 mV: the ECG rides on a few millivolts of baseline wander, and a motion artefact at 6 s is larger than the QRS complexes. Simulated.</figcaption>
</figure>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

Tolerate ±300 mV of electrode DC offset at every input without saturating. With a 1.2 V supply and a front-end gain of 50 or more, this offset must be removed before or inside the first stage ([Chapter 10]({% link chapters/10_dsl.md %})).

</div>

## <span class="secnum">3.3</span>The electrode–skin model

[Figure 3.2](#fig-3-2) (top) is the standard equivalent circuit of a wet electrode on the skin. At the metal–gel interface, the half-cell potential $$E_\mathrm{hc}$$ is in series with the **Randles** network {% include cite.html keys="randles1947" %}: a charge-transfer resistance $$R_\mathrm{d}$$, through which the reaction passes current, in parallel with the double-layer capacitance $$C_\mathrm{d}$$, the thin layer of charge that forms at any electrode surface. The gel adds a series resistance $$R_\mathrm{s}$$. The outer layer of the skin, the epidermis, adds its own potential $$E_\mathrm{se}$$ and a resistance $$R_\mathrm{e}$$ in parallel with a capacitance $$C_\mathrm{e}$$. The dermis and the tissue below are almost purely resistive, $$R_\mathrm{u}$$.

<figure id="fig-3-2">
  <img src="{{ '/assets/figs/ch03_electrode_model.svg' | relative_url }}" style="width:720px" alt="Equivalent circuit of the electrode–skin interface and its simplified form">
  <figcaption><span class="capnum">Figure 3.2.</span> <strong>The electrode–skin interface as a circuit.</strong> Top: the full model, with the half-cell potential and Randles network of the electrode, the gel resistance, and the skin potential and RC network of the epidermis. Bottom: the simplified model used in <code>biosig.py</code>, one series resistance and one parallel RC (or a constant-phase element for an implanted microelectrode), with the values of the three electrode types.</figcaption>
</figure>

For design, the two parallel networks merge into one, giving the simplified model at the bottom of the figure. Its impedance is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Simplified electrode impedance</div>

$$
Z_\mathrm{e}(f) = R_\mathrm{s} + \frac{R_\mathrm{p}}{1 + j2\pi f R_\mathrm{p} C_\mathrm{p}},
\qquad f_\mathrm{p} = \frac{1}{2\pi R_\mathrm{p} C_\mathrm{p}}
$$

</div>

Below the corner $$f_\mathrm{p}$$ the electrode is resistive, $$R_\mathrm{s} + R_\mathrm{p}$$; above it, the capacitor takes over and the impedance falls towards $$R_\mathrm{s}$$. For the wet electrode the model uses 1 kΩ in series with 51 kΩ‖47 nF, the network the ECG standards use to represent one poor electrode contact; for a dry electrode, 5 kΩ in series with 1 MΩ‖4.7 nF. An implanted microelectrode is better described by a **constant-phase element**, $$Z = 1/(Q(j\omega)^n)$$ with $$n \approx 0.85$$, whose phase stays near $$-n \times 90^\circ \approx -76^\circ$$ at all frequencies.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.1 · Impedance of a wet and a dry electrode</div>

Wet: $$f_\mathrm{p} = 1/(2\pi \cdot 51\ \text{kΩ} \cdot 47\ \text{nF}) = 66$$ Hz. At 0.67 Hz, $$\lvert Z_\mathrm{e}\rvert \approx 1 + 51 = 52$$ kΩ; at 50 Hz, where the capacitor starts to help, 41.5 kΩ.

Dry: $$f_\mathrm{p} = 1/(2\pi \cdot 1\ \text{MΩ} \cdot 4.7\ \text{nF}) = 34$$ Hz. At 0.67 Hz, $$\lvert Z_\mathrm{e}\rvert \approx 1.0$$ MΩ; at 50 Hz, 564 kΩ.

Across the ExG band the dry electrode is about twenty times worse, and its impedance changes more with frequency ([Figure 3.3](#fig-3-3)).

</div>

<figure id="fig-3-3">
  <img src="{{ '/assets/figs/ch03_impedance.svg' | relative_url }}" style="width:720px" alt="Magnitude and phase of the impedance of wet, dry and implanted electrodes versus frequency">
  <figcaption><span class="capnum">Figure 3.3.</span> <strong>Electrode impedance falls with frequency.</strong> (a) Magnitude and (b) phase of the three electrode models of <code>biosig.z_electrode()</code>, with the ExG band shaded. Wet and dry electrodes are resistive at low frequency and capacitive above their corner; the implanted microelectrode is capacitive everywhere.</figcaption>
</figure>

## <span class="secnum">3.4</span>Electrode noise

Any resistance at temperature $$T$$ produces thermal noise, and the electrode is no exception: its noise comes from the real part of its impedance. The noise voltage of one electrode over a band from $$f_1$$ to $$f_2$$ is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Thermal noise of an electrode</div>

$$
v_\mathrm{n}^2 = \int_{f_1}^{f_2} 4kT\,\mathrm{Re}\{Z_\mathrm{e}(f)\}\,df
$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.2 · How much of the noise budget do the electrodes use?</div>

A wet electrode at 310 K is about 52 kΩ at low frequency, so its noise density is $$\sqrt{4kT \cdot 52\ \text{kΩ}} \approx 30$$ nV/√Hz. Over the 99.5 Hz of the EEG band that gives about 0.30 µVrms. The exact integral is a little lower, **0.24 µVrms**, because $$\mathrm{Re}\{Z_\mathrm{e}\}$$ falls above 66 Hz ([Figure 3.4](#fig-3-4)b).

A channel has two electrodes, whose noise adds in power: $$\sqrt{2} \times 0.24 = 0.34$$ µVrms. That leaves $$\sqrt{1.5^2 - 0.34^2} = 1.46$$ µVrms for the amplifier, almost the whole budget.

A dry electrode gives 0.85 µVrms each, or **1.20 µVrms** for the pair. Only $$\sqrt{1.5^2 - 1.2^2} = 0.9$$ µVrms is left for the amplifier, and that is before any excess noise.

</div>

<figure id="fig-3-4">
  <img src="{{ '/assets/figs/ch03_noise.svg' | relative_url }}" style="width:720px" alt="Thermal noise density of three electrode types, and their integrated noise versus bandwidth">
  <figcaption><span class="capnum">Figure 3.4.</span> <strong>Electrode thermal noise.</strong> (a) Noise density of one electrode at 310 K. (b) The same noise integrated from 0.5 Hz up to the frequency on the axis, with the 100 Hz edge of the EEG band dotted and the 1.5 µVrms target of the whole chain dashed. The implanted microelectrode alone is above the target in this band, which is why spike recordings are judged in their own 300 Hz–7 kHz band (2.8 µVrms for this model).</figcaption>
</figure>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Thermal noise is only a lower bound. Real electrodes, dry ones above all, show **excess noise** well above $$4kT\,\mathrm{Re}\{Z\}$$, with a $$1/f$$-like spectrum that comes from the chemistry at the interface and from skin movement. Measure your electrodes before you spend the noise budget.

</div>

## <span class="secnum">3.5</span>Motion artefacts and impedance mismatch

When the skin stretches or the electrode shifts, the skin potential $$E_\mathrm{se}$$ and the charge in the double layer change, and the electrode voltage jumps by millivolts ([Figure 3.1](#fig-3-1)b). These **motion artefacts** fall in the same band as the ECG, so filtering cannot remove them; good skin preparation, firm contact and a stable gel reduce them, and the front-end must at least not saturate when they happen.


The two electrodes of a pair also never have the same impedance. This **impedance mismatch** matters more than the impedance itself, because it turns the common-mode interference on the body into a differential signal that the amplifier cannot reject ([Chapter 4]({% link chapters/04_interference.md %})). The 51 kΩ‖47 nF network in one lead is how the standards create this mismatch on purpose when they test an ECG.

## <span class="secnum">3.6</span>Input impedance

The electrode impedance and the amplifier's input impedance $$Z_\mathrm{in}$$ form a divider, so only part of the electrode voltage reaches the amplifier.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Loss to the input divider</div>

$$
\frac{V_\mathrm{in}}{V_\mathrm{electrode}} = \frac{Z_\mathrm{in}}{Z_\mathrm{e} + Z_\mathrm{in}}
$$

</div>

The ECG standards turn this into a test {% include cite.html keys="medteqzin,iec60601-2-25" %}: a 620 kΩ resistor in parallel with 4.7 nF is placed in series with one input, with ±300 mV of DC offset, and the signal at 0.67 Hz and 40 Hz must not drop by more than 20 %.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.3 · The 2.5 MΩ rule</div>

At 0.67 Hz the 4.7 nF is about 50 MΩ, so the test source is essentially 620 kΩ. A 20 % drop means $$Z_\mathrm{in}/(Z_\mathrm{s} + Z_\mathrm{in}) \geq 0.8$$, or $$Z_\mathrm{in} \geq 4 Z_\mathrm{s}$$:

$$Z_\mathrm{in} \geq 4 \times 620\ \text{kΩ} = 2.48\ \text{MΩ}$$

At 40 Hz the source is 500 kΩ and the requirement 2.0 MΩ. The low-frequency case sets the familiar rule: at least **2.5 MΩ** per input.

</div>

<figure id="fig-3-5">
  <img src="{{ '/assets/figs/ch03_loading.svg' | relative_url }}" style="width:720px" alt="Percentage of the signal lost to the input divider versus amplifier input impedance for three electrode types">
  <figcaption><span class="capnum">Figure 3.5.</span> <strong>2.5 MΩ passes the test, but not with a dry electrode.</strong> Signal lost to the divider versus a resistive input impedance, for a wet and a dry electrode at 10 Hz and an implanted microelectrode at 1 kHz. At 2.5 MΩ the wet electrode loses 2 % but the dry one 27 %; 100 MΩ brings the dry electrode below 1 %.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

2.5 MΩ is the floor the standards set for wet electrodes. Open-BioAFE aims much higher: 100 MΩ or more for dry electrodes, and a common-mode input impedance that keeps mains interference below the noise, which [Chapter 4]({% link chapters/04_interference.md %}) derives (above 1 GΩ at 50 Hz on its own, about 12 MΩ with the right-leg drive of [Chapter 12]({% link chapters/12_cmcontrol.md %})). A plain MOS gate is easily that high; what pulls the input impedance down is the chopper's input capacitors, which [Chapter 10]({% link chapters/10_dsl.md %}) has to boost back up.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Lab 2: electrodes and interference</div>

[Lab 2]({% link chapters/31_labs.md %}#lab-2) builds these electrode models with `biosig.z_electrode()`, computes their noise with `thermal_noise_rms()`, and then adds the body and the mains of Chapter 4 to find the CMRR and input impedance the amplifier needs.

</div>

**Read with this chapter.** Webster {% include cite.html keys="webster" %} for electrode chemistry and models, Chi, Jung and Cauwenberghs {% include cite.html keys="chi2010" %} for dry and non-contact electrodes.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Ag/AgCl with gel is non-polarisable: stable potential, low impedance (about 50 kΩ in the model) and low noise. Dry electrodes are about twenty times higher in impedance; implanted microelectrodes are capacitive.
- Two electrodes never match: expect up to ±300 mV of DC offset, plus drift and motion artefacts in the signal band.
- The simplified model, $$R_\mathrm{s} + R_\mathrm{p} \parallel C_\mathrm{p}$$, is resistive below $$f_\mathrm{p}$$ and capacitive above it.
- Thermal noise of the pair: about 0.34 µVrms (wet) or 1.2 µVrms (dry) in 0.5–100 Hz, against a 1.5 µVrms target. Excess noise comes on top.
- The standards' input-impedance test gives at least 2.5 MΩ per input; dry electrodes and interference push the target to 100 MΩ and above.

</div>
