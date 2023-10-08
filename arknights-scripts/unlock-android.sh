#!/bin/sh

adb shell dumpsys power | grep "Display Power: state=On" | xargs -0 test -z && adb shell input keyevent KEYCODE_WAKEUP
adb shell input touchscreen swipe 930 880 930 380
sleep 1
adb shell input touchscreen swipe 930 880 930 380
adb shell input text 154306

