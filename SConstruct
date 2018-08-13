#
# SConstruct file to build scons packages during development.
#
# See the README.rst file for an overview of how SCons is built and tested.

from __future__ import print_function

copyright_years = '2001 - 2017'

# This gets inserted into the man pages to reflect the month of release.
month_year = 'MONTH YEAR'

#
# __COPYRIGHT__
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
import distutils.command
import fnmatch
import os
import os.path
import re
import stat
import sys
import tempfile
import time
import socket
import textwrap



import bootstrap

project = 'scons'
default_version = '3.1.0.alpha.yyyymmdd'
copyright = "Copyright (c) %s The SCons Foundation" % copyright_years

SConsignFile()


#
# We let the presence or absence of various utilities determine whether
# or not we bother to build certain pieces of things.  This should allow
# people to still do SCons packaging work even if they don't have all
# of the utilities installed
#
gzip = whereis('gzip')
git = os.path.exists('.git') and whereis('git')
unzip = whereis('unzip')
zip = whereis('zip')

#
# Now grab the information that we "build" into the files.
#
date = ARGUMENTS.get('DATE')
if not date:
    date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))

developer = ARGUMENTS.get('DEVELOPER')
if not developer:
    for variable in ['USERNAME', 'LOGNAME', 'USER']:
        developer = os.environ.get(variable)
        if developer:
            break

build_system = ARGUMENTS.get('BUILD_SYSTEM')
if not build_system:
    build_system = socket.gethostname().split('.')[0]

version = ARGUMENTS.get('VERSION', '')
if not version:
    version = default_version

git_status_lines = []

if git:
    cmd = "%s ls-files 2> /dev/null" % git
    git_status_lines = os.popen(cmd, "r").readlines()

revision = ARGUMENTS.get('REVISION', '')
def generate_build_id(revision):
    return revision

if not revision and git:
    git_hash = os.popen("%s rev-parse HEAD 2> /dev/null" % git, "r").read().strip()
    def generate_build_id(revision):
        result = git_hash
        if [l for l in git_status_lines if 'modified' in l]:
            result = result + '[MODIFIED]'
        return result
    revision = git_hash

checkpoint = ARGUMENTS.get('CHECKPOINT', '')
if checkpoint:
    if checkpoint == 'd':
        checkpoint = time.strftime('%Y%m%d', time.localtime(time.time()))
    elif checkpoint == 'r':
        checkpoint = 'r' + revision
    version = version + '.beta.' + checkpoint

build_id = ARGUMENTS.get('BUILD_ID')
if build_id is None:
    if revision:
        build_id = generate_build_id(revision)
    else:
        build_id = ''


python_ver = sys.version[0:3]

#
# Adding some paths to sys.path, this is mainly needed
# for the doc toolchain.
#
addpaths = [os.path.abspath(os.path.join(os.getcwd(), 'bin')),
            os.path.abspath(os.path.join(os.getcwd(), 'testing/framework'))]
for a in addpaths:
    if a not in sys.path:
        sys.path.append(a)


# Re-exporting LD_LIBRARY_PATH is necessary if the Python version was
# built with the --enable-shared option.

ENV = { 'PATH' : os.environ['PATH'] }
for key in ['LOGNAME', 'PYTHONPATH', 'LD_LIBRARY_PATH']:
    if key in os.environ:
        ENV[key] = os.environ[key]

build_dir = ARGUMENTS.get('BUILDDIR', 'build')
if not os.path.isabs(build_dir):
    build_dir = os.path.normpath(os.path.join(os.getcwd(), build_dir))

