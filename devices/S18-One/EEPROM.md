## EEPROM

An ST M24C64 EEPROM (i2c) appears to be present on the 'radio board' of a
Sonos One (Generation 2) [S18]. The purpose of this EEPROM is not currently
completely clear, but it may be used to store configuration data for the
unit - perhaps related to WiFi radio configuration?

### Reading

As U-Boot on the unit supports reading memory via i2c, it is possible to read
data from this EEPROM through the bootloader. This said, read operation do
seem to be temperamental when executed via U-Boot.

The EEPROM appears to be addressed on the i2c bus as `0x55`:

```
Sonos Tupelo > i2c md 0x55 0x00.2 10
0000: 53 4f 4e 4f 53 2e 30 31 00 00 00 00 00 00 07 24    SONOS.01.......$
```

In order to get better access to the EEPROM, the clock and data pins for the
i2c bus the EEPROM is connected to is exposed via `TP18` (`SCK`) and `TP20`
(`SDA`) on the radio board.

![i2c Radio EEPROM](./devices/S18-One/images/photographs/radio-i2c-001.jpg?raw=true)
