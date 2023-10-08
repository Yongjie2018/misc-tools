#!/bin/bash

echo "# python3 --version 2>&1"
python3 --version 2>&1

echo "# ls "$(which python3)"* -l 2>&1"
ls "$(which python3)"* -l 2>&1

echo "# uname -r 2>&1"
uname -r

echo "# ls /boot/config-* -l 2>&1"
ls /boot/config-* -l 2>&1

echo "# cat /boot/config-$(uname -r) 2>&1 | grep DEVMEM"
cat /boot/config-$(uname -r) 2>&1 | grep DEVMEM

echo "# ls -l /lib/modules/$(uname -r)/build 2>&1"
ls -l /lib/modules/$(uname -r)/build 2>&1

echo "# ls -FH /lib/modules/$(uname -r)/build 2>&1"
ls -FH /lib/modules/$(uname -r)/build 2>&1

echo "# find $(ls -l /lib/modules/$(uname -r)/build | sed 's/.*-> //g') -maxdepth 2 2>&1"
find $(ls -l /lib/modules/$(uname -r)/build | sed 's/.*-> //g') -maxdepth 2 2>&1

if echo "$(cat /etc/os-* | grep PRETTY_NAME)" | grep -e "Red Hat" -e "CentOS"; then
	echo "# rpm -qa | grep kernel-headers-$(uname -r) 2>&1"
	rpm -qa | grep kernel-headers-$(uname -r) 2>&1
else
	echo "# apt list linux-headers-$(uname -r) 2>&1"
	apt list linux-headers-$(uname -r) 2>&1
fi