command_line_variables = [
    ("BUILDDIR=",       "The directory in which to build the packages.  " +
                        "The default is the './build' subdirectory."),

    ("BUILD_ID=",       "An identifier for the specific build." +
                        "The default is the Subversion revision number."),

    ("BUILD_SYSTEM=",   "The system on which the packages were built.  " +
                        "The default is whatever hostname is returned " +
                        "by socket.gethostname()."),

    ("CHECKPOINT=",     "The specific checkpoint release being packaged, " +
                        "which will be appended to the VERSION string.  " +
                        "A value of CHECKPOINT=d will generate a string " +
                        "of 'd' plus today's date in the format YYYMMDD.  " +
                        "A value of CHECKPOINT=r will generate a " +
                        "string of 'r' plus the Subversion revision " +
                        "number.  Any other CHECKPOINT= string will be " +
                        "used as is.  There is no default value."),

    ("DATE=",           "The date string representing when the packaging " +
                        "build occurred.  The default is the day and time " +
                        "the SConstruct file was invoked, in the format " +
                        "YYYY/MM/DD HH:MM:SS."),

    ("DEVELOPER=",      "The developer who created the packages.  " +
                        "The default is the first set environment " +
                        "variable from the list $USERNAME, $LOGNAME, $USER."),

    ("REVISION=",       "The revision number of the source being built.  " +
                        "The default is the git hash returned " +
                        "'git rev-parse HEAD', with an appended string of " +
                        "'[MODIFIED]' if there are any changes in the " +
                        "working copy."),

    ("VERSION=",        "The SCons version being packaged.  The default " +
                        "is the hard-coded value '%s' " % default_version +
                        "from this SConstruct file."),

]

Default('.', build_dir)

packaging_flavors = [
    ('tar-gz',          "The normal .tar.gz file for end-user installation."),
    ('local-tar-gz',    "A .tar.gz file for dropping into other software " +
                        "for local use."),
    ('zip',             "The normal .zip file for end-user installation."),
    ('local-zip',       "A .zip file for dropping into other software " +
                        "for local use."),
]

test_tar_gz_dir       = os.path.join(build_dir, "test-tar-gz")
test_src_tar_gz_dir   = os.path.join(build_dir, "test-src-tar-gz")
test_local_tar_gz_dir = os.path.join(build_dir, "test-local-tar-gz")
test_zip_dir          = os.path.join(build_dir, "test-zip")
test_src_zip_dir      = os.path.join(build_dir, "test-src-zip")
test_local_zip_dir    = os.path.join(build_dir, "test-local-zip")

unpack_tar_gz_dir     = os.path.join(build_dir, "unpack-tar-gz")
unpack_zip_dir        = os.path.join(build_dir, "unpack-zip")

if is_windows():
    tar_hflag = ''
    python_project_subinst_dir = os.path.join("Lib", "site-packages", project)
    project_script_subinst_dir = 'Scripts'
else:
    tar_hflag = 'h'
    python_project_subinst_dir = os.path.join("lib", project)
    project_script_subinst_dir = 'bin'




indent_fmt = '  %-26s  '

Help("""\
The following aliases build packages of various types, and unpack the
contents into build/test-$PACKAGE subdirectories, which can be used by the
runtest.py -p option to run tests against what's been actually packaged:

""")

aliases = sorted(packaging_flavors + [('doc', 'The SCons documentation.')])

for alias, help_text in aliases:
    tw = textwrap.TextWrapper(
        width = 78,
        initial_indent = indent_fmt % alias,
        subsequent_indent = indent_fmt % '' + '  ',
    )
    Help(tw.fill(help_text) + '\n')

Help("""
The following command-line variables can be set:

""")

for variable, help_text in command_line_variables:
    tw = textwrap.TextWrapper(
        width = 78,
        initial_indent = indent_fmt % variable,
        subsequent_indent = indent_fmt % '' + '  ',
    )
    Help(tw.fill(help_text) + '\n')




revaction = SCons_revision
revbuilder = Builder(action = Action(SCons_revision,
                                     varlist=['COPYRIGHT', 'VERSION']))


# Just make copies, don't symlink them.
SetOption('duplicate', 'copy')

