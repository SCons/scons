#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003, 2004 The SCons Foundation
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
#       -a              Run all tests; does a virtual 'find' for
#                       all SCons tests under the current directory.
#
#       --aegis         Print test results to an output file (specified
#                       by the -o option) in the format expected by
#                       aetest(5).  This is intended for use in the
#                       batch_test_command field in the Aegis project
#                       config file.
#
#       -d              Debug.  Runs the script under the Python
#                       debugger (pdb.py) so you don't have to
#                       muck with PYTHONPATH yourself.
#
#       -f file         Only execute the tests listed in the specified
#                       file.
#
#       -h              Print the help and exit.
#
#       -o file         Print test results to the specified file.
#                       The --aegis and --xml options specify the
#                       output format.
#
#       -P Python       Use the specified Python interpreter.
#
#       -p package      Test against the specified package.
#
#       --passed        In the final summary, also report which tests
#                       passed.  The default is to only report tests
#                       which failed or returned NO RESULT.
#
#       -q              Quiet.  By default, runtest.py prints the
#                       command line it will execute before
#                       executing it.  This suppresses that print.
#
#       -X              The scons "script" is an executable; don't
#                       feed it to Python.
#
#       -x scons        The scons script to use for tests.
#
#       --xml           Print test results to an output file (specified
#                       by the -o option) in an SCons-specific XML format.
#                       This is (will be) used for reporting results back
#                       to a central SCons test monitoring infrastructure.
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
import popen2
import re
import stat
import string
import sys

all = 0
debug = ''
format = None
tests = []
printcommand = 1
package = None
print_passed_summary = None
scons = None
scons_exec = None
outputfile = None
testlistfile = None
version = ''

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
  --aegis                     Print results in Aegis format.
  -d, --debug                 Run test scripts under the Python debugger.
  -f FILE, --file FILE        Run tests in specified FILE.
  -h, --help                  Print this message and exit.
  -o FILE, --output FILE      Print test results to FILE.
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
  --passed                    Summarize which tests passed.
  -q, --quiet                 Don't print the test being executed.
  -v version                  Specify the SCons version.
  -X                          Test script is executable, don't feed to Python.
  -x SCRIPT, --exec SCRIPT    Test SCRIPT.
  --xml                       Print results in SCons XML format.
