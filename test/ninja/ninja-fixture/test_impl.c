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


DLLEXPORT int
library_function(void)
{
    printf("library_function");
    return 0;
}
