#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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
import os.path
import sys

(head, tail) = os.path.split(sys.argv[0])

if head:
    os.chdir(head)
    sys.argv[0] = tail

try:
    from distutils.core import setup
    from distutils.command.install_lib import install_lib
except ImportError:
    sys.stderr.write("""Could not import distutils.

Building or installing SCons from this package requires that the Python
distutils be installed.  See the README or README.txt file from this
package for instructions on where to find distutils for installation on
your system, or on how to install SCons from a different package.
""")
    sys.exit(1)

class my_install_lib(install_lib):
    def finalize_options(self):
        install_lib.finalize_options(self)
	head = self.install_dir
        drive, head = os.path.splitdrive(self.install_dir)
        while head:
	    if head == os.sep:
		head = None
		break
	    else:
	        head, tail = os.path.split(head)
            if tail[:6] == "python":
                self.install_dir = os.path.join(drive + head, "scons")
                # Our original packaging scheme placed the build engine
                # in a private library directory that contained the SCons
                # version number in the directory name.  Here's how this
                # was supported here.  See the Construct file for details
                # on other files that would need to be changed to support
                # this as well.
                #self.install_dir = os.path.join(drive + head, "scons-__VERSION__")
                return
            elif tail[:6] == "Python":
                self.install_dir = os.path.join(drive + head, tail)
                return

arguments = {
    'name'             : "scons",
    'version'          : "__VERSION__",
    'packages'         : ["SCons",
                          "SCons.Node",
                          "SCons.Optik",
                          "SCons.Platform",
                          "SCons.Scanner",
                          "SCons.Script",
                          "SCons.Sig",
                          "SCons.Tool"],
    'package_dir'      : {'' : 'engine'},
    'scripts'          : ["script/scons"],
    'cmdclass'         : {'install_lib' : my_install_lib}
}

try:
    if sys.argv[1] == "bdist_wininst":
        arguments['data_files'] = [('.', ["script/scons.bat"])]
except IndexError:
    pass

apply(setup, (), arguments)
