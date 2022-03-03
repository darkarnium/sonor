#!/bin/sh


case "$1" in
    sonosnet|station|open|credcheck|deauth|wfacert|wacexit|up)
        MODE="$1"
        WAC=0
        ;;
    wacstart|wacapclose|wactimeout)
        MODE="$1"
        WAC=1
        ;;
    waccredcheck)
        MODE=credcheck
        WAC=1
        ;;
    wacapopen)
        MODE=open
        WAC=1
        ;;
    wacstation)
        MODE=station
        WAC=1
        ;;
    *)
        echo "Illegal mode!"
        exit 1
        ;;
esac

PARAM1="$2"
PARAM2="$3"

MODEL=`/bin/mdputil | /usr/sbin/keyval ^MODEL`
SUBMODEL=`/bin/mdputil | /usr/sbin/keyval ^SUBMODEL`
WIFITYPE=`/bin/mdputil | /usr/sbin/keyval ^WIFITYPE`

if [ -f /jffs/debug/testpoints.sh ] && \
   [ "`cat /proc/sonos-lock/exec_enable`" == "1" ]; then
    . /jffs/debug/testpoints.sh || true
fi

if [ "${WAC}" = "0" ]; then
    if [ -f /tmp/wacd.pid ]; then
        kill `cat /tmp/wacd.pid`
        rm -f /tmp/wacd.pid
    fi
fi

if [ "${MODE}" = "wacexit" ]; then
    exit 0
fi

NETSETTINGSFILE=/jffs/netsettings.txt
if [ -f /ramdisk/tmp/netsettings_check.txt ]; then
    USE_SSIDLIST=0
    if [ "${MODE}" = "station" ] || [ "${MODE}" = "credcheck" ]; then
        NETSETTINGSFILE=/ramdisk/tmp/netsettings_check.txt
    fi
else
    USE_SSIDLIST=`cat /jffs/net/settings/ssidlist.txt | /usr/sbin/keyval ^UseSSIDList`
    if [ "${MODE}" = "credcheck" ]; then
        echo "credcheck file not found"
        exit 1
    fi
fi

ATHCONFIG=/wifi/athconfig

killall wpa_supplicant
if [ "${MODE}" = "station" ] || [ "${MODE}" = "credcheck" ]; then
    if [ "${PARAM1}" != "external" ]; then
        rm -f /var/run/wpa_supplicant.conf

        if [ -f /jffs/debug/wpa_supplicant.conf ]; then
            WPACONFIG=/jffs/debug/wpa_supplicant.conf
	    WPACONFIGOUT="/dev/null"
        else
            WPACONFIG=/var/run/wpa_supplicant.conf
	    WPACONFIGOUT=${WPACONFIG}
	fi

	if [ "${USE_SSIDLIST}" = "1" ]; then
            SSID_FILE=1 /wifi/wpaconfig /jffs/net/settings/ssidlist.txt ${WPACONFIGOUT}
	else
            SSID_FILE=0 /wifi/wpaconfig ${NETSETTINGSFILE} ${WPACONFIGOUT}
	fi

        if [ -f /jffs/debug/supplicant ]; then
            WPADEBUG="-dd -t -K"
        else
            WPADEBUG="-t"
        fi

        if [ -f /jffs/debug/wpa_supplicant ] && \
           [ "`cat /proc/sonos-lock/exec_enable`" == "1" ]; then
            WPABIN=/jffs/debug/wpa_supplicant
        else
            WPABIN=/wifi/wpa_supplicant
        fi
    fi
    KEYHEX=`/usr/sbin/keyval ^NFWPwd ${NETSETTINGSFILE}`
    SSIDHEX=`/usr/sbin/keyval ^NFWSSID ${NETSETTINGSFILE}`
fi

