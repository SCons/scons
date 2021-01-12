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

import os

import SCons.Node
import SCons.Node.FS
import SCons.Scanner
import SCons.Util


def _subst_libs(env, libs):
    """
    Substitute environment variables and split into list.
    """
    if SCons.Util.is_String(libs):
        libs = env.subst(libs)
        if SCons.Util.is_String(libs):
            libs = libs.split()
    elif SCons.Util.is_Sequence(libs):
        _libs = []
        for l in libs:
            _libs += _subst_libs(env, l)
        libs = _libs
    else:
        # libs is an object (Node, for example)
        libs = [libs]
    return libs


def scan(node, env, libpath=()):
    classpath = env.get('JAVACLASSPATH', [])
    classpath = _subst_libs(env, classpath)

    bootclasspath = env.get('JAVABOOTCLASSPATH', [])
    bootclasspath = _subst_libs(env, bootclasspath)

    return bootclasspath + classpath


def JavaScanner():
    return SCons.Scanner.Base(scan, 'JavaScanner',
                              skeys=['.java'])

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
