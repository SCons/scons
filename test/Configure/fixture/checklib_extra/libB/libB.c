// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

#include <stdio.h>
#include "libA.h"
#include "libB.h"

LIBB_DECL void libB (void) {
    printf("libB\\n");
    libA();
}