env = Environment(
                   ENV                 = ENV,

                   BUILD               = build_id,
                   BUILDDIR            = build_dir,
                   BUILDSYS            = build_system,
                   COPYRIGHT           = copyright,
                   DATE                = date,
                   DEB_DATE            = deb_date,
                   DEVELOPER           = developer,
                   DISTDIR             = os.path.join(build_dir, 'dist'),
                   MONTH_YEAR          = month_year,
                   REVISION            = revision,
                   VERSION             = version,

                   TAR_HFLAG           = tar_hflag,

                   ZIP                 = zip,
                   ZIPFLAGS            = '-r',
                   UNZIP               = unzip,
                   UNZIPFLAGS          = '-o -d $UNPACK_ZIP_DIR',

                   ZCAT                = zcat,

                   TEST_SRC_TAR_GZ_DIR = test_src_tar_gz_dir,
                   TEST_SRC_ZIP_DIR    = test_src_zip_dir,
                   TEST_TAR_GZ_DIR     = test_tar_gz_dir,
                   TEST_ZIP_DIR        = test_zip_dir,

                   UNPACK_TAR_GZ_DIR   = unpack_tar_gz_dir,
                   UNPACK_ZIP_DIR      = unpack_zip_dir,

                   BUILDERS            = { 'SCons_revision' : revbuilder,
                                           'SOElim' : soelimbuilder },

                   PYTHON              = '"%s"' % sys.executable,
                   PYTHONFLAGS         = '-tt',
                 )

Version_values = [Value(version), Value(build_id)]

#
# Define SCons packages.
#
# In the original, more complicated packaging scheme, we were going
# to have separate packages for:
#
#       python-scons    only the build engine
#       scons-script    only the script
#       scons           the script plus the build engine
#
# We're now only delivering a single "scons" package, but this is still
# "built" as two sub-packages (the build engine and the script), so
# the definitions remain here, even though we're not using them for
# separate packages.
#

from distutils.sysconfig import get_python_lib


python_scons = {
        'pkg'           : 'python-' + project,
        'src_subdir'    : 'engine',
        'inst_subdir'   : get_python_lib(),

        'debian_deps'   : [
                            'debian/changelog',
                            'debian/compat',
                            'debian/control',	    
                            'debian/copyright',
                            'debian/dirs',
                            'debian/docs',
                            'debian/postinst',
                            'debian/prerm',
                            'debian/rules',
                          ],

        'files'         : [ 'LICENSE.txt',
                            'README.txt',
                            'setup.cfg',
                            'setup.py',
                          ],

        'filemap'       : {
                            'LICENSE.txt' : '../LICENSE.txt'
                          },

        'buildermap'    : {},

        'explicit_deps' : {
                            'SCons/__init__.py' : Version_values,
                          },
}


scons_script = {
        'pkg'           : project + '-script',
        'src_subdir'    : 'script',
        'inst_subdir'   : 'bin',

        'debian_deps'   : [
                            'debian/changelog',
                            'debian/compat',
                            'debian/control',
                            'debian/copyright',
                            'debian/dirs',
                            'debian/docs',
                            'debian/postinst',
                            'debian/prerm',
                            'debian/rules',
                          ],

        'files'         : [
                            'LICENSE.txt',
                            'README.txt',
                            'setup.cfg',
                            'setup.py',
                          ],

        'filemap'       : {
                            'LICENSE.txt'       : '../LICENSE.txt',
                            'scons'             : 'scons.py',
                            'sconsign'          : 'sconsign.py',
                            'scons-time'        : 'scons-time.py',
                            'scons-configure-cache'        : 'scons-configure-cache.py',
                           },

        'buildermap'    : {},

        'explicit_deps' : {
                            'scons'       : Version_values,
                            'sconsign'    : Version_values,
                          },
}

scons = {
        'pkg'           : project,

        'debian_deps'   : [
                            'debian/changelog',
                            'debian/compat',
                            'debian/control',
                            'debian/copyright',
                            'debian/dirs',
                            'debian/docs',
                            'debian/postinst',
                            'debian/prerm',
                            'debian/rules',
                          ],

        'files'         : [
                            'CHANGES.txt',
                            'LICENSE.txt',
                            'README.txt',
                            'RELEASE.txt',
                            'scons.1',
                            'sconsign.1',
                            'scons-time.1',
                            'script/scons.bat',
                            'setup.cfg',
                            'setup.py',
                          ],

        'filemap'       : {
                            'scons.1' : '$BUILDDIR/doc/man/scons.1',
                            'sconsign.1' : '$BUILDDIR/doc/man/sconsign.1',
                            'scons-time.1' : '$BUILDDIR/doc/man/scons-time.1',
                          },

        'buildermap'    : {
                            'scons.1' : env.SOElim,
                            'sconsign.1' : env.SOElim,
                            'scons-time.1' : env.SOElim,
                          },

        'subpkgs'       : [ python_scons, scons_script ],

        'subinst_dirs'  : {
                             'python-' + project : python_project_subinst_dir,
                             project + '-script' : project_script_subinst_dir,
                           },
}

