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
Tool-specific initialization for vcpkg.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.


TODO:
  * find a way to push package build into SCons's normal build phase
  * ensure Linux works
  * handle complex feature supersetting scenarios
  * parallel builds?
  * can we ensure granular detection, and fail on undetected dependencies?
  * batch depend-info calls to vcpkg for better perf?
  * Make "vcpkg search" faster by supporting a strict match option
  * Is there a way to make vcpkg build only dgb/rel libs?

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


# Named constants for verbosity levels supported by _vcpkg_print
Silent = 0
Normal = 1
Debug = 2

_max_verbosity = Normal # Can be changed with --silent or --vcpkg-debug

# Add --vcpkg-debug command-line option
SCons.Script.AddOption('--vcpkg-debug', dest = 'vcpkg-debug', default = False, action = 'store_true',
                       help = 'Emit verbose debugging spew from the vcpkg builder')

def _vcpkg_print(verbosity, *args):
    """If the user wants to see messages of 'verbosity', prints *args with a 'vcpkg' prefix"""

    if verbosity <= _max_verbosity:
        print('vcpkg: ', end='')
        print(*args)


def _get_built_vcpkg_full_version(vcpkg_exe):
    """Runs 'vcpkg version' and parses the version string from the output"""

    if not vcpkg_exe.exists():
        raise InternalError(vcpkg_exe.get_path() + ' does not exist')

    line = subprocess.check_output([vcpkg_exe.get_abspath(), 'version'], text = True)
    match_version = re.search(r' version (\S+)', line)
    if (match_version):
        version = match_version.group(1)
        _vcpkg_print(Debug, 'vcpkg full version is "' + version + '"')
        return version
    raise InternalError(vcpkg_exe.get_path() + ': failed to parse version string')


def _get_built_vcpkg_base_version(vcpkg_exe):
    """Returns just the base version from 'vcpkg version' (i.e., with any '-whatever' suffix stripped off"""
    full_version = _get_built_vcpkg_full_version(vcpkg_exe)

    # Allow either 2022-02-02 or 2022.02.02 date syntax
    match = re.match(r'^(\d{4}[.-]\d{2}[.-]\d{2})', full_version)
    if match:
        base_version = match.group(1)
        _vcpkg_print(Debug, 'vcpkg base version is "' + base_version + '"')
        return base_version

    _vcpkg_print(Debug, 'vcpkg base version is identical to full version "' + full_version + '"')
    return full_version


def _get_source_vcpkg_version(vcpkg_root):
    """Parses the vcpkg source code version out of VERSION.txt"""

    if not vcpkg_root.exists():
        raise InternalError(vcpkg_root.get_path() + ' does not exist')

    # Older vcpkg versions had the source version in VERSION.txt
    version_txt = vcpkg_root.File('toolsrc/VERSION.txt')
    if version_txt.exists():
        _vcpkg_print(Debug, "Looking for source version in " + version_txt.get_path())
        for line in open(version_txt.get_abspath()):
            match_version = re.match(r'^"(.*)"$', line)
            if (match_version):
                version = match_version.group(1)

                # Newer versions of vcpkg have a hard-coded invalid date in the VERSION.txt for local builds,
                # and the actual version comes from the bootstrap.ps1 script
                if version != '9999.99.99':
                    _vcpkg_print(Debug, 'Found valid vcpkg source version "' + version + '" in VERSION.txt')
                    return version
                else:
                    _vcpkg_print(Debug, 'VERSION.txt contains invalid vcpkg source version "' + version + '"')
                    break

    # Newer versions of bootstrap-vcpkg simply download a pre-built executable from GitHub, and the version to download
    # is hard-coded in a deployment script.
    bootstrap_ps1 = vcpkg_root.File('scripts/bootstrap.ps1')
    if bootstrap_ps1.exists():
        for line in open(bootstrap_ps1.get_abspath()):
            match_version = re.match(r"\$versionDate\s*=\s*'(.*)'", line)
            if match_version:
                version = match_version.group(1)
                _vcpkg_print(Debug, 'Found valid vcpkg source version "' + version + '" in bootstrap.ps1')
                return version

    raise InternalError("Failed to determine vcpkg source version")


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
            _vcpkg_print(Normal, 'vcpkg executable (version ' + built_version + ') is out of date (source version: ' + source_version + '); rebuilding')
            build_vcpkg = True
        else:
            _vcpkg_print(Debug, 'vcpkg executable (version ' + built_version + ') is up-to-date')

    # If we need to build, do it now, and ensure that it built
    if build_vcpkg:
        if not bootstrap_vcpkg_script.exists():
            raise InternalError(bootstrap_vcpkg_script.get_path() + ' does not exist...what gives?')
        _vcpkg_print(Normal, 'Building vcpkg binary')
        if subprocess.call(bootstrap_vcpkg_script.get_abspath()) != 0:
            raise BuildError(bootstrap_vcpkg_script.get_path() + ' failed')
        vcpkg_exe.clear_memoized_values()
        if not vcpkg_exe.exists():
            raise BuildError(bootstrap_vcpkg_script.get_path() + ' failed to create ' + vcpkg_exe.get_path())

    # Remember this, so we don't run these checks again
    env['_VCPKG_EXE'] = vcpkg_exe
    return vcpkg_exe


