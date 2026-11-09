# Focused circuit review — 2026-11-09

Reviewed native baseline netlist against manufacturer documents. This document reports electrical reasoning; it does not claim bench testing.

## U10 / Q2: correction required

Original LM5050-1 is specified for IN, OUT and VS >=5 V (TI SNVS629F, pp.4–5). Its VS is fed from nominal +5 V through R8=100 ohm. AP63205's regulated rail has tolerance and MOSFET body-diode startup further reduces downstream voltage. Consequently the original topology does not guarantee U10's operating conditions even though its polarity is correct (Q2 source at regulator output, drain at Pi +5 V).

Recommended replacement: LM74700QDBVRQ1, DBV SOT-23-6. TI SNOSD17G pin table p.3:

| Pin | Signal | Required connection |
|---|---|---|
| 1 | VCAP | Charge-pump capacitor only |
| 2 | GND | Ground |
| 3 | EN | ANODE for always-enabled operation |
| 4 | CATHODE | Pi +5 V, Q2 drain |
| 5 | GATE | Q2 gate |
| 6 | ANODE | Regulator output, Q2 source |

Remove/DNP old R8 VS-feed. Repurpose C39 between VCAP and ANODE, not ground. TI requires effective C_VCAP >=100 nF and recommends >=10*Ciss(Q2). Use a qualified 220 nF/50 V X7R 0805 with bias/tolerance/temperature margin; selection requires checking its actual curve. Original 100 nF/16 V 0402 must not be reused uncritically at a 13 V charge-pump bias.

LM74700 electrical operating minimum is 4 V with POR rising max3.9 V (p.6), appropriate for 5 V minus regulation tolerance. Gate drive can reach13 V and TI explicitly requires MOSFET VGS rating >=15 V (p.17). Original HL3400 +/-12 V gate rating is insufficient. Select a pin-compatible G1/S2/D3 MOSFET with +/-20 V VGS, low RDS(on) and verified 2 A thermal capability, e.g. qualified DMN3023L-7. Its separate pinout review must confirm exact ratings.

Sources:
- https://www.ti.com/lit/gpn/LM5050-1
- https://www.ti.com/lit/gpn/LM74700-Q1

## U9, L4 and output capacitance

Diodes AP63205 fixed5 V/2 A variant is correctly wired with FB directly at pre-ideal-diode regulated output. EN may be tied to VIN. Bootstrap capacitor100 nF is correct. DS41326 Rev3-2, p.13 recommends4.7 uH, two22 uF output capacitors; permissible general inductor range2.2–10 uH, DC current rating >=2.7 A and DCR<100 milliohm. L4 must also have sufficient saturation current.

For4.7 uH, VIN=28 V, VOUT=5 V, f=1.1 MHz, ripple=0.794 A and peak at2 A load=2.397 A. Including -20% inductance and -6% frequency gives ripple1.056 A, peak2.528 A. Select Isat>=3 A, Irms>=2.7 A and DCR<100 milliohm; check heating with actual copper and enclosure. An original label of2 A alone does not meet the recommended margin. Lower input voltage reduces ripple; these calculations preserve the original high-input envelope.

DS41326 p.14 states22–68 uF ceramic sufficient for most applications, with low ESR and load-transient sizing; it is not an absolute allowed nominal-capacitance range. Account for MLCC DC bias.

Do not select GRM31CR61C226KE15L merely for its larger1206 case: Murata marks it to-be-discontinued and its published5 V DC-bias curve is around -44%, leaving about24.6 uF total typical for two22 uF devices, before tolerance and temperature.

Preferred C21/C22 candidate: two GRM31CR61C476ME44L,47 uF/16 V/X5R/1206, +/-20%. Murata lists this as the recommended alternative to NRND1210 GRM32ER61C476KE15L. Its exact published DC-bias curve at5 V is around -48%, giving about49 uF total typical. Multiplying by0.8 initial tolerance and0.85 X5R temperature factor gives approximately33 uF, retaining margin above22 uF. This is an engineering estimate from typical curves, not a guaranteed capacitance at all combined conditions; bench load-transient verification remains required. At zero bias its94 uF nominal charges during regulator soft-start;5 V/4 ms implies approximately118 mA average capacitive startup current, comfortably below2 A before load contribution. Layout must accommodate the larger footprints and preserve short output/ground loops.

Sources:
- https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf
- https://pim.murata.com/en-global/pim/details/?productCategoryId=&partNum=GRM31CR61C476ME44%23
- Exact curve PDF downloaded via manufacturer's visible Electrical Characteristics Data link: `C:/Users/M/Downloads/GRM31CR61C476ME44#_EC-data.pdf`.

## U12 IMU pin compatibility

LSM6DSV16X DS13510 Rev4 pp.9–11 confirms the native LSM6DSM-symbol pin map is electrically compatible for the selected Mode1 I2C wiring:1SA0,2SDx,3SCx,4INT1,5VDD_IO,6/7GND,8VDD,9INT2,10OCS_Aux,11SDO_Aux,12CS,13SCL,14SDA. Grounding2/3 is permitted when analog hub/Qvar disabled;10/11 may be unconnected but soldered to isolated lands;CS high enables I2C.100 nF at each supply is recommended. Update the incorrect native datasheet link and symbol naming so future reviews do not infer the old device's register map. Firmware must support the exact LSM6DSV16X, whose WHO_AM_I is0x70; physical pin compatibility does not establish software compatibility.

Source: https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf

## Scope boundary

This review does not validate all input transient conditions, total Pi/audio loads, independent physical copper connectivity, thermals or finished-product EMC. No PCB geometry or schematic was changed by this reviewer.
