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
        install_lib.finalize_options(self)
	head = self.install_dir
        while head:
	    if head == os.sep:
		head = None
		break
	    else:
	        head, tail = os.path.split(head)
	    open("/dev/tty", 'w').write("head = " + head + "\n")
	    if tail[:6] in ["python", "Python"]:
	        break
        if head:
            self.install_dir = os.path.join(head, "scons-__VERSION__")

setup(name = "scons",
      version = "__VERSION__",
      description = "an Open Source software construction tool",
      long_description = """SCons is an Open Source software construction tool--that is, a build tool; an
improved substitute for the classic Make utility; a better way to build
software.""",
      author = "Steven Knight",
      author_email = "knight@baldmt.com",
      url = "http://www.scons.org/",
      license = "MIT, freely distributable",
      keywords = "scons, cons, make, build tool, make tool",
      packages = ["SCons",
                  "SCons.Node",
                  "SCons.Scanner",
                  "SCons.Sig"],
      package_dir = {'': 'engine'},
      scripts = ["script/scons"],
      cmdclass = {'install_lib': my_install_lib})
