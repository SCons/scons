#
# SConstruct file to build scons packages during development.
#

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

import distutils.util
import os
import os.path
import stat
import string
import sys
import time

project = 'scons'
default_version = '0.05'

Default('.')

#
# An internal "whereis" routine to figure out if we have a
# given program available.  Put it in the "cons::" package
# so subsidiary Conscript files can get at it easily, too.
#

def whereis(file):
    for dir in string.split(os.environ['PATH'], os.pathsep):
        f = os.path.join(dir, file)
        if os.path.isfile(f):
            try:
                st = os.stat(f)
            except:
                continue
            if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                return f
    return None

#
# We let the presence or absence of various utilities determine
# whether or not we bother to build certain pieces of things.
# This will allow people to still do SCons work even if they
# don't have Aegis or RPM installed, for example.
#
aegis = whereis('aegis')
aesub = whereis('aesub')
rpm = whereis('rpm')
dh_builddeb = whereis('dh_builddeb')
fakeroot = whereis('fakeroot')

# My installation on Red Hat doesn't like any debhelper version
# beyond 2, so let's use 2 as the default on any non-Debian build.
if os.path.isfile('/etc/debian_version'):
    dh_compat = 3
else:
    dh_compat = 2

#
# Now grab the information that we "build" into the files (using sed).
#
try:
    date = ARGUMENTS['date']
except:
    date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
    
if ARGUMENTS.has_key('developer'):
    developer = ARGUMENTS['developer']
elif os.environ.has_key('USERNAME'):
    developer = os.environ['USERNAME']
elif os.environ.has_key('LOGNAME'):
    developer = os.environ['LOGNAME']
elif os.environ.has_key('USER'):
    developer = os.environ['USER']

try:
    revision = ARGUMENTS['version']
except:
    if aesub:
        revision = os.popen(aesub + " \\$version", "r").read()[:-1]
    else:
        revision = default_version

a = string.split(revision, '.')
arr = [a[0]]
for s in a[1:]:
    if len(s) == 1:
        s = '0' + s
    arr.append(s)
revision = string.join(arr, '.')

# Here's how we'd turn the calculated $revision into our package $version.
# This makes it difficult to coordinate with other files (debian/changelog
# and rpm/scons.spec) that hard-code the version number, so just go with
# the flow for now and hard code it here, too.
#if len(arr) >= 2:
#    arr = arr[:-1]
#def xxx(str):
#    if str[0] == 'C' or str[0] == 'D':
#        str = str[1:]
#    while len(str) > 2 and str[0] == '0':
#        str = str[1:]
#    return str
#arr = map(lambda x, xxx=xxx: xxx(x), arr)
#version = string.join(arr, '.')
version = default_version

try:
    change = ARGUMENTS['change']
except:
    if aesub:
        change = os.popen(aesub + " \\$change", "r").read()[:-1]
    else:
        change = default_version

python_ver = sys.version[0:3]

platform = distutils.util.get_platform()

if platform == "win32":
    archsuffix = "zip"
else:
    archsuffix = "tar.gz"

ENV = { 'PATH' : os.environ['PATH'] }
if os.environ.has_key('AEGIS_PROJECT'):
    ENV['AEGIS_PROJECT'] = os.environ['AEGIS_PROJECT']

lib_project = os.path.join("lib", project)

unpack_dir = os.path.join(os.getcwd(), "build", "unpack")

test_arch_dir = os.path.join(os.getcwd(),
                             "build",
                             "test-%s" % string.replace(archsuffix, '.', '-'))

test_src_arch_dir = os.path.join(os.getcwd(),
                                 "build",
                                 "test-src-%s" % string.replace(archsuffix,
                                                                '.',
                                                                '-'))

test_rpm_dir = os.path.join(os.getcwd(), "build", "test-rpm")

test_deb_dir = os.path.join(os.getcwd(), "build", "test-deb")

