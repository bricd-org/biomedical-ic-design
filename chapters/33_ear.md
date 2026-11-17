---
title: 33. Ear-EEG and Multimodal Sensing at the Ear
parent: "Part VI · Wearable Systems"
nav_order: 33
permalink: /part-6/ch33/
chapter: 33
---

# <span class="chapnum">Chapter 33</span>Ear-EEG and Multimodal Sensing at the Ear

The ear holds an earpiece steady, sits a few centimetres from the temporal lobe, and is a place people already wear technology all day.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain what ear-EEG records, and why its signals are smaller than scalp EEG;
- choose electrode sites and references in and around the ear;
- budget the noise of an ear-EEG channel, and see why the contact matters more than the amplifier;
- add photoplethysmography, pulse oximetry, temperature and motion at the ear;
- partition an ear-worn system between the earpiece, the rest of the device and a phone, on one clock.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What input noise, electrode contact and electrode placement does an ear-worn front-end need to record EEG that is worth recording?

</div>

Clinical EEG uses a cap of electrodes spread over the scalp, held with gel, applied by a technician, and worn for an hour. That suits a hospital, not daily life. **Ear-EEG** places the electrodes in and around the ear, where an earpiece holds them in place without a cap {% include cite.html keys="looney2012" %}. It cannot see the whole brain, but it records the activity that reaches the temporal regions well: sleep rhythms, alpha, auditory responses and, for some patients, seizures {% include cite.html keys="mikkelsen2015,kidmose2013" %}. The same earpiece can also measure the pulse, blood oxygen, temperature and head motion. This chapter is about what that means for the front-end of Parts II and III.

## <span class="secnum">33.1</span>What the ear can record

EEG potentials are the far field of synchronised cortical currents ([Chapter 2]({% link chapters/02_signals.md %})). What a pair of electrodes records depends on how much of that field lies between them: two electrodes close together, both in one ear, see only a small part of it. Ear-EEG measured *within* one ear therefore has amplitudes several times smaller than scalp EEG between distant electrodes, while measurements *between* the two ears, or between the ear and the mastoid or the side of the head, are larger {% include cite.html keys="mikkelsen2015" %}. Studies comparing ear-EEG with nearby scalp electrodes find that it follows the temporal scalp channels closely, that auditory evoked responses are recorded with useful signal-to-noise ratio, and that sleep stages can be scored from it {% include cite.html keys="kidmose2013,mikkelsen2015" %}. Electrodes printed on a flexible sheet *around* the ear extend the same idea to larger distances {% include cite.html keys="debener2015" %}.

## <span class="secnum">33.2</span>Electrode sites and references

An earpiece offers a handful of sites: the **ear canal**, the bowl of the outer ear (the **concha** and the smaller **cymba** above it), the skin **behind the ear** and over the **mastoid** bone. Their trade-offs:

- **Canal electrodes** sit closest to the temporal lobe and are held firmly by the earpiece, but the canal is small, moist, and its shape differs between people; the earpiece must be sized or shaped to each ear for a stable contact.
- **Concha and cymba electrodes** have more area and less variation, and they add distance from the canal electrodes.
- **Behind-the-ear and mastoid sites** give the longest distances within one side of the head and a convenient place for the right-leg-drive or reference electrode ([Chapter 12]({% link chapters/12_cmcontrol.md %})).

The **reference** shapes what is recorded. A reference in the same ear makes every channel a short, low-amplitude bipolar pair. A reference in the other ear, or on the far mastoid, gives much larger signals, at the cost of a wire, or a radio and a shared clock, between the two sides of the head. Recording each electrode against a common reference and forming the pairs digitally keeps every option open.

## <span class="secnum">33.3</span>Dry contacts and the noise budget

Gel and an ear are a poor combination for daily use, so ear-EEG is usually recorded with **dry** electrodes: sintered Ag/AgCl, metals coated with iridium oxide or similar, or conductive polymers, shaped to the ear {% include cite.html keys="kappel2019" %}. Their impedance is higher and less stable than a gel electrode's, which brings back every concern of [Chapter 3]({% link chapters/03_electrodes.md %}) and [Chapter 10]({% link chapters/10_dsl.md %}): input impedance, offset range, the noise of the contact itself and its motion artefacts ([Chapter 32]({% link chapters/32_quality.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 33.1 · An ear-EEG noise budget</div>

