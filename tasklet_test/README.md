# use tasklet to simulate a softirq stress test
The purpose of this test is to check whether a pending softirq is migrated to another core if the current core is set offline.

# how to test
```
# insmod tasklet_test.ko
# on a 4 cores system, try to disable core 1/2/3 and enable them back for 100 times as a stress
# for x in {1..100}; do echo -n "."; echo 0 > /sys/devices/system/cpu/cpu3/online && echo 0 > /sys/devices/system/cpu/cpu2/online && echo 0 > /sys/devices/system/cpu/cpu1/online; sleep 1; echo 1 > /sys/devices/system/cpu/cpu3/online && echo 1 > /sys/devices/system/cpu/cpu2/online && echo 1 > /sys/devices/system/cpu/cpu1/online; sleep 1; done
# rmmod tasklet_test
# to check the count in "Tasklet migration count xxx"
# dmesg | tail
```