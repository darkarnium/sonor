#
# checkroot.sh	Check to root file system.
#
# Version:	@(#)checkroot.sh  2.78-4  25-Jun-2000  miquels@cistron.nl
#
# chkconfig: S 10 0
#

. /etc/default/rcS

#
# Set SULOGIN in /etc/default/rcS to yes if you want a sulogin to be spawned
# from this script *before anything else* with a timeout, like SCO does.
#
[ "$SULOGIN" = yes ] && sulogin -t 30 $CONSOLE

#
# Activate the swap device(s) in /etc/fstab. This needs to be done
# before fsck, since fsck can be quite memory-hungry.
#
if [ -x /sbin/swapon ]
then
  mount -n /proc
  if ! grep -qs resync /proc/mdstat
  then
	[ "$VERBOSE" != no ] && echo "Activating swap..."
	swapon -a 2> /dev/null
  fi
  umount -n /proc
fi

#
# Ensure that bdflush (update) is running before any major I/O is
# performed (the following fsck is a good example of such activity :).
#
[ -x /sbin/update ] && update

#
# Read /etc/fstab.
#
exec 9>&0 </etc/fstab
rootmode=rw
rootopts=rw
rootcheck=yes
devfs=
while read fs mnt type opts dump pass junk
do
	case "$fs" in
		""|\#*)
			continue;
			;;
	esac
	[ "$type" = devfs ] && devfs="$fs"
	[ "$mnt" != / ] && continue
	rootopts="$opts"
	[ "$pass" = 0 ] && rootcheck=no
	case "$opts" in
		ro|ro,*|*,ro|*,ro,*)
			rootmode=ro
			;;
	esac
done
exec 0>&9 9>&-

#
# Check the root file system.
#
if [ -f /fastboot ] || [ $rootcheck = no ]
then
  [ $rootcheck = yes ] && echo "Fast boot, no file system check"
else
  #
  # Ensure that root is quiescent and read-only before fsck'ing.
  #
  mount -n -o remount,ro /
  if [ $? = 0 ]
  then
    if [ -f /forcefsck ]
    then
	force="-f"
    else
	force=""
    fi
    if [ "$FSCKFIX" = yes ]
    then
	fix="-y"
    else
	fix="-a"
    fi
    echo "Checking root file system..."
    fsck -C $force $fix /
    #
    # If there was a failure, drop into single-user mode.
    #
    # NOTE: "failure" is defined as exiting with a return code of
    # 2 or larger.  A return code of 1 indicates that file system
    # errors were corrected but that the boot may proceed.
    #
    if [ $? -gt 1 ]
    then
      # Surprise! Re-directing from a HERE document (as in
      # "cat << EOF") won't work, because the root is read-only.
      echo
      echo "fsck failed.  Please repair manually and reboot.  Please note"
      echo "that the root file system is currently mounted read-only.  To"
      echo "remount it read-write:"
      echo
      echo "   # mount -n -o remount,rw /"
      echo
      echo "CONTROL-D will exit from this shell and REBOOT the system."
      echo
      # Start a single user shell on the console
      /sbin/sulogin $CONSOLE
      reboot -f
    fi
  else
    echo "*** ERROR!  Cannot fsck root fs because it is not mounted read-only!"
    echo
  fi
fi

#
#	If the root filesystem was not marked as read-only in /etc/fstab,
#	remount the rootfs rw but do not try to change mtab because it
#	is on a ro fs until the remount succeeded. Then clean up old mtabs
#	and finally write the new mtab.
#
mount -n -o remount,$rootopts /
if [ "$rootmode" = rw ]
then
	rm -f /etc/mtab~ /etc/nologin
	: > /etc/mtab
	mount -f -o remount,$rootopts /
	mount /proc
	[ "$devfs" ] && grep -q '^devfs /dev' /proc/mounts && mount -f "$devfs"
else
	mount -n /proc
fi

