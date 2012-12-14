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
# When any -p option is specified, this script assumes it's in a
# directory in which a build has been performed, and sets PYTHONPATH
# so that it *only* references the modules that have unpacked from
# the specified built package, to test whether the packages are good.
#
# Options:
#
#       -3              Run with the python -3 option,
#
#       -a              Run all tests; does a virtual 'find' for
#                       all SCons tests under the current directory.
#                       You can also specify a list of subdirectories
#                       (not available with the "--qmtest" option!). Then,
#                       only the given folders are searched for test files.
#
#       -d              Debug.  Runs the script under the Python
#                       debugger (pdb.py) so you don't have to
#                       muck with PYTHONPATH yourself.
#
#       -e              Starts the script in external mode, for
#                       testing separate Tools and packages.
#
#       -f file         Only execute the tests listed in the specified
#                       file.
#
#       -h              Print the help and exit.
#
#       -k              Suppress printing of count and percent progress for
#                       the single tests.
#
#       -l              List available tests and exit.
#
#       -n              No execute, just print command lines.
#
#       -o file         Print test results to the specified file.
#                       The --xml option specifies the
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
#       -s              Short progress.  Prints only the command line
#                       and a percentage value, based on the total and
#                       current number of tests.
#                       All stdout and stderr messages get suppressed (this
#                       does only work with subprocess though)!
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

import getopt
import glob
import os
import re
import stat
import sys
import time

cwd = os.getcwd()

all = 0
baseline = 0
builddir = os.path.join(cwd, 'build')
external = 0
debug = ''
execute_tests = 1
format = None
list_only = None
printcommand = 1
package = None
print_passed_summary = None
python3incompatibilities = None
scons = None
scons_exec = None
outputfile = None
testlistfile = None
version = ''
print_times = None
python = None
sp = []
print_progress = 1
suppress_stdout = False
suppress_stderr = False
allow_pipe_files = True

helpstr = """\
Usage: runtest.py [OPTIONS] [TEST ...]
Options:
  -3                          Warn about Python 3.x incompatibilities.
  -a, --all                   Run all tests.
  -b BASE, --baseline BASE    Run test scripts against baseline BASE.
  --builddir DIR              Directory in which packages were built.
  -d, --debug                 Run test scripts under the Python debugger.
  -e, --external              Run the script in external mode (for testing separate Tools)
  -f FILE, --file FILE        Run tests in specified FILE.
  -h, --help                  Print this message and exit.
  -k, --no-progress           Suppress count and percent progress messages.
  -l, --list                  List available tests and exit.
  -n, --no-exec               No execute, just print command lines.
  --noqmtest                  Execute tests directly, not using QMTest.
  --nopipefiles               Doesn't use the "file pipe" workaround for subprocess.Popen()
                              for starting tests. WARNING: Only use this when too much file
                              traffic is giving you trouble AND you can be sure that none of
                              your tests create output that exceed 65K chars! You might
                              run into some deadlocks else.
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
  -s, --short-progress        Short progress, prints only the command line
                              and a percentage value, based on the total and
                              current number of tests.
  -t, --time                  Print test execution time.
  -v version                  Specify the SCons version.
  --verbose=LEVEL             Set verbose level: 1 = print executed commands,
                                2 = print commands and non-zero output,
                                3 = print commands and all output.
  -X                          Test script is executable, don't feed to Python.
  -x SCRIPT, --exec SCRIPT    Test SCRIPT.
  --xml                       Print results in SCons XML format.

Environment Variables:

  PRESERVE, PRESERVE_{PASS,FAIL,NO_RESULT}: preserve test subdirs
  TESTCMD_VERBOSE: turn on verbosity in TestCommand
"""

