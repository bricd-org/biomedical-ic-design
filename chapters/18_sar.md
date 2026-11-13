---
title: 18. The SAR ADC
parent: "Part III · Data Converters"
nav_order: 18
permalink: /part-3/ch18/
chapter: 18
---

# <span class="chapnum">Chapter 18</span>The SAR ADC

Binary search in silicon: the 12-bit asynchronous SAR is the converter for the multiplexed EMG and spike modes of Open-BioAFE.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- implement the binary search algorithm with a CDAC, a comparator and SAR logic;
- choose between synchronous and asynchronous timing;
- write the SAR logic in Verilog and synthesise or hand-build it;
- add redundancy with non-binary weights and calibrate digitally;
- power-gate and duty-cycle the converter between biosignal samples.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What SAR design reaches 12 bits at the lowest energy per conversion for eight multiplexed channels?

</div>

Chapters [15]({% link chapters/15_switches.md %})–[17]({% link chapters/17_cdac.md %}) built the parts: a bootstrapped sampler, a 4 pF capacitive DAC of 1 fF units, and a dynamic comparator. This chapter connects them with a few hundred gates of logic, and adds the redundancy and calibration that let the small DAC reach 12 bits.

## <span class="secnum">18.1</span>The binary search algorithm

After sampling, the converter knows only that the input lies somewhere in the full range. It tries the midpoint: the MSB capacitor is switched so that the top plate moves by half the reference, and the comparator says whether the input is above or below. The MSB is kept or removed accordingly, and the next bit tries half of what remains. After $$N$$ comparisons the DAC's code is the input to within an LSB.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · SAR timing</div>

$$
T_\mathrm{conv} = T_\mathrm{sample} + M\,(t_\mathrm{DAC} + t_\mathrm{comp} + t_\mathrm{logic}), \qquad M \ge N
$$

</div>

$$M$$ is the number of comparison cycles: $$N$$ for a binary array, more with redundancy. For the Open-BioAFE SAR, eight channels at 2 kS/s mean 16 000 conversions per second, 62.5 µs each. Each cycle could take up to 4 µs, a hundred times more than the circuits need, so the SAR converts in a short burst and sleeps for the rest of the period (section 18.5).

## <span class="secnum">18.2</span>Synchronous versus asynchronous timing

A **synchronous** SAR steps through its cycles on an external clock of at least $$M$$ times the conversion rate. Every cycle must be long enough for the slowest one, usually the MSB's DAC settling and the comparator's longest, near-metastable decision. Simple, but the clock runs at a rate set by the worst case.

An **asynchronous** SAR generates its own timing. The comparator signals when it has decided, and that signal triggers the next DAC step and the next comparison. Easy decisions finish quickly, the clock distribution disappears, and only one external pulse per conversion is needed. It needs a timeout, so that a metastable decision ([Chapter 16]({% link chapters/16_comparators.md %})) cannot stall the conversion, and a delay line that guarantees the DAC has settled before each comparison. At biosignal rates either works; asynchronous timing saves the clock's power and lets the whole burst finish in a few microseconds.

## <span class="secnum">18.3</span>SAR logic

The logic is a shift register that walks a "current bit" pointer from the MSB down, and a register that keeps or clears each bit according to the comparator. In Verilog the heart of it is a few lines:

```verilog
// One SAR step per comparator decision (asynchronous: clk = comparator ready)
always @(posedge clk or posedge start) begin
  if (start) begin                 // new conversion: try the MSB
    ptr  <= 1 << (M-1);
    code <= 1 << (M-1);
  end else if (ptr != 0) begin       // comp = 1: input above the trial level
    code <= (comp ? code : (code & ~ptr)) | (ptr >> 1);  // keep or drop, try next
    ptr  <= ptr >> 1;
  end
end
assign done = (ptr == 0);
```

