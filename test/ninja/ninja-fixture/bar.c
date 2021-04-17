#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("bar.c");
        exit (0);
}
