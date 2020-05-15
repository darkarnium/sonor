import sys
import serial
import datetime
import logging
import argparse
import string
import time

PROMPT = '=> '
SERIAL_DEVICE = '/dev/ttyUSB0'
SERIAL_BAUD = 38400

# A list of commands to NOT execute.
NOEXECUTE = [
    'nandboot',
    '_recoverme',
]


def console_from_powerup():
    '''
    Attempts to drop the unit into U-Boot console at power-up.
    '''
    buffer = bytes()
    with serial.Serial(SERIAL_DEVICE, SERIAL_BAUD, timeout=10) as interface:
        # Wait until a prompt.
        while True:
            buffer += interface.readline()

            try:
                line = str(buffer, 'utf-8')
            except UnicodeDecodeError:
                buffer = bytes()
                continue

            # Start writing interrupt sequences as early as the 'using default'
            # line. Due to the boot timeout being zero there's a very small
            # window to interrupt the boot process, so we have to start early.
            if line.lower().startswith('using default'):
                interface.write(b'\r\n' * 10)
                buffer = bytes()
                continue

            # Drop out of the loop when we see the U-Boot prompt
            if line.lower().startswith(PROMPT):
                buffer = bytes()
                break

            # Dump the buffer contents if no matches.
            buffer = bytes()


def brute_force_command(start_char, alphabet):
    '''
    Attempts to brute force a command over serial.

    Args:
        start_char (str): The character to start from.
        alphabet (list): The alphabet to use when searching.

    Returns:
        str: The enumerated command
    '''
    ptr = 0
    command = start_char
    with serial.Serial(SERIAL_DEVICE, SERIAL_BAUD, timeout=10) as interface:
        while True:
            # Start again, or finish, when we've exhausted a suitable search
            # space.
            if len(command) > 10:
                return command

            # Return with any detected commands once we've exhausted our
            # alphabet
            if ptr >= len(alphabet):
                if len(command) > 1:
                    return command
                else:
                    return None

            # Build the new command and check whether it's blank, or on the
            # NOEXECUTE list before sending to the device.
            outgoing = '{0}{1}\n'.format(command, alphabet[ptr])
            if not outgoing.strip():
                ptr += 1

            if outgoing.strip() in NOEXECUTE:
                return outgoing.strip()

            # Push the command, and discard loopback.
            interface.write(bytes(outgoing, 'utf-8'))
            interface.readline()

            # Read until prompt, and then check whether the result was as
            # expected
            buffer = bytes()
            while True:
                peek = interface.read(1)
                buffer += peek

                # Break out of the loop if the prompt is detected. 
                if len(buffer) >= len(PROMPT):
                    if str(buffer[-len(PROMPT):], 'utf-8') == PROMPT:
                        break

            try:
                line = str(buffer, 'utf-8')
            except UnicodeDecodeError:
                continue

            if line.lower().startswith('unknown'):
                ptr += 1
            else:
                command += alphabet[ptr]
                ptr = 0


def main(args):
    '''
    Args:
        args (...): A set of arguments parsed by the Python argparse module.
    '''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
    )
    logger = logging.getLogger(__name__)

    # Start by attempting to drop the device into console.
    logger.info('Waiting for U-Boot messages, please power on device now')
    console_from_powerup()
    logger.info('Device at U-Boot console, starting brute force')

    # Kick off the brute force.
    candidates = []
    candidates.extend(list(string.ascii_letters))
    candidates.extend(list(string.digits))
    candidates.append('_')
    candidates.append(' ')

    for candidate in candidates:
        command = brute_force_command(candidate, candidates)
        if command:
            logger.info('Found command {0}'.format(command))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Attempts to brute force U-Boot commands"
    )
    main(parser.parse_args())
