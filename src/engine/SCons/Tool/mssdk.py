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

"""engine.SCons.Tool.mssdk

Tool-specific initialization for Microsoft SDKs, both Platform
SDKs and Windows SDKs.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

from SCons.Tool.MSCommon.sdk import detect_sdk, \
                                    set_default_sdk, \
                                    set_sdk_by_directory, \
                                    set_sdk_by_version

def generate(env):
    """Add construction variables for an MS SDK to an Environment."""
    if env.has_key('MSSDK_DIR'):
        set_sdk_by_directory(env, env.subst('$MSSDK_DIR'))
        return

    if env.has_key('MSSDK_VERSION'):
        set_sdk_by_version(env, env.subst('$MSSDK_VERSION'))
        return

    if env.has_key('MSVS_VERSION'):
        set_default_sdk(env, env['MSVS_VERSION'])

    #print "No MSVS_VERSION: this is likely to be a bug"
    return

def exists(env):
    return detect_sdk()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