if [ "${MODE}" = "credcheck" ]; then

    $ATHCONFIG stasetenable ath0 2
    if [ "${PARAM1}" = "external" ]; then
        /wifi/iwpriv apcli0 set Apcli_Clear_Nw_Profile=255
        if [ "${USE_SSIDLIST}" = "1" ]; then
            prof_num=0
            while read LINE
            do
                SSIDHEX=`echo "${LINE}" | /usr/sbin/keyval ^SSID | cut -d: -f 1`
                KEYHEX=`echo "${LINE}" | /usr/sbin/keyval ^SSID | cut -d: -f 2`

                if [ "${#SSIDHEX}" -ne "0" ]; then
                    if [ "${#KEYHEX}" -ne "0" ]; then
                        /wifi/iwpriv apcli0 set Apcli_Nw_Profile="${prof_num}:${SSIDHEX}:WPAPSKWPA2PSK:TKIPAES:${KEYHEX}:1"
                    else
                        /wifi/iwpriv apcli0 set Apcli_Nw_Profile="${prof_num}:${SSIDHEX}:OPEN:NONE:00:1"
                    fi
                    prof_num=`expr $prof_num + 1`
                fi
            done < /jffs/net/settings/ssidlist.txt
        else
            if [ "${#KEYHEX}" -ne "0" ]; then
                /wifi/iwpriv apcli0 set Apcli_Nw_Profile="0:${SSIDHEX}:WPAPSKWPA2PSK:TKIPAES:${KEYHEX}:1"
            else
                /wifi/iwpriv apcli0 set Apcli_Nw_Profile="0:${SSIDHEX}:OPEN:NONE:00:1"
            fi
        fi
        /wifi/iwpriv apcli0 set ApCliEnable=1
    else
        ${WPABIN} -s -B -D sonos -i ath0 -c ${WPACONFIG} ${WPADEBUG}
    fi

    exit 0
fi


if [ "${WAC}" = "0" ] && [ "${MODE}" != "open" ]; then
    touch /var/run/waitforip
else
    rm -f /var/run/waitforip
fi

if [ -f /tmp/udhcpc.pid ]; then kill `cat /tmp/udhcpc.pid`; fi
if [ -f /tmp/udhcpc.eth0.pid ]; then kill `cat /tmp/udhcpc.eth0.pid`; fi

$ATHCONFIG setopenmode ath0 DISABLE
$ATHCONFIG stasetenable ath0 0
$ATHCONFIG stasetenable ath1 0
$ATHCONFIG scanabort ath0
$ATHCONFIG satenable ath0 0

/usr/sbin/brctl delif br0 eth0
/usr/sbin/brctl delif br0 eth1

/sbin/ifconfig apcli0 down

/sbin/ifconfig ath0 down
/sbin/ifconfig ath1 down

/sbin/ifconfig br0 down
/usr/sbin/brctl delbr br0

if [ "${MODE}" = "deauth" ]; then
    /usr/sbin/brctl addbr br0
    BRMAC=`/usr/sbin/setmac -S | /usr/sbin/keyval ^br0`
    /usr/sbin/brctl setmac br0 ${BRMAC}

    /sbin/ifconfig ath0 0.0.0.0
    exit 0
fi

AP=""
WEPKEY="disable"
HHID=""
CHANNEL=2412
BONJOURNAME=""
PRIMARYUUID=""
PRIORITYBR=0
HAVE_NETSETTINGS=0
if [ -f ${NETSETTINGSFILE} ]; then
    HAVE_NETSETTINGS=1
    WEPKEY=`/usr/sbin/keyval ^WEPKey ${NETSETTINGSFILE}`
    HHID=`/usr/sbin/keyval ^HouseholdID ${NETSETTINGSFILE}`
    CHANNEL=`/usr/sbin/keyval ^Channel ${NETSETTINGSFILE}`
    PRIORITYBR=`/usr/sbin/keyval ^PriorityBridge ${NETSETTINGSFILE}`
    BONJOURNAME=`/usr/sbin/keyval -s BonjourName ${NETSETTINGSFILE}`
    PRIMARYUUID=`/usr/sbin/keyval ^PrimaryUUID ${NETSETTINGSFILE}`
fi

