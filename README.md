# Robot HAT D1-M1 — PCBWay prototype package

**Current fork revision: D1-M1, ten assembled prototype boards.** Use [the complete M1 PCBA archive](production/M1/Robot_HAT_M1_PCBA_10.zip), [ordering instructions](ORDERING.md) and [qualification record](QUALIFICATION.md). Original D1 production files below are historical. M1 targets a 2S battery (6.0–8.4 V) and a combined 5 V load up to 2 A; the original 5–28 V statement is superseded for this revision.

M1 corrects U12 pad/mask spacing, audio filter labels, component sourcing/pinouts and the regulator/ideal-diode circuit. It includes coherent Gerber, drills, BOM, placement, assembly drawings and dated sourcing. Native checks and export verification are recorded in the package. Physical prototype testing remains required.

## Original upstream description

> "RPI_Robot_HAT" is a raspberry pi HAT designed for small/medium size robots. It has an IMU, Dynamixel connectors and audio. Its size fits a Raspberry PI zero.

<img src="./docs/img/elec_RPI_Robot_HAT.png" alt="3d view" width="400"/>

The RPI_Robot_HAT gathers:

- **IMU** over I2C + data fusion
- **Dynamixel motor communication**: both TTL and 485 to drive Dynamixel/Feetech motor (requires cable adaptation)
- **in/out audio device** with an integrated mems microphone. Wago connectors allows connection of loudspeaker and extra microphone.
- **expension Qwiic connectors**, 1 mm/3V3. Please refer to the schematic for knowing which can be use on you raspberry pi.

The RPI_Robot_HAT can be power from 5 to 28V. It is designed to use of the motor connector as an power input.


## Releases
| Release | Date       | Designer | Check  | Comments                               |
|---------|------------|----------|--------|----------------------------------------|
| A1      | 06/03/2026 | EB       | SN     | Initial drawing                        |
| B1      | 06/05/2026 | EB       | SN     |[fixed] Acc. is at 0x19 I2C address<br />[fixed] Soft reset of the audio DAC<br />[fixed] Ideal diode<br />[fixed] Know position of IMU<br />[update] Dynamixel_dir is based on Tx<br />[added] IMU can be disconnected<br />[added] IMU_IT is cabled<br />[added] Access to I2C0<br />[added] Switch off detection|
| C1      | 08/07/2026 | EB       | SN     | [fix] 3V3 on IO10/11<br />[fix] MOS direction of Ideal diode<br />[update] I2C3 is by default instead of reserved I2C|
| D1      | 06/10/2026 | EB       | Claude | [update] IMU is now LSM6DSV16XTR<br />[update] RS485 Driver<br /> [update] screwable terminals for audio|




## Basically
 - Designed with KiCAD 9.

## Rebuilding M1

The checked-in production/M1 archive is ready for supplier review. To reproduce it, use KiCad9 CLI/Python and Python3 with shapely, gerbonara and PyMuPDF, then run python build_release.py. The builder runs physical connectivity, the deliberate U12 negative control, native all-severity checks and export reconciliation before packaging. --package-only refreshes packaging from existing exports and requires an up-to-date native connectivity report; it does not export new CAD data.
