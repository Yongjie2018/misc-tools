#!/bin/bash

x=1200
y=336

while [ $y -lt 1200 ]
do
	while [ $x -lt 1920 ]
	do
		echo -n "tapping $x $y"
		adb shell input touchscreen tap $x $y
		echo "."
		sleep 1

		let x=$x+10
	done
	let y=$y+10
done
