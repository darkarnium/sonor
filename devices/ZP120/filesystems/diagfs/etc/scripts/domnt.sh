#!/bin/sh

# default settings
IP=""
HOME="/home"

# parse if called with one command line argument
if [ "$#" = "1" ]; then
    IP="$1"
fi

# parse if called with two command line arguments
if [ "$#" = "2" ]; then
    IP="$1"
    HOME="$2"
fi

if [ "$IP" = "" ]; then
    # argument 1 is required and argument 2 is optional
    echo "usage: $0 <ip_address> [home_absolute_path]"
    echo "     examples: $0 10.20.32.237"
    echo "               $0 10.20.1.15 /home"
    exit 1
fi

if [ ! -f /jffs/sunrpc.o ]; then
    ARCH=`uname -m`
    if [ "$ARCH" = "sh4" ]; then
        wget -O /jffs/sunrpc.o http://10.20.32.240/~build/nfs/sh4/sunrpc.o
        wget -O /jffs/lockd.o  http://10.20.32.240/~build/nfs/sh4/lockd.o
        wget -O /jffs/nfs.o    http://10.20.32.240/~build/nfs/sh4/nfs.o
    elif [ "$ARCH" = "ppc" ]; then
        wget -O /jffs/sunrpc.o http://10.20.32.240/~build/nfs/ppc/sunrpc.o
        wget -O /jffs/lockd.o  http://10.20.32.240/~build/nfs/ppc/lockd.o
        wget -O /jffs/nfs.o    http://10.20.32.240/~build/nfs/ppc/nfs.o
    else
        echo "error: modules have not been built for the '${ARCH}' architecture"
        exit 1
    fi
fi

insmod /jffs/sunrpc.o
insmod /jffs/lockd.o
insmod /jffs/nfs.o

/bin/mount -t nfs -o nolock,soft,vers=2 ${IP}:"${HOME}" /mnt
