#!/usr/bin/env python
#
# __COPYRIGHT__
#
# runtest.py - wrapper script for running SCons tests
#
# This script mainly exists to set PYTHONPATH to the right list of
# directories to test the SCons modules.
#
# By default, it directly uses the modules in the local tree:
# ./src/ (source files we ship) and ./QMTest/ (other modules we don't).
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
#       -l              List available tests and exit.
#
#       -n              No execute, just print command lines.
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
#       --sp            The Aegis search path.
#
#       --spe           The Aegis executable search path.
#
#       -t              Print the execution time of each test.
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
import re
import stat
import string
import sys
import time

if not hasattr(os, 'WEXITSTATUS'):
    os.WEXITSTATUS = lambda x: x

cwd = os.getcwd()

all = 0
baseline = 0
builddir = os.path.join(cwd, 'build')
debug = ''
execute_tests = 1
format = None
list_only = None
printcommand = 1
package = None
print_passed_summary = None
scons = None
scons_exec = None
outputfile = None
testlistfile = None
version = ''
print_times = None
python = None
sp = None
spe = None

helpstr = """\
Usage: runtest.py [OPTIONS] [TEST ...]
Options:
  -a, --all                   Run all tests.
  --aegis                     Print results in Aegis format.
  -b BASE, --baseline BASE    Run test scripts against baseline BASE.
  --builddir DIR              Directory in which packages were built.
  -d, --debug                 Run test scripts under the Python debugger.
  -f FILE, --file FILE        Run tests in specified FILE.
  -h, --help                  Print this message and exit.
  -l, --list                  List available tests and exit.
  -n, --no-exec               No execute, just print command lines.
  --noqmtest                  Execute tests directly, not using QMTest.
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
  --qmtest                    Run using the QMTest harness.
  -q, --quiet                 Don't print the test being executed.
  --sp PATH                   The Aegis search path.
  --spe PATH                  The Aegis executable search path.
  -t, --time                  Print test execution time.
  -v version                  Specify the SCons version.
  --verbose=LEVEL             Set verbose level: 1 = print executed commands,
                                2 = print commands and non-zero output,
                                3 = print commands and all output.
  -X                          Test script is executable, don't feed to Python.
  -x SCRIPT, --exec SCRIPT    Test SCRIPT.
  --xml                       Print results in SCons XML format.
"""

opts, args = getopt.getopt(sys.argv[1:], "ab:df:hlno:P:p:qv:Xx:t",
                            ['all', 'aegis', 'baseline=', 'builddir=',
                             'debug', 'file=', 'help',
                             'list', 'no-exec', 'noqmtest', 'output=',
                             'package=', 'passed', 'python=', 'qmtest',
                             'quiet', 'sp=', 'spe=', 'time',
                             'version=', 'exec=',
                             'verbose=', 'xml'])

for o, a in opts:
    if o in ['-a', '--all']:
        all = 1
    elif o in ['-b', '--baseline']:
        baseline = a
    elif o in ['--builddir']:
        builddir = a
        if not os.path.isabs(builddir):
            builddir = os.path.normpath(os.path.join(cwd, builddir))
    elif o in ['-d', '--debug']:
        for dir in sys.path:
            pdb = os.path.join(dir, 'pdb.py')
            if os.path.exists(pdb):
                debug = pdb
                break
    elif o in ['-f', '--file']:
        if not os.path.isabs(a):
            a = os.path.join(cwd, a)
        testlistfile = a
    elif o in ['-h', '--help']:
        print helpstr
        sys.exit(0)
    elif o in ['-l', '--list']:
        list_only = 1
    elif o in ['-n', '--no-exec']:
        execute_tests = None
    elif o in ['--noqmtest']:
        qmtest = None
    elif o in ['-o', '--output']:
        if a != '-' and not os.path.isabs(a):
            a = os.path.join(cwd, a)
        outputfile = a
    elif o in ['-p', '--package']:
        package = a
    elif o in ['--passed']:
        print_passed_summary = 1
    elif o in ['-P', '--python']:
        python = a
    elif o in ['--qmtest']:
        if sys.platform == 'win32':
            # typically in c:/PythonXX/Scripts
            qmtest = 'qmtest.py'
        else:
            qmtest = 'qmtest'
    elif o in ['-q', '--quiet']:
        printcommand = 0
    elif o in ['--sp']:
        sp = string.split(a, os.pathsep)
    elif o in ['--spe']:
        spe = string.split(a, os.pathsep)
    elif o in ['-t', '--time']:
        print_times = 1
    elif o in ['--verbose']:
        os.environ['TESTCMD_VERBOSE'] = a
    elif o in ['-v', '--version']:
        version = a
    elif o in ['-X']:
        scons_exec = 1
    elif o in ['-x', '--exec']:
        scons = a
    elif o in ['--aegis', '--xml']:
        format = o

if not args and not all and not testlistfile:
    sys.stderr.write("""\
runtest.py:  No tests were specified.
             List one or more tests on the command line, use the
             -f option to specify a file containing a list of tests,
             or use the -a option to find and run all tests.

""")
    sys.exit(1)

