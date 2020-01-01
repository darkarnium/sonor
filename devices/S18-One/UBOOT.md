## U-Boot

Based on the Sonos employee email in the U-Boot version string it is likely
that this version of U-Boot is customised for Sonos. It likely also contains
Amlogic provided U-Boot patches for the A113 SoC.

Unfortunately, it appears that `tftp`, `base`, and other commands which may
assist in either dumping or loading data from U-Boot have been removed.

Although the full scope of the differences between vanilla U-Boot and the
Sonos `U-Boot 2016.11-A113-Strict-Rev0.14` version used by this unit are
currently unknown, the 'vanilla' U-Boot sources for `2016.11` can be found
at the following URL:

* [U-Boot 2016.11](https://github.com/u-boot/u-boot/tree/29e0cfb4f77f7aa369136302cee14a91e22dca71)

### Options / Commands

A brief summary of the commands available at the U-Boot prompt can be found
in the following text dump:

* [J3-Console-Uboot-Help.txt](./dumps/j3-console-uboot-help.txt)

### Memory Read-Out

Arbitrary memory read-out has been achived by abusing the `i2c` commands
present in the version of U-Boot as shipped with the unit. Though the use of
Python, the [serial console](./CONSOLE.md), and a logic analyser connected
to the [i2c bus](./EEPROM.md) it is possible to slowly read data directly
from memory, and onto the i2c bus.

The following script (`i2c-thief.py`) provides a working example of how this
can be achieved, though this process is exceedingly slow. Current estimates
put the speed in the range of around **55-bytes a second**.

* [i2c-thief.py](./scripts/i2c-thief.py)
