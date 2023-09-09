#!/bin/bash

rm -f hello.c Makefile

cat <<EOF >>hello.c
#include <linux/module.h>
#include <linux/kernel.h>

int init_module(void)
{
        printk(KERN_INFO "Hello world!\n");
        return 0;
}

void cleanup_module(void)
{
	printk(KERN_INFO "Bye world!\n");
}

MODULE_LICENSE("GPL");
EOF

cat <<EOF >>Makefile
obj-m += hello.o
EOF

if make -C /lib/modules/$(uname -r)/build M=$(pwd) modules 2>&1; then
	insmod hello.ko 2>&1
	rmmod hello 2>&1
	dmesg | tail
fi

rm -f hello.c Makefile hello.ko hello.mod.c hello.mod.o hello.o modules.order Module.symvers

