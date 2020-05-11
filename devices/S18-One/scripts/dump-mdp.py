'''
Provides a mechanism to process the MDP from a device and output a human
readable view of the data contained within. This script will attempt to find
the MDP inside of the provided image, so a full NAND dump can be provided.
'''

import sys
import json
import pathlib
import struct
import logging
import argparse
import collections

# The MDP is quite large, so let's wrangle it with a namedtuple.
ManufacturerDataPage = collections.namedtuple(
    'ManufacturerDataPage',
    [
        'mdp_magic',
        'mdp_vendor',
        'mdp_model',
        'mdp_submodel',
        'mdp_revision',
        'mdp_serial',
        'mdp_region',
        'mdp_reserved',
        'mdp_copyright_statement',
        'mdp_flags',
        'mdp_hwfeatures',
        'mdp_ch11spurimmunitylevel',
        'mdp_reserved2',
        'mdp_version',
        'mdp2_version',
        'mdp3_version',
        'mdp_pages_present',
        'mdp_authorized_flags',
        'mdp_unused',
        'mdp_fusevalue',
        'mdp_sw_features',
        'mdp_pin',
        'mdp_series_id',
        'mdp_reserved3',
        'u_reserved',
    ]
)

# MDP can be detected using the following magic.
MDP_BE_MAGIC = struct.pack('>I', 0xce10e47d)
MDP_LE_MAGIC = struct.pack('<I', 0xce10e47d)


def main(args):
    '''
    Provides a mechanism to process the MDP from a device and output a human
    readable view of the data contained within. This script will attempt to
    find the MDP inside of the provided image, so a full NAND dump can be
    provided.

    Args:
        args (...): A set of arguments parsed by the Python argparse module.
    '''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
    )
    logger = logging.getLogger(__name__)

    # Normalise / expand the input path.
    input_path = pathlib.Path(args.input).expanduser().resolve()

    # Open and process the input file in chunks - looking for the magic. This
    # is in order to keep the memory footprint as low as possible.
    buffer = bytearray()
    mdp_offset = None
    bigendian = False

    try:
        logger.info(
            'Attempting to locate MDP in %s, this may take some time',
            input_path
        )
        with open(input_path, 'rb') as fin:
            pointer = 0x0
            while True:
                chunk = fin.read(0x4)
                if not chunk:
                    break

                # Check if we have a match and if so track endianness.
                if chunk == MDP_LE_MAGIC or chunk == MDP_BE_MAGIC:
                    mdp_offset = pointer
                    if chunk == MDP_BE_MAGIC:
                        bigendian = True
                    else:
                        bigendian = False

                    # Read the next 0x5196 bytes - 0x5200 including this chunk.
                    buffer.extend(chunk)
                    buffer.extend(fin.read(0x5200 - 0x4))
                    break

                # Increment pointer and loop.
                pointer += 0x4
    except IOError as err:
        logger.fatal('Unable to read from %s: %s', input_path, err)
        sys.exit(-1)

    # We can't continue if no MDP was found.
    if mdp_offset is None:
        logger.fatal('Could not find MDP, cannot continue')
        sys.exit(-2)
    
    endianness = '>'
    if bigendian:
        logger.info('Located MDP at 0x%08x (big endian)', mdp_offset)
    else:
        endianness = '<'
        logger.info('Located MDP at 0x%08x (little endian)', mdp_offset)

    # Unpack the MDP.
    mdp = ManufacturerDataPage(
        *struct.unpack(
            '{0}IIIII8pII64sIIB3pIIIIIIII8p4p100p256p'.format(endianness),
            buffer[:512]
        )
    )
    for field in mdp._fields:
        logger.info(
            '{0:26s}: {1}'.format(field, mdp._asdict().get(field))
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sonos MDP Dumper',
    )
    parser.add_argument(
        '--input',
        help='The input file to process the MDP from [default: mmcblk0.bin]',
        default='mmcblk0.bin'
    )
    main(parser.parse_args())
