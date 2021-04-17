#include <stdio.h>
#include <stdlib.h>

#ifdef WIN32
#ifdef LIBRARY_BUILD
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT __declspec(dllimport)
#endif
#else
#define DLLEXPORT
#endif

DLLEXPORT extern int library_function(void);

int
main(int argc, char *argv[])
{
    library_function();
    exit(0);
}
