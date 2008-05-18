#
# SConstruct file to build scons packages during development.
#
# See the README file for an overview of how SCons is built and tested.
#

# When this gets changed, you must also change the copyright_years string
# in QMTest/TestSCons.py so the test scripts look for the right string.
copyright_years = '2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008'

# This gets inserted into the man pages to reflect the month of release.
month_year = 'May 2008'

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
import fnmatch
import os
import os.path
import re
import stat
import string
import sys
import tempfile

project = 'scons'
default_version = '0.98.4'
copyright = "Copyright (c) %s The SCons Foundation" % copyright_years

SConsignFile()

#
# An internal "whereis" routine to figure out if a given program
# is available on this system.
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
# We let the presence or absence of various utilities determine whether
# or not we bother to build certain pieces of things.  This should allow
# people to still do SCons packaging work even if they don't have all
# of the utilities installed (e.g. RPM).
#
dh_builddeb = whereis('dh_builddeb')
fakeroot = whereis('fakeroot')
gzip = whereis('gzip')
rpmbuild = whereis('rpmbuild') or whereis('rpm')
svn = whereis('svn')
unzip = whereis('unzip')
zip = whereis('zip')

#
# Now grab the information that we "build" into the files.
#
date = ARGUMENTS.get('DATE')
if not date:
    import time
    date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))

developer = ARGUMENTS.get('DEVELOPER')
if not developer:
    for variable in ['USERNAME', 'LOGNAME', 'USER']:
        developer = os.environ.get(variable)
        if developer:
            break

build_system = ARGUMENTS.get('BUILD_SYSTEM')
if not build_system:
    import socket
    build_system = string.split(socket.gethostname(), '.')[0]

version = ARGUMENTS.get('VERSION', '')
if not version:
    version = default_version

revision = ARGUMENTS.get('REVISION', '')
if not revision and svn:
    svn_info = os.popen("%s info 2> /dev/null" % svn, "r").read()
    m = re.search('Revision: (\d+)', svn_info)
    if m:
        revision = m.group(1)

checkpoint = ARGUMENTS.get('CHECKPOINT', '')
if checkpoint:
    if checkpoint == 'd':
        import time
        checkpoint = time.strftime('d%Y%m%d', time.localtime(time.time()))
    elif checkpoint == 'r':
        checkpoint = 'r' + revision
    version = version + '.' + checkpoint

svn_status = None
svn_status_lines = []

if svn:
    svn_status = os.popen("%s status --verbose 2> /dev/null" % svn, "r").read()
    svn_status_lines = svn_status[:-1].split('\n')

build_id = ARGUMENTS.get('BUILD_ID')
if build_id is None:
    if revision:
        build_id = 'r' + revision
        if filter(lambda l: l[0] in 'ACDMR', svn_status_lines):
            build_id = build_id + '[MODIFIED]'
    else:
        build_id = ''

python_ver = sys.version[0:3]

platform = distutils.util.get_platform()

# Re-exporting LD_LIBRARY_PATH is necessary if the Python version was
# built with the --enable-shared option.

ENV = { 'PATH' : os.environ['PATH'] }
for key in ['LOGNAME', 'PYTHONPATH', 'LD_LIBRARY_PATH']:
    if os.environ.has_key(key):
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
                        "The default is the Subversion revision returned " +
                        "'svn info', with an appended string of " +
                        "'[MODIFIED]' if there are any changes in the " +
                        "working copy."),

    ("VERSION=",        "The SCons version being packaged.  The default " +
                        "is the hard-coded value '%s' " % default_version +
                        "from this SConstruct file."),
]

Default('.', build_dir)

packaging_flavors = [
    ('deb',             "A .deb package.  (This is currently not supported.)"),

    ('rpm',             "A RedHat Package Manager file."),

    ('tar-gz',          "The normal .tar.gz file for end-user installation."),

    ('src-tar-gz',      "A .tar.gz file containing all the source " +
                        "(including tests and documentation)."),

    ('local-tar-gz',    "A .tar.gz file for dropping into other software " +
                        "for local use."),

    ('zip',             "The normal .zip file for end-user installation."),

    ('src-zip',         "A .zip file containing all the source " +
                        "(including tests and documentation)."),

    ('local-zip',       "A .zip file for dropping into other software " +
                        "for local use."),
]