def _call_vcpkg(env, params, check_output = False, check = True):
    """Run the vcpkg executable wth the given set of parameters, optionally returning its standard output as a string. If the vcpkg executable is not yet built, or out of date, it will be rebuilt."""

    vcpkg_exe = _bootstrap_vcpkg(env)
    command_line = [vcpkg_exe.get_abspath()] + params
    _vcpkg_print(Debug, "Running " + str(command_line))
    try:
        result = subprocess.run(command_line, text = True, capture_output = check_output or _max_verbosity == Silent, check = check)
        if check_output:
            _vcpkg_print(Debug, result.stdout)
            return result.stdout
        else:
            return result.returncode
    except subprocess.CalledProcessError as ex:
        if check_output:
            _vcpkg_print(Silent, ex.stdout)
            _vcpkg_print(Silent, ex.stderr)
            return ex.stdout
        else:
            return ex.returncode


def _install_packages(env, packages):
    packages_args = list(map(lambda p: str(p), packages))
    _vcpkg_print(Silent, ' '.join(packages_args) + ' (install)')
    result = _call_vcpkg(env, ['install'] + packages_args)
    if result != 0:
        _vcpkg_print(Silent, "Failed to install package(s) " + ' '.join(packages_args))
    return result


def _upgrade_packages(env, packages):
    packages_args = list(map(lambda p: str(p), packages))
    _vcpkg_print(Silent, ' '.join(packages_args) + ' (upgrade)')
    result = _call_vcpkg(env, ['upgrade', '--no-dry-run'] + packages_args)
    if result != 0:
        _vcpkg_print(Silent, "Failed to upgrade package(s) " + ' '.join(packages_args))
    return result


def _get_vcpkg_triplet(env, static):
    """Computes the appropriate VCPkg 'triplet' for the current build environment"""

    platform = env['PLATFORM']

    # TODO: this relies on having a C++ compiler tool enabled. Is there a better way to compute this?
    if 'TARGET_ARCH' in env and env['TARGET_ARCH'] is not None:
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
        if arch == 'x86_64':
            return 'x64-linux'

    raise UserError('This architecture/platform (%s/%s) is currently unsupported with VCPkg' % (arch, platform))


def _read_vcpkg_file_list(env, list_file):
    """Read a .list file for a built package and return a list of File nodes for the files it contains (ignoring directories)"""

    files = []
    for line in open(list_file.get_abspath()):
        if not line.rstrip().endswith('/'):
            files.append(env.File('$VCPKGROOT/installed/' + line))
    return files


def is_mismatched_version_installed(env, spec):
    _vcpkg_print(Debug, 'Checking for mismatched version of "' + spec + '"')
    output = _call_vcpkg(env, ['update'], check_output = True)
    for line in output.split('\n'):
        match = re.match(r'^\s*(\S+)\s*(\S+) -> (\S+)', line)
        if match and match.group(1) == spec:
            _vcpkg_print(Debug, 'Package "' + spec + '" can be updated (' + match.group(2) + ' -> ' + match.group(3) + ')')
            return True
    return False


