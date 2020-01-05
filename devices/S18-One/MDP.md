## MDP (Manufacturer Device Page)

The Sonos One (Generation 2) [S18] appears to have a section of flash for
storage of device specific configuration, known as the Manufacturer Device
Page or MDP.

### U-Boot

Methods exist in U-Boot to read from and write to the MDP. These are as
follows:

* `0x1004DA0` - `sonos_mdp_read(...)`
* `0x1004DB4` - `sonos_mdp_write(...)`

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


### References

* [Sonos GPL 10.6](http://www.sonos.com/documents/gpl/10.6/gpl.html)
