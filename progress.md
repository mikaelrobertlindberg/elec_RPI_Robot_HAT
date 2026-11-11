# Robot HAT D1-M1

Completed native design for ten PCBA prototypes, Pi Zero2W / Microduck,2S6.0–8.4V,5V2A combined budget.

- Fork baseline6de8628; local libraries, U12 copper/mask spacing, C8/C9 filter values, corrected exact parts and pinouts.
- Power ECO: LM74700, DMN3023L, SBR3U40P1 startup rectifier,220nF qualified chargepump, Eaton4.7uH and2x47uF bias-qualified output. R8 removed.
- Sourcing44 datedrows,113 fitted components/board,43 uniqueMPNs. Exact stock sufficient for ten plus stated spares; C39 NRND intentional batch selection.
- Native all-severityDRC0/unconnected0/parity0/ERC0. U12 oversizedpad negativecontrol detects errors.
- Independent native physical copper check:2111shapes,407pads,74connectednets;0disconnected/0shorts. Deliberateopen/short controls detected. PCB SHAc81cfaddd14d99ccb39da780481cf95eba0c403e1bb88e17e0a5df1c117468d7.
- M1 fabrication/stencil/BOM/CPL/schema exported. Independent Gerber verification passed:193drillprimitives, U12copper/maskgap0.20mm,420copperislands with0cross-netshorts;306powertrackschecked. Improved assemblyPDFs visually inspected. Final readable power sheet exported; native ERC/DRC/parity0. Coherent manifest/archive built and ZIP hashes verified. Release commit f1a4aa049b356e85f6473292791f7ae73fad8ffb pushed to origin/main and remote SHA verified.
- Artifacts: production/M1; instructionsORDERING.md, qualificationQUALIFICATION.md, calculations/pinouts in reviewdocuments. OriginalD1 production files remain historical.
- No assembled hardwaretested, orderplaced or suppliermessages sent. New PCBWayprice needed for revisedM1.

## D1-M2 U8-only ECO, 2026-11-11

- Restored U8 pad9 to isolated copper, matching upstream6de8628; pin5 remains GND. No other circuit, BOM, placement, pad, mask, paste, drill or stackup change. Local B.Cu fill only; sub-nm refill rounding documented.
- Native ERC/DRC/unconnected/parity zero; independent native and Gerber connectivity pass. M1/M2 netlist differs only U8.9; BOM/CPL/DNP byte-identical. See production/M2/U8_only_change_verification.json and U8_only_change.png.
- Complete production/M2/Robot_HAT_M2_PCBA_10.zip SHA256 ad2eff448c9f284028c3dfc97a4fe8c5aaf5213cc33941a6715baf5b5be6800d.
- Sent ZIP and focused comparison PNG to Catherine service15@pcbway.com on 11 Nov09:38 Sweden, Sent3237. Both downloaded sent attachments verified byte-identical. Portal HAT thread7254939 hold request16:26:19 and M2 delivery notice16:39:33 China time.
- Order W212983ASI18 / T-I19W212983A,10boards; user reported paid. No CAM replacement/hold confirmation received yet; cannot assert fabrication has not begun. Await supplier acknowledgement. No change applies to UFH8.
- Private delivery: https://aoostar.tempel-morpho.ts.net:8443/robot-hat-m2-20261111/