def _get_package_version(env, spec):
    """Read the available version of a package (i.e., what would be installed)"""

    name = spec.split('[')[0]
    output = _call_vcpkg(env, ['search', name], check_output = True)
    for line in output.split('\n'):
        match = re.match(r'^(\S+)\s*(\S+)', line)
        if match and match.group(1) == name:
            version = match.group(2)
            _vcpkg_print(Debug, 'Available version of package "' + name + '" is ' + version)
            return version
    raise UserError('No package "' + name + '" found via vcpkg search')


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

    name = spec.split('[')[0]
    output = _call_vcpkg(env, params, check_output = True)
    for line in output.split('\n'):
        match = re.match(r'^([^:[]+)(?:\[[^]]+\])?:\s*(.+)?', line)
        if match and match.group(1) == name:
            deps_list = []
            if match.group(2):
                deps_list = list(filter(lambda s: s != "", map(lambda s: s.strip(), match.group(2).split(','))))
            _vcpkg_print(Debug, 'Package ' + spec + ' has dependencies [' + ','.join(deps_list) + ']')
            return deps_list
    raise InternalError('Failed to parse output from vcpkg ' + ' '.join(params) + '\n' + output)


def get_package_descriptors_map(env):
    """Returns an Environment-global mapping of previously-seen package name -> PackageDescriptor, ensuring a 1:1
       correspondence between a package and its PackageDescriptor. This global mapping is needed because a package
       may need to be built due to being a dependency of a user-requested package, and a given package may be a
       dependency of multiple user-requested packages, or may be a dependency of a user-requested package via multiple
       paths in the package dependency graph."""
    if not hasattr(env, '_vcpkg_package_descriptors_map'):
        env._vcpkg_package_descriptors_map = {}
    return env._vcpkg_package_descriptors_map

def get_package_targets_map(env):
    """Returns an Environment-global mapping of previously-seen package name -> PackageContents. This global mapping
       is needed because the contents-enumeration methods of PackageContents need to be able to access the contents
       of their dependencies when transitive = True is specified."""
    if not hasattr(env, '_vcpkg_package_targets_map'):
        env._vcpkg_package_targets_map = {}
    return env._vcpkg_package_targets_map

class PackageDescriptor(SCons.Node.Python.Value):
    """PackageDescriptor is the 'source' node for the VCPkg builder. A PackageDescriptor instance includes the package
       name, version and linkage (static or dynamic), and a list of other packages that it depends on."""

    def __init__(self, env, spec, static = False):
        _bootstrap_vcpkg(env)

        triplet = _get_vcpkg_triplet(env, static)
        env.AppendUnique(CPPPATH = ['$VCPKGROOT/installed/' + triplet + '/include/'])
        if env.subst('$VCPKGDEBUG') == 'True':
            env.AppendUnique(LIBPATH = ['$VCPKGROOT/installed/' + triplet + '/debug/lib/'])
        else:
            env.AppendUnique(LIBPATH = ['$VCPKGROOT/installed/' + triplet + '/lib/'])

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
            'triplet':  triplet
        }

        super(PackageDescriptor, self).__init__(value)
        self.env = env
        self.package_deps = list(map(lambda p: get_package_descriptor(env, p), depends))

    def get_name(self):
        return self.value['name']

    def get_static(self):
        return self.value['static']

    def get_triplet(self):
        return self.value['triplet']

    def get_package_string(self):
        s = self.value['name']
        if self.value['features'] is not None:
            s += '[' + self.value['features'] + ']'
        s += ':' + self.value['triplet']
        return s

    def get_listfile_basename(self):
        # Trim off any suffix like '#3' from the version, as this doesn't appear in the listfile name
        version = self.value['version']
        hash_pos = version.find('#')
        if hash_pos != -1:
            version = version[0:hash_pos]
        return self.value['name'] + '_' + version + '_' + self.value['triplet']

    def __str__(self):
        return self.get_package_string()

    def target_from_source(self, pre, suf, splitext):
        _bootstrap_vcpkg(self.env)

        target = PackageContents(self.env, self)
        target.state = SCons.Node.up_to_date

        package_targets_map = get_package_targets_map(self.env)

        for pkg in self.package_deps:
            if pkg in package_targets_map:
                _vcpkg_print(Debug, 'Reused dep: ' + str(package_targets_map[pkg]))
                self.env.Depends(target, package_targets_map[pkg])
            else:
                _vcpkg_print(Debug, "New dep: " + str(pkg))
                dep = self.env.VCPkg(pkg)
                self.env.Depends(target, dep[0])

        if not SCons.Script.GetOption('help'):
            if not target.exists():
                if is_mismatched_version_installed(self.env, str(self)):
                    if _upgrade_packages(self.env, [self]) != 0:
                        target.state = SCons.Node.failed
                else:
                    if _install_packages(self.env, [self]) != 0:
                        target.state = SCons.Node.failed
                target.clear_memoized_values()
                if not target.exists():
                    _vcpkg_print(Silent, "What gives? vcpkg install failed to create '" + target.get_abspath() + "'")
                    target.state = SCons.Node.failed

        target.precious = True
        target.noclean = True

        _vcpkg_print(Debug, "Caching target for package: " + self.value['name'])
        package_targets_map[self] = target

        return target


