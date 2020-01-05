## Sources

1. [Usage](#usage)
1. [U-Boot](#u-boot)

Unfortunately, it appears that the build root referenced in the public Amlogic
documentation is no longer accessible via the published URL. In addition to
this, access to an alternate Git source requires an account:

* [Amlogic_A311D_Buildroot_Preview_Release_Notes_V20180706.pdf](http://openlinux.amlogic.com:8000/download/doc/Amlogic_A311D_Buildroot_Preview_Release_Notes_V20180706.pdf)

However, a few relevant resources appear to be mirrored in a number of
locations which have been submoduled into this directory. These have not
been mirrored in this repository as they may be liable for take-down requests
due to the potential for them to include 'propriatary code'.

### Usage

Perform a recursive clone of the submodules in the root of this repository in
order to clone these:

```
cd ../../../
git submodule update --init
```

### U-Boot

Though far from identical to the Sonos unit, the submoduled U-Boot sources
contain support for an Amlogic S400 development board. This board appears to
use the same SoC, and may serve as a reference point for how the Sonos U-Boot
image _may_ have been constructed - given that this is proprietary.

* [Amlogic S400 README](./u-boot-amlogic/board/amlogic/s400/README)
