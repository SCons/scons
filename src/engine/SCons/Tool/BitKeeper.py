"""SCons.Tool.BitKeeper.py

Tool-specific initialization for the BitKeeper source code control
system.

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

import SCons.Builder

def generate(env, platform):
    """Add a Builder factory function and construction variables for
    BitKeeper to an Environment."""

    def BitKeeperFactory(repos, module='', env=env):
        """ """
        # fail if repos is not an absolute path name?
        if module != '':
           module = os.path.join(module, '')
        return SCons.Builder.Builder(action = "$BITKEEPERCOM",
                                     env = env,
                                     overrides = {'BKREPOSITORY':repos,
                                                  'BKMODULE':module})

    setattr(env, 'BitKeeper', BitKeeperFactory)

    env['BITKEEPER']      = 'bk'
    env['BITKEEPERFLAGS'] = ''
    env['BITKEEPERCOM']   = '$BITKEEPER get $BITKEEPERFLAGS -p $BKREPOSITORY/$BKMODULE$TARGET > $TARGET'

def exists(env):
    return env.Detect('bk')
