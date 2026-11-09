# Exact-part pinout review — 2026-11-09

Read-only review of the original native netlist and current embedded footprints. No CAD was changed by this review. Manufacturer-authored PDFs were obtained through the LCSC product page's visible Download control in the Codex side browser. LCSC EasyEDA images were used only as secondary corroboration.

| Ref | Exact part / source | Native connection check | Result |
|---|---|---|---|
| U8 | GATEMODE GM3088ENA; https://www.lcsc.com/datasheet/C49423279.pdf | 1 RO, 2 /RE, 3 DE, 4 DI, 5 GND, 6 A, 7 B, 8 VCC match manufacturer page 2. VCC is +3V3, within 3.0–5.5 V operating range. DFN8 3x3, 0.65 mm pitch matches. | Pins 1–8 match. Native symbol description and datasheet link still refer to SP3485/SOIC and should be corrected. See EP detail below. |
| MK1 | LinkMems LMA2718T421-OA5-2; https://www.lcsc.com/datasheet/C7587901.pdf | Manufacturer page 5: 1 OUT to C10/audio input, 2/3 GND, 4 VDD to +3V3. Supply 1.6–3.6 V. Package 2.75x1.85x0.9 mm, top acoustic port. | Electrical pin map matches. Native 0.6x0.6 mm pads at (+/-0.53,+/-0.99) surround the manufacturer's 0.56x0.54 mm terminals; terminal centers are about +/-0.505,+/-0.965. Footprint provides overlap at nominal dimensions. No PCB acoustic hole is required for this top-port device. |
| U3 | UMW XC6206P182MR; https://www.lcsc.com/datasheet/C347373.pdf | Manufacturer page 1 SOT23: 1 GND, 2 OUT, 3 IN. Native: 1 GND, 2 +1V8, 3 +3V3. Page 2 coding P18=1.8 V, 2=2.5% accuracy, M=SOT23. | Pinout, voltage and package match. M1 now uses an exact local UMW symbol and UMW datasheet, replacing the original Torex link. |
| Q2 | R+O HL3400; https://www.lcsc.com/datasheet/C22469448.pdf | Manufacturer page 1: G1/S2/D3. Native: 1 LM5050 gate, 2 local regulator output, 3 Pi +5V. SOT23 package matches the native TSOT23 land pattern. | Pin mapping and body-diode orientation match intended ideal-diode direction. Native depletion-mode symbol name/description is incorrect: HL3400 is enhancement mode. VGS absolute maximum is +/-12 V: LM5050 gate-clamp compatibility must be checked separately before approving this MPN. |
| J4 | Liansheng FH-00339; https://www.lcsc.com/datasheet/C2685112.pdf | Drawing: 2x20 female, row/pin pitch 2.54 mm, terminal outer span 7.6 mm, lands width1.02mm, 2 mm length. Native pads have 2.54 mm longitudinal pitch, center rows +/-2.8 mm and width1.02/length2 mm, yielding 7.6 mm overall. Native locating holes diameter2 mm separated45.72 mm (=2.54*20-5.08). | Mating geometry matches. Native Pi net assignment matches conventional 40-pin mapping for supply, ground and assigned buses. The contact is SMT female, not the stale Toby THD-20-R field text. Datasheet peak processing is 260 C for10seconds, so assembler must respect the connector limit. |

## U8 exposed pad: what is and is not established

The manufacturer package drawing (page16) gives exposed metal dimensions D1=1.40–1.60 mm (1.50 nominal), E1=2.20–2.40 mm (2.30 nominal). The native footprint has a pad numbered9 at center, sized1.20x2.15 mm and an unnumbered paste-only center aperture0.97x1.73 mm. The original SP3485CN symbol has only eight pins, so EP9 is not represented in schematic connectivity.

The obtained manufacturer datasheet provides **no electrical EP pin-function statement and no explicit requirement to tie EP to GND**. Its page2 pin table lists1–8 only. Therefore this review does not invent a requirement or certify that an arbitrary GND tie is safe. LCSC's secondary EasyEDA symbol labels a ninth EP pad, but also does not establish its electrical function. A documented decision about EP (or an alternate exact MPN with a specified EP policy) is needed for a complete exact-part symbol.

The reduced native EP land is not automatically a short-circuit defect; the neighboring lead geometry remains clear. However the difference from package metal dimensions should be visible in the assembly review, rather than silently treating it as the generic SP3485 footprint.

## Assembly constraints that must reach the supplier

- MK1 manufacturer page6: no washing/cleaning after reflow, no ultrasonic processing, no vacuum over acoustic port. Recommended peak <=260 C for <=30seconds.
- J4 peak processing <=260 C for10seconds; follow the stricter connector limit rather than the microphone's30seconds.
- Correct manufacturer-specific datasheet links and stale symbolic descriptions for U8/U3/Q2/J4 in the release BOM and native schema.

## Q2 replacement qualified against the new U10 choice

The circuit reviewer selected TI LM74700QDBVRQ1; its maximum gate boost is13V and its FET selection guidance requires at least15V VGS capability. Therefore the original HL3400 (+/-12V absolute maximum) is not suitable for that controller.

Diodes **DMN3023L-7** is a pin-compatible enhancement-mode N-channel SOT23 part (G1/S2/D3). Official DS37248 Rev2-2 pages1–2 specify VDS30V, VGS+/-20V, RDS(on)max25mohm at VGS10V and28mohm at4.5V. Total gate charge is18.4nC at10V. It provides7V of gate absolute-maximum headroom above the controller's13V maximum boost.

