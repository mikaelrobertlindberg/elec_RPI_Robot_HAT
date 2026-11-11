# Robot HAT D1-M1 qualification record

Target: ten assembled prototype boards for Raspberry Pi Zero 2 W / Microduck, 2S battery6.0–8.4V. Upstream baseline6de86283297e4c49a9da8312cd3395ab83c437e3. Review2026-11-09.

## Completed design qualification

U12 retains its location and pin map. Fourteen pads have0.30mm narrow dimension, giving0.20mm copper spacing at0.50mm pitch. An explicit0.19mm supplier rule is exercised by verify_geometry.py, which deliberately restores an oversized pad. No DRC exclusions substitute for correction.

C8/C9 are220pF C0G output EMI shunts, not220nF bypass capacitors. Diodes PAM8406 evaluation guide page3 confirms their role. FB2/3 retain exact original ferrites; FB1 label now matches its300mA analog-supply ferrite on a path separate from output power.

D1 is single BAT54WT1G with verified pin mapping. C19 is Panasonic EEE-FK1J100P10uF63V with manufacturer land pattern. U10 is LM74700QDBVRQ1; R8 removed; C39 is qualified220nF charge-pump capacitor betweenVCAP andREG_5V. Q2 is DMN3023L-7 with20V gate rating. D5 provides a separate3A startup rectifier path; the MOSFET body diode is not assumed to carry a2A cold start.

L4 is Eaton SDCHA1V6045-4R7-R with saturation/current margin and manufacturer land pattern. C21/C22 are two Murata47uF16V X5R1206 devices selected using the exact DC-bias curve. See CIRCUIT_REVIEW.md, C39_QUALIFICATION.md, POWER_POST_REVIEW.md and PINOUT_REVIEW.md for reasoning, primary sources and assembly limits.

Local symbols and footprints remove private-library dependencies. Four-layer1mm stack metadata is corrected to35um outer/18um inner copper. Inner power routing and local ground vias are documented in ROUTING_REPAIR.md.

## Release evidence

build_release.py exports one native revision and refuses nonzero all-severity ERC, DRC, unconnected or schematic-parity results. It reconciles exact MPNs, dated stock, BOM and placement coverage. The release contains check reports, exported-file verification and a SHA256 manifest. Only production/M1 is current; originalD1 exports remain historical.

Stock observations dated2026-11-09 include ten-board requirements, MOQ and spares; they are not reservations. C39 is intentionally NRND but stocked for this batch. No unqualified substitutions are approved.

## Prototype boundary and commissioning

No assembledM1 has been physically tested. CAD qualification is distinct from function, EMC and regulatory conformity; this is a prototype release, not a CE-approved product. The original upstream5–28V claim does not apply to M1.

Use externally fused correctly polarized input, maximum3A fuse on HAT branch, and separate motor distribution above the HAT current budget. Combined regulated5V Pi/audio load maximum2A. Raw input is not reverse-polarity protected.

Inspect polarity/resistance, then ramp current-limited input. Verify regulator output, VCAP/gate voltage, startup/reverse blocking and ripple. Test0–2A load steps, simultaneous Pi/audio and temperatures at6.0/8.4V. Confirm Q2 bypasses D5 after startup; D5 is not a qualified continuous2A fallback. Check WHO_AM_I0x70 and firmware, TTL/RS485, microphone/BTL audio and actual header/standoff clearances before battery operation.

External ports are intended for short internal robot wiring. System ESD, long-cable surge and emissions have not been demonstrated; IC handling ratings are not system immunity evidence. Validate intended cables, grounding and enclosure, then applicable pre-compliance testing before market release. No arbitrary port protection parts were added without a defined requirement.

Exact manufacturer documents and stock URLs are referenced in the circuit/pinout reviews and sourcing.csv. ORDERING.md defines the full manufacturing and assembly instructions.


## D1-M2 U8-only correction, 2026-11-11

U8 exposed pad9 is isolated as in upstream6de8628. The M1 ground assignment lacked manufacturer justification and is withdrawn. Pin5 remains GND. No component, placement, mask, paste, drill, stackup or other signal change is intended. See M2 change verification. Earlier M1 review statements are historical. This restores original topology without claiming manufacturer confirmation of EP electrical function.
