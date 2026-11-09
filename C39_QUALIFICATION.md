# C39 charge-pump capacitor

Selected GRM21BR71H224KA01L:220nF50V X7R0805,10% tolerance. PCBWay/LCSC C86042 had6175 units in stock on2026-11-09; required10 plus assembly attrition.

TI LM74700-Q1 requires at least100nF effective VCAP-to-ANODE capacitance and at least10*Ciss(MOSFET). DMN3023L Ciss is substantially below10nF, so100nF is the controlling minimum.

The exact Murata electrical-characteristics PDF downloaded from the product page on2026-11-09 shows only approximately3–5% capacitance loss around13V DC bias. Using a more conservative10% bias loss,10% initial tolerance,15% temperature allowance and5% aging allowance gives:

`220nF *0.90 *0.90 *0.85 *0.95 =143.9nF`.

This has margin above100nF. The curve is typical data; combined-corner capacitance has not been physically measured. The charge pump operates across C39, so its voltage stress is gate-pump voltage (up to13V), not the5V rail alone.50V rating gives ample voltage headroom.

Murata marks this exact part NRND and recommends a newer0603 alternative. The stocked0805 part is intentionally retained for the ten-board batch and the tested land pattern; a later production revision should requalify the recommended active alternative and its bias curve/footprint.

Source: https://pim.murata.com/en-global/pim/details/?productCategoryId=&partNum=GRM21BR71H224KA01%23

Exact downloaded PDF: `GRM21BR71H224KA01#_EC-data.pdf`, electrical characteristics dated Nov2026. Local rendered plot was visually checked at13V. This resolves the missing-curve item in the earlier pinout review.
