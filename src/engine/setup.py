__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import sys

(head, tail) = os.path.split(sys.argv[0])

if head:
    os.chdir(head)
    sys.argv[0] = tail

from distutils.core import setup

setup(name = "scons-pylib",
      version = "__VERSION__",
      description = "scons",
      author = "Steven Knight",
      author_email = "knight@baldmt.com",
      url = "http://www.scons.org/",
      packages = ["SCons",
		  "SCons.Node",
		  "SCons.Scanner",
		  "SCons.Sig"])
