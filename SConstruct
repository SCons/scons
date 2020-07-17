#
# SConstruct file to build scons packages during development.
#
# See the README.rst file for an overview of how SCons is built and tested.
import os.path
import sys
import textwrap
from time import strftime

copyright_years = strftime('2001 - %Y')

# This gets inserted into the man pages to reflect the month of release.
month_year = strftime('%B %Y')
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


project = 'scons'
default_version = '4.0.1'
copyright = "Copyright (c) %s The SCons Foundation" % copyright_years

#
# We let the presence or absence of various utilities determine whether
# or not we bother to build certain pieces of things.  This should allow
# people to still do SCons packaging work even if they don't have all
# of the utilities installed
#
print("git    :%s" % git)
print("gzip   :%s" % gzip)
print("unzip  :%s" % unzip)
print("zip    :%s" % zip_path)

#
# Adding some paths to sys.path, this is mainly needed
# for the doc toolchain.
#
addpaths = [os.path.abspath(os.path.join(os.getcwd(), 'bin')),
            os.path.abspath(os.path.join(os.getcwd(), 'testing/framework'))]
for a in addpaths:
    if a not in sys.path:
        sys.path.append(a)

# Use site_scons logic to process command line arguments
command_line = BuildCommandLine(default_version)
command_line.process_command_line_vars()

Default('.', command_line.build_dir)
# Just make copies, don't symlink them.
SetOption('duplicate', 'copy')

packaging_flavors = [
    ('tar-gz', "The normal .tar.gz file for end-user installation."),
    ('local-tar-gz', "A .tar.gz file for dropping into other software " +
     "for local use."),
    ('zip', "The normal .zip file for end-user installation."),
    ('local-zip', "A .zip file for dropping into other software " +
     "for local use."),
    ('src-tar-gz', "A .tar.gz file containing all the source " +
     "(including tests and documentation)."),
    ('src-zip', "A .zip file containing all the source " +
     "(including tests and documentation)."),
]

test_tar_gz_dir = os.path.join(command_line.build_dir, "test-tar-gz")
test_src_tar_gz_dir = os.path.join(command_line.build_dir, "test-src-tar-gz")
test_local_tar_gz_dir = os.path.join(command_line.build_dir, "test-local-tar-gz")
test_zip_dir = os.path.join(command_line.build_dir, "test-zip")
test_src_zip_dir = os.path.join(command_line.build_dir, "test-src-zip")
test_local_zip_dir = os.path.join(command_line.build_dir, "test-local-zip")

unpack_tar_gz_dir = os.path.join(command_line.build_dir, "unpack-tar-gz")
unpack_zip_dir = os.path.join(command_line.build_dir, "unpack-zip")

if is_windows():
    tar_hflag = ''
#     python_project_subinst_dir = os.path.join("Lib", "site-packages", project)
#     project_script_subinst_dir = 'Scripts'
else:
    tar_hflag = 'h'
#     python_project_subinst_dir = os.path.join("lib", project)
#     project_script_subinst_dir = 'bin'

indent_fmt = '  %-26s  '

Help("""\
The following aliases build packages of various types, and unpack the
contents into build/test-$PACKAGE subdirectories, which can be used by the
runtest.py -p option to run tests against what's been actually packaged:

""")

aliases = sorted(packaging_flavors + [('doc', 'The SCons documentation.')])

for alias, help_text in aliases:
    tw = textwrap.TextWrapper(
        width=78,
        initial_indent=indent_fmt % alias,
        subsequent_indent=indent_fmt % '' + '  ',
    )
    Help(tw.fill(help_text) + '\n')

Help("""
The following command-line variables can be set:

""")

for variable, help_text in command_line.command_line_variables:
    tw = textwrap.TextWrapper(
        width=78,
        initial_indent=indent_fmt % variable,
        subsequent_indent=indent_fmt % '' + '  ',
    )
    Help(tw.fill(help_text) + '\n')

revaction = SCons_revision
revbuilder = Builder(action=Action(SCons_revision,
                                   varlist=['COPYRIGHT', 'VERSION']))

env = Environment(
    ENV=command_line.ENV,

    BUILD=command_line.build_id,
    BUILDDIR=command_line.build_dir,
    BUILDSYS=command_line.build_system,
    COPYRIGHT=copyright,
    DATE=command_line.date,
    DEB_DATE=deb_date,

    DEVELOPER=command_line.developer,
    DISTDIR=os.path.join(command_line.build_dir, 'dist'),
    MONTH_YEAR=month_year,
    REVISION=command_line.revision,
    VERSION=command_line.version,

    TAR_HFLAG=tar_hflag,

    ZIP=zip_path,
    ZIPFLAGS='-r',
    UNZIP=unzip,
    UNZIPFLAGS='-o -d $UNPACK_ZIP_DIR',

    # ZCAT=zcat,
    # ZIPID=zipit,

    TEST_SRC_TAR_GZ_DIR=test_src_tar_gz_dir,
    TEST_SRC_ZIP_DIR=test_src_zip_dir,
    TEST_TAR_GZ_DIR=test_tar_gz_dir,
    TEST_ZIP_DIR=test_zip_dir,

    UNPACK_TAR_GZ_DIR=unpack_tar_gz_dir,
    UNPACK_ZIP_DIR=unpack_zip_dir,

    BUILDERS={'SCons_revision': revbuilder,
              'SOElim': soelimbuilder},

    PYTHON='"%s"' % sys.executable,
    PYTHONFLAGS='-tt',
)

Version_values = [Value(command_line.version), Value(command_line.build_id)]

installed_local_files = create_local_packages(env)

update_init_file(env)
#
#
#
#
# Documentation.
#
Export('command_line', 'env', 'whereis', 'revaction')

SConscript('doc/SConscript')


# Build packages for pypi
env.Command('$DISTDIR/SCons-${VERSION}-py3-none-any.whl', ['setup.cfg', 'setup.py', 'SCons/__init__.py'],
            '$PYTHON setup.py bdist_wheel')

env.Command('$DISTDIR/SCons-${VERSION}.zip', ['setup.cfg', 'setup.py', 'SCons/__init__.py'],
            '$PYTHON setup.py sdist --format=zip')
env.Command('$DISTDIR/SCons-${VERSION}.tar.gz', ['setup.cfg', 'setup.py', 'SCons/__init__.py'],
            '$PYTHON setup.py sdist --format=gztar')

# TODO add auto copyright date to README.rst, LICENSE
# TODO build API DOCS
