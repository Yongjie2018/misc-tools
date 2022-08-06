#include <stdio.h> /* printf */
#include <stdlib.h> /* atoi */
#include <fcntl.h> /* O_ constants */
#include <unistd.h> /* ftruncate */
#include <sys/mman.h> /* mmap */
#include <signal.h> /* signal macros */
#include <malloc.h> /* memalign */
#include <sys/stat.h>

typedef void(*FUNC)(void);

void SIGILL_handler(int sig);

int main(int argc, char **argv)
{
    int signal_num;
    int fd;
    int *map;
    int size = sizeof(int);
    char *name = "/a";
    int *bad;
    int pagesize;

    signal_num = atoi(argv[1]);

    switch (signal_num) {
        case SIGBUS:
        shm_unlink(name);
        fd = shm_open(name, O_RDWR | O_CREAT, (mode_t)0600);
        /* THIS is the cause of the problem. */
        /*ftruncate(fd, size);*/
        map = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        /* This is what generates the SIGBUS. */
        *map = 0;
        break;

	case SIGSEGV:
	*(int *)0 = 0;
	break;

	case SIGILL:
	//signal(SIGILL, SIGILL_handler);

        pagesize = sysconf(_SC_PAGE_SIZE);
        if (pagesize == -1) {
            perror("sysconf");
            exit(1);
        }

        /* allocate 16 aligned pages */
        bad = memalign(pagesize, 16 * pagesize);
        if (NULL == bad) {
            printf("aah, out of mem :-(\n");
            exit(1);
        }

        if (-1 == mprotect(bad, 16 * pagesize, PROT_READ | PROT_WRITE | PROT_EXEC)) {
            perror("mprotect");
            exit(1);
        }

	//*bad = malloc(16);
        //memset(bad, 255, 16);
	*((unsigned char *)bad) = 0x0f;
	*(((unsigned char *)bad) +1) = 0x0b;
        ((FUNC)bad)();
	printf("Returning like it's no big deal\n");

	break;

	default:
	printf("signal %d is not supported yet!\n", signal_num);
	break;
    }

    return signal_num;
}

void SIGILL_handler(int sig)
{
    printf("Handling SIGILL\n");
}

