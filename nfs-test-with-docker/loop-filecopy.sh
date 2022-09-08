#!/bin/bash

count=0
log_file=/mnt/logs/$(hostname)-$(date +"%Y-%m-%d-%H-%M-%S").log

mount.nfs 172.18.211.56:/opt/nfs_share /mnt
if [ $? -ne 0 ]; then
	echo "nfs mount failed"
	exit 1
fi

while [ true ]; do
	if [ -f /mnt/start ]; then
		echo "started $(date)" >> ${log_file}
	else
		sleep 0 # yeild
		continue
	fi

	while [ $count -lt 1000 ]; do
		#echo "hello $count" >> ${log_file}
		cp /mnt/32M.bin . -f

		let count=$count+1
	done
	rm 32M.bin -f
	
	echo "stopped $(date)" >> ${log_file}
	break
done
umount /mnt
