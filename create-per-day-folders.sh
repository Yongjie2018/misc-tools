#!/bin/bash

function create_day()
{
	my_y=$1
	my_m=$(printf "%02d" $2)
	my_d=$(printf "%02d" $3)

	echo ${my_y}-${my_m}-${my_d}
}

function create_month()
{
	y=$1
	m=$2
	max_d=0

	case $m in
		"1"|"3"|"5"|"7"|"8"|"10"|"12")
			for d in {1..31}
			do
				create_day $y $m $d
			done
			max_d=31
			;;
		"4"|"6"|"9"|"11")
			for d in {1..30}
			do
				create_day $y $m $d
			done
			max_d=30
			;;
		"2")
			if [ `expr $y % 400` -eq 0 ]
			then
				max_d=29
			elif [ `expr $y % 100` -eq 0 ]
			then
				max_d=28
			elif [ `expr $y % 4` -eq 0 ]
			then
				max_d=29
			else
				max_d=28
			fi
			;;
		*)
			echo "Unknown month $m"
			;;
	esac

	for (( d=1; d<=$max_d; d++ ))
	do
		create_day $y $m $d
	done
}

function create_year()
{
	y=$1

	for m in {1..12}
	do
		create_month $y $m
	done
}


function create_folder()
{
	for y in {2022..2024}
	do
		create_year $y
	done
}

create_folder
