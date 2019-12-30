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

* [J3-Console-Uboot.txt](./dumps/j3-console-uboot.txt)
