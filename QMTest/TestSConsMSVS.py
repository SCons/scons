"""
TestSConsMSVS.py:  a testing framework for the SCons software construction
tool.

A TestSConsMSVS environment object is created via the usual invocation:

    test = TestSConsMSVS()

TestSConsMSVS is a subsclass of TestSCons, which is in turn a subclass
of TestCommon, which is in turn is a subclass of TestCmd), and hence
has available all of the methods and attributes from those classes,
as well as any overridden or additional methods or attributes defined
in this subclass.
"""

# __COPYRIGHT__

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import string
import sys

from TestSCons import *
from TestSCons import __all__

class TestSConsMSVS(TestSCons):
    """Subclass for testing MSVS-specific portions of SCons."""

    def msvs_versions(self):
        if not hasattr(self, '_msvs_versions'):

            # Determine the SCons version and the versions of the MSVS
            # environments installed on the test machine.
            #
            # We do this by executing SCons with an SConstruct file
            # (piped on stdin) that spits out Python assignments that
            # we can just exec().  We construct the SCons.__"version"__
            # string in the input here so that the SCons build itself
            # doesn't fill it in when packaging SCons.
            input = """\
import SCons
print "self._scons_version =", repr(SCons.__%s__)
env = Environment();
print "self._msvs_versions =", str(env['MSVS']['VERSIONS'])
""" % 'version'
        
            self.run(arguments = '-n -q -Q -f -', stdin = input)
            exec(self.stdout())

        return self._msvs_versions

    def vcproj_sys_path(self, fname):
        """
        """
        orig = 'sys.path = [ join(sys'

        enginepath = repr(os.path.join(self._cwd, '..', 'engine'))
        replace = 'sys.path = [ %s, join(sys' % enginepath

        contents = self.read(fname)
        contents = string.replace(contents, orig, replace)
        self.write(fname, contents)

    def msvs_substitute(self, input, msvs_ver,
                        subdir=None, sconscript=None,
                        python=None,
                        project_guid=None):
        if not hasattr(self, '_msvs_versions'):
            self.msvs_versions()

        if subdir:
            workpath = self.workpath(subdir)
        else:
            workpath = self.workpath()

        if sconscript is None:
            sconscript = self.workpath('SConstruct')

        if python is None:
            python = sys.executable

        if project_guid is None:
            project_guid = "{E5466E26-0003-F18B-8F8A-BCD76C86388D}"

        if os.environ.has_key('SCONS_LIB_DIR'):
            exec_script_main = "from os.path import join; import sys; sys.path = [ r'%s' ] + sys.path; import SCons.Script; SCons.Script.main()" % os.environ['SCONS_LIB_DIR']
        else:
            exec_script_main = "from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-%s'), join(sys.prefix, 'scons-%s'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons') ] + sys.path; import SCons.Script; SCons.Script.main()" % (self._scons_version, self._scons_version)
        exec_script_main_xml = string.replace(exec_script_main, "'", "&apos;")

        result = string.replace(input, r'<WORKPATH>', workpath)
        result = string.replace(result, r'<PYTHON>', python)
        result = string.replace(result, r'<SCONSCRIPT>', sconscript)
        result = string.replace(result, r'<SCONS_SCRIPT_MAIN>', exec_script_main)
        result = string.replace(result, r'<SCONS_SCRIPT_MAIN_XML>', exec_script_main_xml)
        result = string.replace(result, r'<PROJECT_GUID>', project_guid)
        return result

    def get_msvs_executable(self, version):
        """Returns a full path to the executable (MSDEV or devenv)
        for the specified version of Visual Studio.
        """
        common_msdev98_bin_msdev_com = ['Common', 'MSDev98', 'Bin', 'MSDEV.COM']
        common7_ide_devenv_com       = ['Common7', 'IDE', 'devenv.com']
        common7_ide_vcexpress_exe    = ['Common7', 'IDE', 'VCExpress.exe']
        sub_paths = {
            '6.0' : [
                common_msdev98_bin_msdev_com,
            ],
            '7.0' : [
                common7_ide_devenv_com,
            ],
            '7.1' : [
                common7_ide_devenv_com,
            ],
            '8.0' : [
                common7_ide_devenv_com,
                common7_ide_vcexpress_exe,
            ],
        }
        from SCons.Tool.msvs import get_msvs_install_dirs
        vs_path = get_msvs_install_dirs(version)['VSINSTALLDIR']
        for sp in sub_paths[version]:
            p = apply(os.path.join, [vs_path] + sp)
            if os.path.exists(p):
                return p
        return apply(os.path.join, [vs_path] + sub_paths[version][0])
