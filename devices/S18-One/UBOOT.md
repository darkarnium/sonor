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

### Write-What-Where

A write-what-where primitive is possible by using the i2c bus, and a writable
register on a device already present - such as the PWM register of the LP5562
LED controller. This process effectively abuses the i2c bus and the LP5562 LED
controller (which controls the lights on the top of the unit) in order to
provide a write-what-where primitive for run-time patching of U-Boot.

The crux of this example is to flip the `op` bit to convert instruction
`CBZ` (`0x34`) to `CBNZ` (`0x35`) in the `sonosboot` U-Boot command. This
will cause the `enable_console=1` argument to be added to the Linux Kernel
boot arguments (`init`).

0. Trigger an Abort by attempting to read from trustzone addresses to leak
the address of the `i2c_write` function via the `ELR`. Calculate the base
address by subtracting the known offset of this address from the address in
the `ELR` register. In the case of this version of U-Boot on this platform
this offset is `0x2C494`.
```
i2c write 0x82000030 0x51 0x00 0x1
```

1. Read initial opcode bits from instruction at `0x1005830` to LED controller
(`LP5562`) PWM register.
```
i2c write 0x3ff26833 0x30 0x70 0x1
```

2. Get the initial instruction value from the LP5562 PWM register to ensure
it is an `CBZ` (`0x34`) instruction as expected.
```
i2c md 0x30 0x70 0x1
```

3. Flip the `op` bit in the instruction to patch to `CBNZ` (`0x35`), and write
to the LP5562 PWM register. This is required as only values that already exist
somewhere on the i2c bus can be written into memory, so this register is used
as a 'spool'.
```
i2c mw 0x30 0x70 0x35
i2c md 0x30 0x70 0x1
```

4. Read the new instruction from the i2c bus into memory over the top of the
old `CBZ` instruction.
```
i2c read 0x30 0x70 0x1 0x3ff26833
```

5. Confirm the write by reading back to the PWM register to confirm the write
was successful.
```
i2c write 0x3ff26833 0x30 0x70 0x1
i2c md 0x30 0x70 0x1
```

6. Boot the device.
```
sonosboot
```

7. Observe the new console output, though no shell due to additional checks
implemented by Sonos in `secure_console.sh`. Be sad :(
