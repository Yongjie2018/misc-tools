#!/bin/sh

DATESTR="$(date +"%FT%T")"
adb shell screencap -p /sdcard/screen.cap.$DATESTR.png
adb pull /sdcard/screen.cap.$DATESTR.png
adb shell rm -f /sdcard/screen.cap.$DATESTR.png

