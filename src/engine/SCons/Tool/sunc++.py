"""SCons.Tool.sunc++

Tool-specific initialization for C++ on SunOS / Solaris.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""
__revision__ = ""

import os.path
import string

cplusplus = __import__('c++', globals(), locals(), [])

# use the package installer tool lslpp to figure out where cppc and what
# version of it is installed
def get_cppc(env):
    cppcPath = None
    cppcVersion = None

    try:
        cppc = env['CXX']
    except KeyError:
        cppc = 'cppc'
    for package in ['SPROcpl']:
        cmd = "pkginfo -l " + package + " 2>/dev/null | grep '^ *VERSION:'"
        line = os.popen(cmd).readline()
        if line:
            cppcVersion = line.split()[-1]
            cmd = "pkgchk -l " + package + " | grep '^Pathname:.*/bin/CC$' | grep -v '/SC[0-9]*\.[0-9]*/'"
            line = os.popen(cmd).readline()
            cppcPath = os.path.dirname(line.split()[-1])
            break
    return (cppcPath, 'CC', 'CC', cppcVersion)

def generate(env):
    """Add Builders and construction variables for SUN PRO C++ to an Environment."""
    path, cxx, shcxx, version = get_cppc(env)
    if path:
        cxx = os.path.join(path, cxx)
        shcxx = os.path.join(path, shcxx)

    cplusplus.generate(env)

    env['CXX'] = cxx
    env['SHCXX'] = shcxx
    env['CXXVERSION'] = version
    env['SHOBJSUFFIX'] = '.os'
    
def exists(env):
    path, cxx, shcxx, version = get_cppc(env)
    if path and cxx:
        cppc = os.path.join(path, cxx)
        if os.path.exists(cppc):
            return cppc
    return None
