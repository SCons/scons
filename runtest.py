#!/usr/bin/env python
#
# runtest.py - wrapper script for running SCons tests
#
# This script mainly exists to set PYTHONPATH to the right list of
# directories to test the SCons modules.
#
# By default, it directly uses the modules in the local tree:
# ./src/ (source files we ship) and ./etc/ (other modules we don't).
#
# HOWEVER, now that SCons has Repository support, we don't have
# Aegis copy all of the files into the local tree.  So if you're
# using Aegis and want to run tests by hand using this script, you
# must "aecp ." the entire source tree into your local directory
# structure.  When you're done with your change, you can then
# "aecpu -unch ." to un-copy any files that you haven't changed.
#
# When any -p option is specified, this script assumes it's in a
# directory in which a build has been performed, and sets PYTHONPATH
# so that it *only* references the modules that have unpacked from
# the specified built package, to test whether the packages are good.
#
# Options:
#
#	-a		Run all tests; does a virtual 'find' for
#			all SCons tests under the current directory.
#
#	-d		Debug.  Runs the script under the Python
#			debugger (pdb.py) so you don't have to
#			muck with PYTHONPATH yourself.
#
#       -h              Print the help and exit.
#
#       -o file         Print test results to the specified file
#                       in the format expected by aetest(5).  This
#                       is intended for use in the batch_test_command
#                       field in the Aegis project config file.
#
#	-P Python	Use the specified Python interpreter.
#
#	-p package	Test against the specified package.
#
#	-q		Quiet.  By default, runtest.py prints the
#			command line it will execute before
#			executing it.  This suppresses that print.
#
#	-X		The scons "script" is an executable; don't
#			feed it to Python.
#
#       -x scons        The scons script to use for tests.
#
# (Note:  There used to be a -v option that specified the SCons
# version to be tested, when we were installing in a version-specific
# library directory.  If we ever resurrect that as the default, then
# you can find the appropriate code in the 0.04 version of this script,
# rather than reinventing that wheel.)
#

import getopt
import glob
import os
import os.path
import re
import stat
import string
import sys

all = 0
debug = ''
tests = []
printcmd = 1
package = None
scons = None
scons_exec = None
output = None

if os.name == 'java':
    python = os.path.join(sys.prefix, 'jython')
else:
    python = sys.executable

cwd = os.getcwd()

if sys.platform == 'win32' or os.name == 'java':
    lib_dir = os.path.join(sys.exec_prefix, "Lib")
else:
    # The hard-coded "python" here is the directory name,
    # not an executable, so it's all right.
    lib_dir = os.path.join(sys.exec_prefix, "lib", "python" + sys.version[0:3])

helpstr = """\
Usage: runtest.py [OPTIONS] [TEST ...]
Options:
  -a, --all                   Run all tests.
  -d, --debug                 Run test scripts under the Python debugger.
  -h, --help                  Print this message and exit.
  -o FILE, --output FILE      Print test results to FILE (Aegis format).
  -P Python                   Use the specified Python interpreter.
  -p PACKAGE, --package PACKAGE
                              Test against the specified PACKAGE:
                                deb           Debian
                                local-tar-gz  .tar.gz standalone package
                                local-zip     .zip standalone package
                                rpm           Red Hat
                                src-tar-gz    .tar.gz source package
                                src-zip       .zip source package
                                tar-gz        .tar.gz distribution
                                zip           .zip distribution
  -q, --quiet                 Don't print the test being executed.
  -X                          Test script is executable, don't feed to Python.
  -x SCRIPT, --exec SCRIPT    Test SCRIPT.
"""

opts, args = getopt.getopt(sys.argv[1:], "adho:P:p:qXx:",
                            ['all', 'debug', 'help', 'output=',
                             'package=', 'python=', 'quiet', 'exec='])