opts, args = getopt.getopt(sys.argv[1:], "3ab:def:hklno:P:p:qsv:Xx:t",
                            ['all', 'baseline=', 'builddir=',
                             'debug', 'external', 'file=', 'help', 'no-progress',
                             'list', 'no-exec', 'noqmtest', 'nopipefiles', 'output=',
                             'package=', 'passed', 'python=', 'qmtest',
                             'quiet', 'short-progress', 'time',
                             'version=', 'exec=',
                             'verbose=', 'xml'])

for o, a in opts:
    if o in ['-3']:
        python3incompatibilities = 1
    elif o in ['-a', '--all']:
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
    elif o in ['-e', '--external']:
        external = 1
    elif o in ['-f', '--file']:
        if not os.path.isabs(a):
            a = os.path.join(cwd, a)
        testlistfile = a
    elif o in ['-h', '--help']:
        print helpstr
        sys.exit(0)
    elif o in ['-k', '--no-progress']:
        print_progress = 0
    elif o in ['-l', '--list']:
        list_only = 1
    elif o in ['-n', '--no-exec']:
        execute_tests = None
    elif o in ['--noqmtest']:
        qmtest = None
    elif o in ['--nopipefiles']:
        allow_pipe_files = False
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
        suppress_stdout = True
        suppress_stderr = True        
    elif o in ['-s', '--short-progress']:
        print_progress = 1
        suppress_stdout = True
        suppress_stderr = True
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
    elif o in ['--xml']:
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
        pathext = [''] + os.environ['PATHEXT'].split(os.pathsep)
        for dir in os.environ['PATH'].split(os.pathsep):
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    return fext
        return None

else:

    def whereis(file):
        for dir in os.environ['PATH'].split(os.pathsep):
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
    qmtest = None

sp.append(builddir)
sp.append(cwd)

#
_ws = re.compile('\s')

def escape(s):
    if _ws.search(s):
        s = '"' + s + '"'
    s = s.replace('\\', '\\\\')
    return s


import subprocess

if not suppress_stdout and not suppress_stderr:
    # Without any output suppressed, we let the subprocess
    # write its stuff freely to stdout/stderr.
    def spawn_it(command_args):
        p = subprocess.Popen(' '.join(command_args),
                             shell=True)
        return (None, None, p.wait())
