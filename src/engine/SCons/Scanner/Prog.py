#
# __COPYRIGHT__
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

import string

import SCons.Node
import SCons.Node.FS
import SCons.Scanner
import SCons.Util

def ProgScan(fs = SCons.Node.FS.default_fs):
    """Return a prototype Scanner instance for scanning executable
    files for static-lib dependencies"""
    ps = SCons.Scanner.Base(scan, "ProgScan", fs, path_function = path)
    return ps

def path(env, dir, fs = SCons.Node.FS.default_fs):
    try:
        libpath = env['LIBPATH']
    except KeyError:
        return ()
    return tuple(fs.Rsearchall(SCons.Util.mapPaths(libpath, dir, env),
                               clazz = SCons.Node.FS.Dir,
                               must_exist = 0))

def scan(node, env, libpath = (), fs = SCons.Node.FS.default_fs):
    """
    This scanner scans program files for static-library
    dependencies.  It will search the LIBPATH environment variable
    for libraries specified in the LIBS variable, returning any
    files it finds as dependencies.
    """

    try:
        libs = env.Dictionary('LIBS')
    except KeyError:
        # There are no LIBS in this environment, so just return a null list:
        return []
    if SCons.Util.is_String(libs):
        libs = string.split(libs)
    elif not SCons.Util.is_List(libs):
        libs = [libs]

    try:
        prefix = env.Dictionary('LIBPREFIXES')
        if not SCons.Util.is_List(prefix):
            prefix = [ prefix ]
    except KeyError:
        prefix = [ '' ]

    try:
        suffix = env.Dictionary('LIBSUFFIXES')
        if not SCons.Util.is_List(suffix):
            suffix = [ suffix ]
    except KeyError:
        suffix = [ '' ]

    find_file = SCons.Node.FS.find_file
    ret = []
    for suf in map(env.subst, suffix):
        for pref in map(env.subst, prefix):
            for lib in libs:
                if SCons.Util.is_String(lib):
                    f = find_file(pref + lib + suf, libpath, fs.File)
                    if f:
                        ret.append(f)
                else:
                    ret.append(lib)
    return ret
