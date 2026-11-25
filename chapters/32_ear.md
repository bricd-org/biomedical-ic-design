---
title: 32. Ear-EEG and Multimodal Sensing at the Ear
parent: "Part VI · Wearable Systems"
nav_order: 32
permalink: /part-6/ch32/
chapter: 32
---

# <span class="chapnum">Chapter 32</span>Ear-EEG and Multimodal Sensing at the Ear

The ear holds an earpiece steady, sits a few centimetres from the temporal lobe, and is a place people already wear technology all day.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain what ear-EEG records, and why its signals are smaller than scalp EEG;
- choose electrode sites and references in and around the ear;
- budget the noise of an ear-EEG channel, and see why the contact matters more than the amplifier;
- work out the input impedance and common-mode rejection that dry ear contacts demand, and what an impedance tone above the band can see of them;
- add photoplethysmography, pulse oximetry, temperature and motion at the ear, and estimate SpO<sub>2</sub> from the ratio of ratios;
- budget the data and power of an ear-worn system, and partition it between the earpiece, the rest of the device and a phone, on one clock.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What input noise, electrode contact and electrode placement does an ear-worn front-end need to record EEG that is worth recording, and what does the rest of the earpiece cost around it?

</div>

Clinical EEG uses a cap of electrodes spread over the scalp, held with gel, applied by a technician, and worn for an hour. That suits a hospital, not daily life. **Ear-EEG** places the electrodes in and around the ear, where an earpiece holds them in place without a cap {% include cite.html keys="looney2012" %}. It cannot see the whole brain, but it records the activity that reaches the temporal regions well: sleep rhythms, alpha, auditory responses and, for some patients, seizures {% include cite.html keys="mikkelsen2015,kidmose2013" %}. The same earpiece can also measure the pulse, blood oxygen, temperature and head motion. This chapter is about what that means for the front-end of Parts II and III, and for the earpiece around it.

## <span class="secnum">32.1</span>What the ear can record

EEG potentials are the far field of synchronised cortical currents ([Chapter 2]({% link chapters/02_signals.md %})). What a pair of electrodes records depends on how much of that field lies between them: two electrodes close together, both in one ear, see only a small part of it. Ear-EEG measured *within* one ear therefore has amplitudes several times smaller than scalp EEG between distant electrodes, while measurements *between* the two ears, or between the ear and the mastoid or the side of the head, are larger {% include cite.html keys="mikkelsen2015" %}. Studies comparing ear-EEG with nearby scalp electrodes find that it follows the temporal scalp channels closely, that auditory evoked responses are recorded with useful signal-to-noise ratio, and that sleep stages can be scored from it {% include cite.html keys="kidmose2013,mikkelsen2015" %}. Electrodes printed on a flexible sheet *around* the ear extend the same idea to larger distances {% include cite.html keys="debener2015" %}.

## <span class="secnum">32.2</span>Electrode sites and references

An earpiece offers a handful of sites: the **ear canal**, the bowl of the outer ear (the **concha** and the smaller **cymba** above it), the skin **behind the ear** and over the **mastoid** bone. Their trade-offs:

- **Canal electrodes** sit closest to the temporal lobe and are held firmly by the earpiece, but the canal is small, moist, and its shape differs between people; the earpiece must be sized or shaped to each ear for a stable contact.
- **Concha and cymba electrodes** have more area and less variation, and they add distance from the canal electrodes.
- **Behind-the-ear and mastoid sites** give the longest distances within one side of the head and a convenient place for the right-leg-drive or reference electrode ([Chapter 12]({% link chapters/12_cmcontrol.md %})).

The **reference** shapes what is recorded. A reference in the same ear makes every channel a short, low-amplitude bipolar pair. A reference in the other ear, or on the far mastoid, gives much larger signals, at the cost of a wire, or a radio and a shared clock, between the two sides of the head. Recording each electrode against a common reference and forming the pairs digitally keeps every option open.

## <span class="secnum">32.3</span>Dry contacts and the noise budget

Gel and an ear are a poor combination for daily use, so ear-EEG is usually recorded with **dry** electrodes: sintered Ag/AgCl, metals coated with iridium oxide or similar, or conductive polymers, shaped to the ear {% include cite.html keys="kappel2019" %}. Their impedance is higher and less stable than a gel electrode's, which brings back every concern of [Chapter 3]({% link chapters/03_electrodes.md %}) and [Chapter 10]({% link chapters/10_dsl.md %}): input impedance, offset range, the noise of the contact itself and its motion artefacts ([Chapter 31]({% link chapters/31_quality.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.1 · An ear-EEG noise budget</div>

