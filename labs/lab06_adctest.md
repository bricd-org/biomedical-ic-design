---
title: "Lab 6. Ideal ADC and spectral testing"
parent: Hands-On Labs
nav_order: 6
permalink: /labs/lab-06/
---

# <span class="chapnum">Lab 6 · Python</span>Ideal ADC and spectral testing

**Goal.** Build `adctest.py`, the test bench that Labs 8 and 10 reuse, and learn what each test can and cannot see. Goes with Chapters [13]({% link chapters/13_sampling.md %}), [14]({% link chapters/14_adcspecs.md %}) and [22]({% link chapters/22_adctest.md %}).

**Run.**

```bash
cd labs/python
python adctest.py                  # 12-bit SAR, 1 % unit mismatch, seed 2 (Worked Example 14.1)
python adctest.py --sigma 0.002    # the 0.2 % of Chapter 17
```

`adctest.py` is both the lab and a module. `sine_test()` returns SNDR, SNR, THD, SFDR and ENOB of a sine record, coherent (rectangular window) or not (Hann or four-term Blackman–Harris, with the tone's power summed over its lobe). `ramp_histogram()` and `sine_histogram()` return DNL and INL. The sine version estimates the sine's amplitude and offset from the counts in the two end codes and corrects for the arcsine distribution, so it needs no precision ramp. The converter under test is `biosig.sar_convert()` with the mismatched weights of `biosig.cdac_weights()`; replace it by your own model or by codes exported from a simulation.

**Expected results.**

| Test | Result | Where in the text |
|---|---|---|
| Coherent 97 Hz tone at 2 kS/s, 8192 points, ideal 12-bit | SNDR 74.0 dB, ENOB 12.00 | Section 13.2 |
| Same, 1 % unit mismatch (seed 2) | SNDR 69.5 dB, ENOB 11.26, SFDR 76.2 dB | Worked Example 14.1 |
| Non-coherent tone, ideal converter: rectangular / Hann (±2 bins) / Hann (±30 bins) / Blackman–Harris | SNDR 9.8 / 40.8 / 73.7 / 73.9 dB | Section 22.1 |
| Ramp histogram, 64 hits per code | DNL −0.42 to +1.45 LSB, INL ±0.85 LSB | Worked Example 14.1 |
| Sine histogram, 2<sup>20</sup> samples | amplitude found to 0.01 %, DNL within 0.070 LSB rms of the ramp | Worked Example 22.1 |
| 10 converters each at σ<sub>u</sub> = 0.1, 0.2, 0.5, 1, 2 % | mean ENOB 11.99, 11.98, 11.89, 11.68, 11.20 | Chapter 17 |

The Hann rows show a trap: the Hann window's sidelobes fall slowly, so near a full-scale tone they still hold about −41 dBc. Summing only the three-bin main lobe as signal leaves that skirt in the noise; exclude about 30 bins, or use Blackman–Harris.

**Questions.**

1. Seed 2 at 1 % gives 11.26 effective bits, the ten-seed mean 11.68. What does that say about quoting a converter's ENOB from one simulated or one measured chip? How many chips would you measure?
2. Find the smallest σ<sub>u</sub> at which a missing code appears in 100 seeds. Compare it with the 3σ rule $$\sigma_u < 0.26\,\%$$ of Worked Example 14.1.
3. Reduce the sine-histogram record to 2<sup>16</sup> samples. How large is the DNL error now, and does it match $$1/\sqrt{\text{hits per code}}$$?
4. Add 0.1 LSB rms of white noise before the quantiser (comparator noise, Chapter 16). What happens to the SNDR, and to the DNL that the ramp histogram finds? Why does noise make the DNL look better?
5. Use `band_bins` to test an oversampled converter: quantise a 10 Hz tone at 16 kS/s with 12 bits and compute the SNDR in a 125 Hz band. Compare with `biosig.sqnr_os_db()`.

**Deliverable.** `adctest.py` with your own converter model plugged in, and a table of SNDR, SFDR, ENOB, DNL and INL for the ideal, 0.2 % and 1 % cases.

[All labs]({% link labs.md %}) · Previous: [Lab 5. Chopper amplifier]({% link labs/lab05_chopper.md %}) · Next: [Lab 7. StrongARM comparator]({% link labs/lab07_comparator.md %})
