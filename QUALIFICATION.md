# PCBWay candidate — not released for manufacture

Upstream baseline: 6de86283297e4c49a9da8312cd3395ab83c437e3.
Review date: 2026-11-09. Target: ten assembled boards, Pi Zero 2 W interface retained.

## Confirmed changes

- U12 LSM6DSV16X narrow pad dimension reduced from 0.35 to 0.30 mm on all 14 pads. Pad centers, nets and component placement retained. Adjacent parallel pad edges now have 0.20 mm copper spacing. A dedicated 0.19 mm PCBWay rule is exercised by a negative control in `verify_geometry.py`.
- Mask/paste apertures follow the narrowed pads; stencil and solder-joint process still require assembler review. This is not a claim of preserved original paste aperture area.
- Original embedded footprints and missing private symbols are supplied locally. Schematic footprint assignments match the board.
- C8/C9 corrected from 220 nF to 220 pF in schematic and PCB. Their existing BOM MPN is Murata GRM1555C1H221JA01D (LCSC C71693), 220 pF / 50 V / C0G / 0402. They are after FB2/FB3 at the BTL speaker output, not supply decoupling.

## Basis for the audio correction

Diodes PAM8406 EVB User Guide, page 3, lists 220 pF output EMI capacitors with 2 A / 120 ohm ferrites. The native netlist places HAT C8/C9 in that same circuit role. This supports the original MPN and identifies the 220 nF label as the inconsistent item. A 220 nF shunt would present 1000 times the capacitive switching load at a given frequency; it is not an interchangeable bypass value.

- https://www.diodes.com/assets/Evaluation-Boards/PAM8406-User-Guide.pdf
- https://www.diodes.com/datasheet/download/PAM8406.pdf
- https://www.lcsc.com/product-detail/C71693.html

FB1 feeds PAM8406 VDD pin 6; PVDDL/PVDDR pins 4/13 have a separate direct +5 V feed. Do not rate FB1 by loudspeaker output current. Its listed 300 mA MPN and conflicting 1.3 A label still need a documented VDD load/inrush and impedance/DCR check before qualification.

## Remaining release blockers

- Live distributor stock/price not verified: LCSC product page exposed specifications but no purchasing stock/price panel in the side browser. No parts are marked stock-qualified.
- C19: retain 10 uF / 63 V requirement pending a qualified MPN/land-pattern/ESR/temperature/lifetime selection. Existing original BOM MPN is 50 V and remains unapproved.
- C21/C22 and C23/C24/C39: reconcile higher-voltage MPNs with capacitance, dielectric, DC-bias and geometry. These have not yet been signed off merely because the voltage is higher.
- Complete component-by-component circuit qualification, sourcing quantities/MOQ and BOM/POS reconciliation remain outstanding.
- Board stackup metadata needs supplier reconciliation: nominal board thickness is 1 mm, while back-copper metadata says 0.35 mm and board note says 35 um. No stackup has been invented or approved.
- DFM review must cover PCBWay's complete chosen fabrication process, mask registration/dams, stencil, U12 solder joint and mechanical tolerances. Current added rule implements their specific U12 0.19 mm request, not every possible supplier requirement.
- Existing `production/` files are ORIGINAL D1 files and DO NOT include this candidate. Do not upload them as revised manufacturing files.
- Electrical, thermal, audio and EMC behavior are untested on hardware. CAD checks are not a physical or regulatory approval.

## Validation

KiCad 9.0.7. `candidate-drc.json` includes schematic parity; `candidate-erc.json` includes all severities. `u12-geometry-check.json` captures pad dimensions and a negative control. Board/schematic connectivity is checked by native parity; independent physical connectivity and exported Gerber inspection remain release tasks.