test_deb_dir          = os.path.join(build_dir, "test-deb")
test_rpm_dir          = os.path.join(build_dir, "test-rpm")
test_tar_gz_dir       = os.path.join(build_dir, "test-tar-gz")
test_src_tar_gz_dir   = os.path.join(build_dir, "test-src-tar-gz")
test_local_tar_gz_dir = os.path.join(build_dir, "test-local-tar-gz")
test_zip_dir          = os.path.join(build_dir, "test-zip")
test_src_zip_dir      = os.path.join(build_dir, "test-src-zip")
test_local_zip_dir    = os.path.join(build_dir, "test-local-zip")

unpack_tar_gz_dir     = os.path.join(build_dir, "unpack-tar-gz")
unpack_zip_dir        = os.path.join(build_dir, "unpack-zip")

if platform == "win32":
    tar_hflag = ''
    python_project_subinst_dir = os.path.join("Lib", "site-packages", project)
    project_script_subinst_dir = 'Scripts'
else:
    tar_hflag = 'h'
    python_project_subinst_dir = os.path.join("lib", project)
    project_script_subinst_dir = 'bin'



import textwrap

indent_fmt = '  %-26s  '

Help("""\
The following aliases build packages of various types, and unpack the
contents into build/test-$PACKAGE subdirectories, which can be used by the
runtest.py -p option to run tests against what's been actually packaged:

""")

aliases = packaging_flavors + [('doc', 'The SCons documentation.')]
aliases.sort()

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



zcat = 'gzip -d -c'

#
# Figure out if we can handle .zip files.
#
zipit = None
unzipit = None
try:
    import zipfile

    def zipit(env, target, source):
        print "Zipping %s:" % str(target[0])
        def visit(arg, dirname, names):
            for name in names:
                path = os.path.join(dirname, name)
                if os.path.isfile(path):
                    arg.write(path)
        zf = zipfile.ZipFile(str(target[0]), 'w')
        olddir = os.getcwd()
        os.chdir(env['CD'])
        try: os.path.walk(env['PSV'], visit, zf)
        finally: os.chdir(olddir)
        zf.close()

    def unzipit(env, target, source):
        print "Unzipping %s:" % str(source[0])
        zf = zipfile.ZipFile(str(source[0]), 'r')
        for name in zf.namelist():
            dest = os.path.join(env['UNPACK_ZIP_DIR'], name)
            dir = os.path.dirname(dest)
            try:
                os.makedirs(dir)
            except:
                pass
            print dest,name
            # if the file exists, then delete it before writing
            # to it so that we don't end up trying to write to a symlink:
            if os.path.isfile(dest) or os.path.islink(dest):
                os.unlink(dest)
            if not os.path.isdir(dest):
                open(dest, 'wb').write(zf.read(name))

except:
    if unzip and zip:
        zipit = "cd $CD && $ZIP $ZIPFLAGS $( ${TARGET.abspath} $) $PSV"
        unzipit = "$UNZIP $UNZIPFLAGS $SOURCES"

def SCons_revision(target, source, env):
    """Interpolate specific values from the environment into a file.

    This is used to copy files into a tree that gets packaged up
    into the source file package.
    """
    t = str(target[0])
    s = source[0].rstr()
    contents = open(s, 'rb').read()
    # Note:  We construct the __*__ substitution strings here
    # so that they don't get replaced when this file gets
    # copied into the tree for packaging.
    contents = string.replace(contents, '__BUILD'     + '__', env['BUILD'])
    contents = string.replace(contents, '__BUILDSYS'  + '__', env['BUILDSYS'])
    contents = string.replace(contents, '__COPYRIGHT' + '__', env['COPYRIGHT'])
    contents = string.replace(contents, '__DATE'      + '__', env['DATE'])
    contents = string.replace(contents, '__DEVELOPER' + '__', env['DEVELOPER'])
    contents = string.replace(contents, '__FILE'      + '__', str(source[0]))
    contents = string.replace(contents, '__MONTH_YEAR'+ '__', env['MONTH_YEAR'])
    contents = string.replace(contents, '__REVISION'  + '__', env['REVISION'])
    contents = string.replace(contents, '__VERSION'   + '__', env['VERSION'])
    contents = string.replace(contents, '__NULL'      + '__', '')
    open(t, 'wb').write(contents)
    os.chmod(t, os.stat(s)[0])

