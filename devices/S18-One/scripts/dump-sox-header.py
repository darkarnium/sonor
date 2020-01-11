'''
A quick and dirty script to dump the 'Sox' header from the `kernX` partitions
of a Sonos One (Generation 2) [S18].

Oh, by the way: This code is awful, it's PoC grade at best :)

Author: Peter Adkins (@Darkarnium)
'''

import sys
import struct
import pathlib
import collections

SoxHeader = collections.namedtuple(
    'SoxHeader',
    ', '.join(
        [
            'magic',
            'version',
            'bootgen',
            'kernel_offset',
            'kernel_checksum',
            'kernel_length',
        ]
    )
)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: dump-sox-header.py <image.bin>')
        sys.exit(-1)

    filepath = pathlib.Path(sys.argv[1]).expanduser().resolve()
    with open(filepath, 'rb') as fin:
        sox_hdr = SoxHeader._make(
            struct.unpack("<IHHIII12x", fin.read(0x20))
        )

    print(sox_hdr)
