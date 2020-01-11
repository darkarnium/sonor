#!/usr/bin/env python3
'''
A quick and dirty script to dump a Kernel image from an input ITB (Image Tree
Binary) file. This is intended for use with data dumped from a Sonos One
(Generation 2) [S18].

Oh, by the way: This code is awful, it's PoC grade at best :)

Author: Peter Adkins (@Darkarnium)
'''

import sys
import struct
import pathlib
import collections

from pyfdt.pyfdt import FdtBlobParse


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: dump-kernel-from-itb.py <tree.itb> <kernel.gz>')
        sys.exit(-1)

    in_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    out_path = pathlib.Path(sys.argv[2]).expanduser().resolve()

    # Load the ITB.
    print('[-] Attempting to load ITB from {0}'.format(in_path))
    with open(in_path, 'rb') as fin:
        itb = FdtBlobParse(fin).to_fdt()

    # Locate the Kernel, and process it.
    print('[-] Looking for kernel@1 image in ITB')
    kernel = itb.resolve_path(path='/images/kernel@1')
    kernel_image = None
    kernel_description = None
    kernel_compression = None
    kernel_checksum_type = None
    kernel_checksum_value = None

    for node in kernel:
        # Find the checksum, and type.
        if node.name == 'hash@1':
            for entry in node:
                if entry.name == 'value':
                    kernel_checksum_value = entry.words[0]
                if entry.name == 'algo':
                    kernel_checksum_type = entry.strings[0]

        # Find the description.
        if node.name == 'description':
            kernel_description = node.strings[0]

        # Find the compression type.
        if node.name == 'compression':
            kernel_compression = node.strings[0]

        # Find the data entry.
        if node.name == 'data':
            kernel_image = node.words

    if not kernel_image:
        print('[!] Could not find kernel image in ITB! Cannot continue')
        sys.exit(-1)

    print('[-] Attempting to write kernel to {0}'.format(out_path))
    try:
        with open(out_path, 'wb') as fout:
            for byte in kernel_image:
                fout.write(struct.pack(">I", byte))
    except Exception as err:
        print('[!] Failed to extract kernel: {0}'.format(err))
        sys.exit(-2)

    print('[+] Write complete, have fun! :)')
