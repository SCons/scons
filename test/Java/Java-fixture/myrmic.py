# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import os
import sys

args = sys.argv[1:]
while args:
    arg = args[0]
    if arg == '-d':
        outdir = args[1]
        args = args[1:]
    elif arg == '-classpath':
        args = args[1:]
    elif arg == '-sourcepath':
        args = args[1:]
    else:
        break
    args = args[1:]
for file in args:
    out = os.path.join(outdir, file.lower().replace('.java', '.class'))
    with open(file, 'rb') as infile, open(out, 'wb') as outfile:
        for line in infile:
            if not line.startswith(b'/*rmic*/'):
                outfile.write(line)

sys.exit(0)
