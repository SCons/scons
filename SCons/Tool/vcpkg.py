# -*- coding: utf-8; -*-

"""SCons.Tool.vcpkg

Tool-specific initialization for vcpkg.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.


TODO:
  * ensure that upgrading to a new package version works after a repo update
  * ensure Linux works
  * unit tests
  * verify that feature supersetting works
  * print errors from vcpkg on console
  * print vcpkg commands unless in silent mode
  * debug libs
  * install/symlink built dlls into variant dir
  * flag detection

"""

#
# Copyright (c) 2001 - 2019 The SCons Foundation
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

import re
import subprocess
import SCons.Builder
import SCons.Node.Python
import SCons.Script
from SCons.Errors import UserError, InternalError, BuildError

def _get_built_vcpkg_full_version(vcpkg_exe):
    """Runs 'vcpkg version' and parses the version string from the output"""

    if not vcpkg_exe.exists():
        raise InternalError(vcpkg_exe.get_path() + ' does not exist')

    line = subprocess.check_output([vcpkg_exe.get_abspath(), 'version'], text = True)
    match_version = re.search(r' version (\S+)', line)
    if (match_version):
        version = match_version.group(1)
        return version
    raise InternalError(vcpkg_exe.get_path() + ': failed to parse version string')


def _get_built_vcpkg_base_version(vcpkg_exe):
    """Returns just the base version from 'vcpkg version' (i.e., with any '-whatever' suffix stripped off"""
    full_version = _get_built_vcpkg_full_version(vcpkg_exe)
    dash_pos = full_version.find('-')
    if dash_pos != -1:
        return full_version[0:dash_pos]
    return full_version


def _get_source_vcpkg_version(vcpkg_root):
    """Parses the vcpkg source code version out of VERSION.txt"""

    if not vcpkg_root.exists():
        raise InternalError(vcpkg_root.get_path() + ' does not exist')

    version_txt = vcpkg_root.File('toolsrc/VERSION.txt')
    if not version_txt.exists():
        raise InternalError(version_txt.get_path() + ' does not exist; did something change in the vcpkg directory structure?')

    for line in open(version_txt.get_abspath()):
        match_version = re.match(r'^"(.*)"$', line)
        if (match_version):
            return match_version.group(1)
    raise InternalError(version_txt.get_path() + ": Failed to parse vcpkg version string")


def _bootstrap_vcpkg(env):
    """Ensures that VCPKGROOT is set, and that the vcpkg executable has been built."""

    # If we've already done these checks, return the previous result
    if '_VCPKG_EXE' in env:
        return env['_VCPKG_EXE']

    if 'VCPKGROOT' not in env:
        raise UserError('$VCPKGROOT must be set in order to use the VCPkg builder')

    vcpkgroot_dir = env.Dir(env.subst('$VCPKGROOT'))
    sentinel_file = vcpkgroot_dir.File('.vcpkg-root')
    if not sentinel_file.exists():
        raise UserError(sentinel_file.get_path() + ' does not exist...$VCPKGROOT must point to the root directory of a VCPkg repository containing this file')

    if env['PLATFORM'] == 'win32':
        vcpkg_exe = vcpkgroot_dir.File('vcpkg.exe')
        bootstrap_vcpkg_script = vcpkgroot_dir.File('bootstrap-vcpkg.bat')
    elif env['PLATFORM'] == 'darwin' or env['PLATFORM'] == 'posix':
        vcpkg_exe = vcpkgroot_dir.File('vcpkg')
        bootstrap_vcpkg_script = vcpkgroot_dir.File('bootstrap-vcpkg.sh')
    else:
        raise UserError('This architecture/platform (%s/%s) is currently unsupported with VCPkg' % (env['TARGET_ARCH'], env['PLATFORM']))

    # We need to build vcpkg.exe if it doesn't exist, or if it has a different "base" version than the source code
    build_vcpkg = not vcpkg_exe.exists()
    if not build_vcpkg:
        built_version = _get_built_vcpkg_base_version(vcpkg_exe)
        source_version = _get_source_vcpkg_version(vcpkgroot_dir)
        if built_version != source_version and not built_version.startswith(source_version + '-'):
            print(vcpkg_exe.get_path() + ' (version ' + built_version + ') is out of date (source version: ' + source_version + '); rebuilding')
            build_vcpkg = True
        else:
            print(vcpkg_exe.get_path() + ' (version ' + built_version + ') is up-to-date')

    # If we need to build, do it now, and ensure that it built
    if build_vcpkg:
        if not bootstrap_vcpkg_script.exists():
            raise InternalError(bootstrap_vcpkg_script.get_path() + ' does not exist...what gives?')
        print('Building vcpkg binary')
        if subprocess.call(bootstrap_vcpkg_script.get_abspath()) != 0:
            raise BuildError(bootstrap_vcpkg_script.get_path() + ' failed')
        vcpkg_exe.clear_memoized_values()
        if not vcpkg_exe.exists():
            raise BuildError(bootstrap_vcpkg_script.get_path() + ' failed to create ' + vcpkg_exe.get_path())

    # Remember this, so we don't run these checks again
    env['_VCPKG_EXE'] = vcpkg_exe
    return vcpkg_exe


