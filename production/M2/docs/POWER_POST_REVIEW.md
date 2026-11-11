# Power candidate independent follow-up — 2026-11-09

Scope: M1 prototype, 2S battery6.0–8.4 V, combined5 V load up to2 A. Read-only review; no CAD or rule changes.

## Specific remaining issue: Q2 startup diode rating

DMN3023L DS37248 Rev2-2 page2 rates body-diode source current IS at1.5 A. Its44 A/380 us IDM rating is a MOSFET channel rating and must not be reused as a body-diode pulse rating. Its6.2 A channel rating likewise does not establish a2 A body-diode rating.

LM74700 initially allows current through Q2's body diode until its charge pump is ready. TI SNOSD17G p.7 specifies charge-pump source current162/300/600 uA min/typ/max at the listed12 V test conditions; gate release threshold is5.8/6.6/7.7 V above ANODE. C39=220 nF therefore adds approximately1.45 uC typical charge to that threshold, with an order-of-magnitude millisecond charging period. This is not a guaranteed5 V startup delay: the published current condition is12 V. The later enable-to-gate delay110 us maximum assumes VCAP already above its UV threshold.

Conclusion: DMN3023L is suitable for the2 A enhanced-channel case with thermal verification, but it does not establish unrestricted2 A cold-start operation. Preferred corrective action is an exact pin-compatibleG1/S2/D3 N-MOSFET withVGS>=20 V and documented body-diode continuous current>=2 A, avoiding a newly imposed1.5 A startup restriction. The candidate exact Nexperia part must be checked from its manufacturer PDF before approval. No unverified pulse-current allowance is claimed.

If this MPN were retained for an explicitly restricted engineering prototype, a necessary bench criterion would be<=1.5 A through Q2 until gate enhancement, under cold-start and restart with the intended Pi/audio load; this is not the desired unrestricted2 A board specification.

## Read-only routing observations

The inspected candidate has0.5 mm F.Cu SW routing and a dedicated REG_5V load route to Q2 using1 mm traces and three0.3 mm drill vias. Q2's +5 V load route uses1 mm traces into an approximately1.8 mm inner-layer trunk. The0.25 mm REG_5V branches are controller sense/enable connections rather than the primary2 A load route. No definite new high-current routing bottleneck was identified in this limited post-review. This observation is not a thermal measurement or an independent proof of all filled-zone connections.

## FB1 value correction

The native netlist puts BLM15AG601SN1D between+5 V and PAM8406 pin6VDD with C33/C34 local bypass. The power-stage supplies pin4PVDDL and pin13PVDDR are directly on+5 V and do not pass through FB1. Therefore rating FB1 from speaker power current would be wrong. Correcting the stale1.3 A label to the exact part's0.3 A rating is justified and does not change its electrical behavior.

PAM8406 DS43342 p.4 gives typical total no-load current10 mA inClassD and25 mA inClassAB, not a guaranteed separate VDD-pin maximum. Those typical figures support the topology's plausibility but must not be promoted into a guaranteed VDD current ceiling. No verified evidence of a300 mA DC overload at FB1 was found; there is no demonstrated need to substitute a different ferrite purely because of the label mismatch. The assembled-board analog rail/drop should be observed in the normal startup/audio load test rather than claiming a guaranteed maximum from typicalIq.

## C39 and application envelope

Parent reports exact Murata C39 DC-bias data verified at13 V with144 nF conservative effective capacitance after stated allowances. That exceeds TI's100 nF minimum. This follow-up does not reclassify the original100 nF/16 V0402 as usable; only the specifically qualified220 nF50 V0805 variant is intended.

At2S maximum8.4 V the Eaton4.7 uH inductor's on-state differential voltage is approximately3.4 V (plus switching excursions), comfortably below its20 V reference operating voltage. This M1 assessment does not extend the board's qualified operating input range to the original28 V claim.

## Exact alternative checked: PMV20EN rejected

Nexperia PMV20EN product data sheet5July2018 p.3 specifies body-diode IS maximum1.1 A at25C, even with6cm2 drain copper. Its6A channel current does not solve the2A startup requirement. G1/S2/D3 andVGS+/-20V are compatible, but this exact part must not be selected as a body-diode upgrade. Local source C:/Users/M/Downloads/PMV20EN.pdf.

An alternative architectural fix is a separately rated>=3A Schottky diode acrossQ2, anodeREG_5V/source and cathode+5V/drain, carrying startup current beforeMOSFET enhancement. Its exact MPN/land pattern/thermal data and layout must be qualified. No such diode has been selected or added by this reviewer.

## Final D5 cold-start ECO: SBR3U40P1-7

Final exact part: Diodes SBR3U40P1-7, LCSC C97127, PowerDI123. It replaces the earlier B340A/SMA candidate for available board space. Manufacturer DS31164 Rev12-2 pp1-2 specifies3A average rectified current and40V reverse rating. The specified20% capacitive-load derating gives2.4A, above M1 total2A. It also specifies75A8.3ms half-sine nonrepetitive surge; this is not relabeled as an unrestricted repetitive pulse rating.

D5 native pin1/K is the band-marked cathode on+5V; pin2/A connectsREG_5V. The manufacturer identifies polarity by the cathode band; the KiCad pin numbers1K/2A are the design convention implemented in the corresponding footprint. Cathode band orientation must match that pad in assembly.

Its maximumVF is0.47V at3A/25C. Conservative2A startup loss using that bound is0.94W while D5 conducts. The listedRthetaJA175C/W assumes the manufacturer minimum2oz board, so sustained2A diode-only operation is not qualified for this1oz board. D5 carries only the initial startup interval; Q2 must enhance and bypass it. Check cold-start/restart at6.0 and8.4V under the intended2A total-load condition, observingVGS and voltage acrossQ2 to confirm transition to the low-dropMOSFET channel. Do not infer steady-state thermal approval from the diode3A headline alone.

Reverse direction remains blocked whenPi+5V is externally powered whileREG_5V isoff, subject to leakage. ManufacturerIR is400uA maximum at40V/25C and40mA maximum at40V/125C; the lower actual5V reverse bias is not guaranteed as zero-leakage isolation.

Only nativeD5 value/MPN/LCSC/datasheet/footprint fields were changed for this finalECO. Root runs finalERC/parity and verifies thePowerDI123 copper/polarity. Source file C:/Users/M/Downloads/SBR3U40P1.pdf.
