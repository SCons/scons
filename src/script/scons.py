#! /usr/bin/env python
#
# SCons - a Software Constructor
#
# Copyright (c) 2001, 2002 Steven Knight
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

__version__ = "__VERSION__"

__build__ = "__BUILD__"

__buildsys__ = "__BUILDSYS__"

__date__ = "__DATE__"

__developer__ = "__DEVELOPER__"

import sys
import os.path
import os

# Strip the script directory from sys.path() so on case-insensitive
# (WIN32) systems Python doesn't think that the "scons" script is the
# "SCons" package.  Replace it with our own library directories
# (version-specific first, in case they installed by hand there,
# followed by generic) so we pick up the right version of the build
# engine modules if they're in either directory.

script_dir = sys.path[0]

if script_dir in sys.path:
    sys.path.remove(script_dir)

libs = []

if os.environ.has_key("SCONS_LIB_DIR"):
    libs.append(os.environ["SCONS_LIB_DIR"])

local = 'scons-local-' + __version__
if script_dir:
    local = os.path.join(script_dir, local)
libs.append(local)

if sys.platform == 'win32':
    libs.extend([ os.path.join(sys.prefix, 'SCons-%s' % __version__),
                  os.path.join(sys.prefix, 'SCons') ])
else:
    prefs = []

    _bin = os.path.join('', 'bin')
    _usr = os.path.join('', 'usr')
    _usr_local = os.path.join('', 'usr', 'local')

    if script_dir == 'bin':
        prefs.append(os.getcwd())
    else:
        if script_dir == '.' or script_dir == '':
            script_dir = os.getcwd()
        if script_dir[-len(_bin):] == _bin:
            prefs.append(script_dir[:-len(_bin)])

    if sys.prefix[-len(_usr):] == _usr:
        prefs.append(sys.prefix)
	prefs.append(os.path.join(sys.prefix, "local"))
    elif sys.prefix[-len(_usr_local):] == _usr_local:
        _local = os.path.join('', 'local')
        prefs.append(sys.prefix[:-len(_local)])
        prefs.append(sys.prefix)
    else:
        prefs.append(sys.prefix)

    libs.extend(map(lambda x: os.path.join(x, 'lib', 'scons-%s' % __version__), prefs))
    libs.extend(map(lambda x: os.path.join(x, 'lib', 'scons'), prefs))

sys.path = libs + sys.path

import SCons.Script
SCons.Script.main()