def SCons_revision(target, source, env):
    """Interpolate specific values from the environment into a file.
    
    This is used to copy files into a tree that gets packaged up
    into the source file package.
    """
    print "SCons_revision() < %s > %s" % (source[0], target)
    inf = open(source[0], 'rb')
    outf = open(target, 'wb')
    for line in inf.readlines():
        # Note:  We construct the __*__ substitution strings here
        # so that they don't get replaced when this file gets
        # copied into the tree for packaging.
        line = string.replace(line, '_' + '_DATE__', env['DATE'])
        line = string.replace(line, '_' + '_DEVELOPER__', env['DEVELOPER'])
        line = string.replace(line, '_' + '_FILE__', source[0])
        line = string.replace(line, '_' + '_REVISION__', env['REVISION'])
        line = string.replace(line, '_' + '_VERSION__', env['VERSION'])
        outf.write(line)
    inf.close()
    outf.close()
    os.chmod(target, os.stat(source[0])[0])

revbuilder = Builder(name = 'SCons_revision', action = SCons_revision)

env = Environment(
                   ENV           = ENV,
 
                   DATE          = date,
                   DEVELOPER     = developer,
                   REVISION      = revision,
                   VERSION       = version,
                   DH_COMPAT     = dh_compat,

                   BUILDERS      = [ revbuilder ],
                 )

#
# Define SCons packages.
#
# In the original, more complicated packaging scheme, we were going
# to have separate packages for:
#
#	python-scons	only the build engine
#	scons-script	only the script
#	scons		the script plus the build engine
#
# We're now only delivering a single "scons" package, but this is still
# "built" as two sub-packages (the build engine and the script), so
# the definitions remain here, even though we're not using them for
# separate packages.
#

python_scons = {
        'pkg'           : 'python-' + project,
        'src_subdir'    : 'engine',
        'inst_subdir'   : os.path.join('lib', 'python1.5', 'site-packages'),

        'debian_deps'   : [
                            'debian/rules',
                            'debian/control',
                            'debian/changelog',
                            'debian/copyright',
                            'debian/python-scons.postinst',
                            'debian/python-scons.prerm',
                          ],

        'files'         : [ 'LICENSE.txt',
                            'README.txt',
                            'setup.cfg',
                            'setup.py',
                          ],

        'filemap'       : {
                            'LICENSE.txt' : '../LICENSE.txt'
                          },
}

#
# The original packaging scheme would have have required us to push
# the Python version number into the package name (python1.5-scons,
# python2.0-scons, etc.), which would have required a definition
# like the following.  Leave this here in case we ever decide to do
# this in the future, but note that this would require some modification
# to src/engine/setup.py before it would really work.
#
#python2_scons = {
#        'pkg'          : 'python2-' + project,
#        'src_subdir'   : 'engine',
#        'inst_subdir'  : os.path.join('lib', 'python2.1', 'site-packages'),
#
#        'debian_deps'  : [
#                           'debian/rules',
#                           'debian/control',
#                           'debian/changelog',
#                           'debian/copyright',
#                           'debian/python2-scons.postinst',
#                           'debian/python2-scons.prerm',
#                          ],
#
#        'files'        : [
#                            'LICENSE.txt',
#                            'README.txt',
#                            'setup.cfg',
#                            'setup.py',
#                          ],
#        'filemap'      : {
#                            'LICENSE.txt' : '../LICENSE.txt',
#                          },
#}
#

scons_script = {
        'pkg'           : project + '-script',
        'src_subdir'    : 'script',
        'inst_subdir'   : 'bin',

        'debian_deps'   : [
                            'debian/rules',
                            'debian/control',
                            'debian/changelog',
                            'debian/copyright',
                            'debian/python-scons.postinst',
                            'debian/python-scons.prerm',
                          ],

        'files'         : [
                            'LICENSE.txt',
                            'README.txt',
                            'setup.cfg',
                            'setup.py',
                          ],

        'filemap'       : {
                            'LICENSE.txt' : '../LICENSE.txt',
                            'scons'       : 'scons.py',
                           }
}

scons = {
        'pkg'           : project,

        'debian_deps'   : [ 
                            'debian/rules',
                            'debian/control',
                            'debian/changelog',
                            'debian/copyright',
                            'debian/scons.postinst',
                            'debian/scons.prerm',
                          ],

        'files'         : [ 
                            'CHANGES.txt',
                            'LICENSE.txt',
                            'README.txt',
                            'RELEASE.txt',
                            'os_spawnv_fix.diff',
                            'scons.1',
                            'script/scons.bat',
                            'setup.cfg',
                            'setup.py',
                          ],

        'filemap'       : {
                            'scons.1' : '../doc/man/scons.1',
                          },

        'subpkgs'	: [ python_scons, scons_script ],

        'subinst_dirs'	: {
                             'python-' + project : lib_project,
                             project + '-script' : 'bin',
                           },
}

