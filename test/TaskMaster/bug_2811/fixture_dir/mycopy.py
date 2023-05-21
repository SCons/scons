# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import sys
import shutil

ffrom = sys.argv[1]
to = sys.argv[2]
shutil.copyfile(ffrom, to)

sys.exit(0)
