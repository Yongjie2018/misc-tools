#!/bin/bash


res_x=1120
res_y=1111
p_x=0
p_y=0

loop=0

if [ $# -ne 2 ]; then 
	echo "Usage: $0 <times> <duration>"
	exit
fi

cycle=$1

min=0
sec=0

rand=0

while [ $loop -lt $cycle ]
do
	# tap kai shi xing dong
	let p_x=152
	let p_y=98
	let p_x=$p_x*$res_x/100
	let p_y=$p_y*$res_y/100
	echo -n "[$loop] starting [$p_x, $p_y],"
	adb shell input touchscreen tap $p_x $p_y
	sleep 3

	# tap kai shi xing dong, the bigger button
	let p_x=150
	let p_y=75
	let p_x=$p_x*$res_x/100
	let p_y=$p_y*$res_y/100
	echo "[$p_x, $p_y]"
	adb shell input touchscreen tap $p_x $p_y
	
	# 4-4 needs 2:30 + 15s
	# LS-5, zhan shu yan xi needs 2:15 + 15s
	# CE-5, huo wu yun song needs 2:05 + 15s

	let duration=$2+15
	while [ $duration -gt 0 ]
	do
		let min=$duration/60
		let sec=$duration%60
		echo -ne "$min:$sec \r"
		sleep 1
		let duration=$duration-1
	done

	# add some random delay to fool ArkNights possible censorship
	let rand=$RANDOM%5
	sleep $rand
	
	# tap the score screen 1st
	let p_x=150
	let p_y=54
	let p_x=$p_x*$res_x/100
	let p_y=$p_y*$res_y/100
	echo -n "[$loop] ending [$p_x, $p_y],"
	adb shell input touchscreen tap $p_x $p_y
	sleep 1
	
	# tap the score screen 2nd
	let p_x=150
	let p_y=54
	let p_x=$p_x*$res_x/100
	let p_y=$p_y*$res_y/100
	echo "[$p_x, $p_y]"
	adb shell input touchscreen tap $p_x $p_y
	
	# wait for 5 second to avoid starting next cycle too soon
	sleep 5

	# add some random delay to fool ArkNights possible censorship
	let rand=$RANDOM%5
	sleep $rand
	
	let loop=$loop+1

done

echo "Accomplished $cycle cycle(s) of $0"

