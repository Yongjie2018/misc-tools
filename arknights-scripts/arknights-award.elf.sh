#!/bin/bash


res_x=1120
res_y=1111
p_x=0
p_y=0

loop=0

if [ $# -ne 1 ]; then 
	echo "Usage: $0 <times>"
	exit
fi

cycle=$1

min=0
sec=0

while [ $loop -lt $cycle ]
do
	# tap kai shi xing dong
	let p_x=152
	let p_y=25
	let p_x=$p_x*$res_x/100
	let p_y=$p_y*$res_y/100
	echo "[$loop] tapping [$p_x, $p_y]"
	adb shell input touchscreen tap $p_x $p_y
	sleep 1
	
	let loop=$loop+1

done

echo "Accomplished $cycle cycle(s) of $0"