"""

opts, args = getopt.getopt(sys.argv[1:], "adf:ho:P:p:qv:Xx:",
                            ['all', 'aegis',
                             'debug', 'file=', 'help', 'output=',
                             'package=', 'passed', 'python=', 'quiet',
                             'version=', 'exec=',
                             'xml'])

for o, a in opts:
    if o == '-a' or o == '--all':
        all = 1
    elif o == '-d' or o == '--debug':
        debug = os.path.join(lib_dir, "pdb.py")
    elif o == '-f' or o == '--file':
        if not os.path.isabs(a):
            a = os.path.join(cwd, a)
        testlistfile = a
    elif o == '-h' or o == '--help':
        print helpstr
        sys.exit(0)
    elif o == '-o' or o == '--output':
        if a != '-' and not os.path.isabs(a):
            a = os.path.join(cwd, a)
        outputfile = a
    elif o == '-p' or o == '--package':
        package = a
    elif o == '--passed':
        print_passed_summary = 1
    elif o == '-P' or o == '--python':
        python = a
    elif o == '-q' or o == '--quiet':
        printcommand = 0
    elif o == '-v' or o == '--version':
        version = a
    elif o == '-X':
        scons_exec = 1
    elif o == '-x' or o == '--exec':
        scons = a
    elif o in ['--aegis', '--xml']:
        format = o

def whereis(file):
    for dir in string.split(os.environ['PATH'], os.pathsep):
        f = os.path.join(dir, file)
        if os.path.isfile(f):
            try:
                st = os.stat(f)
            except OSError:
                continue
            if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                return f
    return None

aegis = whereis('aegis')

sp = []

if aegis:
    paths = os.popen("aesub '$sp' 2>/dev/null", "r").read()[:-1]
    sp.extend(string.split(paths, os.pathsep))
    spe = os.popen("aesub '$spe' 2>/dev/null", "r").read()[:-1]
    spe = string.split(spe, os.pathsep)
else:
    spe = []

sp.append(cwd)

#
_ws = re.compile('\s')

def escape(s):
    if _ws.search(s):
        s = '"' + s + '"'
    return s

# Set up lowest-common-denominator spawning of a process on both Windows
# and non-Windows systems that works all the way back to Python 1.5.2.
try:
    os.spawnv
except AttributeError:
    def spawn_it(command_args):
        pid = os.fork()
        if pid == 0:
            os.execv(command_args[0], command_args)
        else:
            pid, status = os.waitpid(pid, 0)
            return status >> 8
else:
    def spawn_it(command_args):
	command_args = map(escape, command_args)
        return os.spawnv(os.P_WAIT, command_args[0], command_args)

class Base:
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

class SystemExecutor(Base):
    def execute(self):
        s = spawn_it(self.command_args)
        self.status = s
        if s < 0 or s > 2:
            sys.stdout.write("Unexpected exit status %d\n" % s)

try:
    popen2.Popen3
except AttributeError:
    class PopenExecutor(Base):
        def execute(self):
            (tochild, fromchild, childerr) = os.popen3(self.command_str)
            tochild.close()
            self.stdout = fromchild.read()
            self.stderr = childerr.read()
            fromchild.close()
            self.status = childerr.close()
            if not self.status:
                self.status = 0
else:
    class PopenExecutor(Base):
        def execute(self):
            p = popen2.Popen3(self.command_str, 1)
            p.tochild.close()
            self.stdout = p.fromchild.read()
            self.stderr = p.childerr.read()
            self.status = p.wait()

class Aegis(SystemExecutor):
    def header(self, f):
        f.write('test_result = [\n')
    def write(self, f):
        f.write('    { file_name = "%s";\n' % self.path)
        f.write('      exit_status = %d; },\n' % self.status)
    def footer(self, f):
        f.write('];\n')

class XML(PopenExecutor):
    def header(self, f):
        f.write('  <results>\n')
    def write(self, f):
        f.write('    <test>\n')
        f.write('      <file_name>%s</file_name>\n' % self.path)
        f.write('      <command_line>%s</command_line>\n' % self.command_str)
        f.write('      <exit_status>%s</exit_status>\n' % self.status)
        f.write('      <stdout>%s</stdout>\n' % self.stdout)
        f.write('      <stderr>%s</stderr>\n' % self.stderr)
        f.write('    </test>\n')
    def footer(self, f):
        f.write('  </results>\n')

format_class = {
    None        : SystemExecutor,
    '--aegis'   : Aegis,
    '--xml'     : XML,
}
Test = format_class[format]

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
    # Find all of the SCons functional tests in the local directory
    # tree.  This is anything under the 'src' subdirectory that ends
    # with 'Tests.py', or any Python script (*.py) under the 'test'
    # subdirectory.
    #
    # Note that there are some tests under 'src' that *begin* with
    # 'test_', but they're packaging and installation tests, not
    # functional tests, so we don't execute them by default.  (They can
    # still be executed by hand, though, and are routinely executed
    # by the Aegis packaging build to make sure that we're building
    # things correctly.)
    tdict = {}

    def find_Tests_py(arg, dirname, names, tdict=tdict):
        for n in filter(lambda n: n[-8:] == "Tests.py", names):
            t = os.path.join(dirname, n)
            if not tdict.has_key(t):
                tdict[t] = Test(t)
    os.path.walk('src', find_Tests_py, 0)

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
elif testlistfile:
    tests = open(testlistfile, 'r').readlines()
    tests = filter(lambda x: x[0] != '#', tests)
    tests = map(lambda x: x[:-1], tests)
    tests = map(Test, tests)
else:
    sys.stderr.write("""\
runtest.py:  No tests were specified on the command line.
             List one or more tests, or use the -a option
             to find and run all tests.
""")


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

os.environ['SCONS_SCRIPT_DIR'] = scons_script_dir
os.environ['SCONS_CWD'] = cwd

os.environ['SCONS_VERSION'] = version

old_pythonpath = os.environ.get('PYTHONPATH')

pythonpaths = [ pythonpath_dir ]
for p in sp:
    pythonpaths.append(os.path.join(p, 'build', 'etc'))
    pythonpaths.append(os.path.join(p, 'etc'))
os.environ['PYTHONPATH'] = string.join(pythonpaths, os.pathsep)

if old_pythonpath:
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + \
                               os.pathsep + \
                               old_pythonpath

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
    t.command_args = [python]
    if debug:
        t.command_args.append(debug)
    t.command_args.append(t.abspath)
    t.command_str = string.join(map(escape, t.command_args), " ")
    if printcommand:
        sys.stdout.write(t.command_str + "\n")
    t.execute()

passed = filter(lambda t: t.status == 0, tests)
fail = filter(lambda t: t.status == 1, tests)
no_result = filter(lambda t: t.status == 2, tests)

if len(tests) != 1:
    if passed and print_passed_summary:
        if len(passed) == 1:
            sys.stdout.write("\nPassed the following test:\n")
        else:
            sys.stdout.write("\nPassed the following %d tests:\n" % len(passed))
        paths = map(lambda x: x.path, passed)
        sys.stdout.write("\t" + string.join(paths, "\n\t") + "\n")
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

if outputfile:
    if outputfile == '-':
        f = sys.stdout
    else:
        f = open(outputfile, 'w')
    tests[0].header(f)
    #f.write("test_result = [\n")
    for t in tests:
        t.write(f)
    tests[0].footer(f)
    #f.write("];\n")
    if outputfile != '-':
        f.close()

if format == '--aegis':
    sys.exit(0)
elif len(fail):
    sys.exit(1)
elif len(no_result):
    sys.exit(2)
else:
    sys.exit(0)
