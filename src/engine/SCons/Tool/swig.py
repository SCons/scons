"""SCons.Tool.swig

Tool-specific initialization for swig.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

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

import SCons.Action
import SCons.Defaults
import SCons.Tool
import SCons.Util
from SCons.Scanner import Scanner
import os
import re

SwigAction = SCons.Action.Action('$SWIGCOM', '$SWIGCOMSTR')

def swigSuffixEmitter(env, source):
    if '-c++' in SCons.Util.CLVar(env.subst("$SWIGFLAGS")):
        return '$SWIGCXXFILESUFFIX'
    else:
        return '$SWIGCFILESUFFIX'

_reInclude = re.compile(r'%include\s+(\S+)')
_reModule = re.compile(r'%module\s+(.+)')

def recurse(path, searchPath):
    global _reInclude
    f = open(path)
    try: contents = f.read()
    finally: f.close()

    found = []
    # Better code for when we drop Python 1.5.2.
    #for m in _reInclude.finditer(contents):
    #    fname = m.group(1)
    for fname in _reInclude.findall(contents):
        for dpath in searchPath:
            absPath = os.path.join(dpath, fname)
            if os.path.isfile(absPath):
                found.append(absPath)
                break

    # Equivalent code for when we drop Python 1.5.2.
    #for f in [f for f in found if os.path.splitext(f)[1] == ".i"]:
    #    found += recurse(f, searchPath)
    for f in filter(lambda f: os.path.splitext(f)[1] == ".i", found):
        found = found + recurse(f, searchPath)
    return found

def _scanSwig(node, env, path):
    r = recurse(str(node), [os.path.abspath(os.path.dirname(str(node))), os.path.abspath(os.path.join("include", "swig"))])
    return r

def _swigEmitter(target, source, env):
    for src in source:
        src = str(src)
        flags = SCons.Util.CLVar(env.subst("$SWIGFLAGS"))
        mnames = None
        if "-python" in flags and "-noproxy" not in flags:
            if mnames is None:
                mnames = _reModule.findall(open(src).read())
            target.extend(map(lambda m: m + ".py", mnames))
        if "-java" in flags:
            if mnames is None:
                mnames = _reModule.findall(open(src).read())
            java_files = map(lambda m: [m + ".java", m + "JNI.java"], mnames)
            java_files = SCons.Util.flatten(java_files)
            outdir = env.subst('$SWIGOUTDIR')
            if outdir:
                 java_files = map(lambda j, o=outdir: os.path.join(o, j), java_files)
            target.extend(java_files)
    return (target, source)

def generate(env):
    """Add Builders and construction variables for swig to an Environment."""
    c_file, cxx_file = SCons.Tool.createCFileBuilders(env)

    c_file.suffix['.i'] = swigSuffixEmitter
    cxx_file.suffix['.i'] = swigSuffixEmitter

    c_file.add_action('.i', SwigAction)
    c_file.add_emitter('.i', _swigEmitter)
    cxx_file.add_action('.i', SwigAction)
    cxx_file.add_emitter('.i', _swigEmitter)

    env['SWIG']              = 'swig'
    env['SWIGFLAGS']         = SCons.Util.CLVar('')
    env['SWIGCFILESUFFIX']   = '_wrap$CFILESUFFIX'
    env['SWIGCXXFILESUFFIX'] = '_wrap$CXXFILESUFFIX'
    env['_SWIGOUTDIR']       = '${"-outdir " + SWIGOUTDIR}'
    env['SWIGCOM']           = '$SWIG -o $TARGET ${_SWIGOUTDIR} $SWIGFLAGS $SOURCES'
    env.Append(SCANNERS=Scanner(function=_scanSwig, skeys=[".i"]))

def exists(env):
    return env.Detect(['swig'])
