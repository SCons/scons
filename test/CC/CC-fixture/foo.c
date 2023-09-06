// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo.c\n");
        exit (0);
}
