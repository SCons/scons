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

import SCons.Scanner
import SCons.Node.FS
import SCons.Util

def ProgScan():
    """Return a prototype Scanner instance for scanning executable
    files for static-lib dependencies"""
    return SCons.Scanner.Base(scan, "ProgScan", SCons.Node.FS.default_fs.File)

def scan(node, env, node_factory):
    """
    This scanner scans program files for static-library
    dependencies.  It will search the LIBPATH environment variable
    for libraries specified in the LIBS variable, returning any
    files it finds as dependencies.
    """

    fs = SCons.Node.FS.default_fs
    try:
        paths = map(lambda x, dir=fs.Dir: dir(x),
                    env.Dictionary("LIBPATH"))
    except KeyError:
        paths = []

    try:
        libs = env.Dictionary("LIBS")
    except KeyError:
        libs = []

    try:
        prefix = env.Dictionary("LIBPREFIX")
    except KeyError:
        prefix=''

    try:
        suffix = env.Dictionary("LIBSUFFIX")
    except KeyError:
        suffix=''

    libs = map(lambda x, s=suffix, p=prefix: p + x + s, libs)
    return SCons.Util.find_files(libs, paths, node_factory)