def _call_vcpkg(env, params, check_output = False):
    """Run the vcpkg executable wth the given set of parameters, optionally returning its standard output as a string. If the vcpkg executable is not yet built, or out of date, it will be rebuilt."""

    vcpkg_exe = _bootstrap_vcpkg(env)
    command_line = [vcpkg_exe.get_abspath()] + params
    print(str(command_line))
    if check_output:
        return str(subprocess.check_output(command_line, universal_newlines = True))
    else:
        return subprocess.call(args = command_line, universal_newlines = True)


def _get_vcpkg_triplet(env, static):
    """Computes the appropriate VCPkg 'triplet' for the current build environment"""

    platform = env['PLATFORM']

    if 'TARGET_ARCH' in env:
        arch = env['TARGET_ARCH']
    else:
        arch = env['HOST_ARCH']

    if platform == 'win32':
        if arch == 'x86' or arch == 'i386':
            return 'x86-windows-static' if static else 'x86-windows'
        elif arch == 'x86_64' or arch == 'x64' or arch == 'amd64':
            return 'x64-windows-static' if static else 'x64-windows'
        elif arch == 'arm':
            return 'arm-windows'
        elif arch == 'arm64':
            return 'arm64-windows'
    elif platform == 'darwin':
        if arch == 'x86_64':
            return 'x64-osx'
    elif platform == 'posix':
#         if arch == 'x86_64':
        return 'x64-linux'

    raise UserError('This architecture/platform (%s/%s) is currently unsupported with VCPkg' % (arch, platform))


def _parse_build_depends(s):
    """Given a string from the Build-Depends field of a CONTROL file, parse just the package name from it"""

    match_name = re.match(r'^\s*([^\(\)\[\] ]+)\s*(\[.*\])?$', s)
    if not match_name:
        print('Failed to parse package name from string "' + s + '"')
        return s

    return match_name.group(1), match_name.group(2)


def _read_vcpkg_file_list(env, list_file):
    """Read a .list file for a built package and return a list of File nodes for the files it contains (ignoring directories)"""

    files = []
    for line in open(list_file.get_abspath()):
        if not line.rstrip().endswith('/'):
            files.append(env.File('$VCPKGROOT/installed/' + line))
    return files


def _get_package_version(env, spec):
    """Read the CONTROL file for a package, returning (version, depends[])"""

    name = spec.split('[')[0]
    control_file = env.File('$VCPKGROOT/ports/' + name + '/CONTROL')
    version = None
    for line in open(control_file.get_abspath()):
        match_version = re.match(r'^Version: (\S+)$', line)
        if match_version:
            version = match_version.group(1)
            break
    if version is None:
        raise InternalError('Failed to parse package version from control file "' + control_file.get_abspath() + '"')
    return version


def _get_package_deps(env, spec, static):
    """Call 'vcpkg depend-info' to query for the dependencies of a package"""

    # TODO: compute these from the vcpkg base version
    _vcpkg_supports_triplet_param = True
    _vcpkg_supports_max_recurse_param = True
    _vcpkg_supports_no_recurse_param = False
    params = ['depend-info']

    # Try to filter to only first-level dependencies
    if _vcpkg_supports_max_recurse_param:
        params.append('--max-recurse=0')
    elif _vcpkg_supports_no_recurse_param:
        params.append('--no-recurse')

    if _vcpkg_supports_triplet_param:
        # Append the package spec + triplet
        params += ['--triplet', _get_vcpkg_triplet(env, static), spec]
    else:
        # OK, VCPkg doesn't know about the --triplet param, which means that it also doesn't understnd package specs
        # containing feature specifications. So, we'll strip these out (but possibly miss some dependencies).
        params.append(spec.split('[')[0])

    output = _call_vcpkg(env, params, check_output = True)
    deps_list = output[output.index(':') + 1:].split(',')
    deps_list = list(map(lambda s: s.strip(), deps_list))
    deps_list = list(filter(lambda s: s != "", deps_list))
    return deps_list


# Global mapping of previously-computed package-name -> list-file targets. This
# exists because we may discover additional packages that we need to build, based
# on the Build-Depends field in the CONTROL file), and these packages may or may
# not have been explicitly requested by the 
# CHECKIN
_package_descriptors_map = {}
_package_targets_map = {}

