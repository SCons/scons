#!/usr/bin/env python
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import re
import time

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('sleep_cat.py', """\
import sys
import time
time.sleep(int(sys.argv[1]))
with open(sys.argv[2], 'wb') as fp:
    for arg in sys.argv[3:]:
        with open(arg, 'rb') as infp:
            fp.write(infp.read())
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=[],
                  PYTHON = r'%(_python_)s',
                  SLEEP_CAT = r'sleep_cat.py',
                  CATCOM = '$PYTHON $SLEEP_CAT $SECONDS $TARGET $SOURCES',
                  SECONDS = ARGUMENTS.get('SLEEP', '0'))
f1 = env.Command('f1.out', 'f1.in', '$CATCOM')
f2 = env.Command('f2.out', 'f2.in', '$CATCOM')
f3 = env.Command('f3.out', 'f3.in', '$CATCOM')
f4 = env.Command('f4.out', 'f4.in', '$CATCOM')
env.Command('output', [f1, f2, f3, f4], '$CATCOM')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")

expected_targets = ['f1.out', 'f2.out', 'f3.out', 'f4.out', 'output', '.']

# Before anything else, make sure we get valid --debug=time results
# when just running the help option.
test.run(arguments = "-h --debug=time")



def num(s, match):
    return float(re.search(match, s).group(1))

def within_tolerance(expected, actual, tolerance):
    return abs((expected-actual)/actual) <= tolerance

def get_total_time(stdout):
    return num(stdout, r'Total build time: (\d+\.\d+) seconds')

def get_sconscript_time(stdout):
    return num(stdout, r'Total SConscript file execution time: (\d+\.\d+) seconds')

def get_scons_time(stdout):
    return num(stdout, r'Total SCons execution time: (\d+\.\d+) seconds')

def get_command_time(stdout):
    return num(stdout, r'Total command execution time: (\d+\.\d+) seconds')



# Try to make our results a little more accurate and repeatable by
# measuring Python overhead executing a minimal file, and reading the
# scons.py script itself from disk so that it's already been cached.
test.write('pass.py', "pass\n")
test.read(test.program)

start_time = time.perf_counter()
test.run(program=TestSCons.python, arguments=test.workpath('pass.py'))
overhead = time.perf_counter() - start_time



start_time = time.perf_counter()
test.run(arguments = "-j1 --debug=time . SLEEP=0")
complete_time = time.perf_counter() - start_time



expected_total_time = complete_time - overhead

pattern = r'Command execution time: (.*): (\d+\.\d+) seconds'
targets = []
times = []
for target,time in re.findall(pattern, test.stdout()):
    targets.append(target)
    times.append(float(time))
expected_command_time = 0.0
for t in times:
    expected_command_time += t


stdout = test.stdout()

total_time      = get_total_time(stdout)
sconscript_time = get_sconscript_time(stdout)
scons_time      = get_scons_time(stdout)
command_time    = get_command_time(stdout)

failures = []
warnings = []

if  targets != expected_targets:
    failures.append("""\
Scons reported the targets of timing information as %(targets)s,
but the actual targets should have been %(expected_targets)s.
""" %locals())

if not within_tolerance(expected_command_time, command_time, 0.01):
    failures.append("""\
SCons -j1 reported a total command execution time of %(command_time)s,
but command execution times really totalled %(expected_command_time)s,
outside of the 1%% tolerance.
""" % locals())

added_times = sconscript_time+scons_time+command_time
if not within_tolerance(total_time, added_times, 0.01):
    failures.append("""\
SCons -j1 reported a total build time of %(total_time)s,
but the various execution times actually totalled %(added_times)s,
outside of the 1%% tolerance.
""" % locals())

if not within_tolerance(total_time, expected_total_time, 0.20):
    # This tolerance check seems empirically to work fine if there's
    # a light load on the system, but on a heavily loaded system the
    # timings get screwy and it can fail frequently.  Some obvious
    # attempts to work around the problem didn't, so just treat it as
    # a warning for now.
    warnings.append("""\
Warning:  SCons -j1 reported total build time of %(total_time)s,
but the actual measured build time was %(expected_total_time)s
(end-to-end time of %(complete_time)s less Python overhead of %(overhead)s),
outside of the 15%% tolerance.
""" % locals())

if failures or warnings:
    print('\n'.join([test.stdout()] + failures + warnings))
if failures:
    test.fail_test(1)

test.run(arguments = "--debug=time . SLEEP=0")

command_time = get_command_time(test.stdout())
if command_time != 0.0:
    print("Up-to-date run received non-zero command time of %s" % command_time)
    test.fail_test()



test.run(arguments = "-c")

test.run(arguments = "-j4 --debug=time . SLEEP=1")



stdout = test.stdout()

total_time      = get_total_time(stdout)
sconscript_time = get_sconscript_time(stdout)
scons_time      = get_scons_time(stdout)
command_time    = get_command_time(stdout)

failures = []

added_times = sconscript_time+scons_time+command_time
if not within_tolerance(total_time, added_times, 0.01):
    failures.append("""\
SCons -j4 reported a total build time of %(total_time)s,
but the various execution times actually totalled %(added_times)s,
outside of the 1%% tolerance.
""" % locals())

if failures:
    print('\n'.join([test.stdout()] + failures))
    test.fail_test(1)

test.run(arguments = "-j4 --debug=time . SLEEP=1")

command_time = get_command_time(test.stdout())
if command_time != 0.0:
    print("Up-to-date run received non-zero command time of %s" % command_time)
    test.fail_test()


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