else:
    # Else, we catch the output of both pipes...
    if allow_pipe_files:
        # The subprocess.Popen() suffers from a well-known
        # problem. Data for stdout/stderr is read into a 
        # memory buffer of fixed size, 65K which is not very much.
        # When it fills up, it simply stops letting the child process
        # write to it. The child will then sit and patiently wait to
        # be able to write the rest of its output. Hang! 
        # In order to work around this, we follow a suggestion
        # by Anders Pearson in
        #   http://http://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/
        # and pass temp file objects to Popen() instead of the ubiquitous
        # subprocess.PIPE. 
        def spawn_it(command_args):
            # Create temporary files
            import tempfile
            tmp_stdout = tempfile.TemporaryFile(mode='w+t')
            tmp_stderr = tempfile.TemporaryFile(mode='w+t')
            # Start subprocess...
            p = subprocess.Popen(' '.join(command_args),
                                 stdout=tmp_stdout,
                                 stderr=tmp_stderr,
                                 shell=True)
            # ... and wait for it to finish.
            ret = p.wait()
            
            try:
                # Rewind to start of files
                tmp_stdout.seek(0)
                tmp_stderr.seek(0)
                # Read output
                spawned_stdout = tmp_stdout.read()
                spawned_stderr = tmp_stderr.read()
            finally:
                # Remove temp files by closing them
                tmp_stdout.close()
                tmp_stderr.close()
                
            # Return values
            return (spawned_stderr, spawned_stdout, ret)
        
    else:
        # We get here only if the user gave the '--nopipefiles'
        # option, meaning the "temp file" approach for
        # subprocess.communicate() above shouldn't be used.
        # He hopefully knows what he's doing, but again we have a
        # potential deadlock situation in the following code:
        #   If the subprocess writes a lot of data to its stderr,
        #   the pipe will fill up (nobody's reading it yet) and the
        #   subprocess will wait for someone to read it. 
        #   But the parent process is trying to read from stdin
        #   (but the subprocess isn't writing anything there).  
        #   Hence a deadlock.
        # Be dragons here! Better don't use this!
        def spawn_it(command_args):
            p = subprocess.Popen(' '.join(command_args),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            spawned_stdout = p.stdout.read()
            spawned_stderr = p.stderr.read()
            return (spawned_stderr, spawned_stdout, p.wait())

class Base(object):
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
        self.stderr, self.stdout, s = spawn_it(self.command_args)
        self.status = s
        if s < 0 or s > 2:
            sys.stdout.write("Unexpected exit status %d\n" % s)

class PopenExecutor(Base):
    # For an explanation of the following 'if ... else'
    # and the 'allow_pipe_files' option, please check out the
    # definition of spawn_it() above.
    if allow_pipe_files:
        def execute(self):
            # Create temporary files
            import tempfile
            tmp_stdout = tempfile.TemporaryFile(mode='w+t')
            tmp_stderr = tempfile.TemporaryFile(mode='w+t')
            # Start subprocess...
            p = subprocess.Popen(self.command_str,
                                 stdout=tmp_stdout,
                                 stderr=tmp_stderr,
                                 shell=True)
            # ... and wait for it to finish.
            self.status = p.wait()
            
            try:
                # Rewind to start of files
                tmp_stdout.seek(0)
                tmp_stderr.seek(0)
                # Read output
                self.stdout = tmp_stdout.read()
                self.stderr = tmp_stderr.read()
            finally:
                # Remove temp files by closing them
                tmp_stdout.close()
                tmp_stderr.close()
    else:        
        def execute(self):
            p = subprocess.Popen(self.command_str,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            self.stdout = p.stdout.read()
            self.stderr = p.stderr.read()
            self.status = p.wait()

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

    if package not in dir:
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

    if not external:
        scons_script_dir = sd or os.path.join(base, 'src', 'script')
        scons_lib_dir = ld or os.path.join(base, 'src', 'engine')
    else:
        scons_script_dir = sd or ''
        scons_lib_dir = ld or ''

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

if external:
    os.environ['SCONS_EXTERNAL_TEST'] = '1'

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

# Add path of the QMTest folder to PYTHONPATH
scriptpath = os.path.dirname(os.path.realpath(__file__))
pythonpaths.append(os.path.join(scriptpath, 'QMTest'))

os.environ['PYTHONPATH'] = os.pathsep.join(pythonpaths)

if old_pythonpath:
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + \
                               os.pathsep + \
                               old_pythonpath

if python3incompatibilities:
    os.environ['SCONS_HORRIBLE_REGRESSION_TEST_HACK'] = '1'

tests = []

def find_Tests_py(directory):
    result = []
    for dirpath, dirnames, filenames in os.walk(directory):
        # Skip folders containing a sconstest.skip file
        if 'sconstest.skip' in filenames:
            continue
        for fname in filenames:
            if fname.endswith("Tests.py"):
                result.append(os.path.join(dirpath, fname))
    return sorted(result)

def find_py(directory):
    result = []
    for dirpath, dirnames, filenames in os.walk(directory):
        # Skip folders containing a sconstest.skip file
        if 'sconstest.skip' in filenames:
            continue
        try:
            exclude_fp = open(os.path.join(dirpath, ".exclude_tests"))
        except EnvironmentError:
            excludes = []
        else:
            excludes = [ e.split('#', 1)[0].strip()
                         for e in exclude_fp.readlines() ]
        for fname in filenames:
            if fname.endswith(".py") and fname not in excludes:
                result.append(os.path.join(dirpath, fname))
    return sorted(result)

if args:
    for a in args:
        for path in glob.glob(a):
            if os.path.isdir(path):
                if path[:3] == 'src':
                    tests.extend(find_Tests_py(path))

                elif path[:4] == 'test':
                    tests.extend(find_py(path))
            else:
                tests.append(path)
elif testlistfile:
    tests = open(testlistfile, 'r').readlines()
    tests = [x for x in tests if x[0] != '#']
    tests = [x[:-1] for x in tests]
    tests = [x.strip() for x in tests]
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
    tests.extend(find_Tests_py('src'))
    tests.extend(find_py('test'))
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

    os.environ['SCONS'] = os.path.join(cwd, 'src', 'script', 'scons.py')

    cmd = ' '.join(qmtest_args + tests)
    if printcommand:
        sys.stdout.write(cmd + '\n')
        sys.stdout.flush()
    status = 0
    if execute_tests:
        status = os.system(cmd)
        try:
            wexitstatus = os.WEXITSTATUS
        except AttributeError:
            pass
        else:
            status = wexitstatus(status)
    sys.exit(status)

#try:
#    os.chdir(scons_script_dir)
#except OSError:
#    pass

tests = [Test(t) for t in tests]

class Unbuffered(object):
    def __init__(self, file):
        self.file = file
        self.softspace = 0  ## backward compatibility; not supported in Py3k
    def write(self, arg):
        self.file.write(arg)
        self.file.flush()
    def __getattr__(self, attr):
        return getattr(self.file, attr)

sys.stdout = Unbuffered(sys.stdout)
sys.stderr = Unbuffered(sys.stderr)

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
os.environ["python_executable"] = python

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
total_num_tests = len(tests)
for idx,t in enumerate(tests):
    command_args = ['-tt']
    if python3incompatibilities:
        command_args.append('-3')
    if debug:
        command_args.append(debug)
    command_args.append(t.path)
    t.command_args = [python] + command_args
    t.command_str = " ".join([escape(python)] + command_args)
    if printcommand:
        if print_progress:
            sys.stdout.write("%d/%d (%.2f%s) %s\n" % (idx+1, total_num_tests,
                                                      float(idx+1)*100.0/float(total_num_tests),
                                                      '%',
                                                      t.command_str))
        else:
            sys.stdout.write(t.command_str + "\n")
    head, tail = os.path.split(t.abspath)
    if head:
        os.environ['PYTHON_SCRIPT_DIR'] = head
    else:
        os.environ['PYTHON_SCRIPT_DIR'] = ''     
    test_start_time = time_func()
    if execute_tests:
        t.execute()
        if not suppress_stdout and t.stdout:
            print t.stdout
        if not suppress_stderr and t.stderr:
            print t.stderr

    t.test_time = time_func() - test_start_time
    print_time_func("Test execution time: %.1f seconds\n", t.test_time)
if len(tests) > 0:
    tests[0].total_time = time_func() - total_start_time
    print_time_func("Total execution time for all tests: %.1f seconds\n", tests[0].total_time)

passed = [t for t in tests if t.status == 0]
fail = [t for t in tests if t.status == 1]
no_result = [t for t in tests if t.status == 2]

if len(tests) != 1 and execute_tests:
    if passed and print_passed_summary:
        if len(passed) == 1:
            sys.stdout.write("\nPassed the following test:\n")
        else:
            sys.stdout.write("\nPassed the following %d tests:\n" % len(passed))
        paths = [x.path for x in passed]
        sys.stdout.write("\t" + "\n\t".join(paths) + "\n")
    if fail:
        if len(fail) == 1:
            sys.stdout.write("\nFailed the following test:\n")
        else:
            sys.stdout.write("\nFailed the following %d tests:\n" % len(fail))
        paths = [x.path for x in fail]
        sys.stdout.write("\t" + "\n\t".join(paths) + "\n")
    if no_result:
        if len(no_result) == 1:
            sys.stdout.write("\nNO RESULT from the following test:\n")
        else:
            sys.stdout.write("\nNO RESULT from the following %d tests:\n" % len(no_result))
        paths = [x.path for x in no_result]
        sys.stdout.write("\t" + "\n\t".join(paths) + "\n")

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

if len(fail):
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
