#!/bin/bash
#
# THIS SHOULD BE CONSIDERED SCRATCH. THIS WILL VERY LIKELY NOT WORK FOR
# ANY OTHER DEVICE THAN THOSE RUNNING THE FOLLOWING BOOT LOADER VERSION
#
#    2016.11-A113-Strict-Rev0.14
#
#

# Patch 'privileged' commands into U-Boot.
python3 write-what-where.py 0x100CD17 0x34
python3 write-what-where.py 0x100CDAC 0x20
python3 write-what-where.py 0x102564F 0x35

# Patch sonosboot to fail at a critical path.
python3 write-what-where.py 0x3ff26933 0x35

# Trigger sonosboot failure, which seems to finish setting up soemthing
# related to keys required for LUKS.
#
# TODO: Investigate this.
#
stty -F /dev/ttyUSB0 min 100 time 2
echo -en 'sonosboot\n' > /dev/ttyUSB0
sleep 1

# Boot from network.
echo -en 'setenv autostart yes\n' > /dev/ttyUSB0
sleep 1
echo -en 'setenv bootargs console=ttyS0,115200n1 gpt root=/dev/mmcblk0p8 rw no_console_suspend earlycon=aml_uart,0xff803000 bootsect=1 bootgen=2 mdpaddr=0000000000000268 enable_console=1 enable_printk=1\n' > /dev/ttyUSB0
sleep 1
echo -en 'dhcp 0x100040 bootme.img\n' > /dev/ttyUSB0
sleep 1

# Start monitoring.
cat /dev/ttyUSB0
