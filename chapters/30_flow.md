---
title: 30. Open-Source Design and Verification Flow
parent: "Part V · Putting It Together"
nav_order: 30
permalink: /part-5/ch30/
chapter: 30
---

# <span class="chapnum">Chapter 30</span>Open-Source Design and Verification Flow

Every circuit in this tutorial can be designed, verified and taped out with free tools and an open PDK.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- set up IIC-OSIC-TOOLS with Xschem, ngspice/Xyce and KLayout;
- check that a simulated number is set by the circuit, not by a simulator setting;
- write and simulate SAR logic in Verilog with mixed-signal co-simulation;
- run corners and Monte Carlo, and decide how many runs a specification needs;
- run DRC, LVS and parasitic extraction in KLayout;
- use the JKU AMS chip template and submit to an IHP OpenMPW shuttle.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you take an Open-BioAFE block from schematic to a verified GDS that IHP will accept?

</div>

Every SG13G2 number in this tutorial came from the same place: the IHP-Open-PDK {% include cite.html keys="ihppdk" %}, simulated with ngspice inside the IIC-OSIC-TOOLS container {% include cite.html keys="iicosic" %}, driven by the scripts in `labs/spice/`. This chapter describes the whole flow those scripts are part of, from schematic to tape-out, and the checks that tell you whether a simulated number can be trusted.

## <span class="secnum">30.1</span>The tool set

