import fnmatch
from setuptools import setup
from setuptools.command.build_py import build_py as build_py_orig


exclude = ['*Tests']


class build_py(build_py_orig):

    def find_package_modules(self, package, package_dir):
        """
        Custom module to find package modules.
        It will strip out any modules which match the glob patters in exclude above
        """
        modules = super().find_package_modules(package, package_dir)
        return [(pkg, mod, file, ) for (pkg, mod, file, ) in modules
                if not any(fnmatch.fnmatchcase(mod, pat=pattern)
                for pattern in exclude)]

setup(
    cmdclass={
        'build_py': build_py,
    }
)