At2A, I-squared-R conduction loss is0.112W using28mohm at25C. The datasheet's144C/W minimum-layout thermal resistance would imply approximately16C rise before temperature-dependent resistance, but that reference uses2oz copper. This is an estimate, not a guaranteed thermal result for the target1oz board; final hardware load testing remains required.

- Official source: https://www.diodes.com/datasheet/download/DMN3023L.pdf
- Manufacturer product page: https://www.diodes.com/part/view/DMN3023L
- Local copy: `C:/Users/M/Downloads/DMN3023L.pdf`

## Pi header orientation and underside clearance

The native J4 is on B.Cu at-90degrees. Board coordinates: pin1=(79.7675,60.84) +3V3; pin2=(79.7675,55.24) +5V; pin39=(128.0275,60.84) GND; pin40=(128.0275,55.24) GPIO21. Numbering follows the required Pi supply/ground/bus map. The footprint's locating-hole separation45.72mm and2mm holes match the drawing; its extra40 NPTH holes permit mating header pins to extend through the HAT.

The connector drawing gives a body height3.50+/-0.15mm and a section dimension3.90+/-0.25mm. Do not treat the LCSC nominal3.9mm listing as a complete board-to-board clearance guarantee: mating Pi male-header body height, insertion and standoffs also matter. With a conventional2.5mm-body Pi male header, the combined nominal body stack is approximately6mm. An underside capacitor with maximum2.5mm height fits within that nominal gap, but the final assembly should specify a compatible male header and approximately6mm standoff stack and check overlap with Pi components. This is a geometric assembly condition, not a claim of physical test fit.

## Local source copies

- U8: `C:/Users/M/Downloads/44dab75e94f614a40755e864ce8fcb1b.pdf`
- MK1: `C:/Users/M/Downloads/499793f63b845096dd1c91b6ab54835a.pdf`
- U3: `C:/Users/M/Downloads/8ec152f6a55cfad03e18463bcd9821c4.pdf`
- Q2: `C:/Users/M/Downloads/bd5e0dde9c521859386cfe9e8936b896.pdf`
- J4: `C:/Users/M/Downloads/f6b712306ee238d037f0521f733ec84a.pdf`

This review establishes the stated pin maps and mechanical correspondence. It is not a physical functional test or an approval of unspecified package-pad electrical behavior.

## Follow-up: L4 switching voltage and C39 charge-pump margin

Eaton ELX1096 (effective December2022), page2 note6, states "Rated operating voltage (across inductor)20Vref." This note applies to the entire SDCHA1V6045 series, including **SDCHA1V6045-4R7-R and -6R8-R**. Changing the inductance within this family does not remove the voltage consideration.

For a buck converter with nominal5V output, L sees approximately VIN-5V during the high-side on interval and approximately-5V during the low-side interval, before switching-node ringing. Thus28V input produces about23V across L during the on interval, beyond the stated20V reference;24V produces19V and leaves only1V nominal ringing/tolerance margin. The note is a reference operating voltage, not an insulation test specification or an explicit absolute maximum.

An M1 application limit of24V maximum input **including input transients** is a reasonable reduction for this selection, with the additional design/test condition that actual switching-node excursions do not take differential L voltage above20V. It is not a proof that every24V supply/transient environment is qualified. The intended2S battery (8.4V maximum charge voltage) gives only about3.4V on-state differential across L and is comfortably inside this reference envelope. If28V input operation must remain supported, select a different inductor family with a documented voltage capability that covers the switching excursion; do not substitute -6R8-R as a voltage fix.

For the proposed **C39 GRM21BR71H224KA01L,220nF/50V/X7R/0805/10%**, a conservative initial-tolerance and temperature estimate is:

`C_eff =220nF *0.90 *0.85 * DC-bias-retention`.

To retain at least100nF at13V bias, the exact part's bias retention must be at least0.5942 (no more than40.6% reduction), before any additional aging allowance. With a further5% aging allowance the required retention is0.6254. A typical bias curve can support an engineering estimate; it is not a guaranteed production minimum under all combined corners.

The parent subsequently obtained Murata's exact Electrical Characteristics Data for **GRM21BR71H224KA01**, dated November2026; this worker independently inspected the PDF and rendered curve. Its13V bias curve shows approximately4% typical capacitance loss. Using a deliberately larger10% bias allowance,10% initial tolerance,15% X7R temperature factor and5% aging allowance gives `220nF *0.90 *0.85 *0.90 *0.95 =143.90nF`, above TI's100nF minimum. This supports the exact selected MPN for the present build; no arbitrary same-value substitute is approved. The manufacturer explicitly identifies the curves as typical rather than a guaranteed combined-corner production minimum. Dimension2.0+/-0.1 by1.25+/-0.1 by1.25+/-0.1mm also fits the0805 land and underside height envelope.

Exact curve source: `C:/Users/M/Downloads/GRM21BR71H224KA01#_EC-data.pdf`, obtained from Murata's product page https://pim.murata.com/en-global/pim/details/?productCategoryId=&partNum=GRM21BR71H224KA01%23 .

Local Eaton source: `C:/Users/M/Downloads/eaton-sdcha1v60-automotive-semi-shielded-power-inductor-data-sheet-elx1096-en.pdf`.