`code` drives the DAC switches directly, through level shifters and drivers sized for the bottom-plate capacitances. The logic can be synthesised with the SG13G2 standard cells and placed by the digital flow ([Chapter 30]({% link chapters/30_flow.md %})), or built by hand from dynamic logic for the lowest energy. At 16 kS/s, synthesised static CMOS costs about 1.5 pJ per conversion, a fifth of the converter's energy, which is acceptable.

## <span class="secnum">18.4</span>Redundancy and calibration

[Chapter 17]({% link chapters/17_cdac.md %}) left the DAC with 0.98 fF units whose 1.24 % mismatch puts 0.8 LSB of DNL at mid-scale. Two digital techniques recover the resolution.

**Calibration** measures the actual weight of each capacitor once, at power-up, by converting known combinations with the converter itself, and stores the weights. Each conversion's bits are then summed with the measured weights instead of the ideal powers of two.

**Redundancy** uses more cycles than bits, with weights of radix below two: a 12-bit converter with 14 cycles of radix 1.8 has weights 1820, 1011, 562, … units. Each bit's weight is now smaller than the sum of all the bits after it, so a wrong early decision, caused by noise, incomplete settling or a too-large MSB, can be corrected by the later bits. That makes calibration always possible (there are no gaps in the transfer curve), and it allows the early decisions to be fast and noisy.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 18.1 · What calibration and redundancy recover</div>

