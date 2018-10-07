"""SCons.Tool.wix

Tool-specific initialization for wix, the Windows Installer XML Tool.

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
import os
import glob

import SCons.Builder
import SCons.Action
import os

def generate(env):
    """Add Builders and construction variables for WiX to an Environment."""
    if not exists(env):
        return

    env['WIXCANDLEFLAGS'] = ['-nologo']
    env['WIXCANDLEINCLUDE'] = []
    env['WIXCANDLECOM'] = '$WIXCANDLE $WIXCANDLEFLAGS -I $WIXCANDLEINCLUDE -o ${TARGET} ${SOURCE}'

    env['WIXLIGHTFLAGS'].append('-nologo')
    env['WIXLIGHTCOM'] = "$WIXLIGHT $WIXLIGHTFLAGS -out ${TARGET} ${SOURCES}"
    env['WIXSRCSUF'] = '.wxs'
    env['WIXOBJSUF'] = '.wixobj'

    object_builder = SCons.Builder.Builder(
        action      = '$WIXCANDLECOM',
        suffix      = '$WIXOBJSUF',
        src_suffix  = '$WIXSRCSUF')

    linker_builder = SCons.Builder.Builder(
        action      = '$WIXLIGHTCOM',
        src_suffix  = '$WIXOBJSUF',
        src_builder = object_builder)

    env['BUILDERS']['WiX'] = linker_builder


def exists(env):
    env['WIXCANDLE'] = 'candle.exe'
    env['WIXLIGHT']  = 'light.exe'

    def check_wix(e, p):
        """try to find the candle and light tools; add to path if found."""
        try:
            files = os.listdir(p)
            if e['WIXCANDLE'] in files and e['WIXLIGHT'] in files:
                e.PrependENVPath('PATH', p)
                # include appropriate flags if running WiX 2.0
                if 'wixui.wixlib' in files and 'WixUI_en-us.wxl' in files:
                    e['WIXLIGHTFLAGS'] = [os.path.join(p, 'wixui.wixlib'),
                                          '-loc',
                                          os.path.join(p, 'WixUI_en-us.wxl')]
                else:
                    e['WIXLIGHTFLAGS'] = []
                return 1
        except OSError:
            pass  # ignore this, could be a stale PATH entry.
        return None

    # look in existing paths first
    for path in os.environ['PATH'].split(os.pathsep):
        if not path:
            continue

        # workaround for some weird python win32 bug.
        if path[0] == '"' and path[-1:] == '"':
            path = path[1:-1]

        # normalize the path
        path = os.path.normpath(path)

        if check_wix(env, path):
            return 1

    # Wix is not in scons' PATH. Let's look in typical install locations.
    wix_env = os.environ.get('WIX', None)
    if wix_env:
        wix_installs = [os.path.join(wix_env, 'bin')]
    else:
        wix_path = r'C:\Program Files (x86)\WiX Toolset v*.*\bin'
        wix_installs = glob.glob(wix_path)
    for path in wix_installs:
        if check_wix(env, path):
            return 1

    return None

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
