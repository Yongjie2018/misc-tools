#!/bin/bash

x=4
e=24
#let e=$x+24

while [ $x -lt $e ]; do
	echo 1 > /sys/devices/system/cpu/cpu$x/online
	echo $x
	let x=$x+1
done

let x=24
let e=$e+24
while [ $x -lt $e ]; do
	echo 1 > /sys/devices/system/cpu/cpu$x/online
	echo $x
	let x=$x+1
done

let x=48
let e=$e+24
while [ $x -lt $e ]; do
	echo 1 > /sys/devices/system/cpu/cpu$x/online
	echo $x
	let x=$x+1
done

let x=72
let e=$e+24
while [ $x -lt $e ]; do
	echo 1 > /sys/devices/system/cpu/cpu$x/online
	echo $x
	let x=$x+1
done
