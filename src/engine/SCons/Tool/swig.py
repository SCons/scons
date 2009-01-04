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

import os.path
import re

import SCons.Action
import SCons.Defaults
import SCons.Scanner
import SCons.Tool
import SCons.Util

SwigAction = SCons.Action.Action('$SWIGCOM', '$SWIGCOMSTR')

def swigSuffixEmitter(env, source):
    if '-c++' in SCons.Util.CLVar(env.subst("$SWIGFLAGS", source=source)):
        return '$SWIGCXXFILESUFFIX'
    else:
        return '$SWIGCFILESUFFIX'

# Match '%module test', as well as '%module(directors="1") test'
# Also allow for test to be quoted (SWIG permits double quotes, but not single)
_reModule = re.compile(r'%module(\s*\(.*\))?\s+("?)(.+)\2')

def _find_modules(src):
    """Find all modules referenced by %module lines in `src`, a SWIG .i file.
       Returns a list of all modules."""
    mnames = []
    matches = _reModule.findall(open(src).read())
    for m in matches:
        mnames.append(m[2])
    return mnames

def _swigEmitter(target, source, env):
    swigflags = env.subst("$SWIGFLAGS", target=target, source=source)
    flags = SCons.Util.CLVar(swigflags)
    for src in source:
        src = str(src.rfile())
        mnames = None
        if "-python" in flags and "-noproxy" not in flags:
            if mnames is None:
                mnames = _find_modules(src)
            target.extend(map(lambda m, d=target[0].dir:
                                     d.File(m + ".py"), mnames))
        if "-java" in flags:
            if mnames is None:
                mnames = _find_modules(src)
            java_files = map(lambda m: [m + ".java", m + "JNI.java"], mnames)
            java_files = SCons.Util.flatten(java_files)
            outdir = env.subst('$SWIGOUTDIR', target=target, source=source)
            if outdir:
                 java_files = map(lambda j, o=outdir: os.path.join(o, j), java_files)
            java_files = map(env.fs.File, java_files)
            for jf in java_files:
                t_from_s = lambda t, p, s, x: t.dir
                SCons.Util.AddMethod(jf, t_from_s, 'target_from_source')
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

    java_file = SCons.Tool.CreateJavaFileBuilder(env)

    java_file.suffix['.i'] = swigSuffixEmitter

    java_file.add_action('.i', SwigAction)
    java_file.add_emitter('.i', _swigEmitter)

    env['SWIG']              = 'swig'
    env['SWIGFLAGS']         = SCons.Util.CLVar('')
    env['SWIGCFILESUFFIX']   = '_wrap$CFILESUFFIX'
    env['SWIGCXXFILESUFFIX'] = '_wrap$CXXFILESUFFIX'
    env['_SWIGOUTDIR']       = '${"-outdir " + str(SWIGOUTDIR)}'
    env['SWIGPATH']          = []
    env['SWIGINCPREFIX']     = '-I'
    env['SWIGINCSUFFIX']     = ''
    env['_SWIGINCFLAGS']     = '$( ${_concat(SWIGINCPREFIX, SWIGPATH, SWIGINCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'
    env['SWIGCOM']           = '$SWIG -o $TARGET ${_SWIGOUTDIR} ${_SWIGINCFLAGS} $SWIGFLAGS $SOURCES'

    expr = '^[ \t]*%[ \t]*(?:include|import|extern)[ \t]*(<|"?)([^>\s"]+)(?:>|"?)'
    scanner = SCons.Scanner.ClassicCPP("SWIGScan", ".i", "SWIGPATH", expr)

    env.Append(SCANNERS = scanner)

def exists(env):
    return env.Detect(['swig'])