if [ "${MODE}" = "open" ]; then

    if [ "${PARAM2}z" != "z" ]; then
        CHANNEL=${PARAM2}
    fi

    if [ -f /jffs/debug/openchannel ]; then
        CHANNEL=`cat /jffs/debug/openchannel`
    fi

    /usr/sbin/setmac -L

    /sbin/ifconfig eth0 0.0.0.0
    /sbin/ifconfig eth1 0.0.0.0

    $ATHCONFIG setchannel ath0 $CHANNEL
    $ATHCONFIG setopenmode ath0 $PARAM1

    /sbin/ifconfig ath0 10.69.69.1
    /sbin/ifconfig apcli0 0.0.0.0

    /sbin/route add 255.255.255.255 ath0
    /sbin/route add -net 224.0.0.0 netmask 240.0.0.0 ath0
    exit 0

fi

/usr/sbin/brctl addbr br0
/usr/sbin/brctl sethello br0 1.0
/usr/sbin/brctl setfd br0 4.0
/usr/sbin/brctl setmaxage br0 6.0

if [ "${MODE}" = "sonosnet" ]; then

    BRMAC=`/usr/sbin/setmac | /usr/sbin/keyval ^br0`

    /sbin/ifconfig eth0 0.0.0.0
    /sbin/ifconfig eth1 0.0.0.0

    /usr/sbin/brctl addif br0 eth0
    /usr/sbin/brctl addif br0 eth1

    /usr/sbin/brctl uplink br0 0

    echo -n "0" > /var/run/netmanager_extender_flags.tmp
    mv -f /var/run/netmanager_extender_flags.tmp /var/run/netmanager_extender_flags

else

    BRMAC=`/usr/sbin/setmac -S | /usr/sbin/keyval ^br0`

    /sbin/ifconfig eth0 0.0.0.0
    /sbin/ifconfig eth1 0.0.0.0

    /usr/sbin/brctl uplink br0 1
fi

if [ "${MODEL}" = "5" ]; then
    /sbin/ifconfig eth0 txqueuelen 100
fi

/usr/sbin/brctl setmac br0 ${BRMAC}


UUIDA=`/sbin/ifconfig eth0 | /usr/sbin/keyval -d: HWaddr`
UUIDP=`/usr/sbin/keyval ^Port /opt/conf/anacapa.conf`
UUID='RINCON_'$UUIDA'0'$UUIDP

$ATHCONFIG setwepkey ath0 $WEPKEY
$ATHCONFIG setssid ath0 $HHID
$ATHCONFIG setchannel ath0 $CHANNEL
$ATHCONFIG ssidinbeaconenable ath0 0
$ATHCONFIG beaconenable ath0 0

if [ "${MODE}" = "station" ] || [ "${MODE}" = "wfacert" ]; then

    $ATHCONFIG stasetenable ath0 1

elif [ "${MODE}" = "up" ]; then

    /sbin/ifconfig ath0 0.0.0.0
    /sbin/ifconfig apcli0 0.0.0.0
    exit 0

elif [ "${MODE}" = "wacstart" ] || [ "${MODE}" = "wactimeout" ]; then
    /sbin/ifconfig ath0 0.0.0.0

    if [ -f /tmp/wacd.pid ]; then kill `cat /tmp/wacd.pid`; fi

    if [ "${MODE}" = "wactimeout" ] ; then
	WACDARG="-timeout"
    fi

    /wifi/wacd $WACDARG

    exit 0

elif [ "${MODE}" = "wacapclose" ]; then
    exit 0
fi

ISHTSATELLITE=0
if [ "${PRIMARYUUID}z" != "z" ]; then
    ISHTSATELLITE=1
    $ATHCONFIG setprimaryuuid ath0 $PRIMARYUUID
    $ATHCONFIG satenable ath0 1

elif ( [ "${MODEL}" = "9" ] || [ "${MODEL}" = "14" ] || [ "${MODEL}" = "23" ] || [ "${MODEL}" = "24" ] || [ "${MODEL}" = "27" ] ) && ( [ "${MODE}" = "sonosnet" ] || [ "${MODE}" = "station" ] ); then

    $ATHCONFIG setuuid ath0 $UUID

    $ATHCONFIG setuuid ath1 $UUID
    $ATHCONFIG acs ath1 1
    $ATHCONFIG acslmenable ath1 1
    $ATHCONFIG setwepkey ath1 $WEPKEY
    $ATHCONFIG setssid ath1 $HHID
fi


