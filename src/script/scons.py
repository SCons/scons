#! /usr/bin/env python
#
# SCons - a Software Constructor
#
# Copyright (c) 2001 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import os.path
import os

#XXX once we migrate to the new scheme of using /usr/lib/scons
#    instead of /usr/lib/scons-X.Y this hardcoding will go away:
scons_lib_dir = "scons-0.01"

script_dir = sys.path[0]
if os.environ.has_key("SCONS_LIB_DIR"):
    lib_dir = os.environ["SCONS_LIB_DIR"]
elif script_dir and script_dir != os.curdir:
    (head, tail) = os.path.split(script_dir)
    lib_dir = os.path.join(head, "lib", scons_lib_dir)
else:
    lib_dir = os.path.join(os.pardir, "lib", scons_lib_dir)

sys.path = [lib_dir] + sys.path

import SCons.Script
SCons.Script.main()
