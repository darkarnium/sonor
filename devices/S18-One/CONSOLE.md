## Console

An unpopulated connector which provides a serial console can be found at the
base of the logic board PCB labelled as `J3` on the Sonos One (Generation 2)
[S18].

The console baud is `115200` (`8N1`).

### Pinout

The pinout for `J3` is as follows:

![UART / Console Pinout](./images/photographs/ports-uart.jpg?raw=true)

### Boot Console

The boot-time output from the unit can be found in the following text dump:

* [J3-Console-Boot.txt](./dumps/j3-console-boot.txt)

### U-Boot Options

A brief summary of the options available at the U-Boot prompt can be found
in the following text dump:

* [J3-Console-Uboot-Help.txt](./dumps/j3-console-uboot-help.txt)

Based on the Sonos employee email in the U-Boot version string it is likely
that this version of U-Boot is customised for Sonos. It likely also contains
Amlogic provided U-Boot patches for the A113 SoC.

Unfortunately, it appears that `tftp`, `base`, and other commands which may
assist in either dumping or loading data from U-Boot have been removed.

Although the full scope of the differences between vanilla U-Boot, and the
Sonos `U-Boot 2016.11-A113-Strict-Rev0.14` version used by this unit are
currently unknown the 'vanilla' U-Boot sources for `2016.11` can be found
at the following URL:

* [U-Boot 2016.11](https://github.com/u-boot/u-boot/tree/29e0cfb4f77f7aa369136302cee14a91e22dca71)