for o, a in opts:
    if o == '-a' or o == '--all':
        all = 1
    elif o == '-d' or o == '--debug':
        debug = os.path.join(lib_dir, "pdb.py")
    elif o == '-h' or o == '--help':
        print helpstr
        sys.exit(0)
    elif o == '-o' or o == '--output':
        if not os.path.isabs(a):
            a = os.path.join(cwd, a)
        output = a
    elif o == '-P' or o == '--python':
        python = a
    elif o == '-p' or o == '--package':
        package = a
    elif o == '-q' or o == '--quiet':
        printcmd = 0
    elif o == '-X':
        scons_exec = 1
    elif o == '-x' or o == '--exec':
        scons = a

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

aegis = whereis('aegis')

spe = None
if aegis:
    spe = os.popen("aesub '$spe' 2>/dev/null", "r").read()[:-1]
    spe = string.split(spe, os.pathsep)

class Test:
    def __init__(self, path, spe=None):
        self.path = path
        self.abspath = os.path.abspath(path)
        if spe:
            for dir in spe:
                f = os.path.join(dir, path)
                if os.path.isfile(f):
                    self.abspath = f
                    break
        self.status = None

if args:
    if spe:
        for a in args:
            if os.path.isabs(a):
                for g in glob.glob(a):
                    tests.append(Test(g))
            else:
                for dir in spe:
                    x = os.path.join(dir, a)
                    globs = glob.glob(x)
                    if globs:
                        for g in globs:
                            tests.append(Test(g))
                        break
    else:
        for a in args:
            for g in glob.glob(a):
                tests.append(Test(g))
elif all:
    tdict = {}

    def find_Test_py(arg, dirname, names, tdict=tdict):
        for n in filter(lambda n: n[-8:] == "Tests.py", names):
            t = os.path.join(dirname, n)
            if not tdict.has_key(t):
                tdict[t] = Test(t)
    os.path.walk('src', find_Test_py, 0)

    def find_py(arg, dirname, names, tdict=tdict):
        for n in filter(lambda n: n[-3:] == ".py", names):
            t = os.path.join(dirname, n)
            if not tdict.has_key(t):
                tdict[t] = Test(t)
    os.path.walk('test', find_py, 0)

    if aegis:
        cmd = "aegis -list -unf pf 2>/dev/null"
        for line in os.popen(cmd, "r").readlines():
            a = string.split(line)
            if a[0] == "test" and not tdict.has_key(a[-1]):
                tdict[a[-1]] = Test(a[-1], spe)
        cmd = "aegis -list -unf cf 2>/dev/null"
        for line in os.popen(cmd, "r").readlines():
            a = string.split(line)
            if a[0] == "test":
                if a[1] == "remove":
                    del tdict[a[-1]]
                elif not tdict.has_key(a[-1]):
                    tdict[a[-1]] = Test(a[-1], spe)

    keys = tdict.keys()
    keys.sort()
    tests = map(tdict.get, keys)

if package:

    dir = {
        'deb'          : 'usr',
        'local-tar-gz' : None,
        'local-zip'    : None,
        'rpm'          : 'usr',
        'src-tar-gz'   : '',
        'src-zip'      : '',
        'tar-gz'       : '',
        'zip'          : '',
    }

    # The hard-coded "python2.1" here is the library directory
    # name on Debian systems, not an executable, so it's all right.
    lib = {
        'deb'        : os.path.join('python2.1', 'site-packages')
    }

    if not dir.has_key(package):
        sys.stderr.write("Unknown package '%s'\n" % package)
        sys.exit(2)

    test_dir = os.path.join(cwd, 'build', 'test-%s' % package)

    if dir[package] is None:
        scons_script_dir = test_dir
        globs = glob.glob(os.path.join(test_dir, 'scons-local-*'))
        if not globs:
            sys.stderr.write("No `scons-local-*' dir in `%s'\n" % test_dir)
            sys.exit(2)
        scons_lib_dir = None
        pythonpath_dir = globs[len(globs)-1]
    elif sys.platform == 'win32':
        scons_script_dir = os.path.join(test_dir, dir[package], 'Scripts')
        scons_lib_dir = os.path.join(test_dir, dir[package])
        pythonpath_dir = scons_lib_dir
    else:
        scons_script_dir = os.path.join(test_dir, dir[package], 'bin')
        l = lib.get(package, 'scons')
        scons_lib_dir = os.path.join(test_dir, dir[package], 'lib', l)
        pythonpath_dir = scons_lib_dir