if sys.platform in ('win32', 'cygwin'):

    def whereis(file):
        pathext = [''] + string.split(os.environ['PATHEXT'], os.pathsep)
        for dir in string.split(os.environ['PATH'], os.pathsep):
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    return fext
        return None

else:

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

# See if --qmtest or --noqmtest specified
try:
    qmtest
except NameError:
    # Neither specified; find it in path.
    qmtest = None
    for q in ['qmtest', 'qmtest.py']:
        path = whereis(q)
        if path:
            # The name was found on $PATH; just execute the found name so
            # we don't have to worry about paths containing white space.
            qmtest = q
            break
    if not qmtest:
        msg = ('Warning:  found neither qmtest nor qmtest.py on $PATH;\n' +
               '\tassuming --noqmtest option.\n')
        sys.stderr.write(msg)
        sys.stderr.flush()

aegis = whereis('aegis')

if format == '--aegis' and aegis:
    change = os.popen("aesub '$c' 2>/dev/null", "r").read()
    if change:
        if sp is None:
            paths = os.popen("aesub '$sp' 2>/dev/null", "r").read()[:-1]
            sp = string.split(paths, os.pathsep)
        if spe is None:
            spe = os.popen("aesub '$spe' 2>/dev/null", "r").read()[:-1]
            spe = string.split(spe, os.pathsep)
    else:
        aegis = None

if sp is None:
    sp = []
if spe is None:
    spe = []

sp.append(builddir)
sp.append(cwd)

#
_ws = re.compile('\s')

def escape(s):
    if _ws.search(s):
        s = '"' + s + '"'
    s = string.replace(s, '\\', '\\\\')
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
        command = command_args[0]
        command_args = map(escape, command_args)
        return os.spawnv(os.P_WAIT, command, command_args)

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
    import subprocess
except ImportError:
    import popen2
    try:
        popen2.Popen3
    except AttributeError:
        class PopenExecutor(Base):
            def execute(self):
                (tochild, fromchild, childerr) = os.popen3(self.command_str)
                tochild.close()
                self.stderr = childerr.read()
                self.stdout = fromchild.read()
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
else:
    class PopenExecutor(Base):
        def execute(self):
            p = subprocess.Popen(self.command_str, shell=True)
            p.stdin.close()
            self.stdout = p.stdout.read()
            self.stdout = p.stderr.read()
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
        f.write('      <time>%.1f</time>\n' % self.test_time)
        f.write('    </test>\n')
    def footer(self, f):
        f.write('  <time>%.1f</time>\n' % self.total_time)
        f.write('  </results>\n')

format_class = {
    None        : SystemExecutor,
    '--aegis'   : Aegis,
    '--xml'     : XML,
}

Test = format_class[format]

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

    test_dir = os.path.join(builddir, 'test-%s' % package)

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

    scons_runtest_dir = builddir

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

    if not baseline or baseline == '.':
        base = cwd
    elif baseline == '-':
        # Tentative code for fetching information directly from the
        # QMTest context file.
        #
        #import qm.common
        #import qm.test.context
        #qm.rc.Load("test")
        #context = qm.test.context.Context()
        #context.Read('context')

        url = None
        svn_info =  os.popen("svn info 2>&1", "r").read()
        match = re.search('URL: (.*)', svn_info)
        if match:
            url = match.group(1)
        if not url:
            sys.stderr.write('runtest.py: could not find a URL:\n')
            sys.stderr.write(svn_info)
            sys.exit(1)
        import tempfile
        base = tempfile.mkdtemp(prefix='runtest-tmp-')

        command = 'cd %s && svn co -q %s' % (base, url)

        base = os.path.join(base, os.path.split(url)[1])
        if printcommand:
            print command
        if execute_tests:
            os.system(command)
    else:
        base = baseline

    scons_runtest_dir = base

    scons_script_dir = sd or os.path.join(base, 'src', 'script')

    scons_lib_dir = ld or os.path.join(base, 'src', 'engine')

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

os.environ['SCONS_RUNTEST_DIR'] = scons_runtest_dir
os.environ['SCONS_SCRIPT_DIR'] = scons_script_dir
os.environ['SCONS_CWD'] = cwd

os.environ['SCONS_VERSION'] = version

old_pythonpath = os.environ.get('PYTHONPATH')

# FIXME: the following is necessary to pull in half of the testing
#        harness from $srcdir/etc. Those modules should be transfered
#        to QMTest/ once we completely cut over to using that as
#        the harness, in which case this manipulation of PYTHONPATH
#        should be able to go away.
pythonpaths = [ pythonpath_dir ]

for dir in sp:
    if format == '--aegis':
        q = os.path.join(dir, 'build', 'QMTest')
    else:
        q = os.path.join(dir, 'QMTest')
    pythonpaths.append(q)

os.environ['SCONS_SOURCE_PATH_EXECUTABLE'] = string.join(spe, os.pathsep)

os.environ['PYTHONPATH'] = string.join(pythonpaths, os.pathsep)

if old_pythonpath:
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + \
                               os.pathsep + \
                               old_pythonpath

