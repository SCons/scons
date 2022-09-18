#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Unit tests for the VCPkg() builder
"""

import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
import unittest

import TestUnit

import SCons.Errors
import SCons.Tool.vcpkg
from SCons.Environment import Environment

# TODO:
#  * Test upgrade/downgrade of vcpkg itself
#  * Test parsing of real vcpkg.exe output
#  * Test feature super-setting
#  * Test "static" installs
#  * Test "debug" installs
#  * Test enumerating package contents

class MockPackage:
    def __init__(self, name, version, dependencies):
        self.name = name
        self.version = version
        self.dependencies = dependencies
        self._installedFiles = []

    def install(self, env, static):
        assert not self._installedFiles, f"Trying to install package '{self.name}' more than once!"
        listfile = f"{env['VCPKGROOT']}/installed/vcpkg/info/{self.name}_{self.version}_{SCons.Tool.vcpkg._get_vcpkg_triplet(env, static)}.list"
        Path(listfile).touch()
        self._installedFiles = [listfile]

    def clean_up(self):
        for file in self._installedFiles:
            os.remove(file)
        self._installedFiles = []


class MockVCPkg:
    """Singleton object that replaces low-level VCPkg builder functions with mocks"""

    #
    # MockVCPkg lifecycle management
    #

    __instance = None

    # Singleton accessor
    def getInstance():
        if MockVCPkg.__instance is None:
            MockVCPkg.__instance = MockVCPkg()
        MockVCPkg.__instance.acquire()
        return MockVCPkg.__instance

    def __init__(self):
        self._availablePackages = {}
        self._installedPackages = {}
        self._expectations = []
        self._useCount = 0

    def assert_empty(self):
        """Asserts that all test configuration and expectations have been removed"""
        assert not self._availablePackages, f"There is/are still {len(self._availablePackages)} AvailablePackage(s)"
        assert not self._installedPackages, f"There is/are still {len(self._installedPackages)} InstalledPackage(s)"
        assert not self._expectations, f"There is/are still {len(self._expectations)} Expectation(s)"

    def acquire(self):
        """Called to acquire a ref-count on the singleton MockVCPkg object. This is needed because multiple objects can be using the MockVCPkg object simultaneously, and it needs to tear itself down when the last user releases it"""
        self._useCount += 1
        if self._useCount == 1:
            # There shouldn't be anything configured yet
            self.assert_empty()

            # Save original functions to restore later
            self._orig_bootstrap_vcpkg = SCons.Tool.vcpkg._bootstrap_vcpkg
            self._orig_call_vcpkg = SCons.Tool.vcpkg._call_vcpkg
            self._orig_install_packages = SCons.Tool.vcpkg._install_packages
            self._orig_upgrade_packages = SCons.Tool.vcpkg._upgrade_packages
            self._origis_mismatched_version_installed = SCons.Tool.vcpkg.is_mismatched_version_installed
            self._orig_get_package_version = SCons.Tool.vcpkg._get_package_version
            self._orig_get_package_deps = SCons.Tool.vcpkg._get_package_deps
            self._orig_read_vcpkg_file_list = SCons.Tool.vcpkg._read_vcpkg_file_list

            # Replace the low-level vcpkg functions with our mocks
            SCons.Tool.vcpkg._bootstrap_vcpkg = MockVCPkg._bootstrap_vcpkg
            SCons.Tool.vcpkg._call_vcpkg = MockVCPkg._call_vcpkg
            SCons.Tool.vcpkg._install_packages = MockVCPkg._install_packages
            SCons.Tool.vcpkg._upgrade_packages = MockVCPkg._upgrade_packages
            SCons.Tool.vcpkg.is_mismatched_version_installed = MockVCPkg.is_mismatched_version_installed
            SCons.Tool.vcpkg._get_package_version = MockVCPkg._get_package_version
            SCons.Tool.vcpkg._get_package_deps = MockVCPkg._get_package_deps
            SCons.Tool.vcpkg._read_vcpkg_file_list = MockVCPkg._read_vcpkg_file_list

    def release(self):
        """Called to release a ref-count on the singleton MockVCPkg object. When this hits zero, the MockVCPkg instance will tear itself down"""
        assert(self._useCount > 0)
        self._useCount -= 1
        if self._useCount == 0:
            # There shouldn't be any configuration still remaining
            self.assert_empty()

            # Restore original functions
            SCons.Tool.vcpkg._bootstrap_vcpkg = self._orig_bootstrap_vcpkg
            SCons.Tool.vcpkg._call_vcpkg = self._orig_call_vcpkg
            SCons.Tool.vcpkg._install_packages = self._orig_install_packages
            SCons.Tool.vcpkg._upgrade_packages = self._orig_upgrade_packages
            SCons.Tool.vcpkg.is_mismatched_version_installed = self._origis_mismatched_version_installed
            SCons.Tool.vcpkg._get_package_version = self._orig_get_package_version
            SCons.Tool.vcpkg._get_package_deps = self._orig_get_package_deps
            SCons.Tool.vcpkg._read_vcpkg_file_list = self._orig_read_vcpkg_file_list

            # Finally, free the singleton
            MockVCPkg.__instance = None


    #
    # State modification functions used by contextmanager functions below
    #

    def addAvailablePackage(self, name, version, dependencies):
        assert name not in self._availablePackages, f"Already have an AvailablePackage with name '{name}' (version {self._availablePackages[name].version})"
        pkg = MockPackage(name, version, dependencies)
        self._availablePackages[name] = pkg
        return pkg

    def removeAvailablePackage(self, pkg):
        pkg.clean_up()
        assert self._availablePackages.pop(pkg.name), f"Trying to remove AvailablePackage with name '{pkg.name}' that is not currently registered"

    def addInstalledPackage(self, env, name, version, dependencies, static):
        assert name not in self._installedPackages, f"Already have an InstalledPackage with name '{name}' (version {self._availablePackages[name].version})"
        pkg = MockPackage(name, version, dependencies)
        pkg.install(env, static)
        self._installedPackages[name] = pkg
        return pkg

    def removeInstalledPackage(self, pkg):
        pkg.clean_up()
        assert self._installedPackages.pop(pkg.name), f"Trying to remove InstalledPackage with name '{pkg.name}' that is not currently registered"

    def addExpectation(self, exp):
        assert exp not in self._expectations, "Trying to add an Expectation twice?"
        self._expectations.append(exp)
        return exp

    def removeExpectation(self, exp):
        assert exp in self._expectations, "Trying to remove Expectation that is not currently registered"
        self._expectations.remove(exp)


    #
    # Mock implementations of low-level VCPkg builder functions
    #

    def _bootstrap_vcpkg(env):
        pass

    def _call_vcpkg(env, params, check_output = False, check = True):
        assert False, "_call_vcpkg() should never be called...did we forget to hook a function?"

    def _install_packages(env, packages):
        instance = MockVCPkg.__instance
        for exp in instance._expectations:
            exp.onInstall(env, packages)
        for p in packages:
            name = p.get_name()
            assert name not in instance._installedPackages, f"Trying to install package with name '{name}' that is reported as already-installed"
            assert name in instance._availablePackages, f"Trying to install package with name '{name}' that is not among the available packages"
            instance._availablePackages[name].install(env, p.get_static())

    def _upgrade_packages(env, packages):
        instance = MockVCPkg.__instance
        for exp in MockVCPkg.__instance._expectations:
            exp.onUpgrade(env, packages)
        for p in packages:
            name = p.get_name()
            assert name in instance._installedPackages, f"Trying to upgrade package with name '{name}' that is not reported as already-installed"
            assert name in instance._availablePackages, f"Trying to upgrade package with name '{name}' that is not among the available packages"
            instance._installedPackages[name].clean_up()
            instance._availablePackages[name].install(env, p.get_static())

    def is_mismatched_version_installed(env, spec):
        name = re.sub(r':.*$', '', spec)
        instance = MockVCPkg.__instance
        return name in instance._installedPackages and (name not in instance._availablePackages or instance._installedPackages[name].version != instance._availablePackages[name].version)

    def _get_package_version(env, spec):
        name = re.sub(r':.*$', '', spec)
        pkg = MockVCPkg.__instance._availablePackages[name]
        assert pkg is not None, f"_get_package_version() for not-registered package '{spec}'"
        return pkg.version

    def _get_package_deps(env, spec, static):
        name = re.sub(r':.*$', '', spec)
        return MockVCPkg.__instance._availablePackages[name].dependencies

    def _read_vcpkg_file_list(env, list_file):
        return []


class InstallExpectation:
    def __init__(self, packages):
        self._packageInstalled = {}
        for p in packages:
            self._packageInstalled[p] = False

    def onInstall(self, env, packages):
        for p in packages:
            name = p.get_name()
            assert name in self._packageInstalled, f"Installing unexpected package '{name}'" 
            assert self._packageInstalled[name] == False, f"Installing package '{name}' more than once!"
            self._packageInstalled[name] = True

    def onUpgrade(self, env, packages):
        for p in packages:
            assert p.get_name() not in self._packageInstalled, f"Expected package '{p.get_name()}' to be installed, but it was upgraded instead."

    def finalize(self):
        for p in self._packageInstalled:
            assert self._packageInstalled[p], f"Expected package '{p}' to be installed, but it was not."


class UpgradeExpectation:
    def __init__(self, packages, static = False):
        self._packageUpgraded = {}
        for p in packages:
            self._packageUpgraded[p] = False

    def onInstall(self, env, packages):
        for p in packages:
            assert p.get_name() not in self._packageUpgraded, f"Expected package '{p.get_name()}' to be upgraded, but it was installed instead."

    def onUpgrade(self, env, packages):
        for p in packages:
            name = p.get_name()
            assert name in self._packageUpgraded, f"Upgrading unexpected package '{name}'" 
            assert self._packageUpgraded[name] == False, f"Upgrading package '{name}' more than once!"
            self._packageUpgraded[name] = True

    def finalize(self):
        for p in self._packageUpgraded:
            assert self._packageUpgraded[p], f"Expected package '{p}' to be upgraded, but it was not."


class NoChangeExpectation:
    def onInstall(self, env, packages):
        assert False, "Expected no package changes, but this/these were installed: " + ' '.join(map(lambda p: str(p), packages))

    def onUpgrade(self, env, packages):
        assert False, "Expected no package changes, but this/these were upgraded: " + ' '.join(map(lambda p: str(p), packages))

    def finalize(self):
        pass


@contextmanager
def MockVCPkgUser():
    """ContextManager providing scoped usage of the MockVCPkg singleton"""
    instance = MockVCPkg.getInstance()
    try:
        yield instance
    finally:
        instance.release()


@contextmanager
def AvailablePackage(name, version, dependencies = []):
    """ContextManager temporarily adding an 'available' package to the MockVCPkg during its 'with' scope"""
    with MockVCPkgUser() as vcpkg:
        pkg = vcpkg.addAvailablePackage(name, version, dependencies)
        try:
            yield pkg
        finally:
            vcpkg.removeAvailablePackage(pkg)


@contextmanager
def InstalledPackage(env, name, version, dependencies = [], static = False):
    """ContextManager temporarily adding an 'installed' package to the MockVCPkg during its 'with' scope"""
    with MockVCPkgUser() as vcpkg:
        pkg = vcpkg.addInstalledPackage(env, name, version, dependencies, static)
        try:
            yield pkg
        finally:
            vcpkg.removeInstalledPackage(pkg)


@contextmanager
def Expect(exp):
    """ContextManager temporarily adding an expectation to the MockVCPkg that must be fulfilled within its 'with' scope"""
    with MockVCPkgUser() as vcpkg:
        exp = vcpkg.addExpectation(exp)
        try:
            yield exp
            exp.finalize()
        finally:
            vcpkg.removeExpectation(exp)


@contextmanager
def ExpectInstall(packages):
    """ContextManager adding an expectation that the specified list of packages will be installed within its 'with' scope"""
    exp = InstallExpectation(packages)
    with Expect(exp):
        yield exp


@contextmanager
def ExpectNoInstall():
    """ContextManager adding an expectation that no packages will be installed within its 'with' scope"""
    exp = InstallExpectation(packages = [])
    with Expect(exp):
        yield exp


@contextmanager
def ExpectUpgrade(packages):
    """ContextManager adding an expectation that the specified list of packages will be upgraded within its 'with' scope"""
    exp = UpgradeExpectation(packages)
    with Expect(exp):
        yield exp


@contextmanager
def ExpectNoUpgrade():
    """ContextManager adding an expectation that no packages will be upgraded within its 'with' scope"""
    exp = UpgradeExpectation(packages = [])
    with Expect(exp):
        yield exp


@contextmanager
def ExpectNoChange():
    """ContextManager temporarily adding an expectation that no package installation changes will occur within its 'with' scope"""
    exp = NoChangeExpectation()
    with Expect(exp):
        yield exp


@contextmanager
def MakeVCPkgEnv():
    """Returns an Environment suitable for testing VCPkg"""
    with tempfile.TemporaryDirectory() as vcpkg_root:
        # Ensure that the .vcpkg-root sentinel file and directory structure exists
        Path(f"{vcpkg_root}/.vcpkg-root").touch()
        os.makedirs(f"{vcpkg_root}/installed/vcpkg/info")

        env = Environment(tools=['default', 'vcpkg'])
        env['VCPKGROOT'] = vcpkg_root
        yield env


class VCPkgTestCase(unittest.TestCase):
    def test_VCPKGROOT(self):
        """Test that VCPkg() fails with an exception if the VCPKGROOT environment variable is unset or invalid"""

        env = Environment(tools=['vcpkg'])

        # VCPKGROOT unset (should fail)
        exc_caught = None
        try:
            if 'VCPKGROOT' in env:
                del env['VCPKGROOT']
            env.VCPkg('pretend_package')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            assert "$VCPKGROOT must be set" in str(e), e
        assert exc_caught, "did not catch expected UserError"

        # VCPKGROOT pointing to a bogus path (should fail)
        exc_caught = None
        try:
            env['VCPKGROOT'] = '/usr/bin/phony/path'
            env.VCPkg('pretend_package')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            assert "$VCPKGROOT must point to" in str(e), e
        assert exc_caught, "did not catch expected UserError"

        # VCPKGROOT pointing to a valid path that is not a vcpkg instance (should fail)
        exc_caught = None
        try:
            env['VCPKGROOT'] = '#/'
            env.VCPkg('pretend_package')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            assert "$VCPKGROOT must point to" in str(e), e
        assert exc_caught, "did not catch expected UserError"

    def test_install_existing_with_no_dependency(self):
        """Test that the VCPkg builder installs missing packages"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("frobotz", "1.2.3"), \
             InstalledPackage(env, "frobotz", "1.2.3"), \
             ExpectNoInstall():
            env.VCPkg("frobotz")

    def test_install_with_no_dependency(self):
        """Test that the VCPkg builder installs missing packages"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage( "frobotz", "1.2.3"), \
             ExpectInstall(["frobotz"]):
            env.VCPkg("frobotz")

    def test_duplicate_install(self):
        """Test that duplicate invocations of the VCPkg builder installs a package only once"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("frobotz", "1.2.3"), \
             ExpectInstall(["frobotz"]):
            env.VCPkg("frobotz")
            env.VCPkg("frobotz")

    def test_install_with_satisfied_dependency(self):
        """Test that installing a package depending on an installed package does not attempt to reinstall that package"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("xyzzy", "0.1"), \
             AvailablePackage("frobotz", "1.2.1", dependencies = ["xyzzy"]), \
             InstalledPackage(env, "xyzzy", "0.1"), \
             ExpectInstall(["frobotz"]), \
             ExpectNoUpgrade():
            env.VCPkg("frobotz")

    def test_install_with_missing_dependency(self):
        """Test that installing a package depending on a not-installed package also installs that package"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("xyzzy", "0.1"), \
             AvailablePackage("frobotz", "1.2.1", dependencies = ["xyzzy"]), \
             ExpectInstall(["xyzzy", "frobotz"]), \
             ExpectNoUpgrade():
            env.VCPkg("frobotz")

    def test_install_with_missing_dependencies(self):
        """Test that installing a package depending on multiple not-installed packages also installs those packages"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("xyzzy", "0.1"), \
             AvailablePackage("battered_lantern", "0.2"), \
             AvailablePackage("frobotz", "1.2.1", dependencies = ["xyzzy", "battered_lantern"]), \
             ExpectInstall(["xyzzy", "battered_lantern", "frobotz"]), \
             ExpectNoUpgrade():
            env.VCPkg("frobotz")

    def test_install_with_mixed_dependencies(self):
        """Test that installing a package depending on a not-installed package also installs that package"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("xyzzy", "0.1"), \
             AvailablePackage("battered_lantern", "0.2"), \
             AvailablePackage("frobotz", "1.2.1", dependencies = ["xyzzy"]), \
             InstalledPackage(env, "battered_lantern", "0.2"), \
             ExpectInstall(["xyzzy", "frobotz"]), \
             ExpectNoUpgrade():
            env.VCPkg("frobotz")

    def test_upgrade(self):
        """Test that the VCPkg builder correctly upgrades existing packages to match the vcpkg configuration"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("frobotz", "1.2.1"), \
             InstalledPackage(env, "frobotz", "1.2.2"), \
             ExpectNoInstall(), \
             ExpectUpgrade(["frobotz"]):
            env.VCPkg("frobotz")

    def test_downgrade(self):
        """Test that the VCPkg builder correctly downgrades existing packages to match the vcpkg configuration"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("frobotz", "1.2.3"), \
             InstalledPackage(env, "frobotz", "1.2.2"), \
             ExpectNoInstall(), \
             ExpectUpgrade(["frobotz"]):
            env.VCPkg("frobotz")

    def test_upgrade_with_satisfied_dependency(self):
        """Test that the VCPkg builder correctly upgrades existing packages to match the vcpkg configuration"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("glowing_sword", "0.5"), \
             AvailablePackage("frobotz", "1.2.2", dependencies = ["glowing_sword"]), \
             InstalledPackage(env, "glowing_sword", "0.5"), \
             InstalledPackage(env, "frobotz", "1.2.3"), \
             ExpectNoInstall(), \
             ExpectUpgrade(["frobotz"]):
            env.VCPkg("frobotz")

    def test_upgrade_with_missing_dependency(self):
        """Test that the VCPkg builder correctly upgrades existing packages to match the vcpkg configuration"""
        with MakeVCPkgEnv() as env, \
             AvailablePackage("glowing_sword", "0.5"), \
             AvailablePackage("frobotz", "1.2.2", dependencies = ["glowing_sword"]), \
             InstalledPackage(env, "frobotz", "1.2.3"), \
             ExpectInstall(["glowing_sword"]), \
             ExpectUpgrade(["frobotz"]):
            env.VCPkg("frobotz")


if __name__ == "__main__":
    suite = unittest.makeSuite(VCPkgTestCase, 'test_')
    TestUnit.run(suite)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