A behavioural Monte Carlo (`figsrc/ch18_figs.py`) converts a near-full-scale sine with SG13G2-sized units ($$\sigma_u = 1.24$$ %) and a comparator with LSB/4 of noise ([Figure 18.1](#fig-18-1)a). The median effective resolution is:

- binary, 12 cycles: **11.5 bits** uncalibrated, 11.8 bits with calibrated weights;
- radix 1.8, 14 cycles: 11.3 bits uncalibrated, **11.8 bits** calibrated.

Uncalibrated, the redundant array is worse, because its non-binary weights do not add up to a uniform code. Calibrated, both reach the noise limit. Redundancy pays for its two extra cycles elsewhere: it guarantees a gap-free curve for every die, not just the median one, and it lets the first ten decisions use the fast, noisy comparator mode of [Chapter 16]({% link chapters/16_comparators.md %}), which saves most of the comparator's energy.

</div>

<figure id="fig-18-1">
  <img src="{{ '/assets/figs/ch18_sar.svg' | relative_url }}" style="width:720px" alt="Effective number of bits versus unit-capacitor mismatch for binary and redundant SAR arrays with and without calibration, and the estimated energy per conversion broken down by block">
  <figcaption><span class="capnum">Figure 18.1.</span> <strong>Calibration recovers the small DAC; the comparator dominates the energy.</strong> (a) Median ENOB of a behavioural 12-bit SAR against unit-capacitor mismatch, for a binary array (12 cycles) and a radix-1.8 array (14 cycles), with ideal (solid) and calibrated (dashed) weights; the dotted line marks the 0.98 fF SG13G2 unit. (b) Estimated energy per conversion of the Open-BioAFE SAR: comparator with the noise-mode trick (Chapter 16), CDAC switching and average reference charge (Chapter 17), SAR logic and sampler. Computed in <code>figsrc/ch18_figs.py</code>; the logic and sampler figures are estimates.</figcaption>
</figure>

## <span class="secnum">18.5</span>Power gating and duty cycling

A biosignal SAR spends most of its time doing nothing. With asynchronous timing the 14 cycles finish in a few microseconds, leaving most of the 62.5 µs period idle. Everything with static current should be off during that time: the comparator's bias (if it has any), the reference buffer's fast path, the bootstrap charge pumps. Dynamic logic and dynamic comparators draw nothing when not clocked, which is why they suit the job. Leakage is then the floor. In 130 nm thin-oxide logic, a few hundred gates leak only nanoamperes at body temperature, but more at 85 °C ([Chapter 15]({% link chapters/15_switches.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 18.2 · The SAR's power budget</div>

The energy per conversion adds up to about **7.6 pJ** ([Figure 18.1](#fig-18-1)b): comparator 3.9 pJ, SAR logic 1.5 pJ, CDAC switching 0.84 pJ, average reference charge 0.84 pJ, sampler and timing 0.5 pJ. At 16 kS/s that is **0.12 µW** for all eight channels, 15 nW per channel. With 11 effective bits the Walden figure of merit is $$7.6\ \text{pJ}/2^{11} = 3.7$$ fJ per step, inside the 10 fJ/step target of [Chapter 14]({% link chapters/14_adcspecs.md %}).

</div>

## <span class="secnum">18.6</span>Case study: a 12-bit SAR in a seizure-detection SoC

The EEG acquisition SoC of Verma et al. {% include cite.html keys="verma2010" %} is a useful reference design to read alongside this chapter. It multiplexes many EEG channels into a low-voltage SAR converter, chops its front-ends, and computes seizure-detection features on chip. While reading it, look for the choices this chapter discussed: how the sampling capacitor is sized against $$kT/C$$ and leakage, how the DAC is switched, how the converter is clocked and duty-cycled, and how much of the total power the converter takes compared with the front-ends and the digital processor. Then compare with the open 12-bit SAR of Moser and Pretl in SKY130 {% include cite.html keys="jkusar" %}, whose schematics, layout and verification are public, and with the 8-bit synchronous SAR of the IHP Analog Academy in SG13G2 {% include cite.html keys="ihpacademy" %}.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Convert in a fast asynchronous burst and sleep for the rest of the period, so nothing with static current runs between samples. Build the DAC from small units, about 1 fF, and recover the linearity digitally: 14 redundant cycles of radix 1.8 and weights calibrated at power-up give 11.8 bits for every die and allow the early decisions to be fast and noisy. Expect the comparator to dominate the energy, then the logic. A converter at about 8 pJ per conversion, 0.12 µW for eight channels, is negligible beside the front-ends.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Open-BioAFE target</div>

12-bit asynchronous SAR, 14 cycles at radix 1.8 with foreground weight calibration, 16 kS/s shared by eight channels (2 kS/s each; 25 kS/s for one channel in spike mode), ENOB ≥ 11, about 7.6 pJ per conversion (3.7 fJ/step), duty-cycled with a burst of a few microseconds per sample.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Calibrating with the converter's own noise in the loop. A weight measured from a single conversion inherits the comparator's noise and freezes it into every later conversion. Average each calibration measurement over many conversions (64 or more), and repeat the calibration when the temperature changes by more than a few degrees.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 8]({% link chapters/31_labs.md %}#lab-8) builds the SAR: bootstrapped sample-and-hold, monotonic CDAC, Verilog SAR logic, mixed-signal simulation and `adctest.py`. Before the transistor-level work, run `figsrc/ch18_figs.py` with your own unit size and comparator noise to see what ENOB to expect.

</div>

**Read with this chapter.** Verma et al. {% include cite.html keys="verma2010" %}, Moser and Pretl {% include cite.html keys="jkusar" %}, the IHP Analog Academy SAR module {% include cite.html keys="ihpacademy" %}, Pelgrom {% include cite.html keys="pelgrom" %} (SAR converters).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A SAR makes $$M \ge N$$ comparisons per conversion; at 16 kS/s there is time for a hundred times slower circuits, so the converter runs in bursts and sleeps.
- Asynchronous timing removes the fast clock and adapts each cycle to its decision; it needs a metastability timeout.
- Calibrated weights recover the small DAC (0.98 fF units) to 11.8 bits; a redundant radix-1.8 array with 14 cycles guarantees it for every die and tolerates noisy early decisions.
- The energy is about 7.6 pJ per conversion, dominated by the comparator: 3.7 fJ/step and 0.12 µW for eight channels.

</div>
