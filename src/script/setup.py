__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

from string import join, split

from distutils.core import setup

setup(name = "scons",
      version = "__VERSION__",
      description = "scons",
      author = "Steven Knight",
      author_email = "knight@baldmt.com",
      url = "http://www.baldmt.com/scons",
      scripts = ["scons.py"])