src_deps = []
src_files = []

for p in [ scons ]:
    #
    # Initialize variables with the right directories for this package.
    #
    pkg = p['pkg']
    pkg_version = "%s-%s" % (pkg, version)

    src = 'src'
    if p.has_key('src_subdir'):
        src = os.path.join(src, p['src_subdir'])

    build = os.path.join('build', pkg)

    #
    # Read up the list of source files from our MANIFEST.in.
    # This list should *not* include LICENSE.txt, MANIFEST,
    # README.txt, or setup.py.  Make a copy of the list for the
    # destination files.
    #
    src_files = map(lambda x: x[:-1],
                    open(os.path.join(src, 'MANIFEST.in')).readlines())
    dst_files = src_files[:]

    if p.has_key('subpkgs'):
        #
        # This package includes some sub-packages.  Read up their
        # MANIFEST.in files, and add them to our source and destination
        # file lists, modifying them as appropriate to add the
        # specified subdirs.
        #
        for sp in p['subpkgs']:
            ssubdir = sp['src_subdir']
            isubdir = p['subinst_dirs'][sp['pkg']]
            f = map(lambda x: x[:-1],
                    open(os.path.join(src, ssubdir, 'MANIFEST.in')).readlines())
            src_files.extend(map(lambda x, s=ssubdir: os.path.join(s, x), f))
            dst_files.extend(map(lambda x, i=isubdir: os.path.join(i, x), f))
            for k in sp['filemap'].keys():
                f = sp['filemap'][k]
                if f:
                    k = os.path.join(sp['src_subdir'], k)
                    p['filemap'][k] = os.path.join(sp['src_subdir'], f)

    #
    # Now that we have the "normal" source files, add those files
    # that are standard for each distribution.  Note that we don't
    # add these to dst_files, because they don't get installed.
    # And we still have the MANIFEST to add.
    #
    src_files.extend(p['files'])

    #
    # Now run everything in src_file through the sed command we
    # concocted to expand __FILE__, __VERSION__, etc.
    #
    for b in src_files:
	s = p['filemap'].get(b, b)
        env.SCons_revision(os.path.join(build, b), os.path.join(src, s))

    #
    # NOW, finally, we can create the MANIFEST, which we do
    # by having Python spit out the contents of the src_files
    # array we've carefully created.  After we've added
    # MANIFEST itself to the array, of course.
    #
    src_files.append("MANIFEST")
    def copy(target, source, **kw):
        global src_files
	src_files.sort()
        f = open(target, 'wb')
        for file in src_files:
            f.write(file + "\n")
        f.close()
        return 0
    env.Command(os.path.join(build, 'MANIFEST'),
                os.path.join(src, 'MANIFEST.in'),
                copy)

    #
    # Use the Python distutils to generate the packages.
    #
    archive = os.path.join(build, 'dist', "%s.%s" % (pkg_version, archsuffix))
    platform_archive = os.path.join(build,
                                    'dist',
                                    "%s.%s.%s" % (pkg_version,
                                                  platform,
                                                  archsuffix))
    win32_exe = os.path.join(build, 'dist', "%s.win32.exe" % pkg_version)

    src_deps.append(archive)

    build_targets = [ platform_archive, archive, win32_exe ]
    install_targets = build_targets[:]

    # We can get away with calling setup.py using a directory path
    # like this because we put a preamble in it that will chdir()
    # to the directory in which setup.py exists.
    bdist_dirs = [
        os.path.join(build, 'build', 'lib'),
        os.path.join(build, 'build', 'scripts'),
    ]
    setup_py = os.path.join(build, 'setup.py')
    commands = [
        "rm -rf %s && python %s bdist" %
            (string.join(map(lambda x: str(x), bdist_dirs)), setup_py),
        "python %s sdist" % setup_py,
        "python %s bdist_wininst" % setup_py,
    ]

    if rpm:
        topdir = os.path.join(os.getcwd(), build, 'build',
                              'bdist.' + platform, 'rpm')

	BUILDdir = os.path.join(topdir, 'BUILD', pkg + '-' + version)
	RPMSdir = os.path.join(topdir, 'RPMS', 'noarch')
	SOURCESdir = os.path.join(topdir, 'SOURCES')
	SPECSdir = os.path.join(topdir, 'SPECS')
	SRPMSdir = os.path.join(topdir, 'SRPMS')

        specfile = os.path.join(SPECSdir, "%s-1.spec" % pkg_version)
        sourcefile = os.path.join(SOURCESdir,
                                  "%s.%s" % (pkg_version, archsuffix));
        rpm = os.path.join(RPMSdir, "%s-1.noarch.rpm" % pkg_version)
        src_rpm = os.path.join(SRPMSdir, "%s-1.src.rpm" % pkg_version)

        env.InstallAs(specfile, os.path.join('rpm', "%s.spec" % pkg))
        env.InstallAs(sourcefile, archive)

        targets = [ rpm, src_rpm ]
        cmd = "rpm --define '_topdir $(%s$)' -ba $SOURCES" % topdir
        if not os.path.isdir(BUILDdir):
            cmd = ("$( mkdir -p %s; $)" % BUILDdir) + cmd
        env.Command(targets, specfile, cmd)
        env.Depends(targets, sourcefile)

        install_targets.extend(targets)

        dfiles = map(lambda x, d=test_rpm_dir: os.path.join(d, 'usr', x),
                     dst_files)
        env.Command(dfiles,
                    rpm,
                    "rpm2cpio $SOURCES | (cd %s && cpio -id)" % test_rpm_dir)

    build_src_files = map(lambda x, b=build: os.path.join(b, x), src_files)

    if dh_builddeb and fakeroot:
        # Debian builds directly into build/dist, so we don't
        # need to add the .debs to the install_targets.
        deb = os.path.join('build', 'dist', "%s_%s-1_all.deb" % (pkg, version))
        env.Command(deb, build_src_files, [
            "fakeroot make -f debian/rules VERSION=$VERSION DH_COMPAT=$DH_COMPAT ENVOKED_BY_CONSTRUCT=1 binary-%s" % pkg,
            "env DH_COMPAT=$DH_COMPAT dh_clean"
                    ])
        env.Depends(deb, p['debian_deps'])

        dfiles = map(lambda x, d=test_deb_dir: os.path.join(d, 'usr', x),
                     dst_files)
        env.Command(dfiles,
                    deb,
                    "dpkg --fsys-tarfile $SOURCES | (cd %s && tar -xf -)" % test_deb_dir)

    #
    # Now set up creation and installation of the packages.
    #
    env.Command(build_targets, build_src_files, commands)
    env.Install(os.path.join('build', 'dist'), install_targets)

    #
    # Unpack the archive created by the distutils into
    # build/unpack/scons-{version}.
    #
    unpack_files = map(lambda x, u=unpack_dir, pv=pkg_version:
                              os.path.join(u, pv, x),
                       src_files)

    #
    # We'd like to replace the last three lines with the following:
    #
    #	tar zxf %< -C $unpack_dir
    #
    # but that gives heartburn to Cygwin's tar, so work around it
    # with separate zcat-tar-rm commands.
    env.Command(unpack_files, archive, [
        "rm -rf %s" % os.path.join(unpack_dir, pkg_version),
        "zcat $SOURCES > .temp",
        "tar xf .temp -C %s" % unpack_dir,
        "rm -f .temp",
    ])

    #
    # Run setup.py in the unpacked subdirectory to "install" everything
    # into our build/test subdirectory.  The runtest.py script will set
    # PYTHONPATH so that the tests only look under build/test-{package},
    # and under etc (for the testing modules TestCmd.py, TestSCons.py,
    # and unittest.py).  This makes sure that our tests pass with what
    # we really packaged, not because of something hanging around in
    # the development directory.
    #
    # We can get away with calling setup.py using a directory path
    # like this because we put a preamble in it that will chdir()
    # to the directory in which setup.py exists.
    dfiles = map(lambda x, d=test_arch_dir: os.path.join(d, x), dst_files)
    env.Command(dfiles, unpack_files, [
        "rm -rf %s" % os.path.join(unpack_dir, pkg_version, 'build'),
        "rm -rf %s" % test_arch_dir,
        "python %s install --prefix=%s" % (os.path.join(unpack_dir,
                                                        pkg_version,
                                                        'setup.py'),
                                           test_arch_dir
                                          ),
    ])