scripts = ['scons', 'sconsign', 'scons-time', 'scons-configure-cache']

src_deps = []
src_files = []

for p in [ scons ]:
    #
    # Initialize variables with the right directories for this package.
    #
    pkg = p['pkg']
    pkg_version = "%s-%s" % (pkg, version)

    src = 'src'
    if 'src_subdir' in p:
        src = os.path.join(src, p['src_subdir'])

    build = os.path.join(build_dir, pkg)

    tar_gz = os.path.join(build, 'dist', "%s.tar.gz" % pkg_version)
    platform_tar_gz = os.path.join(build,
                                   'dist',
                                   "%s.%s.tar.gz" % (pkg_version, platform))
    zip = os.path.join(build, 'dist', "%s.zip" % pkg_version)
    platform_zip = os.path.join(build,
                                'dist',
                                "%s.%s.zip" % (pkg_version, platform))


    #
    # Update the environment with the relevant information
    # for this package.
    #
    # We can get away with calling setup.py using a directory path
    # like this because we put a preamble in it that will chdir()
    # to the directory in which setup.py exists.
    #
    setup_py = os.path.join(build, 'setup.py')
    env.Replace(PKG = pkg,
                PKG_VERSION = pkg_version,
                SETUP_PY = '"%s"' % setup_py)
    Local(setup_py)

    #
    # Read up the list of source files from our MANIFEST.in.
    # This list should *not* include LICENSE.txt, MANIFEST,
    # README.txt, or setup.py.  Make a copy of the list for the
    # destination files.
    #
    manifest_in = File(os.path.join(src, 'MANIFEST.in')).rstr()
    manifest_in_lines = open(manifest_in).readlines()
    src_files = bootstrap.parseManifestLines(src, manifest_in_lines)
    raw_files = src_files[:]
    dst_files = src_files[:]

    MANIFEST_in_list = []


    if 'subpkgs' in p:
        #
        # This package includes some sub-packages.  Read up their
        # MANIFEST.in files, and add them to our source and destination
        # file lists, modifying them as appropriate to add the
        # specified subdirs.
        #
        for sp in p['subpkgs']:
            ssubdir = sp['src_subdir']
            isubdir = p['subinst_dirs'][sp['pkg']]

            MANIFEST_in = File(os.path.join(src, ssubdir, 'MANIFEST.in')).rstr()
            MANIFEST_in_list.append(MANIFEST_in)
            files = bootstrap.parseManifestLines(os.path.join(src, ssubdir), open(MANIFEST_in).readlines())

            raw_files.extend(files)
            src_files.extend([os.path.join(ssubdir, x) for x in files])

               
            files = [os.path.join(isubdir, x) for x in files]
            dst_files.extend(files)
            for k, f in sp['filemap'].items():
                if f:
                    k = os.path.join(ssubdir, k)
                    p['filemap'][k] = os.path.join(ssubdir, f)
            for f, deps in sp['explicit_deps'].items():
                f = os.path.join(build, ssubdir, f)
                env.Depends(f, deps)

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
        if not s[0] == '$' and not os.path.isabs(s):
            s = os.path.join(src, s)

        builder = p['buildermap'].get(b, env.SCons_revision)
        x = builder(os.path.join(build, b), s)

        Local(x)

    #
    # NOW, finally, we can create the MANIFEST, which we do
    # by having Python spit out the contents of the src_files
    # array we've carefully created.  After we've added
    # MANIFEST itself to the array, of course.
    #
    src_files.append("MANIFEST")
    MANIFEST_in_list.append(os.path.join(src, 'MANIFEST.in'))

    def write_src_files(target, source, **kw):
        global src_files
        src_files.sort()
        f = open(str(target[0]), 'w')
        for file in src_files:
            f.write(file + "\n")
        f.close()
        return 0
    env.Command(os.path.join(build, 'MANIFEST'),
                MANIFEST_in_list,
                write_src_files)

    #
    # Now go through and arrange to create whatever packages we can.
    #
    build_src_files = [os.path.join(build, x) for x in src_files]
    Local(*build_src_files)

    distutils_formats = []
    distutils_targets = []
    dist_distutils_targets = []

    for target in distutils_targets:
        dist_target = env.Install('$DISTDIR', target)
        AddPostAction(dist_target, Chmod(dist_target, 0o644))
        dist_distutils_targets += dist_target

    if not gzip:
        print("gzip not found in %s; skipping .tar.gz package for %s." % (os.environ['PATH'], pkg))
    else:

        distutils_formats.append('gztar')

        src_deps.append(tar_gz)

        distutils_targets.extend([ tar_gz, platform_tar_gz ])

        dist_tar_gz             = env.Install('$DISTDIR', tar_gz)
        dist_platform_tar_gz    = env.Install('$DISTDIR', platform_tar_gz)
        Local(dist_tar_gz, dist_platform_tar_gz)
        AddPostAction(dist_tar_gz, Chmod(dist_tar_gz, 0o644))
        AddPostAction(dist_platform_tar_gz, Chmod(dist_platform_tar_gz, 0o644))

        #
        # Unpack the tar.gz archive created by the distutils into
        # build/unpack-tar-gz/scons-{version}.
        #
        # We'd like to replace the last three lines with the following:
        #
        #       tar zxf $SOURCES -C $UNPACK_TAR_GZ_DIR
        #
        # but that gives heartburn to Cygwin's tar, so work around it
        # with separate zcat-tar-rm commands.
        #
        unpack_tar_gz_files = [os.path.join(unpack_tar_gz_dir, pkg_version, x)
                               for x in src_files]
        env.Command(unpack_tar_gz_files, dist_tar_gz, [
                    Delete(os.path.join(unpack_tar_gz_dir, pkg_version)),
                    "$ZCAT $SOURCES > .temp",
                    "tar xf .temp -C $UNPACK_TAR_GZ_DIR",
                    Delete(".temp"),
        ])

        #
        # Run setup.py in the unpacked subdirectory to "install" everything
        # into our build/test subdirectory.  The runtest.py script will set
        # PYTHONPATH so that the tests only look under build/test-{package},
        # and under testing/framework (for the testing modules TestCmd.py, TestSCons.py,
        # etc.).  This makes sure that our tests pass with what
        # we really packaged, not because of something hanging around in
        # the development directory.
        #
        # We can get away with calling setup.py using a directory path
        # like this because we put a preamble in it that will chdir()
        # to the directory in which setup.py exists.
        #
        dfiles = [os.path.join(test_tar_gz_dir, x) for x in dst_files]
        env.Command(dfiles, unpack_tar_gz_files, [
            Delete(os.path.join(unpack_tar_gz_dir, pkg_version, 'build')),
            Delete("$TEST_TAR_GZ_DIR"),
            '$PYTHON $PYTHONFLAGS "%s" install "--prefix=$TEST_TAR_GZ_DIR" --standalone-lib' % \
                os.path.join(unpack_tar_gz_dir, pkg_version, 'setup.py'),
        ])

        #
        # Generate portage files for submission to Gentoo Linux.
        #
        gentoo = os.path.join(build, 'gentoo')
        ebuild = os.path.join(gentoo, 'scons-%s.ebuild' % version)
        digest = os.path.join(gentoo, 'files', 'digest-scons-%s' % version)
        env.Command(ebuild, os.path.join('gentoo', 'scons.ebuild.in'), SCons_revision)

        def Digestify(target, source, env):
            import hashlib
            src = source[0].rfile()
            contents = open(str(src),'rb').read()
            m = hashlib.md5()
            m.update(contents)
            sig = m.hexdigest()
            bytes = os.stat(str(src))[6]
            open(str(target[0]), 'w').write("MD5 %s %s %d\n" % (sig,
                                                                src.name,
                                                                bytes))
        env.Command(digest, tar_gz, Digestify)

    if not zipit:
        print("zip not found; skipping .zip package for %s." % pkg)
    else:

        distutils_formats.append('zip')

        src_deps.append(zip)

        distutils_targets.extend([ zip, platform_zip ])

        dist_zip            = env.Install('$DISTDIR', zip)
        dist_platform_zip   = env.Install('$DISTDIR', platform_zip)
        Local(dist_zip, dist_platform_zip)
        AddPostAction(dist_zip, Chmod(dist_zip, 0o644))
        AddPostAction(dist_platform_zip, Chmod(dist_platform_zip, 0o644))

        #
        # Unpack the zip archive created by the distutils into
        # build/unpack-zip/scons-{version}.
        #
        unpack_zip_files = [os.path.join(unpack_zip_dir, pkg_version, x)
                                         for x in src_files]

        env.Command(unpack_zip_files, dist_zip, [
            Delete(os.path.join(unpack_zip_dir, pkg_version)),
            unzipit,
        ])

        #
        # Run setup.py in the unpacked subdirectory to "install" everything
        # into our build/test subdirectory.  The runtest.py script will set
        # PYTHONPATH so that the tests only look under build/test-{package},
        # and under testing/framework (for the testing modules TestCmd.py, TestSCons.py,
        # etc.).  This makes sure that our tests pass with what
        # we really packaged, not because of something hanging around in
        # the development directory.
        #
        # We can get away with calling setup.py using a directory path
        # like this because we put a preamble in it that will chdir()
        # to the directory in which setup.py exists.
        #
        dfiles = [os.path.join(test_zip_dir, x) for x in dst_files]
        env.Command(dfiles, unpack_zip_files, [
            Delete(os.path.join(unpack_zip_dir, pkg_version, 'build')),
            Delete("$TEST_ZIP_DIR"),
            '$PYTHON $PYTHONFLAGS "%s" install "--prefix=$TEST_ZIP_DIR" --standalone-lib' % \
                os.path.join(unpack_zip_dir, pkg_version, 'setup.py'),
        ])



    #
    # Use the Python distutils to generate the appropriate packages.
    #
    commands = [
        Delete(os.path.join(build, 'build', 'lib')),
        Delete(os.path.join(build, 'build', 'scripts')),
    ]

    if distutils_formats:
        commands.append(Delete(os.path.join(build,
                                            'build',
                                            'bdist.' + platform,
                                            'dumb')))
        for format in distutils_formats:
            commands.append("$PYTHON $PYTHONFLAGS $SETUP_PY bdist_dumb -f %s" % format)

        commands.append("$PYTHON $PYTHONFLAGS $SETUP_PY sdist --formats=%s" %  \
                            ','.join(distutils_formats))

    env.Command(distutils_targets, build_src_files, commands)

    #
    # Now create local packages for people who want to let people
    # build their SCons-buildable packages without having to
    # install SCons.
    #
    s_l_v = '%s-local-%s' % (pkg, version)

    local = pkg + '-local'
    build_dir_local = os.path.join(build_dir, local)
    build_dir_local_slv = os.path.join(build_dir, local, s_l_v)

    dist_local_tar_gz = os.path.join("$DISTDIR/%s.tar.gz" % s_l_v)
    dist_local_zip = os.path.join("$DISTDIR/%s.zip" % s_l_v)
    AddPostAction(dist_local_tar_gz, Chmod(dist_local_tar_gz, 0o644))
    AddPostAction(dist_local_zip, Chmod(dist_local_zip, 0o644))

    commands = [
        Delete(build_dir_local),
        '$PYTHON $PYTHONFLAGS $SETUP_PY install "--install-script=%s" "--install-lib=%s" --no-install-man --no-compile --standalone-lib --no-version-script' % \
                                                (build_dir_local, build_dir_local_slv),
    ]

    for script in scripts:
        # add .py extension for scons-local scripts on non-windows platforms
        if is_windows():
            break
        local_script = os.path.join(build_dir_local, script)
        commands.append(Move(local_script + '.py', local_script))

    rf = [x for x in raw_files if not x in scripts]
    rf = [os.path.join(s_l_v, x) for x in rf]
    for script in scripts:
        rf.append("%s.py" % script)
    local_targets = [os.path.join(build_dir_local, x) for x in rf]

    env.Command(local_targets, build_src_files, commands)

    scons_LICENSE = os.path.join(build_dir_local, 'scons-LICENSE')
    l = env.SCons_revision(scons_LICENSE, 'LICENSE-local')
    local_targets.append(l)
    Local(l)

    scons_README = os.path.join(build_dir_local, 'scons-README')
    l = env.SCons_revision(scons_README, 'README-local')
    local_targets.append(l)
    Local(l)

    if gzip:
        if is_windows():
            # avoid problem with tar interpreting c:/ as a remote machine
            tar_cargs = '-cz --force-local -f'
        else:
            tar_cargs = '-czf'
        env.Command(dist_local_tar_gz,
                    local_targets,
                    "cd %s && tar %s $( ${TARGET.abspath} $) *" % (build_dir_local, tar_cargs))

        unpack_targets = [os.path.join(test_local_tar_gz_dir, x) for x in rf]
        commands = [Delete(test_local_tar_gz_dir),
                    Mkdir(test_local_tar_gz_dir),
                    "cd %s && tar xzf $( ${SOURCE.abspath} $)" % test_local_tar_gz_dir]

        env.Command(unpack_targets, dist_local_tar_gz, commands)

    if zipit:
        env.Command(dist_local_zip, local_targets, zipit,
                    CD = build_dir_local, PSV = '.')

        unpack_targets = [os.path.join(test_local_zip_dir, x) for x in rf]
        commands = [Delete(test_local_zip_dir),
                    Mkdir(test_local_zip_dir),
                    unzipit]

        env.Command(unpack_targets, dist_local_zip, unzipit,
                    UNPACK_ZIP_DIR = test_local_zip_dir)

