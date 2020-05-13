## Console

1. [Overview](#overview)
1. [Pinout](#pinout)
1. [Boot Console](#boot-console)

### Overview

An unpopulated connector which provides a serial console can be found under the
CPU shield can just below the MiniPCI connector on the Sonos ZP120 logic board.
This is labelled `J15005`

The console baud is `38400` (`8N1`).

### Pinout

The pinout for `J15005` is as follows:

![UART / Console Pinout](./images/photographs/ports-uart.jpg?raw=true)

### Boot Console

The boot-time output from the unit can be found in the following text dump:

* [J15005-Console-Boot.txt](./dumps/j15005-console-boot.txt)
