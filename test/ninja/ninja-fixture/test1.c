#include <stdio.h>
#include <stdlib.h>

extern int library_function(void);

int
main(int argc, char *argv[])
{
    library_function();
}
