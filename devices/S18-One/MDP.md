## MDP (Manufacturer Device Page)

1. [Overview](#overview)
1. [Structure](#structure)
1. [U-Boot](#u-boot)
    1. [Modify `mdp_authorized_flags`](#modify-mdp_authorized_flags)
1. [References](#references)

### Overview

The Sonos One (Generation 2) [S18] appears to have a section of flash for
storage of unit specific configuration, known as the 'Manufacturer Device
Page' or MDP.

### Structure

This section appears to be `0x5200` bytes long and is defined as the
following structures - per the `mdp.h` from the Sonos GPL packages.

```c
struct smdp {
    struct manufacturing_data_page      mdp;
    struct manufacturing_data_page2     mdp2;
    struct manufacturing_data_page3     mdp3;
};
```

```c
#define MDP_PIN_LENGTH 8
#define MDP_SERIES_ID_LENGTH 4

struct manufacturing_data_page {
    uint32_t mdp_magic;
    uint32_t mdp_vendor;
    uint32_t mdp_model;
    uint32_t mdp_submodel;
    uint32_t mdp_revision;
    uint8_t mdp_serial[8];
    uint32_t mdp_region;
    uint32_t mdp_reserved;
    char mdp_copyright_statement[64];
    uint32_t mdp_flags;
    uint32_t mdp_hwfeatures;
    uint8_t mdp_ch11spurimmunitylevel;
    uint8_t mdp_reserved2[3];
    uint32_t mdp_version;
    uint32_t mdp2_version;
    uint32_t mdp3_version;
    uint32_t mdp_pages_present;
    uint32_t mdp_authorized_flags;
    uint32_t mdp_unused;
    uint32_t mdp_fusevalue;
    uint32_t mdp_sw_features;
    char mdp_pin[MDP_PIN_LENGTH];
    char mdp_series_id[MDP_SERIES_ID_LENGTH];
    uint8_t mdp_reserved3[100];
    union {
        uint8_t u_reserved[256];
        struct {
            int32_t mdp_zp_dcofs[4];
        } zp;
    } u;
};
```

```c
struct manufacturing_data_page2 {
    uint32_t mdp2_magic;
    uint32_t mdp2_keylen;
    union {
        uint8_t mdp2_key[4088];
        struct {
            uint8_t old_rsa_private[708];
            uint8_t old_rsa_sig[128];
            uint8_t old_fsn_sig[128];
            uint8_t old_unit_sig[128];
            uint32_t  old_variant;

            uint8_t old_reserved[4088 - (708 + (128 * 3) + 4)];
        } ;
        struct {
            uint8_t prod_rsa_private[1024];
            uint8_t prod_unit_sig[128];
            uint32_t  prod_cert_flags;

            uint8_t dev_rsa_private[1024];
            uint8_t dev_unit_sig[128];
            uint32_t  dev_cert_flags;

            uint8_t prod_rsa_sig[128];
            uint8_t dev_rsa_sig[128];

            uint32_t  variant;


            uint8_t dev_reserved[4088 - ((1024 * 2) + (128 * 4) + (4 * 3))];
        } ;
    } mdp2_sigdata;
};
```

```c
struct manufacturing_data_page3 {
    uint32_t mdp3_magic;
    uint32_t mdp3_version;
    uint8_t mdp3_reserved[376];

    uint8_t mdp3_auth_sig[512];
    uint8_t mdp3_cpuid_sig[512];

    uint8_t mdp3_fskey1[256];
    uint8_t mdp3_fskey2[256];
    uint8_t mdp3_model_private_key[2048];

    uint8_t mdp3_prod_unit_rsa_key[2048];
    uint8_t mdp3_prod_unit_rsa_cert[2048];
    uint8_t mdp3_dev_unit_rsa_key[2048];
    uint8_t mdp3_dev_unit_rsa_cert[2048];

    uint8_t mdp3_reserved2[4096 + 128];
};
```

### U-Boot

Methods exist in U-Boot to read from and write to the MDP. These are as
follows:

* `0x1004DA0` - `sonos_mdp_read(...)`
* `0x1004DB4` - `sonos_mdp_write(...)`

#### Modify `mdp_authorized_flags`

Patch the address of the `printf` operation in the `do_mdp` command to print
`mdp3_version` in place of `mdp_sw_features` when the `mdp` command is run
without arguments. This should be done to ensure offsets are calculated
correctly as a bad write to the MDP would be extremely problematic, and may
not be recoverable.

If successful the value of `MDP sw_features` should read `2` rather than `0`.
This is due to the `mdp3_version` member from the `manufacturing_data_page`
being read, rather than `mdp_sw_features` - as the patch changes the offset
from `0x220` to `0x200`.

```shell
#
# Original - mdp_sw_features
# 
# 0x10051F0 - LDR	W1, [X29, #220] - (A1 DF 40 B9)
# 1 0 1 1 1 0 0 1 0 1 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 0 1 0 0 0 0 1
#                     \_____________________/\________/\________/
#                              IMM12             Rn        Rt
#
$ python3 i2c-thief.py 0x10051F0 0x10051F4

#
# Patch to mdp3_version
# 
# 0x10051F0 - LDR	W1, [X29, #200] - (A1 CB 40 B9)
# 1 0 1 1 1 0 0 1 0 1 0 0 0 0 0 0 1 1 0 0 1 0 1 1 1 0 1 0 0 0 0 1
#                     \_____________________/\________/\________/
#                              IMM12			Rn         Rt
#
$ python3 i2c-thief.py 0x10051F0 0x10051F4
$ python3 write-what-where.py 0x10051F1 0xCB

#
# Confirm the `mdp` command now returns `mdp3_version` in place of
# `sw_features`
#
$ stty -F /dev/ttyUSB0 min 100 time 2
$ echo 'mdp' > /dev/ttyUSB0 && cat /dev/ttyUSB0
MDP is initialized, diags are disabled
MDP model is 26
MDP MDP_FLAG_HAS_VERSION yes
MDP mdp_version 4
MDP mdp2_version 5
MDP mdp3_version 2
MDP mdp_pages_present 7
MDP auth_flags 0
MDP sw_features 2
Sonos Tupelo > ^C
```

Next, reboot the unit before attempting to patch. A reboot must be performed
before patching to ensure everything is clean. Failure to do so may cause
irreparable damage to the MDP.

After a reboot use the `mdp sw_features` command to set `mdp_sw_features` to
the same value as will be set later in `mdp_authorized_flags`:

```shell
#
#   MDP_AUTH_FLAG_KERNEL_PRINTK_ENABLE = 0x00000001 
#   MDP_AUTH_FLAG_CONSOLE_ENABLE = 0x00000002
#   MDP_AUTH_FLAG_TELNET_ENABLE = 0x00000008
#   MDP_AUTH_FLAG_EXEC_ENABLE = 0x00000010
#   MDP_AUTH_FLAG_UBOOT_UNLOCK_ENABLE = 0x00000020
#   
#   print(
#       '{0:08x}'.format(
#           MDP_AUTH_FLAG_KERNEL_PRINTK_ENABLE |
#           MDP_AUTH_FLAG_CONSOLE_ENABLE |
#           MDP_AUTH_FLAG_TELNET_ENABLE |
#           MDP_AUTH_FLAG_EXEC_ENABLE |
#           MDP_AUTH_FLAG_UBOOT_UNLOCK_ENABLE
#       )
#   )
#
mdp sw_features 0000003b
```

Patch the `do_mdp` command so that the `sw_features` subcommand writes the
specified value to the address of `mdp_authorized_flags`, rather than to
`mdp_sw_features`. This provides an easy way of writing to
`mdp_authorized_flags` which is not possible using the `mdp` command without
modification.

```shell
#
# Original - mdp_sw_features
# 
# 0x1005024 - STR	W0, [X29, #220] - (A0 DF 00 B9)
# 1 0 1 1 1 0 0 1 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 0 1 0 0 0 0 0
#                     \_____________________/\________/\________/
#                              IMM12             Rn        Rt
$ python3 i2c-thief.py 0x1005024 0x1005028

# 
# Patch to mdp_authorized_flags
# 
# 0x1005024 - STR	W0, [X29, #208] - (A0 D3 00 B9)
# 1 0 1 1 1 0 0 1 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 0 1 0 0 0 0 0
#                     \_____________________/\________/\________/
#                              IMM12             Rn        Rt
#
$ python3 i2c-thief.py 0x1005024 0x1005028
$ python3 write-what-where.py 0x1005025 0xD3
```

Use the now modified `mdp sw_features` command to write the following flags
to `mdp_authorized_flags`. This should be done via a terminal emulator if
performed interactively, as a `Really modify MDP info <y/N>` prompt must be
answered before writes will occur:

```shell
#
#   MDP_AUTH_FLAG_KERNEL_PRINTK_ENABLE = 0x00000001 
#   MDP_AUTH_FLAG_CONSOLE_ENABLE = 0x00000002
#   MDP_AUTH_FLAG_TELNET_ENABLE = 0x00000008
#   MDP_AUTH_FLAG_EXEC_ENABLE = 0x00000010
#   MDP_AUTH_FLAG_UBOOT_UNLOCK_ENABLE = 0x00000020
#   
#   print(
#       '{0:08x}'.format(
#           MDP_AUTH_FLAG_KERNEL_PRINTK_ENABLE |
#           MDP_AUTH_FLAG_CONSOLE_ENABLE |
#           MDP_AUTH_FLAG_TELNET_ENABLE |
#           MDP_AUTH_FLAG_EXEC_ENABLE |
#           MDP_AUTH_FLAG_UBOOT_UNLOCK_ENABLE
#       )
#   )
#
mdp sw_features 0000003b
```

Use the `mdp` command to confirm that the new `mdp_authorized_flags` value
has been written, and reboot.

```shell
$ stty -F /dev/ttyUSB0 min 100 time 2
$ echo 'mdp' > /dev/ttyUSB0 && cat /dev/ttyUSB0
MDP is initialized, diags are disabled
MDP model is 26
MDP MDP_FLAG_HAS_VERSION yes
MDP mdp_version 4
MDP mdp2_version 5
MDP mdp3_version 2
MDP mdp_pages_present 7
MDP auth_flags 3b
MDP sw_features 0
Sonos Tupelo > ^C
```

### References

* [Sonos GPL 10.6](http://www.sonos.com/documents/gpl/10.6/gpl.html)
