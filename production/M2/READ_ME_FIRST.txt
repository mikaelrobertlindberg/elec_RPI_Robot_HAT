# Robot HAT D1-M2 — ten assembled prototype boards

Use ONLY the files inside `production/M2/Robot_HAT_M2_PCBA_10.zip` for this revision. The original D1 files elsewhere in `production/` are historical and must not be mixed with M1.

## M2 single-change notice

M2 supersedes M1 solely to restore U8 GM3088ENA exposed pad 9 to an electrically isolated solder land, matching the upstream board. Pin 5 remains GND. Remove only the local B.Cu ground connections to the exposed pad; retain its copper, solder mask and paste apertures. BOM, placements, pad geometry, drills, stackup, outline and all other signal connections are unchanged. Board artwork may retain the M1 label; identify this ECO by the M2 ZIP/manifest and U8 detail. Do not mix old copper files with this revision.

## Files for PCBWay

- PCB fabrication: `Robot_HAT_M2_Gerber.zip` (four copper layers, mask, silkscreen, board outline and separate plated/nonplated drill files).
- Assembly: `BOM_PCBA_10.csv`, `CPL_PCBA_10.csv`, `Do_not_populate.csv`, top/bottom assembly drawings and schematic PDF.
- `Sourcing_2026-11-09.csv` contains dated distributor stock checks and MOQ/spare quantities. BOM quantities are per board AND total for ten boards; assemble ten boards, not ten times the total column.
- CPL uses native KiCad9 CSV convention, millimeters, common drill/place origin at the lower-left board corner (native X71.397501,Y84.540001mm), positive X right and positive Y up, both sides, bottom X NOT negated. Do not silently apply historical original-D1 rotation offsets to the newly exported CPL. Check pin1/polarity against the assembly drawings and exact MPN orientation before programming the placement machine.
- `manifest.json` binds source and output SHA256 hashes. Keep all files as one revision.

## Fabrication order settings

4-layer FR4, nominal finished thickness1.0mm, outer copper35um (1oz), inner copper18um (0.5oz), green solder mask, white silkscreen, lead-free ENIG, IPC-A-600 class2 workmanship and100% electrical test. No controlled-impedance requirement. Layer order F.Cu / In1.Cu / In2.Cu / B.Cu. Use supplier's standard manufacturable FR4 stack for these finished thickness/copper targets; the native dielectric thicknesses are nominal modeling values, not a proprietary laminate requirement. Supplier must report any inability to meet the stated dimensions or copper targets before fabrication.

Copper clearance0.15mm, track width0.16mm minimum; U12 adjacent pad clearance0.20mm meets the specific PCBWay request of at least0.19mm. Preserve individual U12 solder-mask openings and dams. Through vias include0.20mm drills; do not widen these holes without checking the design. Preserve mounting, locating and Pi pass-through holes.

## Assembly requirements

Turnkey PCBA, ten units, both sides. Mount all `Populate=YES` BOM items including through-hole connectors. No substitutions without an engineering check of value, dielectric/bias, pin mapping, footprint, polarity and temperature rating. Allow normal SMT attrition quantities (shown in sourcing file); quantities are not extra assembled boards.

U12 is LSM6DSV16XTR, not LSM6DSM. Use appropriate solder-paste/stencil control for its LGA lands and inspect hidden joints; U2 is an exposed-pad QFN. Follow manufacturer paste/reflow recommendations and perform AOI plus hidden-joint inspection. Exact rotations must be checked by the assembler; a placement file alone does not qualify machine orientation.

Use a120um stencil for the fine-pitch lands, with a local150um step/paste-volume provision at Eaton L4 per its manufacturer recommendation, or an assembler-qualified equivalent local paste-addition process. U12's0.30x0.625mm aperture has area ratio about0.845 at120um; do not silently apply a thick global stencil without checking paste release and bridging at the LGA/QFN.

Microphone MK1 is top-port: do not obstruct its port, wash it, ultrasonically clean it or expose it to incompatible cleaning/reflow. Pi socket J4 maximum soldering temperature/time is260C/10s per its drawing. If this is incompatible with the board's lead-free reflow profile, assemble J4 after reflow with a controlled compatible selective/manual process. Through-hole terminals/JST connectors may use selective/manual soldering. Do not force all components through one common reflow profile.

C19 is Panasonic EEE-FK1J100P,10uF63V, positive pad1 at+BATT. D1 is a SINGLE onsemi BAT54WT1G, anode1, NC2, cathode3. Do not fit the original dual BAT54SW. Q2 is DMN3023L-7, G1/S2/D3,20V gate rating. U10 is LM74700QDBVRQ1, NOT LM5050. C39 is its220nF50V charge-pump capacitor betweenVCAP andREG_5V, not a ground bypass. R8 is removed.

D5 SBR3U40P1-7 is the dedicated3A40V PowerDI123 startup rectifier across Q2, anode2=REG_5V and cathode1=+5V. Keep its cathode-band orientation correct. It carries the initial capacitive/boot current until Q2 is enhanced; Q2 then provides the low-loss normal path. Reverse-current blocking includes the specified semiconductor leakage and is not galvanic or zero-current isolation.

C39's exact MPN is NRND but has dated stock sufficient for this ten-board batch. It is an intentional exact-part selection for this batch; do not assume continuing supply for a future production run. Other replacement options need a fresh qualification.

## Intended use and commissioning

This M1 build targets the Microduck/Pi Zero2W with a2S lithium battery (6.0–8.4V). Treat the original upstream's broad5–28V statement as superseded for M1: this revision has not been qualified for28V input. Supply external motor power distribution when motor/combined connector currents exceed the connector and board supply budget; do not infer unlimited servo current from the number of sockets. The regulated rail is5V,2A maximum including Pi and audio together. Use current-limited bench power for first startup and check simultaneous Pi/audio/motor behavior and temperature before installing an unrestricted battery.

Use a correctly polarized, keyed and externally fused battery branch (3A maximum fuse for the HAT input branch). Power the servo bus from a suitable external distribution point when its current exceeds the HAT branch rating; share ground and data. The HAT is not a high-current battery distribution board. Its5V ideal-diode circuit protects the regulated-rail power direction; it does not make the raw battery input reverse-polarity-proof.

The Pi Zero2W requires a correctly installed2x20 male header. Use compatible approximately6mm board spacing/standoffs and check clearance above Pi components against underside capacitors. Keep the original mounting interface and verify actual mating before tightening standoffs.

Firmware must explicitly support LSM6DSV16X (WHO_AM_I0x70), the correct I2C bus and audio codec. Physical pin compatibility with the older IMU does not make old LSM6DSM register programming valid. External IMU breakout remains an optional system choice; it is not required just to manufacture this HAT.

CAD/ERC/DRC and stock checks support ordering a prototype batch. They do not replace physical function, load-transient, thermal or EMC tests, and are not a CE/product approval. Before first commissioning: inspect polarity/shorts; ramp current-limited input; verify REG_5V and protected+5V, gate-source voltage and reverse-current blocking; check regulator ripple/load steps; read IMU identity; exercise TTL/RS485, microphone and speaker; measure temperature under combined intended loads. Do not connect either BTL speaker terminal to ground.

## Price

The earlier PCBWay quote covered original D1. M1 changes parts, footprints and assembly, so a fresh supplier price is required. The dated stock file is not a PCBWay reservation or final price and excludes supplier sourcing/setup, assembly, board fabrication, shipping and tax unless separately quoted.
