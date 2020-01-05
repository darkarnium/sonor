'''
i2c-thief utilises the U-Boot console and an i2c bus to read data from
arbitrary memory locations on devices where U-Boot has been stripped of 'all'
useful memory read primitives.

This script was developed for performing read-out of data via U-Boot for Sonos
One (Generation 2) [S18] devices.

### NOTE ###

The address on the i2c bus to write to must be that of a device present on the
bus or writes will fail. Interestingly, writes to the M24C64 EEPROM on the
Sonos One (Generation 2) [S18] do not error, but data does not appear to ever
be properly written to the EEPROM - nor are any NACKs observed on the bus. As
a result of this quirk, the `i2c write` command can be abused to read memory
255-bytes at a time.

Data is read directly off the i2c bus using a logic analyser attached to i2c
SDA and SCK test points on the 'radio board' of the unit.

Please be advised that this is *NOT* a quick process.

Author: Peter Adkins (@Darkarnium)
'''

import sys
import serial
import datetime

PROMPT = 'sonos tupelo >'


def unit_to_uboot():
    '''
    Attempt to use a serial console to bring the Unit into a clean U-Boot
    prompt at power on, or reset and re-enter U-Boot if already at a U-Boot
    prompt.
    '''
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=10) as interface:
        # First up, reset the unit to get into a clean state.
        print('[+] Attempting to issue reset command to U-Boot')
        interface.write(b'reset\n')

        # Drop back into U-Boot.
        print('[-] Waiting for U-Boot boot interrupt prompt')
        buffer = bytes()
        while True:
            buffer += interface.readline()

            try:
                line = str(buffer, 'utf-8')
            except UnicodeDecodeError as err:
                buffer = bytes()
                continue

            # The whitelist check is just prior to the U-Boot interupt prompt.
            # When this line is encountered start reading N bytes rather than
            # until EoL - as the count down does not print an \n character
            # until AFTER the timeout.
            if line.lower().startswith('whitelist check completed'):
                # Check whether the 'Hit any key' prompt follows.
                try:
                    peek = interface.read(12)
                    if str(peek, 'utf-8').lower().startswith('hit any key'):
                        print('[+] Writing U-Boot interrupt to console')
                        interface.write(b'A')
                        buffer = bytes()
                        continue
                    else:
                        buffer += peek
                except:
                    # No point in tracking the read bytes if they'll just be
                    # discarded at the top of the next iteration.
                    pass

            # Drop out of the loop when we see the U-Boot prompt
            if line.lower().startswith(PROMPT):
                print('[-] Unit is now at U-Boot prompt')
                buffer = bytes()
                break

            # Dump the buffer contents if no matches.
            buffer = bytes()


def read_from_i2c(device=0x30, register=0x70, length=0x1):
    '''
    Attempt to read a byte from the register on the specified i2c device.

    Args:
        device (int): The address of the device on the i2c bus to read from
        register (int): The address of the register on the i2c device to read
    
    Return:
        The byte read from the device - as an int.
    '''
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as interface:
        command = 'i2c md 0x{0:0x} 0x{1:0x} 0x{2:0x}\n'.format(
            device,
            register,
            length,
        )
        interface.write(bytes(command, 'utf-8'))

        # Loop back is enabled, so throw away the first line.
        interface.readline()
        result = str(interface.read(len(PROMPT)), 'utf-8')

        # Split the value and cast to an integer.
        return int(result.split(' ')[1], 16)


def write_memory_to_i2c(addr, device=0x30, register=0x70, length=0x1):
    '''
    Attempt to read addr from unit memory and write it to the target i2c
    device. This assumes that the i2c commands are available in U-Boot,
    however memory read commands are not required as the i2c write command
    handles this.

    Args:
        addr (int): The address in memory to read from
        device (int): The address of the device on the i2c bus to write to
        register (int): The address of the register on the i2c device to write
        length (int): The number of bytes to read from addr

    Return:
        Whether the write operation was successful (bool).
    '''
    print(
        '[+] Writing {0} bytes from 0x{1:0x} to 0x{2:0x} at 0x{3:0x}'.format(
            length,
            addr,
            device,
            register
        )
    )
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as interface:
        command = 'i2c write 0x{0:0x} 0x{1:0x} 0x{2:0x} 0x{3:0x}\n'.format(
            addr,
            device,
            register,
            length
        )
        interface.write(bytes(command, 'utf-8'))

        # Loop back is enabled, so throw away the first line.
        interface.readline()
        status = str(interface.read(len(PROMPT)), 'utf-8')

        # Check whether the write was successful.
        if status.lower().startswith(PROMPT):
            return True
        else:
            print('[!] Write failed: {0}'.format(status))
            return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: i2c-thief.py <start-address> <end-address>')
        sys.exit(-1)

    # Attempt to dump memory.
    load = 0x01000000
    base = 0x3ff21000
    s_addr = int(sys.argv[1], 16)
    e_addr = int(sys.argv[2], 16)
    result = []

    # Fix the base addresses, if required.
    if s_addr < base:
        print('[-] Fixing base address for 0x{0:0x}'.format(s_addr))
        s_addr = base + (s_addr - load)

    if e_addr < base:
        print('[-] Fixing base address for 0x{0:0x}'.format(e_addr))
        e_addr = base + (e_addr - load)

    print('[-] Dumping 0x{0:0x} to 0x{1:0x}'.format(s_addr, e_addr))
    start_time = datetime.datetime.utcnow()

    c_addr = s_addr
    # unit_to_uboot()
    while c_addr < e_addr:
        write_memory_to_i2c(c_addr)
        result.append(read_from_i2c())
        c_addr += 0x1

    end_time = datetime.datetime.utcnow()
    print('[-] Complete in {0}\n'.format(end_time - start_time))
    print(', '.join(['0x{0:0x}'.format(value) for value in result]))
