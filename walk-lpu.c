

#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <cpuid.h>
#include <assert.h>

int
main(int argc, char *argv[])
{
    cpu_set_t set;
    int j, ret;

    
    for (int j = 0; j < 8; j++)
    {
	unsigned int eax = 0, ebx = 0, ecx = 0, edx = 0;
        CPU_ZERO(&set);
    	CPU_SET(j, &set);
    	ret = sched_setaffinity(getpid(), sizeof(set), &set);
    	if (-1 == ret)
    	{
            printf("sched_setaffinity");
            continue;
        }

	assert (0 == ret);

	ret = __get_cpuid_count(11, 0, &eax, &ebx, &ecx, &edx);
	assert (1 == ret);

	printf("[logic processor %d] apicid %d\n", j, edx);
    }
    
    return 0;
}

