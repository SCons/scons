#!/usr/bin/env python
#
# A script that takes an scons-src-{version}.zip file, unwraps it in
# a temporary location, and calls runtest.py to execute one or more of
# its tests.
#
# The default is to download the latest scons-src archive from the SCons
# web site, and to execute all of the tests.
#
# With a little more work, this will become the basis of an automated
# testing and reporting system that anyone will be able to use to
# participate in testing SCons on their system and regularly reporting
# back the results.  A --xml option is a stab at gathering a lot of
# relevant information about the system, the Python version, etc.,
# so that problems on different platforms can be identified sooner.
#
import atexit
import getopt
import os
import os.path
import sys
import tempfile
import time
import zipfile

try:
    # try Python 3.x style
    from urllib.request import urlretrieve
except ImportError:
    # nope, must be 2.x; this hack is equivalent
    import imp
    # protect import from fixer
    urlretrieve = imp.load_module('urllib',
                                  *imp.find_module('urllib')).urlretrieve

helpstr = """\
Usage: scons-test.py [-f zipfile] [-o outdir] [-v] [--xml] [runtest arguments]
Options:
  -f FILE                     Specify input .zip FILE name
  -o DIR, --out DIR           Change output directory name to DIR
  -v, --verbose               Print file names when extracting
  --xml                       XML output
"""

opts, args = getopt.getopt(sys.argv[1:],
                           "f:o:v",
                           ['file=', 'out=', 'verbose', 'xml'])

format = None
outdir = None
printname = lambda x: x
inputfile = 'http://scons.sourceforge.net/scons-src-latest.zip'

for o, a in opts:
    if o == '-f' or o == '--file':
        inputfile = a
    elif o == '-o' or o == '--out':
        outdir = a
    elif o == '-v' or o == '--verbose':
        def printname(x):
            print(x)
    elif o == '--xml':
        format = o

startdir = os.getcwd()

tempfile.template = 'scons-test.'
tempdir = tempfile.mktemp()

if not os.path.exists(tempdir):
    os.mkdir(tempdir)
    def cleanup(tempdir=tempdir):
        import shutil
        os.chdir(startdir)
        shutil.rmtree(tempdir)
    atexit.register(cleanup)

# Fetch the input file if it happens to be across a network somewhere.
# Ohmigod, does Python make this simple...
inputfile, headers = urlretrieve(inputfile)

# Unzip the header file in the output directory.  We use our own code
# (lifted from scons-unzip.py) to make the output subdirectory name
# match the basename of the .zip file.
zf = zipfile.ZipFile(inputfile, 'r')

if outdir is None:
    name, _ = os.path.splitext(os.path.basename(inputfile))
    outdir = os.path.join(tempdir, name)

def outname(n, outdir=outdir):
    l = []
    while True:
        n, tail = os.path.split(n)
        if not n:
            break
        l.append(tail)
    l.append(outdir)
    l.reverse()
    return os.path.join(*l)

for name in zf.namelist():
    dest = outname(name)
    dir = os.path.dirname(dest)
    try:
        os.makedirs(dir)
    except:
        pass
    printname(dest)
    # if the file exists, then delete it before writing
    # to it so that we don't end up trying to write to a symlink:
    if os.path.isfile(dest) or os.path.islink(dest):
        os.unlink(dest)
    if not os.path.isdir(dest):
        open(dest, 'w').write(zf.read(name))

os.chdir(outdir)

# Load (by hand) the SCons modules we just unwrapped so we can
# extract their version information.  Note that we have to override
# SCons.Script.main() with a do_nothing() function, because loading up
# the 'scons' script will actually try to execute SCons...
src_script = os.path.join(outdir, 'src', 'script')
src_engine = os.path.join(outdir, 'src', 'engine')
src_engine_SCons = os.path.join(src_engine, 'SCons')

fp, pname, desc = imp.find_module('SCons', [src_engine])
SCons = imp.load_module('SCons', fp, pname, desc)

fp, pname, desc = imp.find_module('Script', [src_engine_SCons])
SCons.Script = imp.load_module('Script', fp, pname, desc)

def do_nothing():
    pass
SCons.Script.main = do_nothing

fp, pname, desc = imp.find_module('scons', [src_script])
scons = imp.load_module('scons', fp, pname, desc)
fp.close()

# Default is to run all the tests by passing the -a flags to runtest.py.
if not args:
    runtest_args = '-a'
else:
    runtest_args = ' '.join(args)

if format == '--xml':

    print("<scons_test_run>")
    print("  <sys>")
    sys_keys = ['byteorder', 'exec_prefix', 'executable', 'maxint', 'maxunicode', 'platform', 'prefix', 'version', 'version_info']
    for k in sys_keys:
        print("    <%s>%s</%s>" % (k, sys.__dict__[k], k))
    print("  </sys>")

    fmt = '%a %b %d %H:%M:%S %Y'
    print("  <time>")
    print("    <gmtime>%s</gmtime>" % time.strftime(fmt, time.gmtime()))
    print("    <localtime>%s</localtime>" % time.strftime(fmt, time.localtime()))
    print("  </time>")

    print("  <tempdir>%s</tempdir>" % tempdir)

    def print_version_info(tag, module):
        print("    <%s>" % tag)
        print("      <version>%s</version>" % module.__version__)
        print("      <build>%s</build>" % module.__build__)
        print("      <buildsys>%s</buildsys>" % module.__buildsys__)
        print("      <date>%s</date>" % module.__date__)
        print("      <developer>%s</developer>" % module.__developer__)
        print("    </%s>" % tag)

    print("  <scons>")
    print_version_info("script", scons)
    print_version_info("engine", SCons)
    print("  </scons>")

    environ_keys = [
        'PATH',
        'SCONSFLAGS',
        'SCONS_LIB_DIR',
        'PYTHON_ROOT',
        'QTDIR',

        'COMSPEC',
        'INTEL_LICENSE_FILE',
        'INCLUDE',
        'LIB',
        'MSDEVDIR',
        'OS',
        'PATHEXT',
        'SystemRoot',
        'TEMP',
        'TMP',
        'USERNAME',
        'VXDOMNTOOLS',
        'WINDIR',
        'XYZZY'

        'ENV',
        'HOME',
        'LANG',
        'LANGUAGE',
        'LOGNAME',
        'MACHINE',
        'OLDPWD',
        'PWD',
        'OPSYS',
        'SHELL',
        'TMPDIR',
        'USER',
    ]

    print("  <environment>")
    for key in sorted(environ_keys):
        value = os.environ.get(key)
        if value:
            print("    <variable>")
            print("      <name>%s</name>" % key)
            print("      <value>%s</value>" % value)
            print("    </variable>")
    print("  </environment>")

    command = '"%s" runtest.py -q -o - --xml %s' % (sys.executable, runtest_args)
    #print(command)
    os.system(command)
    print("</scons_test_run>")

else:

    def print_version_info(tag, module):
        print("\t%s: v%s.%s, %s, by %s on %s" % (tag,
                                                 module.__version__,
                                                 module.__build__,
                                                 module.__date__,
                                                 module.__developer__,
                                                 module.__buildsys__))

    print("SCons by Steven Knight et al.:")
    print_version_info("script", scons)
    print_version_info("engine", SCons)

    command = '"%s" runtest.py %s' % (sys.executable, runtest_args)
    #print(command)
    os.system(command)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