class PackageContents(SCons.Node.FS.File):
    """PackageContents is a File node (referring to the installed package's .list file) and is the 'target' node of
       the VCPkg builder (though currently, it doesn't actually get built during SCons's normal build phase, since
       vcpkg currently can't tell us what files will be installed without actually doing the work).

       It includes functionality for enumerating the different kinds of files (headers, libraries, etc.) produced by
       installing the package."""

    def __init__(self, env, descriptor):
        super().__init__(descriptor.get_listfile_basename() + ".list", env.Dir('$VCPKGROOT/installed/vcpkg/info/'), env.fs)
        self.descriptor = descriptor
        self.loaded = False

    def Headers(self, transitive = False):
        """Returns the list of C/C++ header files belonging to the package.
           If `transitive` is True, then files belonging to upstream dependencies of this package are also included."""
        return self.FilesUnderSubPath('include/', transitive)

    def StaticLibraries(self, transitive = False):
        """Returns the list of static libraries belonging to the package.
           If `transitive` is True, then files belonging to upstream dependencies of this package are also included."""
        if self.env.subst('$VCPKGDEBUG') == 'True':
            return self.FilesUnderSubPath('debug/lib/', transitive, self.env['LIBSUFFIX'])
        else:
            return self.FilesUnderSubPath('lib/', transitive, self.env['LIBSUFFIX'])

    def SharedLibraries(self, transitive = False):
        """Returns the list of shared libraries belonging to the package.
           If `transitive` is True, then files belonging to upstream dependencies of this package are also included."""
        if self.env.subst('$VCPKGDEBUG') == 'True':
            return self.FilesUnderSubPath('debug/bin/', transitive, self.env['SHLIBSUFFIX'])
        else:
            return self.FilesUnderSubPath('bin/', transitive, self.env['SHLIBSUFFIX'])

    def FilesUnderSubPath(self, subpath, transitive = False, suffix_filters = None, packages_visited = None):
        """Returns a (possibly empty) list of File nodes belonging to this package that are located under the
           relative path `subpath` underneath the triplet install directory.
           If `transitive` is True, then files belonging to upstream dependencies of this package are also included.
           If 'suffix_filters is not None, but instead a string or a list, then only files ending in the substring(s)
           listed therein will be included."""

        # Load the listfile contents, if we haven't already. This returns a list of File nodes.
        if not self.loaded:
            if not self.exists():
                raise InternalError(self.get_path() + ' does not exist')
            _vcpkg_print(Debug, 'Loading ' + str(self.descriptor) + ' listfile: ' + self.get_path())
            self.files = _read_vcpkg_file_list(self.env, self)
            self.loaded = True

        # Compute the appropriate filter check based on 'suffix_filters'
        if suffix_filters is None:
            matches_filters = lambda f: True
        elif type(suffix_filters) is str:
            matches_filters = lambda f: f.endswith(suffix_filters)
        elif type(suffix_filters) is list:
            matches_filters = lambda f: len(filter(lambda s: f.endswith(s), suffix_filters)) > 0

        prefix = self.env.Dir(self.env.subst('$VCPKGROOT/installed/' + self.descriptor.get_triplet() + "/" + subpath))
        _vcpkg_print(Debug, 'Looking for files under ' + str(prefix))
        matching_files = []
        for file in self.files:
            if file.is_under(prefix) and matches_filters(file.get_abspath()):
                _vcpkg_print(Debug, 'Matching file ' + file.get_abspath())
                matching_files += [file]

        # If the caller requested us to also recurse into dependencies, do that now. However, don't visit the same
        # package more than once (i.e., if it's reachable via multiple paths in the dependency graph)
        if transitive:
            if packages_visited is None:
                packages_visited = []
            package_targets_map = get_package_targets_map(self.env)
            for dep in self.descriptor.package_deps:
                dep_pkg = package_targets_map[dep]
                if dep_pkg not in packages_visited:
                    matching_files += dep_pkg.FilesUnderSubPath(subpath, transitive, suffix_filters, packages_visited)
            packages_visited.append(self)

        return SCons.Util.NodeList(matching_files)

    def __str__(self):
        return "Package: " + super(PackageContents, self).__str__()