#
#
#
Export('env')

SConscript('etc/SConscript')

#
# Documentation.
#
BuildDir('build/doc', 'doc')

Export('env', 'whereis')

SConscript('build/doc/SConscript')

#
# If we're running in the actual Aegis project, pack up a complete
# source archive from the project files and files in the change,
# so we can share it with helpful developers who don't use Aegis.
#

if change:
    df = []
    cmd = "aegis -list -unf -c %s cf 2>/dev/null" % change
    for line in map(lambda x: x[:-1], os.popen(cmd, "r").readlines()):
        a = string.split(line)
        if a[1] == "remove":
            if a[3][0] == '(':
                df.append(a[4])
            else:
                df.append(a[3])

    cmd = "aegis -list -terse pf 2>/dev/null"
    pf = map(lambda x: x[:-1], os.popen(cmd, "r").readlines())
    cmd = "aegis -list -terse cf 2>/dev/null"
    cf = map(lambda x: x[:-1], os.popen(cmd, "r").readlines())
    u = {}
    for f in pf + cf:
        u[f] = 1
    for f in df:
        del u[f]
    sfiles = filter(lambda x: x[-9:] != '.aeignore' 
                              and x[-8:] != '.consign'
                              and x[-9:] != '.sconsign',
                    u.keys())

    if sfiles:
        ps = "%s-src" % project
        psv = "%s-%s" % (ps, version)
        b_ps = os.path.join('build', ps)
        b_psv = os.path.join('build', psv)

        src_archive = os.path.join('build', 'dist', '%s.tar.gz' % psv)

        for file in sfiles:
            env.SCons_revision(os.path.join(b_ps, file), file)

        b_ps_files = map(lambda x, d=b_ps: os.path.join(d, x), sfiles)
        cmds = [
            "rm -rf %s" % b_psv,
            "cp -rp %s %s" % (b_ps, b_psv),
            "find %s -name .consign -exec rm {} \\;" % b_psv,
            "find %s -name .sconsign -exec rm {} \\;" % b_psv,
            "tar czh -f $TARGET -C build %s" % psv,
        ]

        env.Command(src_archive, src_deps + b_ps_files, cmds)

        #
        # Unpack the archive created by the distutils into
        # build/unpack/scons-{version}.
        #
        unpack_files = map(lambda x, u=unpack_dir, psv=psv:
                                  os.path.join(u, psv, x),
                           sfiles)

        #
        # We'd like to replace the last three lines with the following:
        #
        #	tar zxf %< -C $unpack_dir
        #
        # but that gives heartburn to Cygwin's tar, so work around it
        # with separate zcat-tar-rm commands.
        env.Command(unpack_files, src_archive, [
            "rm -rf %s" % os.path.join(unpack_dir, psv),
            "zcat $SOURCES > .temp",
            "tar xf .temp -C %s" % unpack_dir,
            "rm -f .temp",
        ])

        #
        # Run setup.py in the unpacked subdirectory to "install" everything
        # into our build/test subdirectory.  The runtest.py script will set
        # PYTHONPATH so that the tests only look under build/test-{package},
        # and under etc (for the testing modules TestCmd.py, TestSCons.py,
        # and unittest.py).  This makes sure that our tests pass with what
        # we really packaged, not because of something hanging around in
        # the development directory.
        #
        # We can get away with calling setup.py using a directory path
        # like this because we put a preamble in it that will chdir()
        # to the directory in which setup.py exists.
        dfiles = map(lambda x, d=test_src_arch_dir: os.path.join(d, x),
                        dst_files)
        ENV = env.Dictionary('ENV')
        ENV['SCONS_LIB_DIR'] = os.path.join(unpack_dir, psv, 'src', 'engine')
        ENV['USERNAME'] = developer
        env.Copy(ENV = ENV).Command(dfiles, unpack_files, [
            "rm -rf %s" % os.path.join(unpack_dir,
                                       psv,
                                       'build',
                                       'scons',
                                       'build'),
            "rm -rf %s" % test_src_arch_dir,
            "cd %s && python %s %s" % \
                (os.path.join(unpack_dir, psv),
                 os.path.join('src', 'script', 'scons.py'),
                 os.path.join('build', 'scons')),
            "python %s install --prefix=%s" % (os.path.join(unpack_dir,
                                                            psv,
                                                            'build',
                                                            'scons',
                                                            'setup.py'),
                                               test_src_arch_dir
                                              ),
        ])
