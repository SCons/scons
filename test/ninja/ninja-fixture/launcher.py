# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Minimal compiler launcher, like ccache: run the remaining arguments."""

import subprocess
import sys

sys.exit(subprocess.call(sys.argv[1:]))
