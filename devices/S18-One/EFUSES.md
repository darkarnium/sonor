## eFuses

1. [Retail State](#retail-state)
1. [Fuses](#fuses)

### Fuses

The following has been extracted from the efuse driver from the Sonos GPL
sources:

|Index|Name|Expected Length (Bytes)|
|-|-|-|
|0|`ENABLE_SECURE_BOOT`|1|
|1|`ENABLE_ENCRYPTION`|1|
|2|`REVOKE_KPUB_0`|1|
|3|`REVOKE_KPUB_1`|1|
|4|`REVOKE_KPUB_2`|1|
|5|`REVOKE_KPUB_3`|1|
|6|`ENABLE_ANTIROLLBACK`|1|
|7|`ENABLE_JTAG_PASSWORD`|1|
|8|`ENABLE_SCAN_PASSWORD`|1|
|9|`DISABLE_JTAG`|1|
|10|`DISABLE_SCAN`|1|
|11|`ENABLE_USB_BOOT_PASSWORD`|1|
|12|`DISABLE_USB_BOOT`|1|
|257|`SBOOT_KPUB_SHA`|32|
|259|`JTAG_PASSWD_SHA_SALT`|32|
|260|`SCAN_PASSWD_SHA_SALT`|32|
|263|`SBOOT_AES256_SHA2`|32|
|512|`GP_REE`|16|

### Retail State

The fuses appear to be in the following state on a retail unit:

```
fuse_read(ENABLE_SECURE_BOOT): 01
fuse_read(ENABLE_ENCRYPTION): 01
fuse_read(REVOKE_KPUB_0): 01
fuse_read(REVOKE_KPUB_1): 00
fuse_read(REVOKE_KPUB_2): 00
fuse_read(REVOKE_KPUB_3): 00
fuse_read(ENABLE_ANTIROLLBACK): 00
fuse_read(ENABLE_JTAG_PASSWORD): 00
fuse_read(ENABLE_SCAN_PASSWORD): 00
fuse_read(DISABLE_JTAG): 01
fuse_read(DISABLE_SCAN): 01
fuse_read(ENABLE_USB_BOOT_PASSWORD): 00
fuse_read(DISABLE_USB_BOOT): 01
fuse_read(SBOOT_KPUB_SHA):
96014ed3460b0a136dc0d9fafb05c92e6cc05edf9c7c83be1620c27062c939c3
fuse_read(JTAG_PASSWD_SHA_SALT):
919b8668592db9fdc80e971cba307f04789ccf5e1db0198d3c0efbee5efa3c0d
fuse_read(SCAN_PASSWD_SHA_SALT):
4659e01b96105535097eb51f26b55f4f9536b2f26ab3c0234c59d545ecfb7102
fuse_read(SBOOT_AES256_RAW): skipped (write-only)
fuse_read(SBOOT_AES256_SHA2):
dbb823015c2972f7e632bdd03fbc13e4c330a2e53fe40030c7803f0ba72eb0c7
fuse_read(GP_REE): ffffffffffffffff0000000000000000
fuse_read(CPUID): REMOVED_FROM_OUTPUT_BY_AUTHOR__
```
