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
in the following sections:

#### Locked

When a unit is 'locked' U-Boot is restricted to the following:

```
Sonos Tupelo > help
boot    - boot default, i.e., run 'bootcmd'
ddp     - ddputil - Diagnostic Data Page utility
ddr     - DDR memory Bank-Row-Col Access Test
diag    - perform board diagnostics
help    - print command description/usage
i2c     - I2C sub-system
memtest - memtest Memory sub-system
ping    - send ICMP ECHO_REQUEST to network host
printenv- print environment variables
reset   - Perform RESET of the CPU
run     - run commands in an environment variable
saveenv - save environment variables to persistent storage
setenv  - set environment variables
sleep   - delay execution for some time
sonosboot- Boot the freshest section (or optionally the least fresh)
unlock  - device unlock
update  - Upgrade U-boot image on flash
usb     - USB sub-system
version - print monitor, compiler and linker version
```

#### Unlocked

When a unit is 'unlocked' U-Boot provides the following:

```
Sonos Tupelo > help
?       - alias for 'help'
aml_gpio-  Amlogic A113 GPIO dump
audio   - audio sub-system
base    - print or set address offset
bdinfo  - print Board Info structure
boot    - boot default, i.e., run 'bootcmd'
bootd   - boot default, i.e., run 'bootcmd'
bootgen - displays the bootgen stored in a Sonos section
booti   - boot arm64 Linux Image image from memory
bootp   - boot image via network using BOOTP/TFTP protocol
bootz   - boot Linux zImage image from memory
burnfuse- check and burn all security-related OTP fuses
ccg3    - CCG3 sub-system
cmp     - memory compare
coninfo - print console devices and information
cp      - memory copy
crc32   - checksum calculation
dcache  - enable or disable data cache
ddp     - ddputil - Diagnostic Data Page utility
ddr     - DDR memory Bank-Row-Col Access Test
dhcp    - boot image via network using DHCP/TFTP protocol
diag    - perform board diagnostics
dm      - Driver model low level access
echo    - echo args to console
editenv - edit environment variable
env     - environment handling commands
erase   - erase FLASH memory
exit    - exit script
false   - do nothing, unsuccessfully
fdt     - flattened device tree utility commands
flinfo  - print FLASH memory information
go      - start application at address 'addr'
gpio    - query and control gpio pins
gpt     - GUID Partition Table
help    - print command description/usage
i2c     - I2C sub-system
icache  - enable or disable instruction cache
iminfo  - print header information for application image
imxtract- extract a part of a multi-image
itest   - return true/false on integer compare
led_test- Test app for testing U-boot LED patterns
loadb   - load binary file over serial line (kermit mode)
loads   - load S-Record file over serial line
loadx   - load binary file over serial line (xmodem mode)
loady   - load binary file over serial line (ymodem mode)
loop    - infinite loop on address range
md      - memory display
mdio    - MDIO utility commands
mdp     - Display MDP or initialize the MDP and turn autodiag on
          really (UNSAFE) command on a secure unit
memtest - memtest Memory sub-system
mii     - MII utility commands
mm      - memory modify (auto-incrementing address)
mmc     - MMC sub system
mmcinfo - display MMC info
mw      - memory write (fill)
nm      - memory modify (constant address)
pci     - list and access PCI Configuration Space
ping    - send ICMP ECHO_REQUEST to network host
printenv- print environment variables
protect - enable or disable FLASH write protection
rarpboot- boot image via network using RARP/TFTP protocol
reset   - Perform RESET of the CPU
run     - run commands in an environment variable
saveenv - save environment variables to persistent storage
setenv  - set environment variables
setexpr - set environment variable as the result of eval expression
showvar - print local hushshell variables
sleep   - delay execution for some time
smi     - smi - isues read/write command on smi for switch registers
socfuse - read and write SoC-specific OTP fuses
sonosboot- Boot the freshest section (or optionally the least fresh)
source  - run script from memory
temp    - DIAG: display CPU/PA board temperature
test    - minimal test like /bin/sh
tftpboot- boot image via network using TFTP protocol
true    - do nothing, successfully
unlock  - device unlock
update  - Upgrade U-boot image on flash
upgrade - Upgrade a section/kernel/rootfs
usb     - USB sub-system
version - print monitor, compiler and linker version
```

### Memory Read-Out

Arbitrary memory read-out has been achived by abusing the `i2c` commands
present in the version of U-Boot as shipped with the unit. Though the use of
Python, and the [serial console](./CONSOLE.md) it is possible to read and
write to memory 1-byte at a time.

The following script (`i2c-thief.py`) provides a working example of how this
can be achieved.

* [i2c-thief.py](./scripts/i2c-thief.py)

### Write-What-Where

A write-what-where primitive is possible by using the i2c bus, and a writable
register on a device already present - such as the PWM register of the LP5562
LED controller. This process effectively abuses the i2c bus and the LP5562 LED
controller (which controls the lights on the top of the unit) in order to
provide a 'staging area' for bytes to allow for run-time patching of U-Boot.

#### Via `write-what-where.py`

This example allows for overwriting arbitrary memory with the provided
values:

```
$ python3 write-what-where.py
Usage: write-what-where.py <address> <byte>
```

* [write-what-where.py](./scripts/write-what-where.py)

#### Manually

The crux of this example is to flip the `op` bit to convert instruction
`CBZ` (`0x34`) to `CBNZ` (`0x35`) in the `sonosboot` U-Boot command. This
will cause the `enable_console=1` argument to be added to the Linux Kernel
boot arguments (`init`).

0. Trigger an Abort by attempting to read from trustzone addresses to leak
the address of the `i2c_write` function via the `ELR`. Calculate the base
address by subtracting the known offset of this address from the address in
the `ELR` register. In the case of this version of U-Boot on this platform
this offset is `0x2C494`, and thus base address is `0x3FF21000`.
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
implemented by Sonos in `secure_console.sh`.

8. Be sad :(

### Enable Privileged Commands

The version of U-Boot which ships with the Sonos One (Generation 2) [S18]
appears to contain a number of 'privileged' commands which are only enabled
on a unit marked as being 'unlocked'.

It's possible to patch the check used by U-Boot to determine whether the
device is 'unlocked' by patching a `CBNZ` and `MOV` operation to force the
procedure to return `0x1` rather than `0x0`. The procedure itself is at
`0x100CCEC` and has been labelled as the author as `is_device_locked` based
on its operation.

1. Try MDP (privileged) command, to confirm it is not accessible.
```shell
stty -F /dev/ttyUSB0 min 100 time 2
echo 'mdp' > /dev/ttyUSB0 && cat /dev/ttyUSB0

```
2. Patch `CBNZ` to `CBZ` in `is_device_locked`.

```shell
python3 i2c-thief.py 0x100CD14 0x100CD18
python3 write-what-where.py 0x100CD17 0x34
```

3. Patch `MOV W0, #0` to `MOV W0, #1` in `is_device_locked`.
```shell
python3 i2c-thief.py 0x100CDAC 0x100CDB0
python3 write-what-where.py 0x100CDAC 0x20
```

4. Try MDP command again.
```shell
stty -F /dev/ttyUSB0 min 100 time 2
echo 'mdp' > /dev/ttyUSB0 && cat /dev/ttyUSB0
```

5. Be happy :)