else:
    sd = None
    ld = None

    # XXX:  Logic like the following will be necessary once
    # we fix runtest.py to run tests within an Aegis change
    # without symlinks back to the baseline(s).
    #
    #if spe:
    #    if not scons:
    #        for dir in spe:
    #            d = os.path.join(dir, 'src', 'script')
    #            f = os.path.join(d, 'scons.py')
    #            if os.path.isfile(f):
    #                sd = d
    #                scons = f
    #    spe = map(lambda x: os.path.join(x, 'src', 'engine'), spe)
    #    ld = string.join(spe, os.pathsep)

    scons_script_dir = sd or os.path.join(cwd, 'src', 'script')

    scons_lib_dir = ld or os.path.join(cwd, 'src', 'engine')

    pythonpath_dir = scons_lib_dir

if scons:
    # Let the version of SCons that the -x option pointed to find
    # its own modules.
    os.environ['SCONS'] = scons
elif scons_lib_dir:
    # Because SCons is really aggressive about finding its modules,
    # it sometimes finds SCons modules elsewhere on the system.
    # This forces SCons to use the modules that are being tested.
    os.environ['SCONS_LIB_DIR'] = scons_lib_dir

if scons_exec:
    os.environ['SCONS_EXEC'] = '1'

os.environ['PYTHONPATH'] = pythonpath_dir + \
                           os.pathsep + \
                           os.path.join(cwd, 'build', 'etc') + \
                           os.pathsep + \
                           os.path.join(cwd, 'etc')

os.chdir(scons_script_dir)

class Unbuffered:
    def __init__(self, file):
        self.file = file
    def write(self, arg):
        self.file.write(arg)
        self.file.flush()
    def __getattr__(self, attr):
        return getattr(self.file, attr)

sys.stdout = Unbuffered(sys.stdout)

for t in tests:
    cmd = string.join([python, debug, t.abspath], " ")
    if printcmd:
        sys.stdout.write(cmd + "\n")
    s = os.system(cmd)
    if s >= 256:
        s = s / 256
    t.status = s
    if s < 0 or s > 2:
        sys.stdout.write("Unexpected exit status %d\n" % s)

fail = filter(lambda t: t.status == 1, tests)
no_result = filter(lambda t: t.status == 2, tests)

if len(tests) != 1:
    if fail:
        if len(fail) == 1:
            sys.stdout.write("\nFailed the following test:\n")
        else:
            sys.stdout.write("\nFailed the following %d tests:\n" % len(fail))
        paths = map(lambda x: x.path, fail)
        sys.stdout.write("\t" + string.join(paths, "\n\t") + "\n")
    if no_result:
        if len(no_result) == 1:
            sys.stdout.write("\nNO RESULT from the following test:\n")
        else:
            sys.stdout.write("\nNO RESULT from the following %d tests:\n" % len(no_result))
        paths = map(lambda x: x.path, no_result)
        sys.stdout.write("\t" + string.join(paths, "\n\t") + "\n")

if output:
    f = open(output, 'w')
    f.write("test_result = [\n")
    for t in tests:
        f.write('    { file_name = "%s";\n' % t.path)
        f.write('      exit_status = %d; },\n' % t.status)
    f.write("];\n")
    f.close()
    sys.exit(0)
else:
    if len(fail):
        sys.exit(1)
    elif len(no_result):
        sys.exit(2)
    else:
        sys.exit(0)
