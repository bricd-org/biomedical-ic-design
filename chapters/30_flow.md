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
- write and simulate SAR logic in Verilog with mixed-signal co-simulation;
- run corners and Monte Carlo;
- run DRC, LVS and parasitic extraction in KLayout;
- use the JKU AMS chip template and submit to an IHP OpenMPW shuttle.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you take an Open-BioAFE block from schematic to a verified GDS that IHP will accept?

</div>

Every SG13G2 number in this tutorial came from the same place: the IHP-Open-PDK {% include cite.html keys="ihppdk" %}, simulated with ngspice inside the IIC-OSIC-TOOLS container {% include cite.html keys="iicosic" %}, driven by the scripts in `labs/spice/`. This chapter describes the whole flow those scripts are part of, from schematic to tape-out, and the traps this tutorial met on the way.

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

- **$$g_\mathrm{min}$$**: ngspice's default of $$10^{-12}$$ S across junctions is a teraohm in parallel with each device. It capped the thick-oxide pseudo-resistor at $$1.9\times10^{12}$$ Ω instead of the real $$5.6\times10^{13}$$ Ω ([Chapter 8]({% link chapters/08_lna.md %})). Lower it to $$10^{-15}$$ S for teraohm and femtoampere work.
- **Absolute tolerance**: the default 1 pA hides femtoampere leakage ([Chapter 15]({% link chapters/15_switches.md %})). Lower it together with $$g_\mathrm{min}$$, but not to the point where high-impedance internal nodes stop converging.
- **Time-varying circuits**: AC and noise analyses do not see chopping, sampling or regeneration. Use transient noise or periodic steady-state analysis for choppers, comparators and switched-capacitor circuits (Chapters [9]({% link chapters/09_chopper.md %}), [10]({% link chapters/10_dsl.md %}), [16]({% link chapters/16_comparators.md %})).

## <span class="secnum">30.3</span>Mixed-signal co-simulation

The SAR converter is a few hundred gates of logic around an analog DAC and comparator. Simulating it means running both together. ngspice's XSPICE digital extensions can co-simulate a Verilog block compiled with Verilator alongside the transistor-level circuit, exchanging events at the analog–digital boundaries. For long runs, replace the analog part by a validated behavioural model ([Chapter 22]({% link chapters/22_adctest.md %})) and simulate the logic alone with Icarus Verilog or Verilator. For the final check, run one full conversion at the transistor level, with the synthesised gate-level netlist.

## <span class="secnum">30.4</span>Corners and Monte Carlo

A biomedical chip must work across process, voltage and temperature:

- **process**: the PDK's MOS corners (tt, ss, ff, sf, fs), the HBT, resistor and capacitor corners;
- **voltage**: the 1.2 V core at ±10 %;
- **temperature**: 0–45 °C in use on the body, and the extremes of qualification, typically −20 to 85 °C. Leakage and pseudo-resistors move by one to two decades over this range ([Chapters 8]({% link chapters/08_lna.md %}) and [15]({% link chapters/15_switches.md %}));
- **mismatch**: the PDK's mismatch libraries (the `_mismatch` corner sections, with `mm_ok=1` on the devices) apply Pelgrom-scaled random variations ([Chapter 5]({% link chapters/05_devices.md %})). A Monte Carlo loop in an ngspice `.control` block, or a Python driver re-running the netlist with different seeds, gives the offset, CMRR and DNL distributions.

Report the worst case over the corners, and the 3σ of Monte Carlo at the typical corner, for every specification of [Table 29.1]({% link chapters/29_arch.md %}#tab-29-1).

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

The whole flow, from schematic to GDS, is free: IIC-OSIC-TOOLS with the IHP-Open-PDK, scripted so that every number can be regenerated. Script your simulations rather than clicking them, keep the netlists and the results under version control, lower $$g_\mathrm{min}$$ and the tolerances for picoampere work, and simulate time-varying circuits in the time domain. Start the chip from the JKU template, sign off with DRC, LVS and post-layout simulation at the corners, and plan the tests before the shuttle deadline.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

Flow: IIC-OSIC-TOOLS 2026.10 with the IHP-Open-PDK; schematics in Xschem; scripted ngspice simulations (`labs/spice/`); behavioural models in Python (`labs/python/`); digital back end through Yosys and OpenROAD; layout, DRC, LVS and extraction in KLayout; top level in the JKU AMS chip template; submission to an IHP OpenMPW shuttle with all design files under an open licence.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Trusting a simulation because it converged. A converged result can still be wrong when a default setting dominates it: $$g_\mathrm{min}$$ in a teraohm resistor, the absolute tolerance in a femtoampere leakage, an AC analysis of a chopper. Ask what limits each number, change the suspect setting, and check that the result does not move.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 14]({% link chapters/31_labs.md %}#lab-14) lays out the comparator and the CDAC in KLayout, runs DRC, LVS and extraction with the JKU template, and compares post-layout with schematic simulation. Before it, run `labs/spice/sg13_char.py` and `labs/spice/sg13_lna.py` to check that your container reproduces the numbers of Chapters 5 and 8.

</div>

**Read with this chapter.** IIC-OSIC-TOOLS {% include cite.html keys="iicosic" %}, the IHP-Open-PDK {% include cite.html keys="ihppdk" %}, the JKU AMS chip template {% include cite.html keys="jkutemplate" %}, IHP-Open-DesignLib {% include cite.html keys="ihpdesignlib" %}, *The Art of Analog IC Design* {% include cite.html keys="artofaicd" %} for the analog design flow in practice.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- IIC-OSIC-TOOLS bundles Xschem, ngspice, Xyce, KLayout, Verilator, Icarus, Yosys and OpenROAD with the IHP-Open-PDK.
- SG13G2 simulation needs the OSDI models in `.spiceinit`, a corner library and the PDK's subcircuits; script it.
- Lower $$g_\mathrm{min}$$ and the absolute tolerance for teraohm and femtoampere work; use time-domain analyses for time-varying circuits.
- Run corners (process, ±10 % supply, 0–45 °C in use, −20–85 °C qualification) and Monte Carlo with the mismatch libraries.
- Sign off with KLayout DRC, LVS and post-layout simulation; start from the JKU template; submit to an IHP OpenMPW shuttle.

</div>
