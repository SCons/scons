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

import cc
import link
import os.path
import SCons.Action
import SCons.Builder
import SCons.Errors
import SCons.Util

linkers = ['g++', 'gcc', 'c++', 'cc']

def cxxSource(sources):
    for s in sources:
        if os.path.splitext(str(s))[1] in cc.CXXSuffixes:
            return 1
        if cxxSource(s.sources):
            return 1
    return 0

def smart_link(source, target, env, for_signature):
    cppSource = 0
    if source is None:
        # may occur, when env.subst('$LINK') is called
        return '$CXX'
    if not SCons.Util.is_List(source):
        source = [source]
        
    if cxxSource(source):
        return '$CXX'
    else:
        return '$CC'
        
def generate(env):
    """Add Builders and construction variables for gnulink to an Environment."""
    link.generate(env)
    env['LINK'] = smart_link
    
def exists(env):
    return env.Detect(linkers)
