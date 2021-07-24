#!/bin/sh

set -u
set -e

# Add a console on tty1
if [ -e ${TARGET_DIR}/etc/inittab ]; then
    grep -qE '^tty1::' ${TARGET_DIR}/etc/inittab || \
	sed -i '/GENERIC_SERIAL/a\
tty1::respawn:/sbin/getty -L  tty1 0 vt100 # HDMI console' ${TARGET_DIR}/etc/inittab
fi

if [ -e ${TARGET_DIR}/etc/fstab ]; then
    grep -qE '/mnt/readwrite' ${TARGET_DIR}/etc/fstab || \
    echo "/dev/mmcblk0p3 /mnt/readwrite ext2 defaults 0 2" >> ${TARGET_DIR}/etc/fstab
fi