class PackageDescriptor(SCons.Node.Python.Value):

    def __init__(self, env, spec, static = False):
        _bootstrap_vcpkg(env)

        triplet = _get_vcpkg_triplet(env, static)
        env.AppendUnique(CPPPATH = ['$VCPKGROOT/installed/' + triplet + '/include/'])
        if env.subst('$VCPKGDEBUG') == 'True':
            env.AppendUnique(LIBPATH = '$VCPKGROOT/installed/' + triplet + '/debug/lib/')
            env.AppendUnique(PATH = '$VCPKGROOT/installed/' + triplet + '/debug/bin/')
        else:
            env.AppendUnique(LIBPATH = '$VCPKGROOT/installed/' + triplet + '/lib/')
            env.AppendUnique(PATH = '$VCPKGROOT/installed/' + triplet + '/bin/')

        if spec is None or spec == '':
            raise ValueError('VCPkg: Package spec must not be empty')

        matches = re.match(r'^([^[]+)(?:\[([^[]+)\])?$', spec)
        if not matches:
            raise ValueError('VCPkg: Malformed package spec "' + spec + '"')

        name = matches[1]
        features = matches[2]
        version = _get_package_version(env, name)
        depends = _get_package_deps(env, spec, static)
        value = {
            'name':     name,
            'features': features,
            'static':   static,
            'version':  version,
        }

        super(PackageDescriptor, self).__init__(value)
        self.env = env
        self.package_deps = depends

    def get_package_string(self):
        s = self.value['name']
        if self.value['features'] is not None:
            s += '[' + self.value['features'] + ']'
        s += ':' + _get_vcpkg_triplet(self.env, self.value['static'])
        return s

    def __str__(self):
        return self.get_package_string()

    def is_mismatched_version_installed(self):
        triplet = _get_vcpkg_triplet(self.env, self.value['static'])
        list_file = self.env.File('$VCPKGROOT/installed/vcpkg/info/' + self.value['name'] + '_' + self.value['version'] + '_' + triplet + '.list')
        if list_file.exists():
            return False

        installed = _call_vcpkg(self.env, ['list', self.value['name'] + ':' + triplet], check_output = True)
        if installed == '' or installed.startswith('No packages are installed'):
            return False

        match = re.match(r'^\S+\s+(\S+)\s+\S', installed)
        if match[1] == self.value['version']:
            raise InternalError("VCPkg thinks " + str(self) + " is installed, but '" + list_file.get_abspath() + "' does not exist")
        print("Installed is " + match[1])
        return True

    def target_from_source(self, pre, suf, splitext):
        _bootstrap_vcpkg(self.env)

        target = self.env.File('$VCPKGROOT/installed/vcpkg/info/' + self.value['name'] + '_' + self.value['version'] + '_' + _get_vcpkg_triplet(self.env, self.value['static']) + suf)
        target.state = SCons.Node.up_to_date

#         print("target_from_source: " + self.value['name'])
        for pkg in self.package_deps:
            # CHECKIN: verify features
            if pkg in _package_targets_map:
#                 print("Reused dep: " + str(_package_targets_map[pkg]))
                self.env.Depends(target, _package_targets_map[pkg])
            else:
#                 print("New dep: " + str(pkg))
                dep = self.env.VCPkg(pkg)
#                 print("Depends: " + str(dep[0]))
                self.env.Depends(target, dep[0])

        if not target.exists():
            if self.is_mismatched_version_installed():
                if _call_vcpkg(self.env, ['upgrade', '--no-dry-run', str(self)]) != 0:
                    print("Failed to upgrade package '" + str(self) + "'")
                    target.state = SCons.Node.failed
            elif _call_vcpkg(self.env, ['install', str(self)]) != 0:
                print("Failed to install package '" + str(self) + "'")
                target.state = SCons.Node.failed
            target.clear_memoized_values()
            if not target.exists():
                print("What gives? vcpkg install failed to create '" + target.get_abspath() + "'")
                target.state = SCons.Node.failed

        target.precious = True
        target.noclean = True

        print("Caching target for package: " + self.value['name'])
        _package_targets_map[self.value['name']] = target

        return target


def get_package_descriptor(env, spec):
    if spec in _package_descriptors_map:
        return _package_descriptors_map[spec]
    desc = PackageDescriptor(env, spec)
    _package_descriptors_map[spec] = desc
    return desc


def vcpkg_action(target, source, env):
    pass
#     packages = list(map(str, source))
#     print("Running action")
#     return _call_vcpkg(env, ['install'] + packages)


def get_vcpkg_deps(node, env, path, arg):
    print("Scan!!!!")
    deps = []
    if not node.package_deps is None:
        for pkg in node.package_deps:
            target = env.VCPkg(pkg)
            deps += target[0]
            print("Dep: " + str(target[0]))
    return deps


vcpkg_source_scanner = SCons.Script.Scanner(function = get_vcpkg_deps,
                                            argument = None)


def vcpkg_emitter(target, source, env):
    _bootstrap_vcpkg(env)

    for t in target:
        if not t.exists():
            vcpkg_action(target, source, env)
            break

    built = []
    for t in target:
        built += _read_vcpkg_file_list(env, t)

    for f in built:
        f.precious = True
        f.noclean = True
        f.state = SCons.Node.up_to_date

    target += built

    return target, source


# TODO: static?
def generate(env):
    """Add Builders and construction variables for vcpkg to an Environment."""
    VCPkgBuilder = SCons.Builder.Builder(action = vcpkg_action,
                                         source_factory = lambda spec: get_package_descriptor(env, spec),
                                         target_factory = SCons.Node.FS.File,
                                         source_scanner = vcpkg_source_scanner,
                                         suffix = '.list',
                                         emitter = vcpkg_emitter)

    env['BUILDERS']['VCPkg'] = VCPkgBuilder

def exists(env):
    return 1

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