revbuilder = Builder(action = Action(SCons_revision,
                                     varlist=['COPYRIGHT', 'VERSION']))

def soelim(target, source, env):
    """
    Interpolate files included in [gnt]roff source files using the
    .so directive.

    This behaves somewhat like the soelim(1) wrapper around groff, but
    makes us independent of whether the actual underlying implementation
    includes an soelim() command or the corresponding command-line option
    to groff(1).  The key behavioral difference is that this doesn't
    recursively include .so files from the include file.  Not yet, anyway.
    """
    t = str(target[0])
    s = str(source[0])
    dir, f = os.path.split(s)
    tfp = open(t, 'w')
    sfp = open(s, 'r')
    for line in sfp.readlines():
        if line[:4] in ['.so ', "'so "]:
            sofile = os.path.join(dir, line[4:-1])
            tfp.write(open(sofile, 'r').read())
        else:
            tfp.write(line)
    sfp.close()
    tfp.close()

def soscan(node, env, path):
    c = node.get_contents()
    return re.compile(r"^[\.']so\s+(\S+)", re.M).findall(c)

soelimbuilder = Builder(action = Action(soelim),
                        source_scanner = Scanner(soscan))

# When copying local files from a Repository (Aegis),
# just make copies, don't symlink them.
SetOption('duplicate', 'copy')

