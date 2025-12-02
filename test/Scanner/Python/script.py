# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import package1
import package2
import sys

with open(sys.argv[1], 'w') as f:
    f.write('test')
