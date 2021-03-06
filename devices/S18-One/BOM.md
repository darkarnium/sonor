## Bill Of Materials (BOM)

1. [Overview](#overview)
1. [Flattened DeviceTree (FDT)](#flattened-devicetree-fdt)
1. [Data Sheets](#data-sheets)

### Overview

The following list details the major components on the logic board of a Sonos
One (Generation 2) [S18].

|Package|Manufacturer|Part Number|Description|Silk Screen|Board|
|-|-|-|-|-|-|
|LFBGA|Amlogic|A113D|A113D SoC (ARM Cortex-A53)|Ui|Logic Board|
|FBGA|Kingston|EMMC04G-M627|4GB eMMC Flash Memory|U4|Logic Board|
|TFBGA|Nanya|NT5CC512M8EQ|DDR3(L) 4Gb SDRAM (512MB)|U74|Logic Board|
|TFBGA|Nanya|NT5CC512M8EQ|DDR3(L) 4Gb SDRAM (512MB)|U75|Logic Board|
|VQFN|TI|DP83822I|10/100Mbps Ethernet PHY|U17|Logic Board|
|QFN|Cypress|CY8C4245LQI|PSoC 4200 (ARM Cortex-M0)|U1|Microphone Board|
|TFBGA|Mediatek|MT7615N|"Router-on-a-chip" 5-port 10/100/1000 PHY, 1 RGMII|U10|Radio Board|
|DFN8|ST|M24C64|64-Kbit EEPROM (i2c)|U13|Radio Board|

### Flattened DeviceTree (FDT)

The FDT was successfully extracted over the `i2c` bus and converted back to
DTS format - using the `dtc` utility. This tree contains information about
components, their addressing, and other parameters which may be of
assistance.

* [Sonos-Tupelo-v1.dts](./dumps/sonos-tupelo-v1.dts)

### Data Sheets

* [Amlogic A113D](https:///)
* [Nanya NT5CC512M8EQ](https://www.nanya.com/Files/667?Filename=4Gb_DDR3_E_Die_component_Datasheet.PDF&ProductId=4,245)
* [Kingston NT5CC512M8EQ](https:///)
* [Cypress CY8C4245LQI](https://www.cypress.com/file/138656/download)
* [TI DP83822I](http://www.ti.com/lit/ds/symlink/dp83822i.pdf)
* [Mediatek MT7615N](https:///)
* [ST M24C64](https://www.st.com/resource/en/datasheet/m24c64-r.pdf)