def get_package_descriptor(env, spec):
    package_descriptors_map = get_package_descriptors_map(env)
    if spec in package_descriptors_map:
        return package_descriptors_map[spec]
    desc = PackageDescriptor(env, spec)
    package_descriptors_map[spec] = desc
    return desc


# TODO: at the moment, we can't execute vcpkg install at the "normal" point in time, because we need to know what
# files are produced by running this, and we can't do that without actually running the command. Thus, we have to
# shoe-horn the building of packages into the target_from_source function. If vcpkg supported some kind of "outputs"
# mode where it could spit out the contents of the .list file without actually doing the build, then we could defer
# the build until vcpkg_action.
def vcpkg_action(target, source, env):
    pass
#     packages = list(map(str, source))
#     return _call_vcpkg(env, ['install'] + packages)


def get_vcpkg_deps(node, env, path, arg):
    deps = []
    if node.package_deps is not None:
        for pkg in node.package_deps:
            target = env.VCPkg(pkg)
            deps += target[0]
            _vcpkg_print(Debug, 'Found dependency: "' + str(node) + '" -> "' + str(target[0]))
    return deps


vcpkg_source_scanner = SCons.Script.Scanner(function = get_vcpkg_deps,
                                            argument = None)


# TODO: do we need the emitter at all?
def vcpkg_emitter(target, source, env):
    _bootstrap_vcpkg(env)

    for t in target:
        if not t.exists():
            vcpkg_action(target, source, env)
            break

    built = []
#     for t in target:
#         built += _read_vcpkg_file_list(env, t)

    for f in built:
        f.precious = True
        f.noclean = True
        f.state = SCons.Node.up_to_date

    target += built

    return target, source


# TODO: static?
def generate(env):
    """Add Builders and construction variables for vcpkg to an Environment."""

    # Set verbosity to the appropriate level
    global _max_verbosity
    if SCons.Script.GetOption('vcpkg-debug'):
        _max_verbosity = Debug
    elif SCons.Script.GetOption('silent'):
        _max_verbosity = Silent
    else:
        _max_verbosity = Normal

    # single_source = True shouldn't be required, as VCPkgBuilder is capable of handling lists of inputs.
    # However, there are appears to be a bug in how Builder._createNodes processes lists of nodes, and
    # the result is that VCPkgBuilder only gets the first item in the list.
    VCPkgBuilder = SCons.Builder.Builder(action = vcpkg_action,
                                         source_factory = lambda spec: get_package_descriptor(env, spec),
                                         target_factory = lambda desc: PackageContents(env, desc),
                                         source_scanner = vcpkg_source_scanner,
                                         single_source = True,
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