tests = []

if args:
    if spe:
        for a in args:
            if os.path.isabs(a):
                tests.extend(glob.glob(a))
            else:
                for dir in spe:
                    x = os.path.join(dir, a)
                    globs = glob.glob(x)
                    if globs:
                        tests.extend(globs)
                        break
    else:
        for a in args:
            tests.extend(glob.glob(a))
elif testlistfile:
    tests = open(testlistfile, 'r').readlines()
    tests = filter(lambda x: x[0] != '#', tests)
    tests = map(lambda x: x[:-1], tests)
elif all and not qmtest:
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

    def find_Tests_py(tdict, dirname, names):
        for n in filter(lambda n: n[-8:] == "Tests.py", names):
            tdict[os.path.join(dirname, n)] = 1
    os.path.walk('src', find_Tests_py, tdict)

    def find_py(tdict, dirname, names):
        tests = filter(lambda n: n[-3:] == ".py", names)
        try:
            excludes = open(os.path.join(dirname,".exclude_tests")).readlines()
        except (OSError, IOError):
            pass
        else:
            for exclude in excludes:
                exclude = string.split(exclude, '#' , 1)[0]
                exclude = string.strip(exclude)
                if not exclude: continue
                tests = filter(lambda n, ex = exclude: n != ex, tests)
        for n in tests:
            tdict[os.path.join(dirname, n)] = 1
    os.path.walk('test', find_py, tdict)

    if format == '--aegis' and aegis:
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

    tests = tdict.keys()
    tests.sort()

if qmtest:
    if baseline:
        aegis_result_stream = 'scons_tdb.AegisBaselineStream'
        qmr_file = 'baseline.qmr'
    else:
        aegis_result_stream = 'scons_tdb.AegisChangeStream'
        qmr_file = 'results.qmr'

    if print_times:
        aegis_result_stream = aegis_result_stream + "(print_time='1')"

    qmtest_args = [ qmtest, ]

    if format == '--aegis':
        dir = builddir
        if not os.path.isdir(dir):
            dir = cwd
        qmtest_args.extend(['-D', dir])

    qmtest_args.extend([
                'run',
                '--output %s' % qmr_file,
                '--format none',
                '--result-stream="%s"' % aegis_result_stream,
              ])

    if python:
        qmtest_args.append('--context python="%s"' % python)

    if outputfile:
        if format == '--xml':
            rsclass = 'scons_tdb.SConsXMLResultStream'
        else:
            rsclass = 'scons_tdb.AegisBatchStream'
        qof = "r'" + outputfile + "'"
        rs = '--result-stream="%s(filename=%s)"' % (rsclass, qof)
        qmtest_args.append(rs)

    if format == '--aegis':
        tests = map(lambda x: string.replace(x, cwd+os.sep, ''), tests)
    else:
        os.environ['SCONS'] = os.path.join(cwd, 'src', 'script', 'scons.py')

    cmd = string.join(qmtest_args + tests, ' ')
    if printcommand:
        sys.stdout.write(cmd + '\n')
        sys.stdout.flush()
    status = 0
    if execute_tests:
        status = os.WEXITSTATUS(os.system(cmd))
    sys.exit(status)

#try:
#    os.chdir(scons_script_dir)
#except OSError:
#    pass

tests = map(Test, tests)

class Unbuffered:
    def __init__(self, file):
        self.file = file
    def write(self, arg):
        self.file.write(arg)
        self.file.flush()
    def __getattr__(self, attr):
        return getattr(self.file, attr)

sys.stdout = Unbuffered(sys.stdout)

if list_only:
    for t in tests:
        sys.stdout.write(t.path + "\n")
    sys.exit(0)

#
if not python:
    if os.name == 'java':
        python = os.path.join(sys.prefix, 'jython')
    else:
        python = sys.executable

# time.clock() is the suggested interface for doing benchmarking timings,
# but time.time() does a better job on Linux systems, so let that be
# the non-Windows default.

if sys.platform == 'win32':
    time_func = time.clock
else:
    time_func = time.time

if print_times:
    print_time_func = lambda fmt, time: sys.stdout.write(fmt % time)
else:
    print_time_func = lambda fmt, time: None

total_start_time = time_func()
for t in tests:
    t.command_args = [python, '-tt']
    if debug:
        t.command_args.append(debug)
    t.command_args.append(t.path)
    t.command_str = string.join(map(escape, t.command_args), " ")
    if printcommand:
        sys.stdout.write(t.command_str + "\n")
    test_start_time = time_func()
    if execute_tests:
        t.execute()
    t.test_time = time_func() - test_start_time
    print_time_func("Test execution time: %.1f seconds\n", t.test_time)
if len(tests) > 0:
    tests[0].total_time = time_func() - total_start_time
    print_time_func("Total execution time for all tests: %.1f seconds\n", tests[0].total_time)

passed = filter(lambda t: t.status == 0, tests)
fail = filter(lambda t: t.status == 1, tests)
no_result = filter(lambda t: t.status == 2, tests)

if len(tests) != 1 and execute_tests:
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

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
