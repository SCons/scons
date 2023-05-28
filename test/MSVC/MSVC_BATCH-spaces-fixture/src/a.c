// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

#include <stdio.h>

extern void myfuncb();
extern void myfuncc();


void myfunca() {
    printf("myfunca\n");
}

int main(int argc, char *argv[]) {
    myfunca();
    myfuncb();
    myfuncc();
}
