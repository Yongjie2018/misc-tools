//Compile with `gcc -O2 -o sendSMI sendSMI.c'

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/io.h>
#include <signal.h>

#define PORT 0xB2

void signal_handler(int sn)
{
    if (ioperm(PORT, 4, 0)) { perror("ioperm"); exit(1); }

    exit(sn);
}


int main()
{
    signal(SIGINT, signal_handler);

    if (ioperm(PORT, 4, 1)) { perror("ioperm"); exit(1); }

    for (;;) {
        outb(1, PORT);
        system("sudo rdmsr -a 0x34 | sort -u >/dev/null");
        usleep((rand() % 160000) + 500);
    }

    exit(0);
}
