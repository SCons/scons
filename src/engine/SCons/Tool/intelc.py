"""SCons.Tool.icl

Tool-specific initialization for the Intel C/C++ compiler.
Supports Linux and Windows compilers, v7 and up.

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

import sys, os.path, glob, re

is_win32 = sys.platform == 'win32'
is_linux = sys.platform == 'linux2'

if is_win32:
    import SCons.Tool.msvc
elif is_linux:
    import SCons.Tool.gcc
import SCons.Util
import SCons.Warnings


def fltcmp(a, b):
    """Compare strings as floats"""
    return cmp(float(b), float(a))

def get_intel_registry_value(valuename, version=None, abi=None):
    """
    Return a value from the Intel compiler registry tree. (Win32 only)
    """

    # Open the key:
    K = 'Software\\Intel\\Compilers\\C++\\' + version + '\\'+abi.upper()
    try:
        k = SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE, K)
    except SCons.Util.RegError:
        raise SCons.Errors.InternalError, \
              "%s was not found in the registry, for Intel compiler version %s"%(K, version)

    # Get the value:
    try:
        v = SCons.Util.RegQueryValueEx(k, valuename)[0]
        return v  # or v.encode('iso-8859-1', 'replace') to remove unicode?
    except SCons.Util.RegError:
        raise SCons.Errors.InternalError, \
              "%s\\%s was not found in the registry."%(K, value)


def get_all_compiler_versions():
    """Returns a sorted list of strings, like "70" or "80"
    with most recent compiler version first.
    """
    versions=[]
    if is_win32:
        keyname = 'Software\\Intel\\Compilers\\C++'
        try:
            k = SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE,
                                        keyname)
        except WindowsError:
            return []
        i = 0
        versions = []
        try:
            while i < 100:
                subkey = SCons.Util.RegEnumKey(k, i) # raises EnvironmentError
                versions.append(subkey)
                i = i + 1
        except EnvironmentError:
            # no more subkeys
            pass
    elif is_linux:
        # Typical dir here is /opt/intel_cc_80.
        for d in glob.glob('/opt/intel_cc_*'):
            versions.append(re.search(r'cc_(.*)$', d).group(1))
    versions.sort(fltcmp)
    return versions

def get_intel_compiler_top(version=None, abi=None):
    """
    Return the main path to the top-level dir of the Intel compiler,
    using the given version or latest if None.
    The compiler will be in <top>/bin/icl.exe (icc on linux),
    the include dir is <top>/include, etc.
    """

    if is_win32:
        if not SCons.Util.can_read_reg:
            raise SCons.Errors.InternalError, "No Windows registry module was found"
        top = get_intel_registry_value('ProductDir', version, abi)

        if not os.path.exists(os.path.join(top, "Bin", "icl.exe")):
            raise SCons.Errors.InternalError, \
                  "Can't find Intel compiler in %s"%(top)
    elif is_linux:
        top = '/opt/intel_cc_%s'%version
        if not os.path.exists(os.path.join(top, "bin", "icc")):
            raise SCons.Errors.InternalError, \
                  "Can't find version %s Intel compiler in %s"%(version,top)
    return top


def generate(env, version=None, abi=None, topdir=None, verbose=1):
    """Add Builders and construction variables for Intel C/C++ compiler
    to an Environment.
    args:
      version: (string) compiler version to use, like "80"
      abi:     (string) 'win32' or whatever Itanium version wants
      topdir:  (string) compiler top dir, like
                         "c:\Program Files\Intel\Compiler70"
                        If topdir is used, version and abi are ignored.
      verbose: (int)    if >0, prints compiler version used.
    """
    if not (is_linux or is_win32):
        # can't handle this platform
        return

    if is_win32:
        SCons.Tool.msvc.generate(env)
    elif is_linux:
        SCons.Tool.gcc.generate(env)
        
    # if version is unspecified, use latest
    vlist = get_all_compiler_versions()
    if not version:
        if vlist:
            version = vlist[0]
    else:
        if version not in vlist:
            raise SCons.Errors.UserError, \
                  "Invalid Intel compiler version %s: "%version + \
                  "installed versions are %s"%(', '.join(vlist))

    # if abi is unspecified, use ia32 (ia64 is another possibility)
    if abi is None:
        abi = "ia32"                    # or ia64, I believe

    if topdir is None and version:
        try:
            topdir = get_intel_compiler_top(version, abi)
        except (SCons.Util.RegError, SCons.Errors.InternalError):
            topdir = None

    if topdir:

        if verbose:
            print "Intel C compiler: using version %s, abi %s, in '%s'"%(version,abi,topdir)

        env['INTEL_C_COMPILER_TOP'] = topdir
        if is_linux:
            paths={'INCLUDE'         : 'include',
                   'LIB'             : 'lib',
                   'PATH'            : 'bin',
                   'LD_LIBRARY_PATH' : 'lib'}
            for p in paths:
                env.PrependENVPath(p, os.path.join(topdir, paths[p]))
        if is_win32:
            #       env key    reg valname   default subdir of top
            paths=(('INCLUDE', 'IncludeDir', 'Include'),
                   ('LIB'    , 'LibDir',     'Lib'),
                   ('PATH'   , 'BinDir',     'Bin'))
            # Each path has a registry entry, use that or default to subdir
            for p in paths:
                try:
                    path=get_intel_registry_value(p[1], version, abi)
                    env.PrependENVPath(p[0], ';'.split(path))
                    # print "ICL %s: %s, final=%s"%(p[0], path, str(env['ENV'][p[0]]))
                except:
                    env.PrependENVPath(p[0], os.path.join(topdir, p[2]))

    if is_win32:
        env['CC']        = 'icl'
        env['CXX']       = 'icl'
        env['LINK']      = 'xilink'
    else:
        env['CC']        = 'icc'
        env['CXX']       = 'icpc'
        env['LINK']      = '$CC'

    if is_win32:
        # Look for license file dir
        # in system environment, registry, and default location.
        envlicdir = os.environ.get("INTEL_LICENSE_FILE", '')
        K = ('SOFTWARE\Intel\Licenses')
        try:
            k = SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE, K)
            reglicdir = SCons.Util.RegQueryValueEx(k, "w_cpp")[0]
        except (AttributeError, SCons.Util.RegError):
            reglicdir = ""
        defaultlicdir = r'C:\Program Files\Common Files\Intel\Licenses'

        licdir = None
        for ld in [envlicdir, reglicdir]:
            if ld and os.path.exists(ld):
                licdir = ld
                break
        if not licdir:
            licdir = defaultlicdir
            if not os.path.exists(licdir):
                class ICLLicenseDirWarning(SCons.Warnings.Warning):
                    pass
                SCons.Warnings.enableWarningClass(ICLLicenseDirWarning)
                SCons.Warnings.warn(ICLLicenseDirWarning,
                                    "Intel license dir was not found."
                                    "  Tried using the INTEL_LICENSE_FILE environment variable (%s), the registry (%s) and the default path (%s)."
                                    "  Using the default path as a last resort."
                                        % (envlicdir, reglicdir, defaultlicdir))
        env['ENV']['INTEL_LICENSE_FILE'] = licdir

def exists(env):
    if not (is_linux or is_win32):
        # can't handle this platform
        return 0

    try:
        top = get_intel_compiler_top()
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        top = None
    if not top:
        # try env.Detect, maybe that will work
        if is_win32:
            return env.Detect('icl')
        elif is_linux:
            return env.Detect('icc')
    return top is not None

# end of file