env = Environment(
                   ENV                 = ENV,

                   BUILD               = build_id,
                   BUILDDIR            = build_dir,
                   BUILDSYS            = build_system,
                   COPYRIGHT           = copyright,
                   DATE                = date,
                   DEVELOPER           = developer,
                   DISTDIR             = os.path.join(build_dir, 'dist'),
                   MONTH_YEAR          = month_year,
                   REVISION            = revision,
                   VERSION             = version,
                   DH_COMPAT           = 2,

                   TAR_HFLAG           = tar_hflag,

                   ZIP                 = zip,
                   ZIPFLAGS            = '-r',
                   UNZIP               = unzip,
                   UNZIPFLAGS          = '-o -d $UNPACK_ZIP_DIR',

                   ZCAT                = zcat,

                   RPMBUILD            = rpmbuild,
                   RPM2CPIO            = 'rpm2cpio',

                   TEST_DEB_DIR        = test_deb_dir,
                   TEST_RPM_DIR        = test_rpm_dir,
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

python_scons = {
        'pkg'           : 'python-' + project,
        'src_subdir'    : 'engine',
        'inst_subdir'   : os.path.join('lib', 'python1.5', 'site-packages'),
        'rpm_dir'       : '/usr/lib/scons',

        'debian_deps'   : [
                            'debian/changelog',
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

        'extra_rpm_files' : [],

        'explicit_deps' : {
                            'SCons/__init__.py' : Version_values,
                          },
}

# Figure out the name of a .egg-info file that might be generated
# as part of the RPM package.  There are two complicating factors.
#
# First, the RPM spec file we generate will just execute "python", not
# necessarily the one in sys.executable.  If *that* version of python has
# a distutils that knows about Python eggs, then setup.py will generate a
# .egg-info file, so we have to execute any distutils logic in a subshell.
#
# Second, we can't just have the subshell check for the existence of the
# distutils.command.install_egg_info module and generate the expected
# file name by hand, the way we used to, because different systems can
# have slightly different .egg-info naming conventions.  (Specifically,
# Ubuntu overrides the default behavior to remove the Python version
# string from the .egg-info file name.)  The right way to do this is to
# actually call into the install_egg_info() class to have it generate
# the expected name for us.
#
# This is all complicated enough that we do it by writing an in-line
# script to a temporary file and then feeding it to a separate invocation
# of "python" to tell us the actual name of the generated .egg-info file.

print_egg_info_name = """
try:
    from distutils.dist import Distribution
    from distutils.command.install_egg_info import install_egg_info
except ImportError:
    pass
else:
    dist = Distribution({'name' : "scons", 'version' : '%s'})
    i = install_egg_info(dist)
    i.finalize_options()
    import os.path
    print os.path.split(i.outputs[0])[1]
""" % version

try:
    fd, tfname = tempfile.mkstemp()
    tfp = os.fdopen(fd, "w")
    tfp.write(print_egg_info_name)
    tfp.close()
    egg_info_file = os.popen("python %s" % tfname).read()[:-1]
    if egg_info_file:
        python_scons['extra_rpm_files'].append(egg_info_file)
finally:
    try:
        os.unlink(tfname)
    except EnvironmentError:
        pass

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
#        'inst_subdir'  : os.path.join('lib', 'python2.2', 'site-packages'),
#
#        'debian_deps'  : [
#                            'debian/changelog',
#                            'debian/control',
#                            'debian/copyright',
#                            'debian/dirs',
#                            'debian/docs',
#                            'debian/postinst',
#                            'debian/prerm',
#                            'debian/rules',
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
#        'buildermap'    : {},
#}
#

scons_script = {
        'pkg'           : project + '-script',
        'src_subdir'    : 'script',
        'inst_subdir'   : 'bin',
        'rpm_dir'       : '/usr/bin',

        'debian_deps'   : [
                            'debian/changelog',
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
                           },

        'buildermap'    : {},

        'extra_rpm_files' : [
                            'scons-' + version,
                            'sconsign-' + version,
                            'scons-time-' + version,
                          ],

        'explicit_deps' : {
                            'scons'       : Version_values,
                            'sconsign'    : Version_values,
                          },
}

scons = {
        'pkg'           : project,

        'debian_deps'   : [
                            'debian/changelog',
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
                            'os_spawnv_fix.diff',
                            'scons.1',
                            'sconsign.1',
                            'scons-time.1',
                            'script/scons.bat',
                            #'script/scons-post-install.py',
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

scripts = ['scons', 'sconsign', 'scons-time']

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

    build = os.path.join(build_dir, pkg)

    tar_gz = os.path.join(build, 'dist', "%s.tar.gz" % pkg_version)
    platform_tar_gz = os.path.join(build,
                                   'dist',
                                   "%s.%s.tar.gz" % (pkg_version, platform))
    zip = os.path.join(build, 'dist', "%s.zip" % pkg_version)
    platform_zip = os.path.join(build,
                                'dist',
                                "%s.%s.zip" % (pkg_version, platform))
    win32_exe = os.path.join(build, 'dist', "%s.win32.exe" % pkg_version)

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
    src_files = map(lambda x: x[:-1],
                    open(manifest_in).readlines())
    raw_files = src_files[:]
    dst_files = src_files[:]
    rpm_files = []

    MANIFEST_in_list = []

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
            MANIFEST_in = File(os.path.join(src, ssubdir, 'MANIFEST.in')).rstr()
            MANIFEST_in_list.append(MANIFEST_in)
            files = map(lambda x: x[:-1], open(MANIFEST_in).readlines())
            raw_files.extend(files)
            src_files.extend(map(lambda x, s=ssubdir: os.path.join(s, x), files))
            for f in files:
                r = os.path.join(sp['rpm_dir'], f)
                rpm_files.append(r)
                if f[-3:] == ".py":
                    rpm_files.append(r + 'c')
            for f in sp.get('extra_rpm_files', []):
                r = os.path.join(sp['rpm_dir'], f)
                rpm_files.append(r)
            files = map(lambda x, i=isubdir: os.path.join(i, x), files)
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
        f = open(str(target[0]), 'wb')
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
    build_src_files = map(lambda x, b=build: os.path.join(b, x), src_files)
    apply(Local, build_src_files, {})

    distutils_formats = []

    distutils_targets = [ win32_exe ]

    dist_distutils_targets = env.Install('$DISTDIR', distutils_targets)
    Local(dist_distutils_targets)
    AddPostAction(dist_distutils_targets, Chmod(dist_distutils_targets, 0644))

    if not gzip:
        print "gzip not found; skipping .tar.gz package for %s." % pkg
    else:

        distutils_formats.append('gztar')

        src_deps.append(tar_gz)

        distutils_targets.extend([ tar_gz, platform_tar_gz ])

        dist_tar_gz             = env.Install('$DISTDIR', tar_gz)
        dist_platform_tar_gz    = env.Install('$DISTDIR', platform_tar_gz)
        Local(dist_tar_gz, dist_platform_tar_gz)
        AddPostAction(dist_tar_gz, Chmod(dist_tar_gz, 0644))
        AddPostAction(dist_platform_tar_gz, Chmod(dist_platform_tar_gz, 0644))

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
        unpack_tar_gz_files = map(lambda x, u=unpack_tar_gz_dir, pv=pkg_version:
                                         os.path.join(u, pv, x),
                                  src_files)
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
        # and under etc (for the testing modules TestCmd.py, TestSCons.py,
        # and unittest.py).  This makes sure that our tests pass with what
        # we really packaged, not because of something hanging around in
        # the development directory.
        #
        # We can get away with calling setup.py using a directory path
        # like this because we put a preamble in it that will chdir()
        # to the directory in which setup.py exists.
        #
        dfiles = map(lambda x, d=test_tar_gz_dir: os.path.join(d, x), dst_files)
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
            import md5
            def hexdigest(s):
                """Return a signature as a string of hex characters.
                """
                # NOTE:  This routine is a method in the Python 2.0 interface
                # of the native md5 module, but we want SCons to operate all
                # the way back to at least Python 1.5.2, which doesn't have it.
                h = string.hexdigits
                r = ''
                for c in s:
                    i = ord(c)
                    r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
                return r
            src = source[0].rfile()
            contents = open(str(src)).read()
            sig = hexdigest(md5.new(contents).digest())
            bytes = os.stat(str(src))[6]
            open(str(target[0]), 'w').write("MD5 %s %s %d\n" % (sig,
                                                                src.name,
                                                                bytes))
        env.Command(digest, tar_gz, Digestify)

    if not zipit:
        print "zip not found; skipping .zip package for %s." % pkg
    else:

        distutils_formats.append('zip')

        src_deps.append(zip)

        distutils_targets.extend([ zip, platform_zip ])

        dist_zip            = env.Install('$DISTDIR', zip)
        dist_platform_zip   = env.Install('$DISTDIR', platform_zip)
        Local(dist_zip, dist_platform_zip)
        AddPostAction(dist_zip, Chmod(dist_zip, 0644))
        AddPostAction(dist_platform_zip, Chmod(dist_platform_zip, 0644))

        #
        # Unpack the zip archive created by the distutils into
        # build/unpack-zip/scons-{version}.
        #
        unpack_zip_files = map(lambda x, u=unpack_zip_dir, pv=pkg_version:
                                      os.path.join(u, pv, x),
                               src_files)

        env.Command(unpack_zip_files, dist_zip, [
            Delete(os.path.join(unpack_zip_dir, pkg_version)),
            unzipit,
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
        #
        dfiles = map(lambda x, d=test_zip_dir: os.path.join(d, x), dst_files)
        env.Command(dfiles, unpack_zip_files, [
            Delete(os.path.join(unpack_zip_dir, pkg_version, 'build')),
            Delete("$TEST_ZIP_DIR"),
            '$PYTHON $PYTHONFLAGS "%s" install "--prefix=$TEST_ZIP_DIR" --standalone-lib' % \
                os.path.join(unpack_zip_dir, pkg_version, 'setup.py'),
        ])

    if not rpmbuild:
        msg = "@echo \"Warning:  Can not build 'rpm':  no rpmbuild utility found\""
        AlwaysBuild(Alias('rpm', [], msg))
    else:
        topdir = os.path.join(build, 'build',
                              'bdist.' + platform, 'rpm')

        buildroot = os.path.join(build_dir, 'rpm-buildroot')

        BUILDdir = os.path.join(topdir, 'BUILD', pkg + '-' + version)
        RPMSdir = os.path.join(topdir, 'RPMS', 'noarch')
        SOURCESdir = os.path.join(topdir, 'SOURCES')
        SPECSdir = os.path.join(topdir, 'SPECS')
        SRPMSdir = os.path.join(topdir, 'SRPMS')

        specfile_in = os.path.join('rpm', "%s.spec.in" % pkg)
        specfile = os.path.join(SPECSdir, "%s-1.spec" % pkg_version)
        sourcefile = os.path.join(SOURCESdir, "%s.tar.gz" % pkg_version);
        noarch_rpm = os.path.join(RPMSdir, "%s-1.noarch.rpm" % pkg_version)
        src_rpm = os.path.join(SRPMSdir, "%s-1.src.rpm" % pkg_version)

        def spec_function(target, source, env):
            """Generate the RPM .spec file from the template file.

            This fills in the %files portion of the .spec file with a
            list generated from our MANIFEST(s), so we don't have to
            maintain multiple lists.
            """
            c = open(str(source[0]), 'rb').read()
            c = string.replace(c, '__VERSION' + '__', env['VERSION'])
            c = string.replace(c, '__RPM_FILES' + '__', env['RPM_FILES'])
            open(str(target[0]), 'wb').write(c)

        rpm_files.sort()
        rpm_files_str = string.join(rpm_files, "\n") + "\n"
        rpm_spec_env = env.Clone(RPM_FILES = rpm_files_str)
        rpm_spec_action = Action(spec_function, varlist=['RPM_FILES'])
        rpm_spec_env.Command(specfile, specfile_in, rpm_spec_action)

        env.InstallAs(sourcefile, tar_gz)
        Local(sourcefile)

        targets = [ noarch_rpm, src_rpm ]
        cmd = "$RPMBUILD --define '_topdir $(%s$)' --buildroot %s -ba $SOURCES" % (topdir, buildroot)
        if not os.path.isdir(BUILDdir):
            cmd = ("$( mkdir -p %s; $)" % BUILDdir) + cmd
        t = env.Command(targets, specfile, cmd)
        env.Depends(t, sourcefile)

        dist_noarch_rpm = env.Install('$DISTDIR', noarch_rpm)
        dist_src_rpm    = env.Install('$DISTDIR', src_rpm)
        Local(dist_noarch_rpm, dist_src_rpm)
        AddPostAction(dist_noarch_rpm, Chmod(dist_noarch_rpm, 0644))
        AddPostAction(dist_src_rpm, Chmod(dist_src_rpm, 0644))

        dfiles = map(lambda x, d=test_rpm_dir: os.path.join(d, 'usr', x),
                     dst_files)
        env.Command(dfiles,
                    dist_noarch_rpm,
                    "$RPM2CPIO $SOURCES | (cd $TEST_RPM_DIR && cpio -id)")

    if dh_builddeb and fakeroot:
        # Our Debian packaging builds directly into build/dist,
        # so we don't need to Install() the .debs.
        deb = os.path.join(build_dir, 'dist', "%s_%s-1_all.deb" % (pkg, version))
        for d in p['debian_deps']:
            b = env.SCons_revision(os.path.join(build, d), d)
            env.Depends(deb, b)
            Local(b)
        env.Command(deb, build_src_files, [
            "cd %s && fakeroot make -f debian/rules PYTHON=$PYTHON BUILDDEB_OPTIONS=--destdir=../../build/dist binary" % build,
                    ])

        old = os.path.join('lib', 'scons', '')
        new = os.path.join('lib', 'python' + python_ver, 'site-packages', '')
        def xxx(s, old=old, new=new):
            if s[:len(old)] == old:
                s = new + s[len(old):]
            return os.path.join('usr', s)
        dfiles = map(lambda x, t=test_deb_dir: os.path.join(t, x),
                     map(xxx, dst_files))
        env.Command(dfiles,
                    deb,
                    "dpkg --fsys-tarfile $SOURCES | (cd $TEST_DEB_DIR && tar -xf -)")


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
                            string.join(distutils_formats, ','))

    commands.append("$PYTHON $PYTHONFLAGS $SETUP_PY bdist_wininst")

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
    AddPostAction(dist_local_tar_gz, Chmod(dist_local_tar_gz, 0644))
    AddPostAction(dist_local_zip, Chmod(dist_local_zip, 0644))

    commands = [
        Delete(build_dir_local),
        '$PYTHON $PYTHONFLAGS $SETUP_PY install "--install-script=%s" "--install-lib=%s" --no-install-man --no-compile --standalone-lib --no-version-script' % \
                                                (build_dir_local, build_dir_local_slv),
    ]

    for script in scripts:
        #commands.append("mv %s/%s %s/%s.py" % (local, script, local, script))
        local_script = os.path.join(build_dir_local, script)
        commands.append(Move(local_script + '.py', local_script))

    rf = filter(lambda x: not x in scripts, raw_files)
    rf = map(lambda x, slv=s_l_v: os.path.join(slv, x), rf)
    for script in scripts:
        rf.append("%s.py" % script)
    local_targets = map(lambda x, s=build_dir_local: os.path.join(s, x), rf)

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
        env.Command(dist_local_tar_gz,
                    local_targets,
                    "cd %s && tar czf $( ${TARGET.abspath} $) *" % build_dir_local)

        unpack_targets = map(lambda x, d=test_local_tar_gz_dir:
                                    os.path.join(d, x),
                             rf)
        commands = [Delete(test_local_tar_gz_dir),
                    Mkdir(test_local_tar_gz_dir),
                    "cd %s && tar xzf $( ${SOURCE.abspath} $)" % test_local_tar_gz_dir]

        env.Command(unpack_targets, dist_local_tar_gz, commands)

    if zipit:
        env.Command(dist_local_zip, local_targets, zipit,
                    CD = build_dir_local, PSV = '.')

        unpack_targets = map(lambda x, d=test_local_zip_dir:
                                    os.path.join(d, x),
                             rf)
        commands = [Delete(test_local_zip_dir),
                    Mkdir(test_local_zip_dir),
                    unzipit]

        env.Command(unpack_targets, dist_local_zip, unzipit,
                    UNPACK_ZIP_DIR = test_local_zip_dir)

#
#
#
Export('build_dir', 'env')

SConscript('QMTest/SConscript')

#
#
#
files = [
    'runtest.py',
]

def copy(target, source, env):
    t = str(target[0])
    s = str(source[0])
    open(t, 'wb').write(open(s, 'rb').read())

for file in files:
    # Guarantee that real copies of these files always exist in
    # build/.  If there's a symlink there, then this is an Aegis
    # build and we blow them away now so that they'll get "built" later.
    p = os.path.join(build_dir, file)
    if os.path.islink(p):
        os.unlink(p)
    if not os.path.isabs(p):
        p = '#' + p
    sp = env.Command(p, file, copy)
    Local(sp)

#
# Documentation.
#
Export('build_dir', 'env', 'whereis')

SConscript('doc/SConscript')

#
# If we're running in a Subversion working directory, pack up a complete
# source archive from the project files and files in the change.
#

if not svn_status:
   "Not building in a Subversion tree; skipping building src package."
else:
    slines = filter(lambda l: l[0] in ' MA', svn_status_lines)
    sentries = map(lambda l: l.split()[-1], slines)
    sfiles = filter(os.path.isfile, sentries)

    remove_patterns = [
        '.svnt/*',
        '*.aeignore',
        '*.cvsignore',
        'www/*',
    ]

    for p in remove_patterns:
        sfiles = filter(lambda s, p=p: not fnmatch.fnmatch(s, p), sfiles)

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
            env.SCons_revision(os.path.join(b_ps, file), file)

        b_ps_files = map(lambda x, d=b_ps: os.path.join(d, x), sfiles)
        cmds = [
            Delete(b_psv),
            Copy(b_psv, b_ps),
            Touch("$TARGET"),
        ]

        env.Command(b_psv_stamp, src_deps + b_ps_files, cmds)

        apply(Local, b_ps_files, {})

        if gzip:

            env.Command(src_tar_gz, b_psv_stamp,
                        "tar cz${TAR_HFLAG} -f $TARGET -C build %s" % psv)

            #
            # Unpack the archive into build/unpack/scons-{version}.
            #
            unpack_tar_gz_files = map(lambda x, u=unpack_tar_gz_dir, psv=psv:
                                             os.path.join(u, psv, x),
                                      sfiles)

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
            # and under etc (for the testing modules TestCmd.py, TestSCons.py,
            # and unittest.py).  This makes sure that our tests pass with what
            # we really packaged, not because of something hanging around in
            # the development directory.
            #
            # We can get away with calling setup.py using a directory path
            # like this because we put a preamble in it that will chdir()
            # to the directory in which setup.py exists.
            #
            dfiles = map(lambda x, d=test_src_tar_gz_dir: os.path.join(d, x),
                            dst_files)
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
            unpack_zip_files = map(lambda x, u=unpack_zip_dir, psv=psv:
                                             os.path.join(u, psv, x),
                                      sfiles)

            env.Command(unpack_zip_files, src_zip, [
                Delete(os.path.join(unpack_zip_dir, psv)),
                unzipit
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
            #
            dfiles = map(lambda x, d=test_src_zip_dir: os.path.join(d, x),
                            dst_files)
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
        os.path.join(build_dir, 'QMTest'),
        os.path.join(build_dir, 'runtest.py'),
    ])
