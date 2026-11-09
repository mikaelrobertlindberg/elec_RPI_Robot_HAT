# Robot HAT PCBWay revision

Work in progress; not a manufacturing release.

- Fork created from upstream 6de86283297e4c49a9da8312cd3395ab83c437e3.
- Baseline: 9 missing-private-library warnings, zero unconnected items, zero schematic parity findings under upstream 0.15 mm rules. Prior PR's 346 findings are not this project's measured baseline.
- Candidate: local footprint/symbol libraries supplied; U12 pads narrowed to 0.30 mm; C8/C9 corrected to 220 pF with Diodes EVB source. Native DRC/parity and ERC have reached zero; final rerun recorded in candidate reports.
- Preserve board outline, mounting holes and Pi Zero connector interface.
- Investigate C8/C9 audio circuitry, FB1 load and C19 input voltage before substitutions.
- Next: finish component qualification/stock check, resolve stackup inconsistency, independently inspect connectivity/retur paths, generate and inspect reconciled manufacturing package. See QUALIFICATION.md for release blockers. Supplier stock panel unavailable in side browser; no stock claims made.
- No manufacturing approval or supplier response sent.
