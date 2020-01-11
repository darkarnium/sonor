'''
A quick helper to take an input kernel gzip and output an ITS (Image Tree
Source) data line for its contents.

Author: Peter Adkins (@Darkarnium)

'''

import sys
import struct
import pathlib
import collections


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: gzip-to-its.py <kernel.gz> <cache>')
        sys.exit(-1)

    in_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    out_path = pathlib.Path(sys.argv[2]).expanduser().resolve()

    # Load the ITB.
    print('[-] Attempting to load Gzip from {0}'.format(in_path))
    with open(in_path, 'rb') as fin:
        kernel = fin.read()

    # Iterate over in 4-byte chunks.
    c_addr = 0
    kernel_data = ''
    while c_addr <= len(kernel):
        # Add header and trailer.
        if c_addr == 0:
            kernel_data += 'data = <'

        if c_addr >= len(kernel):
            kernel_data += '>;\n'
            break

        increment = 4
        token = '>I'
        sz = len(kernel) - c_addr
        if sz < 4:
            if sz == 1:
                increment = 1
                token = 'B'
            elif sz == 2:
                increment = 2
                token = '>H'
            else:
                increment = 3
                token = '>3B'

        # Add encoded, byte-swapped bytes as string.
        kernel_data += '0x{0:0x} '.format(
            struct.unpack(token, kernel[c_addr:c_addr + increment])[0]
        )
        c_addr += increment

    with open(out_path, 'w') as fout:
        fout.write(kernel_data)