Start from the channel budget of [Chapter 29]({% link chapters/29_arch.md %}), all referred to the input over 0.5–100 Hz: electrodes 0.34 µVrms (wet) or 1.20 µVrms (dry), chopped LNA 0.36 µVrms, input resistors 0.13 µVrms, the rest 0.05 µVrms. The total is 0.51 µVrms wet and 1.26 µVrms dry ([Figure 33.1](#fig-33-1)a). For ear-EEG, whose rhythms are a few microvolts, aim for about 0.5 µVrms. Narrowing the band to the 1–40 Hz that sleep and alpha need scales each white term by $$\sqrt{39/99.5} = 0.63$$: 0.32 µVrms wet, 0.79 µVrms dry. With wet contacts the amplifier and the electrodes share the budget; with dry contacts the electrodes take 90 % of the noise power, and no amount of LNA current reaches 0.5 µVrms. The contact, not the chip, decides.

</div>

<figure id="fig-33-1">
  <img src="{{ '/assets/figs/ch33_ear.svg' | relative_url }}" style="width:720px" alt="Stacked noise power of an ear-EEG channel for wet and dry electrodes over 0.5 to 100 Hz and 1 to 40 Hz, against 0.5 microvolts rms; and SpO2 against the ratio of ratios, falling from about 100 percent at R = 0.4 to 70 percent at R = 1.6">
  <figcaption><span class="capnum">Figure 33.1.</span> <strong>At the ear, the contact sets the noise; the pulse oximeter is a ratio.</strong> (a) Input-referred noise power of one channel, from the Chapter 29 budget, for wet and dry electrodes over the full EEG band and over 1–40 Hz, against the 0.5 µVrms an ear-EEG channel should aim for. (b) The empirical calibration of pulse oximetry, SpO<sub>2</sub> ≈ 110 − 25 R, where R is the ratio of the red and infrared pulse amplitudes, each divided by its steady level; each oximeter is calibrated on its own. From <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

The demo below puts the budget and the referencing together for alpha, the rhythm most ear-EEG studies start with. It starts with dry contacts in one ear and the alpha band alone; try wet gel, a reference behind the ear, and the full EEG band.

{::nomarkdown}
{% include demos/eareeg.html %}
{:/}

## <span class="secnum">33.4</span>More than EEG at the ear

An earpiece reaches more than the brain {% include cite.html keys="allen2007" %}.

- **Photoplethysmography (PPG).** An LED shines into well-perfused skin and a photodiode measures the light that comes back; each heartbeat changes the blood volume and so the signal by a fraction of a per cent. The ear canal and the concha are well perfused and less affected by cold than a finger. PPG gives the heart rate and its variability ([Chapter 24]({% link chapters/24_ecg.md %})) without an ECG electrode.
- **Pulse oximetry.** With two wavelengths, red and infrared, the ratio of ratios $$R = (\mathrm{AC}/\mathrm{DC})_\mathrm{red} / (\mathrm{AC}/\mathrm{DC})_\mathrm{IR}$$ maps to the blood's oxygen saturation through an empirical calibration ([Figure 33.1](#fig-33-1)b). The front-end is a transimpedance amplifier and a converter for the photodiode, and pulsed LED drivers whose current, not the amplifier, dominates the power.
- **Temperature**, from a thermistor or an infrared sensor looking into the canal.
- **Motion**, from an accelerometer and gyroscope: activity, head position, and the reference signals for artefact cancellation of [Chapter 32]({% link chapters/32_quality.md %}). Jaw movement and speech also reach the ear, as artefacts in the EEG and as signals in their own right.
- **An ECG lead**, between electrodes on the two sides of the head or neck: far smaller than a chest lead, but enough for the R peak.

Each modality brings its own front-end, and the EEG's microvolts must coexist with LED current pulses of tens of milliamperes a few millimetres away: separate supplies and grounds, and LED pulses timed away from the EEG's sampling instants, keep the two apart.

## <span class="secnum">33.5</span>Partitioning an ear-worn system

The physics suggests a partition. **Digitise at the ear**: the microvolt signals travel millimetres, not along a cable, and only digital lines leave the earpiece; the front-end chip of this tutorial, at microwatts per channel, is small and cool enough to sit there. **Compute and transmit away from the ear**, in a part of the device with room for a battery and an antenna, or on a phone; [Chapter 27]({% link chapters/27_soc.md %}) sizes the radio link. **Clock everything from one source**: EEG, impedance, PPG, motion and any sound the device plays must share one time base, or the artefact references of [Chapter 32]({% link chapters/32_quality.md %}) and the closed loops of [Chapter 34]({% link chapters/34_closedloop.md %}) fall apart. Two earpieces need either a wire that carries the clock or a radio protocol with common anchor points.

The power budget is set by what draws current continuously. A low-power EEG front-end costs microwatts to a few milliwatts depending on the chip; PPG LEDs cost hundreds of microwatts to milliwatts, depending on how often they flash; a BLE link costs tenths of a milliwatt to milliwatts depending on what it carries. Features computed on the device, short LED pulses and long radio intervals are the levers.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Ear-EEG needs about a third of the input noise that scalp EEG needs, and with dry contacts the electrodes, not the amplifier, set it: invest in the contact, its area and its fit, and narrow the band to what the application uses. Record against a common reference and form pairs digitally, digitise in the earpiece, and run every sensor from one clock.

</div>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common pitfall</div>

Comparing ear-EEG with scalp EEG by amplitude alone. Short within-ear pairs record smaller signals by geometry, not because the electrodes are poor; judge an ear-EEG system by its signal-to-noise ratio for a defined task (an alpha band, an evoked response, sleep stages), with the same references and bands on both sides of the comparison.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it in Python</div>

Change the electrode noise in `figsrc/ch33_figs.py` to model a better dry contact, and find the electrode noise at which the 1–40 Hz budget reaches 0.5 µVrms. Then use `biosig.eeg()` with its alpha amplitude scaled down by four to stand for a within-ear pair, and see how much of it survives that noise.

</div>

**Read with this chapter.** Looney et al. {% include cite.html keys="looney2012" %}, Mikkelsen et al. {% include cite.html keys="mikkelsen2015" %}, Kidmose et al. {% include cite.html keys="kidmose2013" %}, Kappel et al. {% include cite.html keys="kappel2019" %}, Debener et al. {% include cite.html keys="debener2015" %}, Allen {% include cite.html keys="allen2007" %}.

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Ear-EEG follows the temporal scalp channels; within one ear its amplitudes are several times smaller, and references in the other ear or behind it give larger signals.
- Sites: canal, concha and cymba, behind the ear and mastoid; record against a common reference and form pairs digitally.
- Over 1–40 Hz the channel noise is 0.32 µVrms with wet contacts and 0.79 µVrms with dry ones: with dry contacts the electrodes dominate.
- The ear also gives PPG, SpO<sub>2</sub> (a ratio of ratios, calibrated empirically), temperature, motion and an ECG lead.
- Digitise at the ear, compute and transmit away from it, and clock every sensor from one source.

</div>
