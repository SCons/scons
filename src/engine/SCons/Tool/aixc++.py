"""SCons.Tool.aixc++

Tool-specific initialization for IBM xlC / Visual Age C++ compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""
__revision__ = ""

import os.path

import SCons.Platform.aix
import SCons.Script.SConscript

cplusplus = __import__('c++', globals(), locals(), [])

packages = ['vacpp.cmp.core', 'vacpp.cmp.batch', 'vacpp.cmp.C', 'ibmcxx.cmp']

def get_xlc(env):
    xlc = env.get('CXX', 'xlC')
    xlc_r = env.get('SHCXX', 'xlC_r')
    return SCons.Platform.aix.get_xlc(env, xlc, xlc_r, packages)

def smart_cxxflags(source, target, env, for_signature):
    build_dir = SCons.Script.SConscript.GetBuildPath()
    if build_dir:
        return '-qtempinc=' + os.path.join(build_dir, 'tempinc')
    return ''

def generate(env):
    """Add Builders and construction variables for xlC / Visual Age
    suite to an Environment."""
    path, _cxx, _shcxx, version = get_xlc(env)
    if path:
        _cxx = os.path.join(path, _cxx)
        _shcxx = os.path.join(path, _shcxx)

    cplusplus.generate(env)

    env['CXX'] = _cxx
    env['SHCXX'] = _shcxx
    env['CXXVERSION'] = version
    env['SHOBJSUFFIX'] = '.pic.o'
    
def exists(env):
    path, _cxx, _shcxx, version = get_xlc(env)
    if path and _cxx:
        xlc = os.path.join(path, _cxx)
        if os.path.exists(xlc):
            return xlc
    return None
