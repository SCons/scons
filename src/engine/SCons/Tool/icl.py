"""engine.SCons.Tool.icl

Tool-specific initialization for the Intel C/C++ compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import string

import SCons.Tool.msvc
import SCons.Util

# Find Intel compiler:
# Could enumerate subkeys here to be more flexible.
def get_intel_compiler_top(version):
    """
    Return the main path to the top-level dir of the Intel compiler,
    using the given version or latest if 0.
    The compiler will be in <top>/Bin/icl.exe,
    the include dir is <top>/Include, etc.
    """

    if version == 0:
        version = "7.0"                   # XXX: should scan for latest

    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    K = ('Software\\Intel\\' +
         'Intel(R) C/C++ Compiler for 32-bit apps, Version ' + version)
    # Note: v5 had slightly different key:
    #  HKCU\Software\Intel\Intel C/C++ Compiler for 32-bit apps, Version 5.0
    # Note no (R).
    try:
        k = SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_CURRENT_USER, K)
    except SCons.Util.RegError:
        return None

    try:
        # On my machine, this returns:
        #  c:\Program Files\Intel\Compiler70
        top = SCons.Util.RegQueryValueEx(k, "Directory")[0]
    except SCons.Util.RegError:
        raise SCons.Errors.InternalError, "%s was not found in the registry."%K

    if os.path.exists(os.path.join(top, "ia32")):
        top = os.path.join(top, "ia32")

    if not os.path.exists(os.path.join(top, "Bin", "icl.exe")):
        raise SCons.Errors.InternalError, "Can't find Intel compiler in %s"%top

    return top


def generate(env):
    """Add Builders and construction variables for icl to an Environment."""
    SCons.Tool.msvc.generate(env)

    try:
        icltop = get_intel_compiler_top(0)
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        icltop = None

    if icltop:
        env.PrependENVPath('INCLUDE', os.path.join(icltop, 'Include'))
        env.PrependENVPath('PATH', os.path.join(icltop, 'Bin'))

    env['CC']        = 'icl'
    env['CXX']        = 'icl'
    env['LINK']        = 'xilink'

    env['ENV']['INTEL_LICENSE_FILE'] = r'C:\Program Files\Common Files\Intel\Licenses'

def exists(env):
    try:
        top = get_intel_compiler_top(0)
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        top = None

    if not top:
        return env.Detect('icl')
    return top is not None
