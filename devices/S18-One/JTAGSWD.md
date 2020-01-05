## JTAG / SWD

1. [Overview](#overview)

### Overview

Enablement of JTAG is very likely not possible on a retail Sonos One
(Generation 2) [S18] - at least for the A113D SoC. This is based on the
use of OTP fuses to set a `DISABLE_JTAG` flag.

Though it's unknown how JTAG is disabled when this flag is set at this stage,
the value of the fuse itself cannot be modified (decremented) once set:

```
Sonos Tupelo > socfuse read DISABLE_JTAG
fuse_read(DISABLE_JTAG): 01
Sonos Tupelo > socfuse write DISABLE_JTAG 00
fuse_write(DISABLE_JTAG) succeeded
Sonos Tupelo > socfuse read DISABLE_JTAG
fuse_read(DISABLE_JTAG): 01
```
