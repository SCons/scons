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

import os
import os.path
import sys

(head, tail) = os.path.split(sys.argv[0])

if head:
    os.chdir(head)
    sys.argv[0] = tail

# Code to figure out the package name from the current directory.
# May come in handy to allow this setup.py to switch-hit between
# python-scons and python2-scons.
#head, package = os.path.split(os.getcwd())
#suffix = "-__VERSION__"
#if package[-len(suffix):] == suffix:
#    package = package[:-len(suffix)]

package = 'python-scons'

from distutils.core import setup

ver = {
    'python-scons': '1.5',
    'python2-scons': '2.1',
}

setup(name = package,
      version = "__VERSION__",
      description = "SCons Python %s extension modules" % ver[package],
      long_description = """SCons is an Open Source software construction tool--that is, a build tool; an
improved substitute for the classic Make utility; a better way to build
software.""",
      author = "Steven Knight",
      author_email = "knight@baldmt.com",
      url = "http://www.scons.org/",
      licence = "MIT, freely distributable",
      keywords = "scons, cons, make, build tool, make tool",
      packages = ["SCons",
		  "SCons.Node",
		  "SCons.Scanner",
		  "SCons.Sig",
		  "SCons.Script"])
