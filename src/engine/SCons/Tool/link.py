"""SCons.Tool.link

Tool-specific initialization for the generic Posix linker.

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

import sys
import re
import os

import SCons.Tool
import SCons.Util
import SCons.Warnings

from SCons.Tool.FortranCommon import isfortran

from SCons.Tool.DCommon import isD

cplusplus = __import__('c++', globals(), locals(), [])

issued_mixed_link_warning = False

def smart_link(source, target, env, for_signature):
    has_cplusplus = cplusplus.iscplusplus(source)
    has_fortran = isfortran(env, source)
    has_d = isD(env, source)
    if has_cplusplus and has_fortran and not has_d:
        global issued_mixed_link_warning
        if not issued_mixed_link_warning:
            msg = "Using $CXX to link Fortran and C++ code together.\n\t" + \
              "This may generate a buggy executable if the '%s'\n\t" + \
              "compiler does not know how to deal with Fortran runtimes."
            SCons.Warnings.warn(SCons.Warnings.FortranCxxMixWarning,
                                msg % env.subst('$CXX'))
            issued_mixed_link_warning = True
        return '$CXX'
    elif has_d:
        env['LINKCOM'] = env['DLINKCOM']
        env['SHLINKCOM'] = env['SHDLINKCOM']
        return '$DC'
    elif has_fortran:
        return '$FORTRAN'
    elif has_cplusplus:
        return '$CXX'
    return '$CC'

def _lib_emitter(target, source, env, **kw):
    Verbose = False
    if Verbose:
        print "_lib_emitter: str(target[0])=%r" % str(target[0])
    for tgt in target:
        tgt.attributes.shared = 1
    
    try:
        symlink_generator = kw['symlink_generator']
    except KeyError:
        pass
    else:
        if Verbose:
            print "_lib_emitter: symlink_generator=%r" % symlink_generator
        symlinks = symlink_generator(env, target[0])
        if Verbose:
            print "_lib_emitter: symlinks=%r" % symlinks 

        if symlinks:
            SCons.Tool.EmitLibSymlinks(env, symlinks, target[0])
            target[0].attributes.shliblinks = symlinks
    return (target, source)

def shlib_emitter(target, source, env):
    return _lib_emitter(target, source, env, symlink_generator = SCons.Tool.ShLibSymlinkGenerator)

def ldmod_emitter(target, source, env):
    return _lib_emitter(target, source, env, symlink_generator = SCons.Tool.LdModSymlinkGenerator)

# This is generic enough to be included here...
def _versioned_lib_name(env, libnode, version, suffix, suffix_generator, **kw):
    """For libnode='/optional/dir/libfoo.so.X.Y.Z' it returns 'libfoo.so'"""
    Verbose = False

    if Verbose:
        print "_versioned_lib_name: version=%r" % version

    versioned_name = os.path.basename(str(libnode))
    if Verbose:
        print "_versioned_lib_name: versioned_name=%r" % versioned_name

    if Verbose:
        print "_versioned_lib_name: suffix=%r" % suffix

    versioned_suffix = suffix_generator(env, **kw)

    versioned_suffix_re = re.escape(versioned_suffix) + '$'
    name = re.sub(versioned_suffix_re, suffix, versioned_name)
    if Verbose:
        print "_versioned_lib_name: name=%r" % name
    return name

def _versioned_shlib_name(env, libnode, version, suffix, **kw):
    generator = SCons.Tool.ShLibSuffixGenerator
    return _versioned_lib_name(env, libnode, version, suffix, generator, **kw)

def _versioned_ldmod_name(env, libnode, version, suffix, **kw):
    generator = SCons.Tool.LdModSuffixGenerator
    return _versioned_lib_name(env, libnode, version, suffix, generator, **kw)


def generate(env):
    """Add Builders and construction variables for gnulink to an Environment."""
    SCons.Tool.createSharedLibBuilder(env)
    SCons.Tool.createProgBuilder(env)

    env['SHLINK']      = '$LINK'
    env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared')
    env['SHLINKCOM']   = '$SHLINK -o $TARGET $SHLINKFLAGS $__SHLIBVERSIONFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS'
    # don't set up the emitter, cause AppendUnique will generate a list
    # starting with None :-(
    env.Append(SHLIBEMITTER = [shlib_emitter])
    env['SMARTLINK']   = smart_link
    env['LINK']        = "$SMARTLINK"
    env['LINKFLAGS']   = SCons.Util.CLVar('')
    # __RPATH is only set to something ($_RPATH typically) on platforms that support it.
    env['LINKCOM']     = '$LINK -o $TARGET $LINKFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS'
    env['LIBDIRPREFIX']='-L'
    env['LIBDIRSUFFIX']=''
    env['_LIBFLAGS']='${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}'
    env['LIBLINKPREFIX']='-l'
    env['LIBLINKSUFFIX']=''

    if env['PLATFORM'] == 'hpux':
        env['SHLIBSUFFIX'] = '.sl'
    elif env['PLATFORM'] == 'aix':
        env['SHLIBSUFFIX'] = '.a'

    # For most platforms, a loadable module is the same as a shared
    # library.  Platforms which are different can override these, but
    # setting them the same means that LoadableModule works everywhere.
    SCons.Tool.createLoadableModuleBuilder(env)
    env['LDMODULE'] = '$SHLINK'
    env.Append(LDMODULEEMITTER = [ldmod_emitter])
    env['LDMODULEPREFIX'] = '$SHLIBPREFIX'
    env['LDMODULESUFFIX'] = '$SHLIBSUFFIX'
    env['LDMODULEFLAGS'] = '$SHLINKFLAGS'
    env['LDMODULECOM'] = '$LDMODULE -o $TARGET $LDMODULEFLAGS $__LDMODULEVERSIONFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS'
    env['LDMODULEVERSION'] = '$SHLIBVERSION'
    env['LDMODULENOVERSIONSYMLINKS'] = '$SHLIBNOVERSIONSYMLINKS'

def exists(env):
    # This module isn't really a Tool on its own, it's common logic for
    # other linkers.
    return None

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
