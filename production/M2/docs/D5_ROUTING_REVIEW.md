# D5 startup path — native PCB verification

Verified on 2026-11-09 using KiCad 9.0.7. Final child-owned board check is `d5-final-drc.json`: **0 rule violations, 0 unconnected items, 0 schematic-parity findings**, with all severities and the original project rules enabled. Parent owns subsequent metadata/origin/export changes and must repeat the release checks.

## Exact part and land pattern

Selected part: Diodes Incorporated **SBR3U40P1-7**, LCSC **C97127**, PowerDI123. Official source: https://www.diodes.com/datasheet/download/SBR3U40P1.pdf ; reviewed local copy `C:/Users/M/Downloads/SBR3U40P1.pdf` (DS31164). The published package is at most 3.9 × 1.93 × 1.0 mm. Its recommended land geometry corresponds to KiCad's `Diode_SMD:D_PowerDI-123`: cathode land 2.40 × 1.50 mm, anode land 1.05 × 1.50 mm, 0.65 mm inter-pad gap. The local copy is **RobotHAT:D_PowerDI123_D5**. Local pad numbering deliberately assigns **1 = cathode**, **2 = anode**, matching the schematic and package cathode-band orientation; the PDF identifies polarity by the band rather than numbered terminals.

The part is rated 3 A and 40 V; the manufacturer's capacitive-load derating of 20% leaves 2.4 A. This supports the intended 2 A startup bypass of Q2's body diode. The 75 A / 8.3 ms surge rating is a separate nonrepetitive condition, not a continuous-current rating. PCB CAD verification does not replace startup-current and temperature measurement on the assembled prototype.

## Placement and routing

D5 is on **B.Cu**, center **(112.3, 82.9) mm**. Cathode pad 1 is at (111.45, 82.9), connected to **+5V**; anode pad 2 is at (113.825, 82.9), connected to **/Schematic/Power/REG_5V**. Thus current can flow from the raw regulator output toward the protected +5V output during startup. The earlier SMA candidate was rejected and is not the fitted part.

Each terminal uses three parallel through vias, 0.60 mm copper diameter / 0.30 mm drill: cathode x109.0, y81.0/81.7/82.4; anode x114.8, y82.1/82.8/83.5. The vias are outside the SMT lands. Main outside-layer power runs are 1.0 mm wide; the new +5V inner run is 1.8 mm on In2.Cu. Short 0.6 mm array fan-outs share current across the three vias. REG_5V returns to L4's output land on F.Cu. Existing In1 shielding and the earlier gate/sense layout are retained.

At this placement the maximum package-body upper edge is y81.935. The neighboring J1 through-hole land lower edge is y81.645, leaving **0.290 mm geometric separation** from the maximum body envelope; terminal copper and all native electrical clearances also pass DRC. The diode's pad lower edge is y83.65, approximately 0.89 mm from the board edge at y84.540001. The 1 mm front source trace at y83.5 retains approximately **0.54 mm copper-to-edge clearance**. The nearby FID2 local copper clearance is respected. The maximum body height is 1.0 mm.

New routing changed a bottom-ground pour connection at C6. A 0.30 mm B.Cu trace now joins C6 GND (114.3925, 80.425) to the existing GND via (115.3925, 80.545). Final zone refill and full native checking confirm connection.

## Scope of handoff

The PCB and PowerDI footprint are handed back to the parent. No commit was made by this worker. `add_startup_diode.py`, the unused `RobotHAT.pretty/D_SMA_D5.kicad_mod`, and `d5-first-drc.json` describe an obsolete rejected SMA experiment and must not enter the manufacturing release. The release must use the current native PCB and exact PowerDI footprint/MPN.
