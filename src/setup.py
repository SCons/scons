#
# Copyright (c) 2001 Steven Knight
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

from distutils.core import setup
from distutils.command.install_lib import install_lib

class my_install_lib(install_lib):
    def finalize_options(self):
	open("/dev/tty", "w").write("lib:  self.install_dir = %s\n" % self.install_dir)
        install_lib.finalize_options(self)
	open("/dev/tty", "w").write("lib:  self.install_dir = %s\n" % self.install_dir)
	head = self.install_dir
        while head:
	    if head == os.sep:
		head = None
		break
	    else:
	        head, tail = os.path.split(head)
            if tail[:6] == "python":
                self.install_dir = os.path.join(head, "scons")
                # Our original packaging scheme placed the build engine
                # in a private library directory that contained the SCons
                # version number in the directory name.  Here's how this
                # was supported here.  See the Construct file for details
                # on other files that would need to be changed to support
                # this as well.
                #self.install_dir = os.path.join(head, "scons-__VERSION__")
                return
            elif tail[:6] == "Python":
                self.install_dir = os.path.join(head, tail)
                return

description = \
"""SCons is an Open Source software construction tool--that is, a build tool; an
improved substitute for the classic Make utility; a better way to build
software."""

keywords = "scons, cons, make, build tool, make tool, software build tool, software construction tool"

arguments = {
    'name'             : "scons",
    'version'          : "__VERSION__",
    'description'      : "an Open Source software construction tool",
    'long_description' : description,
    'author'           : "Steven Knight",
    'author_email'     : "knight@scons.org",
    'url'              : "http://www.scons.org/",
    'license'          : "MIT, freely distributable",
    'keywords'         : keywords,
    'packages'         : ["SCons",
                          "SCons.Node",
                          "SCons.Scanner",
                          "SCons.Sig"],
    'package_dir'      : {'' : 'engine'},
    'scripts'          : ["script/scons"],
    'cmdclass'         : {'install_lib' : my_install_lib}
}

if sys.argv[1] == "bdist_wininst":
    arguments['data_files'] = [('.', ["script/scons.bat"])]

apply(setup, (), arguments)
