#!/usr/bin/env python
#
# runtest.py - wrapper script for running SCons tests
#
# This script mainly exists to set PYTHONPATH to the right list of
# directories to test the SCons modules.
#
# By default, it directly uses the modules in the local tree:
# ./src/ (source files we ship) and ./etc/ (other modules we don't)
#
# When any -p option is specified, it assumes it's in a directory
# in which a build has been performed, and sets PYTHONPATH so that it
# *only* references the modules that have unpacked from the specified
# built package, to test whether the packages are good.
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
import string
import sys

all = 0
debug = ''
tests = []
printcmd = 1
package = None
scons = None
scons_exec = None

if sys.platform == 'win32':
    lib_dir = os.path.join(sys.exec_prefix, "lib")
else:
    # The hard-coded "python" here is the directory name,
    # not an executable, so it's all right.
    lib_dir = os.path.join(sys.exec_prefix, "lib", "python" + sys.version[0:3])

opts, args = getopt.getopt(sys.argv[1:], "adqp:Xx:",
			    ['all', 'debug', 'exec=', 'quiet', 'package='])

for o, a in opts:
    if o == '-a' or o == '--all': all = 1
    elif o == '-d' or o == '--debug': debug = os.path.join(lib_dir, "pdb.py")
    elif o == '-q' or o == '--quiet': printcmd = 0
    elif o == '-p' or o == '--package': package = a
    elif o == '-X': scons_exec = 1
    elif o == '-x' or o == '--exec': scons = a

cwd = os.getcwd()

if args:
    for a in args:
        tests.extend(glob.glob(os.path.abspath(a)))
elif all:
    def find_Test_py(arg, dirname, names):
	global tests
        n = filter(lambda n: n[-8:] == "Tests.py", names)
        tests.extend(map(lambda x,d=dirname: os.path.join(d, x), n))
    os.path.walk('src', find_Test_py, 0)

    def find_py(arg, dirname, names):
	global tests
        n = filter(lambda n: n[-3:] == ".py", names)
        tests.extend(map(lambda x,d=dirname: os.path.join(d, x), n))
    os.path.walk('test', find_py, 0)

    tests.sort()

if package:

    dir = {
        'deb'        : 'usr',
        'rpm'        : 'usr',
        'src-tar-gz' : '',
        'src-zip'    : '',
        'tar-gz'     : '',
        'zip'        : '',
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

    if sys.platform == 'win32':
        scons_dir = os.path.join(test_dir, dir[package], 'Scripts')
        lib_dir = os.path.join(test_dir, dir[package])
    else:
        scons_dir = os.path.join(test_dir, dir[package], 'bin')
        l = lib.get(package, 'scons')
        lib_dir = os.path.join(test_dir, dir[package], 'lib', l)

else:

    scons_dir = os.path.join(cwd, 'src', 'script')

    lib_dir = os.path.join(cwd, 'src', 'engine')

if scons:
    # Let the version of SCons that the -x option pointed to find
    # its own modules.
    os.environ['SCONS'] = scons
else:
    # Because SCons is really aggressive about finding its modules,
    # it sometimes finds SCons modules elsewhere on the system.
    # This forces SCons to use the modules that are being tested.
    os.environ['SCONS_LIB_DIR'] = lib_dir

if scons_exec:
    os.environ['SCONS_EXEC'] = '1'

os.environ['PYTHONPATH'] = lib_dir + \
                           os.pathsep + \
                           os.path.join(cwd, 'build', 'etc') + \
                           os.pathsep + \
                           os.path.join(cwd, 'etc')

os.chdir(scons_dir)

fail = []
no_result = []

for path in tests:
    if os.path.isabs(path):
	abs = path
    else:
	abs = os.path.join(cwd, path)
    cmd = string.join([sys.executable, debug, abs], " ")
    if printcmd:
	print cmd
    s = os.system(cmd)
    if s == 1 or s == 256:
        fail.append(path)
    elif s == 2 or s == 512:
        no_result.append(path)
    elif s != 0:
        print "Unexpected exit status %d" % s

if len(tests) != 1:
    if fail:
        if len(fail) == 1:
            str = "test"
        else:
            str = "%d tests" % len(fail)
        print "\nFailed the following %s:" % str
        print "\t", string.join(fail, "\n\t")
    if no_result:
        if len(no_result) == 1:
            str = "test"
        else:
            str = "%d tests" % len(no_result)
        print "\nNO RESULT from the following %s:" % str
        print "\t", string.join(no_result, "\n\t")

sys.exit(len(fail) + len(no_result))
