#!python3

import fnmatch
from setuptools import setup
from setuptools.command.build_py import build_py as build_py_orig

import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


exclude = ['*Tests']


class build_py(build_py_orig):

    def find_package_modules(self, package, package_dir):
        """Custom module to find package modules.

        Will strip out any modules which match the glob patters in
        *exclude* above
        """
        modules = super().find_package_modules(package, package_dir)
        return [(pkg, mod, file, ) for (pkg, mod, file, ) in modules
                if not any(fnmatch.fnmatchcase(mod, pat=pattern)
                for pattern in exclude)]

setup(
    cmdclass={
        'build_py': build_py,
    },
)