#
#
#
Export('build_dir', 'env')

SConscript('testing/framework/SConscript')

#
#
#
sp = env.Install(build_dir, 'runtest.py')
Local(sp)
files = [
    'runtest.py',
]


#
# Documentation.
#
Export('build_dir', 'env', 'whereis', 'revaction')

SConscript('doc/SConscript')

#
# If we're running in a Git working directory, pack up a complete
# source archive from the project files and files in the change.
#


sfiles = None
if git_status_lines:
    slines = [l for l in git_status_lines if 'modified:' in l]
    sfiles = [l.split()[-1] for l in slines]
else:
   print("Not building in a Git tree; skipping building src package.")

if sfiles:
    remove_patterns = [
        '*.gitignore',
        '*.hgignore',
        'www/*',
    ]

    for p in remove_patterns:
        sfiles = [s for s in sfiles if not fnmatch.fnmatch(s, p)]

    if sfiles:
        ps = "%s-src" % project
        psv = "%s-%s" % (ps, version)
        b_ps = os.path.join(build_dir, ps)
        b_psv = os.path.join(build_dir, psv)
        b_psv_stamp = b_psv + '-stamp'

        src_tar_gz = os.path.join(build_dir, 'dist', '%s.tar.gz' % psv)
        src_zip = os.path.join(build_dir, 'dist', '%s.zip' % psv)

        Local(src_tar_gz, src_zip)

        for file in sfiles:
            if file.endswith('jpg') or file.endswith('png'):
                # don't revision binary files.
                env.Install(os.path.dirname(os.path.join(b_ps,file)), file)
            else:
                env.SCons_revision(os.path.join(b_ps, file), file)

        b_ps_files = [os.path.join(b_ps, x) for x in sfiles]
        cmds = [
            Delete(b_psv),
            Copy(b_psv, b_ps),
            Touch("$TARGET"),
        ]

        env.Command(b_psv_stamp, src_deps + b_ps_files, cmds)

        Local(*b_ps_files)

        if gzip:

            env.Command(src_tar_gz, b_psv_stamp,
                        "tar cz${TAR_HFLAG} -f $TARGET -C build %s" % psv)

            #
            # Unpack the archive into build/unpack/scons-{version}.
            #
            unpack_tar_gz_files = [os.path.join(unpack_tar_gz_dir, psv, x)
                                   for x in sfiles]

            #
            # We'd like to replace the last three lines with the following:
            #
            #   tar zxf $SOURCES -C $UNPACK_TAR_GZ_DIR
            #
            # but that gives heartburn to Cygwin's tar, so work around it
            # with separate zcat-tar-rm commands.
            env.Command(unpack_tar_gz_files, src_tar_gz, [
                Delete(os.path.join(unpack_tar_gz_dir, psv)),
                "$ZCAT $SOURCES > .temp",
                "tar xf .temp -C $UNPACK_TAR_GZ_DIR",
                Delete(".temp"),
            ])

            #
            # Run setup.py in the unpacked subdirectory to "install" everything
            # into our build/test subdirectory.  The runtest.py script will set
            # PYTHONPATH so that the tests only look under build/test-{package},
            # and under testing/framework (for the testing modules TestCmd.py,
            # TestSCons.py, etc.).  This makes sure that our tests pass with
            # what we really packaged, not because of something hanging around
            # in the development directory.
            #
            # We can get away with calling setup.py using a directory path
            # like this because we put a preamble in it that will chdir()
            # to the directory in which setup.py exists.
            #
            dfiles = [os.path.join(test_src_tar_gz_dir, x) for x in dst_files]
            scons_lib_dir = os.path.join(unpack_tar_gz_dir, psv, 'src', 'engine')
            ENV = env.Dictionary('ENV').copy()
            ENV['SCONS_LIB_DIR'] = scons_lib_dir
            ENV['USERNAME'] = developer
            env.Command(dfiles, unpack_tar_gz_files,
                [
                Delete(os.path.join(unpack_tar_gz_dir,
                                    psv,
                                    'build',
                                    'scons',
                                    'build')),
                Delete("$TEST_SRC_TAR_GZ_DIR"),
                'cd "%s" && $PYTHON $PYTHONFLAGS "%s" "%s" VERSION="$VERSION"' % \
                    (os.path.join(unpack_tar_gz_dir, psv),
                     os.path.join('src', 'script', 'scons.py'),
                     os.path.join('build', 'scons')),
                '$PYTHON $PYTHONFLAGS "%s" install "--prefix=$TEST_SRC_TAR_GZ_DIR" --standalone-lib' % \
                    os.path.join(unpack_tar_gz_dir,
                                 psv,
                                 'build',
                                 'scons',
                                 'setup.py'),
                ],
                ENV = ENV)

        if zipit:

            env.Command(src_zip, b_psv_stamp, zipit, CD = 'build', PSV = psv)

            #
            # Unpack the archive into build/unpack/scons-{version}.
            #
            unpack_zip_files = [os.path.join(unpack_zip_dir, psv, x)
                                for x in sfiles]

            env.Command(unpack_zip_files, src_zip, [
                Delete(os.path.join(unpack_zip_dir, psv)),
                unzipit
            ])

            #
            # Run setup.py in the unpacked subdirectory to "install" everything
            # into our build/test subdirectory.  The runtest.py script will set
            # PYTHONPATH so that the tests only look under build/test-{package},
            # and under testing/framework (for the testing modules TestCmd.py,
            # TestSCons.py, etc.).  This makes sure that our tests pass with
            # what we really packaged, not because of something hanging
            # around in the development directory.
            #
            # We can get away with calling setup.py using a directory path
            # like this because we put a preamble in it that will chdir()
            # to the directory in which setup.py exists.
            #
            dfiles = [os.path.join(test_src_zip_dir, x) for x in dst_files]
            scons_lib_dir = os.path.join(unpack_zip_dir, psv, 'src', 'engine')
            ENV = env.Dictionary('ENV').copy()
            ENV['SCONS_LIB_DIR'] = scons_lib_dir
            ENV['USERNAME'] = developer
            env.Command(dfiles, unpack_zip_files,
                [
                Delete(os.path.join(unpack_zip_dir,
                                    psv,
                                    'build',
                                    'scons',
                                    'build')),
                Delete("$TEST_SRC_ZIP_DIR"),
                'cd "%s" && $PYTHON $PYTHONFLAGS "%s" "%s" VERSION="$VERSION"' % \
                    (os.path.join(unpack_zip_dir, psv),
                     os.path.join('src', 'script', 'scons.py'),
                     os.path.join('build', 'scons')),
                '$PYTHON $PYTHONFLAGS "%s" install "--prefix=$TEST_SRC_ZIP_DIR" --standalone-lib' % \
                    os.path.join(unpack_zip_dir,
                                 psv,
                                 'build',
                                 'scons',
                                 'setup.py'),
                ],
                ENV = ENV)

for pf, help_text in packaging_flavors:
    Alias(pf, [
        os.path.join(build_dir, 'test-'+pf),
        os.path.join(build_dir, 'testing/framework'),
        os.path.join(build_dir, 'runtest.py'),
    ])