**Table 30.1. The open-source flow for an Open-BioAFE block.** All tools are in the IIC-OSIC-TOOLS container (the tutorial used the 2026.10 release).
{: .tabcaption #tab-30-1 }

| Step | Tool | Used in this tutorial for |
|---|---|---|
| Schematic | Xschem | testbenches and netlists of every lab circuit |
| Analog simulation | ngspice (with OSDI models), Xyce | gm/ID, noise, pseudo-resistors, switches (Chapters 5, 8, 15) |
| Behavioural models | Python (numpy, scipy) | converters, ΔΣ loops, DSP and budgets (`labs/python/biosig.py`) |
| Digital design | Verilog, Icarus Verilog, Verilator | SAR logic, decimators, feature paths (Chapters 18, 20, 27) |
| Synthesis and place-and-route | Yosys, OpenROAD (LibreLane) | digital back end on the SG13G2 standard cells |
| Layout | KLayout | analog layout, chip assembly |
| Verification | KLayout DRC and LVS, KLayout-based extraction | sign-off of every block |
| Chip template | JKU ihp-sg13g2-ams-chip-template | padframe and top level {% include cite.html keys="jkutemplate" %} |

The container runs on Linux, macOS and Windows with Docker. On an Apple-silicon Mac, as used for this tutorial, it runs natively; give Docker at least 4 GB of memory for layout verification.

## <span class="secnum">30.2</span>Schematic and simulation

The SG13G2 MOSFETs use the PSP compact model and the HBTs the VBIC/HICUM family, compiled as OSDI modules that ngspice loads at start-up. A simulation needs three things: a `.spiceinit` that loads the OSDI files (`psp103.osdi`, `r3_cmc.osdi` and the capacitor models) and points the source path at the PDK's model directory; a `.lib` line selecting a corner (`cornerMOSlv.lib mos_tt`, `cornerHBT.lib hbt_typ`); and the device subcircuits (`sg13_lv_nmos d g s b w= l=`, `npn13G2 c b e bn Nx=`). `labs/spice/sg13_char.py` writes its own `.spiceinit`, generates the netlists, runs them in the container with `ngspice -b` and parses the results, which is the pattern every lab follows.

Three simulator settings mattered in this tutorial and will matter in yours:

- **$$g_\mathrm{min}$$**: ngspice puts a conductance of $$10^{-12}$$ S by default across the junctions, a teraohm in parallel with each device. It capped the thick-oxide pseudo-resistor at $$1.9\times10^{12}$$ Ω instead of $$5.7\times10^{13}$$ Ω ([Chapter 8]({% link chapters/08_lna.md %})). Lower it until the result stops moving: $$10^{-16}$$ S for that device (Worked Example 30.1).
- **Absolute tolerance** (`abstol`, 1 pA by default) is the other usual suspect in picoampere work. In this tutorial it changed nothing: the pseudo-resistor ([Figure 30.1](#fig-30-1)a) and the switch leakage of [Chapter 15]({% link chapters/15_switches.md %}) read the same at $$10^{-12}$$ and $$10^{-18}$$ A. Check it the same way when a femtoampere current is itself the result.
- **Time-varying circuits**: AC and noise analyses do not see chopping, sampling or regeneration, and ngspice adds no device noise to a transient and has no periodic noise analysis. Simulate choppers, comparators and switched-capacitor circuits in the time domain, with the noise injected as explicit `trnoise` sources sized from the operating point, as [Lab 5]({% link labs/lab05_chopper.md %}) does, or take it from a validated key equation, as [Lab 7]({% link labs/lab07_comparator.md %}) does (Chapters [9]({% link chapters/09_chopper.md %}), [10]({% link chapters/10_dsl.md %}), [16]({% link chapters/16_comparators.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 30.1 · Is it the circuit or the simulator?</div>

`labs/spice/sg13_flow.py` simulates the thick-oxide pseudo-resistor of Worked Example 8.2 (one pair of 1/10 µm PMOS, tt, 27 °C) with $$g_\mathrm{min}$$ from $$10^{-9}$$ to $$10^{-18}$$ S and three values of `abstol` ([Figure 30.1](#fig-30-1)a). With $$g_\mathrm{min}$$ across each of its two devices, the simulator sees

$$R_\mathrm{sim} = \left(\frac{1}{R} + \frac{g_\mathrm{min}}{2}\right)^{-1},$$

and the results follow it exactly:

- at the default $$10^{-12}$$ S: $$1.93\times10^{12}$$ Ω, the simulator's own $$2/g_\mathrm{min}$$; with $$C_2 = 200$$ fF, a high-pass corner of 0.41 Hz;
- at $$10^{-14}$$ S: $$4.46\times10^{13}$$ Ω, still 22 % low;
- at $$10^{-15}$$ S, the setting of Chapter 8: $$5.59\times10^{13}$$ Ω, 3 % low;
- from $$10^{-16}$$ S down: $$5.75\times10^{13}$$ Ω, settled to 0.1 %, a corner of 0.014 Hz.

Changing `abstol` from $$10^{-12}$$ to $$10^{-18}$$ A moves none of these numbers. The default result is thirty times wrong, and it is the dangerous kind of wrong: 0.41 Hz *meets* the 0.5 Hz band edge, so no specification check flags it. The 3 % left at $$10^{-15}$$ S does not matter for a corner that the process moves by a factor of six (Worked Example 30.2), but it shows what "lower $$g_\mathrm{min}$$" means: not a value to copy, but a sweep, continued until the number stops moving.

</div>

<figure id="fig-30-1">
  <img src="{{ '/assets/figs/ch30_checks.svg' | relative_url }}" style="width:720px" alt="Three checks on simulated numbers: pseudo-resistor resistance against gmin, its high-pass corner at five process corners against temperature, and the running Monte Carlo estimate of an input pair's offset against the number of runs">
  <figcaption><span class="capnum">Figure 30.1.</span> <strong>Three checks on a simulated number: the settings, the corners and the statistics.</strong> (a) Small-signal resistance at 20 mV of the thick-oxide pseudo-resistor of Chapter 8 (tt, 27 °C) against \(g_\mathrm{min}\), for the default <code>abstol</code> of 10⁻¹² A (line) and 10⁻¹⁸ A (circles): above 10⁻¹⁴ S the simulator's own \(2/g_\mathrm{min}\) (dashed) sets it; from 10⁻¹⁶ S down it settles at 5.75 × 10¹³ Ω (dotted). (b) The LNA's high-pass corner with \(C_2\) = 200 fF set by the same pair, at the five MOS corners from −20 to 85 °C; shaded, the range in use; dashed, the 0.5 Hz band edge and the 0.05 Hz edge of diagnostic ECG. (c) Running estimate of the offset σ of two diode-connected 4/1 µm NMOS at 1 µA from N Monte Carlo runs with the PDK's mismatch models; shaded, where a correct estimate falls 95 % of the time; dashed, the hand prediction of Worked Example 30.3; dotted, the PDK's per-device coefficient misread as a pair's. Simulated with ngspice in SG13G2 (<code>labs/spice/sg13_flow.py</code>), plotted by <code>figsrc/ch30_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">30.3</span>Mixed-signal co-simulation

The SAR converter is a few hundred gates of logic around an analog DAC and comparator. Simulating it means running both together. ngspice's XSPICE digital extensions can co-simulate a Verilog block compiled with Verilator alongside the transistor-level circuit, exchanging events at the analog–digital boundaries. For long runs, replace the analog part by a validated behavioural model ([Chapter 22]({% link chapters/22_adctest.md %})) and simulate the logic alone with Icarus Verilog or Verilator. For the final check, run one full conversion at the transistor level, with the synthesised gate-level netlist.

## <span class="secnum">30.4</span>Corners and Monte Carlo

A biomedical chip must work across process, voltage and temperature:

- **process**: the PDK's MOS corners (tt, ss, ff, sf, fs), the HBT, resistor and capacitor corners;
- **voltage**: the 1.2 V core at ±10 %;
- **temperature**: 0–45 °C in use on the body, and the extremes of qualification, typically −20 to 85 °C, which the chip must survive and keep working through, though not necessarily within every specification. Leakage and pseudo-resistors move by one to two decades over the range in use and by about four over the qualification range (Worked Example 30.2; [Chapters 8]({% link chapters/08_lna.md %}) and [15]({% link chapters/15_switches.md %}));
- **mismatch**: the PDK's mismatch libraries (the `_mismatch` corner sections, with `mm_ok=1` on the devices) give each device its own random threshold and current-factor shift, scaled by Pelgrom's law ([Chapter 5]({% link chapters/05_devices.md %})). A Monte Carlo loop in an ngspice `.control` block calls `mc_source` to draw new values before each run (Worked Example 30.3).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 30.2 · One resistor at every corner</div>

`sg13_flow.py` also runs the pseudo-resistor of Worked Example 30.1 at the five MOS corners from −20 to 85 °C ([Figure 30.1](#fig-30-1)b). With $$C_2 = 200$$ fF the LNA's high-pass corner is:

- at 37 °C: 0.013 Hz (ss), 0.020 Hz (fs), 0.032 Hz (tt), 0.051 Hz (sf) and 0.083 Hz (ff), a factor of 6.5 from process alone;
- over the range in use, 0–45 °C: from 0.0004 Hz (ss, 0 °C) to 0.15 Hz (ff, 45 °C), a factor of about 400;
- at the 85 °C qualification corner: 0.5–2.2 Hz.

Three conclusions follow, and none of them is visible at the typical corner. The 0.5 Hz band edge holds everywhere in use. The 0.05 Hz edge of diagnostic ECG holds at tt and 37 °C, but not at sf or ff, nor at tt and 45 °C (0.060 Hz): a typical-corner simulation would have passed a specification the fast wafers miss. And at the slow end the time constant $$RC_2$$ is 400 s (ss, 0 °C): an LNA saturated by a motion artefact would need about half an hour to settle to 1 %, so the design needs a reset switch across $$C_2$$ or a fast-settling mode, a need that only the cold, slow corner reveals. The same spread would reach the servo loop of [Chapter 10]({% link chapters/10_dsl.md %}) if its integrator used a plain pseudo-resistor, which is why that chapter recommends a bias-controlled one.

</div>

Report the worst case over the corners, and the 3σ of Monte Carlo at the typical corner, for every specification of [Table 29.1]({% link chapters/29_arch.md %}#tab-29-1). A Monte Carlo result is itself a sample, and its uncertainty decides how many runs a specification needs:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · The uncertainty of a Monte Carlo result</div>

$$
\frac{\delta\sigma}{\sigma} \approx \frac{z}{\sqrt{2(N-1)}}, \qquad \frac{\delta p}{p} \approx \frac{z}{\sqrt{Np}}
$$

</div>

for a standard deviation estimated from $$N$$ runs, and for a failure rate $$p$$ counted from them, with $$z = 1.96$$ for 95 % confidence. Forty runs pin σ to ±22 %, 193 runs to ±10 %. Counting failures costs far more: a 3σ failure rate of 0.27 % needs about 36 000 runs to be known to ±20 %. Estimate σ from a few hundred runs, check that the distribution is Gaussian, and design to a margin of $$k\sigma$$; count failures only when the distribution is not Gaussian.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 30.3 · A Monte Carlo checks a hand calculation</div>

[Chapter 16]({% link chapters/16_comparators.md %}) predicts the offset of the comparator's 4/1 µm NMOS input pair from Pelgrom's law. `sg13_flow.py` measures it: 4000 runs of two diode-connected devices at 1 µA each, with the PDK's mismatch models ([Figure 30.1](#fig-30-1)c).

- **The prediction.** The PDK draws each device's threshold shift with $$\sigma = 3.9\ \text{mV·µm}/\sqrt{WL}$$, 1.95 mV here. The difference of two is $$\sqrt2$$ wider, 2.76 mV. A diode-connected device turns a threshold shift into a gate-voltage shift of only $$g_\mathrm{m}/(g_\mathrm{m}+g_\mathrm{ds}) = 0.96$$ of it ($$g_\mathrm{m}/g_\mathrm{ds} = 23$$ at this point), so the pair should show 2.64 mV.
- **The simulation.** 2.60 mV, with 95 % confidence between 2.54 and 2.66 mV: the prediction holds. Nine of the 4000 offsets lie beyond 3σ, against 10.8 for a Gaussian.
- **The misreading.** Taking 3.9 mV·µm as Pelgrom's pair coefficient predicts 1.95 mV. The running estimate leaves that prediction's 95 % band after 20 runs and never returns.

This check found a mistake in an earlier draft of this tutorial, which used the PDK's per-device 3.9 mV·µm as the pair coefficient; [Chapters 5]({% link chapters/05_devices.md %}), [9]({% link chapters/09_chopper.md %}) and [16]({% link chapters/16_comparators.md %}) now use 5.5 mV·µm. It also puts the 40-run Monte Carlo of [Lab 7]({% link labs/lab07_comparator.md %}) in proportion: its 4.5 mV for the whole comparator means somewhere between 3.7 and 5.8 mV.

</div>

## <span class="secnum">30.5</span>Layout and verification

Analog layout is drawn in KLayout with the PDK's technology files and parametric cells. The rules of the earlier chapters become layout tasks: common-centroid input pairs and capacitor arrays with dummies ([Chapter 17]({% link chapters/17_cdac.md %})), guard rings around the input pads and between the analog and digital areas ([Chapter 12]({% link chapters/12_cmcontrol.md %}#shielding)), symmetric chopper and comparator layouts.

Three checks sign off every block:

- **DRC** (design-rule check) with the PDK's KLayout rule decks, including density and antenna rules;
- **LVS** (layout versus schematic), which extracts the devices and connectivity from the layout and compares them with the Xschem netlist;
- **parasitic extraction**, which adds the wiring's resistance and capacitance to the netlist for **post-layout simulation**. The top-plate parasitics of the CDAC, the input routing capacitance and the coupling from digital lines to analog nodes appear only here.

## <span class="secnum">30.6</span>From template to tape-out

The JKU ihp-sg13g2-ams-chip-template {% include cite.html keys="jkutemplate" %} provides a padframe with ESD-protected analog and digital pads, a top-level structure and a working verification flow, so that a first chip does not start from an empty die. IHP runs free and low-cost OpenMPW shuttles for open-source designs; IHP-Open-DesignLib {% include cite.html keys="ihpdesignlib" %} documents the designs that have gone through and the submission route.

Before tape-out, check:

1. DRC clean, including fill and density, with the foundry's sign-off deck;
2. LVS clean for every block and for the top level with the padframe;
3. ESD protection on every pad and a seal ring around the die;
4. post-layout simulation of every specification at the corners;
5. test access: a mode that exposes each converter's raw output, and test points or a scan chain for the digital logic ([Chapter 22]({% link chapters/22_adctest.md %}));
6. documentation and an open licence for the design files, so that others can reproduce, measure and extend it.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

The whole flow, from schematic to GDS, is free: IIC-OSIC-TOOLS with the IHP-Open-PDK, scripted so that every number can be regenerated. Script your simulations rather than clicking them, and keep the netlists and the results under version control. Before you trust a number, sweep the setting that could be setting it, run it at the corners in use and not only at tt, and give a Monte Carlo enough runs for the accuracy you claim. Start the chip from the JKU template, sign off with DRC, LVS and post-layout simulation at the corners, and plan the tests before the shuttle deadline.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

Flow: IIC-OSIC-TOOLS 2026.10 with the IHP-Open-PDK; schematics in Xschem; scripted ngspice simulations (`labs/spice/`); behavioural models in Python (`labs/python/`); digital back end through Yosys and OpenROAD; layout, DRC, LVS and extraction in KLayout; top level in the JKU AMS chip template; submission to an IHP OpenMPW shuttle with all design files under an open licence. Verification: simulator settings checked by sweep ($$g_\mathrm{min} \le 10^{-16}$$ S on teraohm nodes); every specification at the five MOS corners, 1.08–1.32 V and 0–45 °C, with −20 and 85 °C for qualification; at least 200 Monte Carlo runs for each mismatch-limited specification.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Trusting a simulation because it converged. A converged result can still be wrong when a default setting dominates it: $$g_\mathrm{min}$$ in a teraohm resistor, which made the pseudo-resistor thirty times too small and still inside the specification; an AC analysis of a chopper. Ask what limits each number, change the suspect setting, and check that the result does not move.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 14]({% link labs/lab14_layout.md %}) lays out the comparator and the CDAC in KLayout, runs DRC, LVS and extraction with the JKU template, and compares post-layout with schematic simulation. Before it, run `labs/spice/sg13_char.py` and `labs/spice/sg13_lna.py` to check that your container reproduces the numbers of Chapters 5 and 8, and `labs/spice/sg13_flow.py` to reproduce [Figure 30.1](#fig-30-1). Then extend it: sweep $$g_\mathrm{min}$$ for the thin-oxide pseudo-resistor, rerun the corners at 1.08 and 1.32 V, or run the Monte Carlo on the PMOS pair and on a 100 µm² pair.

</div>

**Read with this chapter.** IIC-OSIC-TOOLS {% include cite.html keys="iicosic" %}, the IHP-Open-PDK {% include cite.html keys="ihppdk" %}, the JKU AMS chip template {% include cite.html keys="jkutemplate" %}, IHP-Open-DesignLib {% include cite.html keys="ihpdesignlib" %}, *The Art of Analog IC Design* {% include cite.html keys="artofaicd" %} for the analog design flow in practice.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- IIC-OSIC-TOOLS bundles Xschem, ngspice, Xyce, KLayout, Verilator, Icarus, Yosys and OpenROAD with the IHP-Open-PDK.
- SG13G2 simulation needs the OSDI models in `.spiceinit`, a corner library and the PDK's subcircuits; script it.
- A default can set the answer: with ngspice's $$g_\mathrm{min}$$ the thick-oxide pseudo-resistor is thirty times too small, yet inside the specification. Sweep $$g_\mathrm{min}$$ until the result stops moving ($$10^{-16}$$ S here); `abstol` changed nothing in this tutorial's circuits.
- ngspice adds no device noise to a transient: inject `trnoise` sources or use a validated key equation for time-varying circuits.
- Run every specification at the corners in use (process, ±10 % supply, 0–45 °C), with −20 and 85 °C for qualification: the pseudo-resistor's corner moves 6.5 times with process at 37 °C and about 400 times over 0–45 °C, and only the fast and slow corners show what fails.
- A Monte Carlo σ is good to $$\pm1.96/\sqrt{2(N-1)}$$: about 200 runs for ±10 %; a counted 3σ failure rate needs about 36 000. The PDK's mismatch coefficients are per device, so a pair spreads $$\sqrt2$$ wider.
- Sign off with KLayout DRC, LVS and post-layout simulation; start from the JKU template; submit to an IHP OpenMPW shuttle.

</div>
