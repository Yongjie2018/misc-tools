#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define MAXFILENAMELEN 100

/* Prototype for function */
void is_symlink(const char *filename);

int main()
{
    int len;
    char filename[MAXFILENAMELEN];

    printf("Enter a file name: ");
    fgets(filename, MAXFILENAMELEN, stdin);

    /* Remove the newline from the end if it' there */
    len = strlen(filename);
    if (filename[len-1] == '\n') {
        filename[len-1] = '\0';
    }

    /* Call function to test if it is a symlink */
    is_symlink(filename);

    return 0;
}

void is_symlink(const char *filename)
{
    struct stat p_statbuf;

    if (lstat(filename, &p_statbuf) < 0) {  /* if error occured */
        perror("calling stat()");
        exit(1);  /* end progam here */
    }

    if (S_ISLNK(p_statbuf.st_mode) == 1) {
        printf("%s is a symbolic link\n", filename);
    } else {
        printf("%s is NOT a symbolic link\n", filename);
    }
    printf("st_nlink: %d\n", p_statbuf.st_nlink);
    if (p_statbuf.st_nlink > 1) {
        printf("%s is a hard link\n", filename);
    } else {
        printf("%s is NOT a hard link\n", filename);
    }

}
