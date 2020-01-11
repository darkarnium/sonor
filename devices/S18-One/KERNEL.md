## Kernel

1. [Overview](#overview)
1. [Obtaining the 'Sox' Image](#obtaining-the-kernel)
1. [Carving the Kernel](#carving-the-kernel)
1. [Dumping `initramfs`](#dumping-initramfs)

### Overview

The Sonos One (Generation 2) [S18] boot image appears to be encapsulated on
disk in an unknown, potentially propriatary, format. This can be identified
by the file magic of `0x21 0x78 0x6f 0x53`. As this value becomes `Sox!` if
the byte order is flipped this image format is referred to as 'Sox' in this
document.

### Obtaining the 'Sox' Image

Firstly, the contents of the `kern0` parition of the unit will need to be
dumped. This can be done by using the provided script in
[`scripts/dump-from-mmc.py`](scripts/dump-from-mmc.py) which allows for
arbitrary data to be dumped from the MMC over the serial console.

Please be aware that this is a slow process, and takes just over two hours to
dump a kernel image.

```bash
# List all partitions on the MMC, and their start and end blocks.
python3 dump-from-mmc.py

# Dump the contents of kern0 to 'kernel.bin'
python3 dump-from-mmc.py kernel.bin 0x00004000 0x0000bfff
```

Once the contents of the `kern0` parition is dumped, the FIT image and kernel
must first be 'carved' from the 'Sox' image.

### Carving the Kernel

Although the 'Sox' image format appears to be custom the layout does not
appear complicated. A Python snippet to parse and dump the known / required
fields from this header can be found in
[`scripts/dumps-sox-header.py`](./scripts/dump-sox-header.py).

One caveat to the above is that the 'kernel offset' output by this script
is not the beginning of the FIT image. Instead it is the location of a
364-Byte signature which the `sonosboot` U-Boot command appears to use to
validate the authenticity of the FIT image. This can simply be discarded as
the `sonosboot` command will not be used when loading modified FIT images
over TFTP. As a result, the 'real' location of the start of the FIT image
should be `k_offset + 364`.

1. Run `dump-sox-header.py` to parse the required information from the
Sox image.
```bash
$ python3 ../scripts/dump-sox-header.py ./kern0.bin
SoxHeader(
    magic=1399814177,
    version=1,
    bootgen=0,
    kernel_offset=64,
    kernel_checksum=1981269588,
    kernel_length=6936732
)
```
2. Carve the FIT from the Sox image using `dd`:
```bash
$ dd if=kern0.bin of=kern0.itb bs=1 skip=$((64 + 364)) count=6936732
```
3. Ensure that the first eight bytes of the extracted image are `d00dfeed`
```bash
$ xxd kern0.itb | head -n 1
00000000: d00d feed 0069 d730 0000 0038 0069 d354  .....i.0...8.i.T
```
4. (Optiona) Convert the extracted `itb` (Image Tree Binary) file into an
Image Tree Source (`its`) file for easier viewing. This can be done using
the `dtc` tool:
```bash
dtc -I dtb -O dts -o kern0.its kern0.itb
```
5. Finally, the Kernel image can be extracted from `/images/kernel@1` using
the `dump-kernel-from-itb.py` script:
```bash
# Dump the kernel gzip.
$ python3  ../scripts/dump-kernel-from-itb.py kern0.itb kern0.gz
[-] Attempting to load ITB from /home/darkarnium/Desktop/Scratch/Sonos/dump/kern0.itb
[-] Looking for kernel@1 image in ITB
[-] Attempting to write kernel to /home/darkarnium/Desktop/Scratch/Sonos/dump/kern0.gz
[+] Write complete, have fun! :)

# Spot check.
$ file kern0.gz
kern0.gz: gzip compressed data, was "Image", last modified: Mon Nov 12 23:29:26 2018, from Unix
```

### Dumping `initramfs`

The following are 'scratch' notes for how to modify the initramfs and repack
both the Kernel and ITB / FIT for booting.

```bash
# Gunzip the Kernel.
$ gunzip kern0.gz

# Dump the initramfs from Kernel
$ dd if=kern0 of=initramfs.gz bs=1 skip=9800328 count=1900200

# Back it up.
$ cp kern0 kern0.original
$ cp initramfs.gz initramfs.original.gz

# Initial size.
$ ls -la initramfs.gz
-rw-rw-r-- 1 darkarnium darkarnium 1900200 Jan 11 18:38 initramfs.gz

# Ensure no trailing garbage.
$ gunzip -v initramfs.gz

# Extract CPIO.
$ mkdir -p rootfs/
$ cp initramfs rootfs/
$ cd rootfs
$ cat initramfs | sudo cpio -idmv
$ rm initramfs

# Patch /init

# Create cpio.
$ find . -print0 | sudo cpio --null --create --verbose --format=newc > initramfs

# Gzip it.
$ gzip initramfs

# Check size, and add pad file to CPIO until same size.
$ ls -la initramfs.gz
-rw-r--r-- 1 darkarnium darkarnium 1899459 Jan 11 18:45 initramfs.gz

# Recheck size, and ensure it matches now.
$ ls -la initramfs.gz
-rw-r--r-- 1 darkarnium darkarnium 1900200 Jan 11 18:51 initramfs.gz

# Patch it in using dd.
$ dd conv=notrunc if=initramfs.gz of=kern0 bs=1 seek=9800328

# Ensure the patched file is the same size.
$ ls -la kern0 kern0.original
-rw-rw-r-- 1 darkarnium darkarnium 12361736 Jan 11 18:54 kern0
-rw-rw-r-- 1 darkarnium darkarnium 12361736 Jan 11 18:52 kern0.original

# Gzip the kernel.
$ gzip --best kern0

# Convert into ITS compatible format.
$ python3 ../scripts/gzip-to-its.py kern0.gz data-fragment.its
```