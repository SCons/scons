"""SCons.Tool.sgic++

Tool-specific initialization for MIPSpro C++ on SGI.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""
__revision__ = ""

import os.path
import string

cplusplus = __import__('c++', globals(), locals(), [])

def generate(env):
    """Add Builders and construction variables for SGI MIPS C++ to an Environment."""

    cplusplus.generate(env)

    env['CXX']         = 'CC'
    env['CXXFLAGS']    = ['$CCFLAGS', '-LANG:std']
    env['SHCXX']       = 'CC'
    env['SHOBJSUFFIX'] = '.o'
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1
    
def exists(env):
    return env.Detect('CC')