if [ "${MODE}" = "wfacert" ] ; then
    if [ "${MODEL}" = "13" ]; then
        $ATHCONFIG settxpower ath0 35
    fi
    $ATHCONFIG forcetxrate ath0 1
    $ATHCONFIG setmcs ath0 -54
fi

if [ "$PRIORITYBR" = "1" ]; then
    /usr/sbin/brctl setbridgeprio br0 28672  # 0x7000
else
    /usr/sbin/brctl setbridgeprio br0 38912  # 0x9800
fi

/sbin/ifconfig br0 0.0.0.0

/sbin/ifconfig ath0 0.0.0.0

/sbin/ifconfig ath1 0.0.0.0
if [ "${ISHTSATELLITE}" = "1" ]; then
    /sbin/ifconfig ath1 down
fi


if [ "${MODE}" = "station" ]; then
    if [ "${PARAM1}" = "external" ]; then
        ifconfig apcli0 up
        /wifi/iwpriv apcli0 set Apcli_Clear_Nw_Profile=255
        if [ -f /jffs/net/settings/ssidlist.txt ]; then
            prof_num=0
            while read LINE
            do
                SSIDHEX=`echo "${LINE}" | /usr/sbin/keyval ^SSID | cut -d: -f 1`
                KEYHEX=`echo "${LINE}" | /usr/sbin/keyval ^SSID | cut -d: -f 2`

                if [ "${#SSIDHEX}" -ne "0" ]; then
                    if [ "${#KEYHEX}" -ne "0" ]; then
                        /wifi/iwpriv apcli0 set Apcli_Nw_Profile="${prof_num}:${SSIDHEX}:WPAPSKWPA2PSK:TKIPAES:${KEYHEX}:1"
                    else
                        /wifi/iwpriv apcli0 set Apcli_Nw_Profile="${prof_num}:${SSIDHEX}:OPEN:NONE:00:1"
                    fi
                    prof_num=`expr $prof_num + 1`
                fi
            done < /jffs/net/settings/ssidlist.txt
        else
            if [ "${#KEYHEX}" -ne "0" ]; then
                /wifi/iwpriv apcli0 set Apcli_Nw_Profile="0:${SSIDHEX}:WPAPSKWPA2PSK:TKIPAES:${KEYHEX}:1"
            else
                /wifi/iwpriv apcli0 set Apcli_Nw_Profile="0:${SSIDHEX}:OPEN:NONE:00:1"
            fi
        fi
        /wifi/iwpriv apcli0 set ApCliEnable=1
    else
        ${WPABIN} -s -B -D sonos -i ath0 -b br0 -c ${WPACONFIG} ${WPADEBUG}
    fi
fi

if [ "${BONJOURNAME}z" != "z" ]; then
    HOST="${BONJOURNAME}"
elif [ "${MODEL}" = "5" ] || [ "${MODEL}" = "12" ]; then
    HOST="SonosZB"
else
    HOST="SonosZP"
fi

/sbin/route add 255.255.255.255 br0
/sbin/route add -net 224.0.0.0 netmask 240.0.0.0 br0

if [ "${MODE}" = "station" ] || [ "${MODE}" = "wfacert" ]; then
    DHCP_FLAGS="-z"
fi

if [ -f /jffs/debug/static_ipaddr ]; then
    ifconfig br0 $(cat /jffs/debug/static_ipaddr)
    rm -f /var/run/waitforip
else
    if [ "${MODEL}" != "5" ]; then
        count=1
        while pidof udhcpc > /dev/null
        do
            sleep 1

            if [ $count -gt 5 ]; then
                killall -SIGKILL udhcpc
                break
            fi
            count=`expr $count + 1`
        done
    fi

    /sbin/udhcpc -f -s /etc/dhcp.script -i br0 -w ath0 -h "${HOST}" -d access.bestbuy.com ${DHCP_FLAGS} &
fi

if [ "${MODE}" = "wfacert" ]; then
    /sbin/udhcpc -f -s /etc/dhcp.eth0.script -i eth0 -p /tmp/udhcpc.eth0.pid -h "${HOST}" ${DHCP_FLAGS} &
fi

exit 0