Start from the channel budget of [Chapter 29]({% link chapters/29_arch.md %}), all referred to the input over 0.5–100 Hz: electrodes 0.34 µVrms (wet) or 1.20 µVrms (dry), chopped LNA 0.36 µVrms, input resistors 0.13 µVrms, the rest 0.05 µVrms. The total is 0.51 µVrms wet and 1.26 µVrms dry ([Figure 32.1](#fig-32-1)a). For ear-EEG, whose rhythms are a few microvolts, aim for about 0.5 µVrms. Narrowing the band to the 1–40 Hz that sleep and alpha need scales each white term by $$\sqrt{39/99.5} = 0.63$$: 0.32 µVrms wet, 0.79 µVrms dry. With wet contacts the amplifier and the electrodes share the budget; with dry contacts the electrodes take 90 % of the noise power, and no amount of LNA current reaches 0.5 µVrms. The contact, not the chip, decides.

</div>

<figure id="fig-32-1">
  <img src="{{ '/assets/figs/ch32_ear.svg' | relative_url }}" style="width:720px" alt="Stacked noise power of an ear-EEG channel for wet and dry electrodes over 0.5 to 100 Hz and 1 to 40 Hz, against 0.5 microvolts rms; and SpO2 against the ratio of ratios, falling from about 100 percent at R = 0.4 to 70 percent at R = 1.6">
  <figcaption><span class="capnum">Figure 32.1.</span> <strong>At the ear, the contact sets the noise; the pulse oximeter is a ratio.</strong> (a) Input-referred noise power of one channel, from the Chapter 29 budget, for wet and dry electrodes over the full EEG band and over 1–40 Hz, against the 0.5 µVrms an ear-EEG channel should aim for. (b) The empirical calibration of pulse oximetry, SpO<sub>2</sub> ≈ 110 − 25 R, where R is the ratio of the red and infrared pulse amplitudes, each divided by its steady level; each oximeter is calibrated on its own. From <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

The demo below puts the budget and the referencing together for alpha, the rhythm most ear-EEG studies start with. It starts with dry contacts in one ear and the alpha band alone; try wet gel, a reference behind the ear, and the full EEG band.

{::nomarkdown}
{% include demos/eareeg.html %}
{:/}

## <span class="secnum">32.4</span>What dry contacts ask of the input

The electrodes are also the source impedances of the input divider of [Chapter 3]({% link chapters/03_electrodes.md %}) and of the common-mode conversion of [Chapter 4]({% link chapters/04_interference.md %}), and at the ear all of them are dry, the right-leg-drive contact included. Chapter 4's amplifier tied to earth is the worst case: an earpiece on its own battery floats with the body and sees less, but not while it charges.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.2 · What a dry ear contact asks of the input</div>

Take two contacts of Chapter 3's dry model, one with half the area of the other and so twice its impedance (964 kΩ and 1.93 MΩ at 10 Hz, 564 kΩ and 1.13 MΩ at 50 Hz), and a right-leg-drive contact like the first.

- **The divider.** The chopped input's 6.25 MΩ ([Chapter 10]({% link chapters/10_dsl.md %})) takes 13 % and 23 % of the signal at 10 Hz, leaving gains of 0.87 and 0.77 within one pair; the boosted 200 MΩ takes 0.46 % and 0.92 %.
- **The common mode.** The 0.217 µA of mains displacement current leaves the body through 564 kΩ instead of the 41.5 kΩ of Worked Example 4.1: 122 mVrms, and 1.21 mVrms after the right-leg drive of [Chapter 12]({% link chapters/12_cmcontrol.md %}) with its loop gain of 100. The loop is unharmed: at its 5 kHz crossover the dry contact is only 8.4 kΩ, and the phase margin is 54°.
- **The conversion.** The imbalance, 564 kΩ, is 13.8 times the standards' 40.7 kΩ; against 200 MΩ it allows an effective CMRR of only 51 dB. Chapter 12's key equation leaves 3.4 µVrms of 50 Hz on the signal, 180 times the wet case and nearly seven times the 0.5 µVrms target ([Figure 32.2](#fig-32-2)a). Without the right-leg drive it would be 345 µVrms, 0.49 mV peak, close to the ±0.625 mV range of EEG mode ([Chapter 25]({% link chapters/25_eeg.md %})).
- **What it would take.** 0.5 µVrms needs 1.40 GΩ of common-mode input impedance, 2.3 pF at 50 Hz; 5 pF of pads alone allow 637 MΩ.

The contact impedance enters twice, setting the common mode and converting it, so contacts twice as poor bring four times the mains. The input impedance cannot win at the ear, so make the mains harmless instead: keep the right-leg drive on, use a band that leaves 50 and 60 Hz outside, as 1–40 Hz does, and read the 50 Hz level as a free measure of the imbalance ([Chapter 31]({% link chapters/31_quality.md %})).

</div>

<figure id="fig-32-2">
  <img src="{{ '/assets/figs/ch32_system.svg' | relative_url }}" style="width:720px" alt="50 Hz interference on the signal against common-mode input impedance for wet contacts with the standards' imbalance and for dry ear contacts, 3.4 microvolts against 0.019 microvolts at 200 megaohms; and stacked average power of an earpiece for three configurations: 583, 282 and 74 microwatts">
  <figcaption><span class="capnum">Figure 32.2.</span> <strong>At the ear the contacts set the mains, and the light and the radio set the power.</strong> (a) 50 Hz on the signal against the common-mode input impedance, with Chapter 12's right-leg drive and 100 dB of intrinsic CMRR, for wet contacts with the standards' 40.7 kΩ imbalance and for the dry ear contacts of Worked Example 32.2; dotted, the boosted input and the limit of 5 pF of pads; dashed, the 0.5 µVrms ear-EEG target. (b) Average power of the earpiece of Worked Example 32.4 in three configurations: front-end, PPG LEDs, and the radio's bits and connection events; the accelerometer and the radio's processor are left out. From <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

**Watching the contact.** The impedance channel tracks each contact with a 51.2 kHz tone and I/Q demodulation ([Chapter 28]({% link chapters/28_bioz.md %})), far above the dry model's 34 Hz corner. There the model reads 5.04 kΩ at −7.5°: the 5 kΩ series resistance in phase, and the interface only through its capacitance, −661 Ω in quadrature. Its 1 MΩ resistance $$R_\mathrm{p}$$, which makes the noise and most of the mains conversion, is invisible to the tone. So track the quadrature output, which follows $$C_\mathrm{p}$$ and so the contact's area: while $$R_\mathrm{p}C_\mathrm{p}$$ stays at the model's 4.7 ms, 848 times it is the interface's impedance at 50 Hz. Calibrate the reference phase against the on-chip resistor, since 1° of error rotates 87 Ω of the in-phase part into the quadrature, 13 % of it. And catch a resistance that rises on its own, as a contact dries, below the corner: in the 50 Hz level and in a DC lead-off check ([Chapter 12]({% link chapters/12_cmcontrol.md %}#lead-off-detection)).

## <span class="secnum">32.5</span>More than EEG at the ear

An earpiece reaches more than the brain {% include cite.html keys="allen2007" %}.

- **Photoplethysmography (PPG).** An LED shines into well-perfused skin and a photodiode measures the light that comes back; each heartbeat changes the blood volume and so the signal by a fraction of a per cent. The ear canal and the concha are well perfused, and the canal, close to the body's core, keeps its pulse when cold constricts a finger's vessels {% include cite.html keys="budidha2014" %}. PPG gives the heart rate and its variability ([Chapter 24]({% link chapters/24_ecg.md %})) without an ECG electrode.
- **Pulse oximetry.** With two wavelengths, red and infrared, the ratio of ratios maps to the blood's oxygen saturation through an empirical calibration (the key equation below, [Figure 32.1](#fig-32-1)b). The front-end is a transimpedance amplifier and a converter for the photodiode, and pulsed LED drivers whose current, not the amplifier, dominates the power.
- **Temperature**, from a thermistor or an infrared sensor looking into the canal.
- **Motion**, from an accelerometer and gyroscope: activity, head position, and the reference signals for artefact cancellation of [Chapter 31]({% link chapters/31_quality.md %}). Jaw movement and speech also reach the ear, as artefacts in the EEG and as signals in their own right.
- **An ECG lead**, between electrodes on the two sides of the head or neck: far smaller than a chest lead, but enough for the R peak.

Each modality brings its own front-end, and the EEG's microvolts must coexist with LED current pulses of ten milliamperes or more a few millimetres away: separate supplies and grounds, and LED pulses timed away from the EEG's sampling instants, keep the two apart.

Oxygenated and deoxygenated haemoglobin absorb red and infrared light differently, so the pulsing part of each wavelength, divided by its own steady level, carries the saturation {% include cite.html keys="mendelson1992" %}. The division cancels the LED's brightness, the photodiode's responsivity and the gain, so only the empirical curve remains to calibrate. The light, not the electronics, sets the power:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Ratio of ratios and the power of the light</div>

$$
R = \frac{(\mathrm{AC}/\mathrm{DC})_\mathrm{red}}{(\mathrm{AC}/\mathrm{DC})_\mathrm{IR}}, \qquad \mathrm{SpO_2} \approx 110 - 25R, \qquad P_\mathrm{LED} = N_\lambda\, I_\mathrm{LED}\, V_\mathrm{LED}\, t_\mathrm{p}\, f_\mathrm{s}
$$

</div>

AC is the pulse amplitude and DC the steady level at each wavelength. The line is a typical calibration; each design is calibrated on its own, against arterial blood samples. $$N_\lambda$$ LEDs pulsed at $$I_\mathrm{LED}$$ for $$t_\mathrm{p}$$, $$f_\mathrm{s}$$ times a second, draw $$P_\mathrm{LED}$$ from their supply $$V_\mathrm{LED}$$; the driver burns whatever the LED does not drop.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.3 · SpO<sub>2</sub> from a ratio of ratios, and what the light costs</div>

Take, as an illustration, an infrared pulse of 1.0 % of its steady level and a red one of 0.5 %: $$R = 0.5$$, SpO<sub>2</sub> ≈ 97.5 %.

- **Resolution.** At 25 points per unit of $$R$$, ±1 point needs $$R$$ to ±0.04: 8 % of $$R$$ at 97.5 %, 4 % at 85 % ($$R = 1$$). Split between the wavelengths, the red pulse must be known to $$2.8\times10^{-4}$$ of its steady level, 71 dB below it, at any saturation. A 12-bit converter with that level at half scale quantises to $$1.4\times10^{-4}$$ per sample, and to $$1.0\times10^{-5}$$ over a 4 s window at 100 S/s: the bits are not the limit.
- **What the ratio cannot cancel**: anything that adds to a steady level without pulsing. Ambient light adds the same photocurrent at both wavelengths. If the red level is half the infrared and the ambient adds 10 % to it, and so 5 % to the infrared, $$R$$ reads 4.5 % low and 85 % reads 86.1 %: high, the wrong way for an alarm. Subtract an LED-off sample, through the same chain, next to every LED sample.
- **The light.** Two LEDs pulsed at 10 mA for 50 µs, 100 times a second each, from 3.3 V (assumed values), draw 330 µW, six times the 54 µW of all eight EEG channels: one flash takes 1.65 µJ, 121 times the 13.6 nJ of one EEG sample of one channel at 6.8 µW and 500 S/s. At 25 S/s and 25 µs they draw 41 µW, still enough for the heart rate and the saturation; beat-to-beat intervals then need the peak interpolation of [Chapter 24]({% link chapters/24_ecg.md %}), and the shorter pulse collects half the charge, 3 dB of signal-to-noise ratio if the receiver's noise is white.

Spend the design effort on the LED duty cycle and on keeping light that does not pulse away from the photodiode.

</div>

## <span class="secnum">32.6</span>Partitioning an ear-worn system

The physics suggests a partition. **Digitise at the ear**: the microvolt signals travel millimetres, not along a cable, and only digital lines leave the earpiece; the front-end chip of this tutorial, at microwatts per channel, is small and cool enough to sit there. **Compute and transmit away from the ear**, in a part of the device with room for a battery and an antenna, or on a phone; [Chapter 27]({% link chapters/27_soc.md %}) sizes the radio link. **Clock everything from one source**: EEG, impedance, PPG, motion and any sound the device plays must share one time base, or the artefact references of [Chapter 31]({% link chapters/31_quality.md %}) and the closed loops of [Chapter 33]({% link chapters/33_closedloop.md %}) fall apart. Two earpieces need either a wire that carries the clock or a radio protocol with common anchor points.

The power budget is set by what draws current continuously, and at the ear that is not the EEG front-end: the LEDs of Worked Example 32.3 draw 41–330 µW, and a BLE link from a few microwatts to a few hundred, depending on what it carries.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.4 · What an earpiece sends, and what it costs</div>

One earpiece records four ear-EEG channels against a common reference, decimated on chip to 250 S/s, PPG at two wavelengths, a three-axis accelerometer at 100 S/s, four contact impedances and a temperature, in 16-bit words. [Chapter 27]({% link chapters/27_soc.md %}) prices the radio: 5 nJ per bit, 10 µJ per connection event, 4 % for framing.

- **Raw.** EEG 16.0 kb/s, PPG at 100 S/s 3.2 kb/s, motion 4.8 kb/s, contact and temperature 0.27 kb/s: 25.2 kb/s, two 244-byte notifications per event at a 100 ms interval. The radio takes 126 µW for the bits and 100 µW for the events.
- **Features.** Six band powers per channel every 2 s as 8-bit log codes ([Chapter 25]({% link chapters/25_eeg.md %}#features-out)), beat times, SpO<sub>2</sub> and perfusion every second, temperature, activity and contact codes, and an 8-byte header per event: 187 b/s, 135 times less. Sent every 2 s, they cost 0.9 µW in bits and 5 µW in events.
- **The whole earpiece** ([Figure 32.2](#fig-32-2)b). Streaming everything with PPG at 100 S/s: 27 µW for the four EEG channels at 6.8 µW each, 330 µW for the LEDs and 226 µW for the radio, 583 µW, which empties the 40 mAh, 3.7 V cell of [Figure 1.2]({% link chapters/01_why.md %}#fig-1-2) in 10.6 days. Streaming with PPG at 25 S/s: 282 µW, 22 days. Features out and PPG at 25 S/s: 74 µW, 83 days. The accelerometer and the radio's processor come on top.

The LEDs and the radio decide the battery, and features turn the radio from the second-largest consumer into the smallest. They also move the artefact cancellation of [Chapter 31]({% link chapters/31_quality.md %}) into the earpiece, because its references no longer leave it. Keep raw data on demand, for the night a clinician will read.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Ear-EEG needs about a third of the input noise that scalp EEG needs, and with dry contacts the electrodes, not the amplifier, set it: invest in the contact, its area and its fit, and narrow the band to what the application uses. Dry contacts also make the mains a contact problem: boost the input impedance, keep the right-leg drive on, keep 50 and 60 Hz outside the band, and track each contact's quadrature impedance with a calibrated phase. Form pairs digitally, digitise in the earpiece, run every sensor from one clock, and budget the light and the radio before the front-end: slower LED pulses and features instead of samples take the example earpiece from 583 µW to 74 µW.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Comparing ear-EEG with scalp EEG by amplitude alone. Short within-ear pairs record smaller signals by geometry, not because the electrodes are poor; judge an ear-EEG system by its signal-to-noise ratio for a defined task (an alpha band, an evoked response, sleep stages), with the same references and bands on both sides of the comparison.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

`python figsrc/ch32_figs.py report` prints every number of Worked Examples 32.1–32.4. Change the electrode noise in `SRC` to model a better dry contact, and find the electrode noise at which the 1–40 Hz budget reaches 0.5 µVrms. Then use `biosig.eeg()` with its alpha amplitude scaled down by four to stand for a within-ear pair, and see how much of it survives that noise. Finally, find the PPG rate in `configs()` at which the LEDs cost as much as the four EEG channels.

</div>

**Read with this chapter.** Looney et al. {% include cite.html keys="looney2012" %}, Mikkelsen et al. {% include cite.html keys="mikkelsen2015" %}, Kidmose et al. {% include cite.html keys="kidmose2013" %}, Kappel et al. {% include cite.html keys="kappel2019" %}, Debener et al. {% include cite.html keys="debener2015" %}, Allen {% include cite.html keys="allen2007" %} (photoplethysmography), Mendelson {% include cite.html keys="mendelson1992" %} (pulse oximetry), Budidha and Kyriacou {% include cite.html keys="budidha2014" %} (the ear canal as a site for oximetry).

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Ear-EEG follows the temporal scalp channels; within one ear its amplitudes are several times smaller, and references in the other ear or behind it give larger signals.
- Sites: canal, concha and cymba, behind the ear and mastoid; record against a common reference and form pairs digitally.
- Over 1–40 Hz the channel noise is 0.32 µVrms with wet contacts and 0.79 µVrms with dry ones: with dry contacts the electrodes dominate.
- Dry contacts set the common mode and convert it: with the right-leg drive and 200 MΩ, 3.4 µVrms of 50 Hz reaches the signal, 180 times the wet case; 0.5 µVrms would need 1.4 GΩ. Keep the mains outside the band.
- A 51.2 kHz tone sees a dry contact's series resistance and capacitance, not the resistance that makes the noise: track the quadrature part, with a calibrated phase.
- SpO<sub>2</sub> ≈ 110 − 25R; ±1 point needs the red pulse to $$2.8\times10^{-4}$$ of its steady level, which the bits easily give; unsubtracted ambient light reads high.
- Two LEDs at 10 mA, 50 µs and 100 S/s draw 330 µW, six times all eight EEG channels; with features and slower light the earpiece needs 74 µW instead of 583 µW.
- Digitise at the ear, compute and transmit away from it, and clock every sensor from one source.

</div>
