#
# Copyright (c) 2001, 2002 Steven Knight
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

import copy
import string

import SCons.Node.FS
import SCons.Scanner
import SCons.Util

class NullProgScanner:
    """A do-nothing ProgScanner for Environments that have no LIBS."""
    def scan(node, env, args = []):
        return []

null_scanner = NullProgScanner()

def ProgScan(fs = SCons.Node.FS.default_fs):
    """Return a prototype Scanner instance for scanning executable
    files for static-lib dependencies"""
    ps = ProgScanner(scan, "ProgScan")
    ps.fs = fs
    return ps

class ProgScanner(SCons.Scanner.Base):
    def __init__(self, *args, **kw):
        apply(SCons.Scanner.Base.__init__, (self,) + args, kw)
        self.hash = None
        self.pathscanners = {}

    def instance(self, env):
        """
        Return a unique instance of a Prog scanner object for a
        given environment.
        """
        try:
            libs = env.Dictionary('LIBS')
        except KeyError:
            # There are no LIBS in this environment, so just return the
            # fake "scanner" instance that always returns a null list.
            return null_scanner
        if SCons.Util.is_String(libs):
            libs = string.split(libs)

        try:
            dirs = tuple(SCons.Util.scons_str2nodes(env.Dictionary('LIBPATH'),
                                                    self.fs.Dir))
        except:
            dirs = ()

        try:
            prefix = env.Dictionary('LIBPREFIX')
        except KeyError:
            prefix = ''

        try:
            suffix = env.Dictionary('LIBSUFFIX')
        except KeyError:
            suffix = ''

        key = (dirs, tuple(libs), prefix, suffix)
        if not self.pathscanners.has_key(key):
            clone = copy.copy(self)
            clone.hash = key
            clone.argument = [self.fs, dirs, libs, prefix, suffix]    # XXX reaching into object
            self.pathscanners[key] = clone
        return self.pathscanners[key]

    def __hash__(self):
        return hash(self.hash)

def scan(node, env, args = [SCons.Node.FS.default_fs, (), [], '', '']):
    """
    This scanner scans program files for static-library
    dependencies.  It will search the LIBPATH environment variable
    for libraries specified in the LIBS variable, returning any
    files it finds as dependencies.
    """
    fs, libpath, libs, prefix, suffix = args
    libs = map(lambda x, s=suffix, p=prefix: p + x + s, libs)
    return SCons.Node.FS.find_files(libs, libpath, fs.File)
