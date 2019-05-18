"""SCons.Tool.pytar

Tool-specific initialization for tar (Python stdlib implementation)

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
import tarfile

import SCons.Builder
import SCons.Defaults
import SCons.Node.FS
import SCons.Util

_tarformat = tarfile.PAX_FORMAT


def tar(target, source, env):
    compression = env.get('TARCOMPRESSION', '')
    tarformat = env.get('TARFORMAT', None)
    tarroot = str(env.get('TARROOT', ''))
    taruid = env.get('TARUID')
    targid = env.get('TARGID')
    tarmtime = env.get('TARMTIME')
    with tarfile.TarFile.open(
            str(target[0]),
            'w' + (compression and ':') + compression,
            format=tarformat) as tar:

        def _filter(info):
            """Return potentially anonymize tarinfo"""
            if taruid != None:
                info.uid = taruid
                info.uname = ""
            if targid != None:
                info.gid = targid
                info.gname = ""
            if tarmtime != None:
                info.mtime = tarmtime
            return info

        for s in source:
            arcname = os.path.relpath(str(s), tarroot)
            tar.add(str(s), arcname=arcname, filter=_filter)


TarAction = SCons.Action.Action(tar, varlist=['TARCOMPRESSION'])

TarBuilder = SCons.Builder.Builder(
    action=SCons.Action.Action('$TARCOM', '$TARCOMSTR'),
    source_factory=SCons.Node.FS.Entry,
    source_scanner=SCons.Defaults.DirScanner,
    suffix='$TARSUFFIX',
    multi=True)


def generate(env):
    """Add Builders and construction variables for TAR to an Environment."""
    try:
        bld = env['BUILDERS']['PyTar']
    except KeyError:
        bld = TarBuilder
        env['BUILDERS']['PyTar'] = bld

    env['TAR'] = 'tar'
    env['TARFLAGS'] = SCons.Util.CLVar('')
    env['TARCOM'] = TarAction
    env['TARFORMAT'] = _tarformat
    env['TARCOMPRESSION'] = ''
    env['TARSUFFIX'] = '.tar'
    env['TARROOT'] = SCons.Util.CLVar('')
    # environment variables to support anonymized tar
    env['TARUID'] = None  # None = use real uid
    env['TARGID'] = None  # None = use real gid
    env['TARMTIME'] = None  # None = use real mtime


def exists(env):
    """Standard library tar function should always exist."""
    return True


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
