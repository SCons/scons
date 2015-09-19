"""SCons.Tool.gnulink

Tool-specific initialization for the gnu linker.

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

import SCons.Util
import SCons.Tool
import os
import sys
import re

import link

def _versioned_lib_suffix(env, suffix, version):
    """For suffix='.so' and version='0.1.2' it returns '.so.0.1.2'"""
    Verbose = False
    if Verbose:
        print "_versioned_lib_suffix: suffix=%r" % suffix
        print "_versioned_lib_suffix: version=%r" % version
    if not suffix.endswith(version):
        suffix = suffix + '.' + version
    if Verbose:
        print "_versioned_lib_suffix: return suffix=%r" % suffix
    return suffix

def _versioned_lib_soname(env, libnode, version, prefix, suffix, name_func):
    """For libnode='/optional/dir/libfoo.so.X.Y.Z' it returns 'libfoo.so.X'"""
    Verbose = False
    if Verbose:
        print "_versioned_lib_soname: version=%r" % version
    name = name_func(env, libnode, version, prefix, suffix)
    if Verbose:
        print "_versioned_lib_soname: name=%r" % name
    major = version.split('.')[0]
    soname = name + '.' + major
    if Verbose:
        print "_versioned_lib_soname: soname=%r" % soname
    return soname

def _versioned_shlib_soname(env, libnode, version, prefix, suffix):
    return _versioned_lib_soname(env, libnode, version, prefix, suffix, link._versioned_shlib_name) 

def _versioned_ldmod_soname(env, libnode, version, prefix, suffix):
    return _versioned_lib_soname(env, libnode, version, prefix, suffix, link._versioned_ldmod_name) 

def _versioned_lib_symlinks(env, libnode, version, prefix, suffix, name_func, soname_func):
    """Generate link names that should be created for a versioned shared lirbrary.
       Returns a dictionary in the form { linkname : linktarget }
    """
    Verbose = False

    if Verbose:
        print "_versioned_lib_symlinks: libnode=%r" % libnode.get_path()
        print "_versioned_lib_symlinks: version=%r" % version

    if sys.platform.startswith('openbsd'):
        # OpenBSD uses x.y shared library versioning numbering convention
        # and doesn't use symlinks to backwards-compatible libraries
        if Verbose:
            print "_versioned_lib_symlinks: return symlinks=%r" % None
        return None

    linkdir = libnode.get_dir()
    if Verbose:
        print "_versioned_lib_symlinks: linkdir=%r" % linkdir.get_path()

    name = name_func(env, libnode, version, prefix, suffix)
    if Verbose:
        print "_versioned_lib_symlinks: name=%r" % name

    soname = soname_func(env, libnode, version, prefix, suffix)

    link0 = env.fs.File(soname, linkdir)
    link1 = env.fs.File(name, linkdir)

    # This allows anything in SHLIBVERSION (especially SHLIBVERSION=1).
    if link0 == libnode:
        symlinks = [ (link1, libnode) ]
    else:
        symlinks = [ (link0, libnode), (link1, link0) ]

    if Verbose:
        print "_versioned_lib_symlinks: return symlinks=%r" % SCons.Tool.StringizeLibSymlinks(symlinks)

    return symlinks

def _versioned_shlib_symlinks(env, libnode, version, prefix, suffix):
    nf = link._versioned_shlib_name
    sf = _versioned_shlib_soname
    return _versioned_lib_symlinks(env, libnode, version, prefix, suffix, nf, sf)

def _versioned_ldmod_symlinks(env, libnode, version, prefix, suffix):
    nf = link._versioned_ldmod_name
    sf = _versioned_ldmod_soname
    return _versioned_lib_symlinks(env, libnode, version, prefix, suffix, nf, sf)

def generate(env):
    """Add Builders and construction variables for gnulink to an Environment."""
    link.generate(env)

    if env['PLATFORM'] == 'hpux':
        env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared -fPIC')

    # __RPATH is set to $_RPATH in the platform specification if that
    # platform supports it.
    env['RPATHPREFIX'] = '-Wl,-rpath='
    env['RPATHSUFFIX'] = ''
    env['_RPATH'] = '${_concat(RPATHPREFIX, RPATH, RPATHSUFFIX, __env__)}'

    # The $_SHLIBVERSIONFLAGS define extra commandline flags used when
    # building VERSIONED shared libraries. It's always set, but used only
    # when VERSIONED library is built (see __SHLIBVERSIONFLAGS).
    if sys.platform.startswith('openbsd'):
        # OpenBSD doesn't usually use SONAME for libraries
        env['_SHLIBVERSIONFLAGS'] = '$SHLIBVERSIONFLAGS'
        env['_LDMODULEVERSIONFLAGS'] = '$LDMODULEVERSIONFLAGS'
    else:
        env['_SHLIBVERSIONFLAGS'] = '$SHLIBVERSIONFLAGS -Wl,-soname=$_SHLINKSONAME'
        env['_LDMODULEVERSIONFLAGS'] = '$LDMODULEVERSIONFLAGS -Wl,-soname=$_LDMODULESONAME'
    env['SHLIBVERSIONFLAGS'] = SCons.Util.CLVar('-Wl,-Bsymbolic')
    env['LDMODULEVERSIONFLAGS'] = '$SHLIBVERSIONFLAGS'

    # libfoo.so.X.Y.Z -> libfoo.so.X
    env['_SHLINKSONAME']   = '${ShLibSonameGenerator(__env__,TARGET)}'
    env['_LDMODULESONAME'] = '${LdModSonameGenerator(__env__,TARGET)}'

    env['ShLibSonameGenerator'] = SCons.Tool.ShLibSonameGenerator
    env['LdModSonameGenerator'] = SCons.Tool.LdModSonameGenerator

    env['LINKCALLBACKS'] = {
        'VersionedShLibSuffix'   : _versioned_lib_suffix,
        'VersionedLdModSuffix'   : _versioned_lib_suffix,
        'VersionedShLibSymlinks' : _versioned_shlib_symlinks,
        'VersionedLdModSymlinks' : _versioned_ldmod_symlinks,
        'VersionedShLibName'     : link._versioned_shlib_name,
        'VersionedLdModName'     : link._versioned_ldmod_name,
        'VersionedShLibSoname'   : _versioned_shlib_soname,
        'VersionedLdModSoname'   : _versioned_shlib_soname,
    }
    
def exists(env):
    # TODO: sync with link.smart_link() to choose a linker
    linkers = { 'CXX': ['g++'], 'CC': ['gcc'] }
    alltools = []
    for langvar, linktools in linkers.items():
        if langvar in env: # use CC over CXX when user specified CC but not CXX
            return SCons.Tool.FindTool(linktools, env)
        alltools.extend(linktools)
    return SCons.Tool.FindTool(alltools, env) # find CXX or CC

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
