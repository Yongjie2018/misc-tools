#!/bin/bash

echo test exit code 0~5
for x in 0 1 2 3 4 5;                        do ./a.out $x; echo $?; done

echo test exit code 0~-5
for x in 0 -1 -2 -3 -4 -5;                   do ./a.out $x; echo $?; done

echo test exit code 0~-5, -255, -256, 255, 256
for x in 0 -1 -2 -3 -4 -5 -255 -256 255 256; do ./a.out $x; echo $?; done

echo test exit code 124~130
for x in 124 125 126 127 128 129 130;        do ./a.out $x; echo $?; done

echo test exit code 124~130 with tool exit
for x in 124 125 126 127 128 129 130;        do exit $x;    echo $?; done

