"""SCons.Tool.hpc++

Tool-specific initialization for c++ on HP/UX.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""
__revision__ = ""

import os.path
import string

cplusplus = __import__('c++', globals(), locals(), [])

acc = None

# search for the acc compiler and linker front end
for dir in os.listdir('/opt'):
    cc = '/opt/' + dir + '/bin/aCC'
    if os.path.exists(cc):
        acc = cc
        break

        
def generate(env):
    """Add Builders and construction variables for g++ to an Environment."""
    cplusplus.generate(env)

    if acc:
        env['CXX']        = acc
        # determine version of aCC
        line = os.popen(acc + ' -V 2>&1').readline().rstrip()
        if string.find(line, 'aCC: HP ANSI C++') == 0:
            env['CXXVERSION'] = string.split(line)[-1]

        if env['PLATFORM'] == 'cygwin':
            env['SHCXXFLAGS'] = '$CXXFLAGS'
        else:
            env['SHCXXFLAGS'] = '$CXXFLAGS +Z'

def exists(env):
    return acc
