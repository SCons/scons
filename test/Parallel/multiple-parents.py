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
#

"""
Verify that a failed build action with -j works as expected.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys

import TestSCons

_python_ = TestSCons._python_

try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

# Test that we can handle parallel builds with a dependency graph
# where:
#    a) Some nodes have multiple parents
#    b) Some targets fail building
#    c) Some targets succeed building
#    d) Some children are ignored
#    e) Some children are pre-requesites
#    f) Some children have side-effects
#    g) Some sources are missing
#    h) Builds that are interrupted

test.write('SConstruct', """
vars = Variables()
vars.Add( BoolVariable('interrupt', 'Interrupt the build.', 0 ) )
varEnv = Environment(variables=vars)

def fail_action(target = None, source = None, env = None):
    return 2

def simulate_keyboard_interrupt(target = None, source = None, env = None):
    # Directly invoked the SIGINT handler to simulate a
    # KeyboardInterrupt. This hack is necessary because there is no
    # easy way to get access to the current Job/Taskmaster object.
    import signal
    handler = signal.getsignal(signal.SIGINT)
    handler(signal.SIGINT, None)
    return 0

interrupt = Command(target='interrupt',  source='', action=simulate_keyboard_interrupt)

touch0 = Touch('${TARGETS[0]}')
touch1 = Touch('${TARGETS[1]}')
touch2 = Touch('${TARGETS[2]}')

failed0  = Command(target='failed00',  source='', action=fail_action)
ok0      = Command(target=['ok00a', 'ok00b', 'ok00c'], 
                   source='', 
                   action=[touch0, touch1, touch2])
prereq0  = Command(target='prereq00',  source='', action=touch0)
ignore0  = Command(target='ignore00',  source='', action=touch0)
igreq0   = Command(target='igreq00',   source='', action=touch0)
missing0 = Command(target='missing00', source='MissingSrc', action=touch0)
withSE0  = Command(target=['withSE00a', 'withSE00b', 'withSE00c'], 
                   source='', 
                   action=[touch0, touch1, touch2, Touch('side_effect')])
SideEffect('side_effect', withSE0) 

prev_level  = failed0 + ok0 + ignore0 + missing0 + withSE0
prev_prereq = prereq0
prev_ignore = ignore0
prev_igreq  = igreq0

if varEnv['interrupt']:
    prev_level = prev_level + interrupt

for i in range(1,20):
    
    failed = Command(target='failed%02d' % i,  source='', action=fail_action)
    ok     = Command(target=['ok%02da' % i, 'ok%02db' % i, 'ok%02dc' % i], 
                     source='',
                     action=[touch0, touch1, touch2])
    prereq = Command(target='prereq%02d' % i,  source='', action=touch0)
    ignore = Command(target='ignore%02d' % i,  source='', action=touch0)
    igreq  = Command(target='igreq%02d' % i,   source='', action=touch0)
    missing = Command(target='missing%02d' %i, source='MissingSrc', action=touch0)
    withSE  = Command(target=['withSE%02da' % i, 'withSE%02db' % i, 'withSE%02dc' % i], 
                       source='', 
                       action=[touch0, touch1, touch2, Touch('side_effect')])
    SideEffect('side_effect', withSE) 

    next_level = failed + ok + ignore + igreq + missing + withSE

    for j in range(1,10):
        a = Alias('a%02d%02d' % (i,j), prev_level)

        Requires(a, prev_prereq)
        Ignore(a, prev_ignore)

        Requires(a, prev_igreq)
        Ignore(a, prev_igreq)

        next_level = next_level + a

    prev_level  = next_level
    prev_prereq = prereq
    prev_ignore = ignore
    prev_igreq  = igreq

all = Alias('all', prev_level)

Requires(all, prev_prereq)
Ignore(all,  prev_ignore)

Requires(all, prev_igreq)
Ignore(all,  prev_igreq)

Default(all)
""")

re_error = """\
(scons: \\*\\*\\* \\[failed\\d+] Error 2\\n)|\
(scons: \\*\\*\\* \\[missing\\d+] Source `MissingSrc' not found, needed by target `missing\\d+'\\.(  Stop\\.)?\\n)|\
(scons: \\*\\*\\* \\[\\w+] Build interrupted\\.\\n)|\
(scons: Build interrupted\\.\\n)\
"""

re_errors = "(" + re_error + ")+"

# Make the script chatty so lack of output doesn't fool buildbot into
# thinking it's hung.

sys.stdout.write('Initial build.\n')
test.run(arguments = 'all',
         status = 2,
         stderr = "scons: *** [failed19] Error 2\n")
test.must_not_exist(test.workpath('side_effect'))
for i in range(20):
    test.must_not_exist(test.workpath('ok%02da' % i))
    test.must_not_exist(test.workpath('ok%02db' % i))
    test.must_not_exist(test.workpath('ok%02dc' % i))
    test.must_not_exist(test.workpath('ignore%02d' % i))
    test.must_not_exist(test.workpath('withSE%02da' % i))
    test.must_not_exist(test.workpath('withSE%02db' % i))
    test.must_not_exist(test.workpath('withSE%02dc' % i))

# prereq19 and igreq19 will exist because, as prerequisites,
# they are now evaluated *before* the direct children of the Node.
for i in range(19):
    test.must_not_exist(test.workpath('prereq%02d' % i))
    test.must_not_exist(test.workpath('igreq%02d' % i))
test.must_exist(test.workpath('prereq19'))
test.must_exist(test.workpath('igreq19'))


sys.stdout.write('-j8 all\n')
for i in range(3):
    test.run(arguments = '-c all')

    test.run(arguments = '-j8 all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)


sys.stdout.write('-j 8 -k all\n')
for i in range(3):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)
    test.must_exist(test.workpath('side_effect'))
    for i in range(20):
        test.must_exist(test.workpath('ok%02da' % i))
        test.must_exist(test.workpath('ok%02db' % i))
        test.must_exist(test.workpath('ok%02dc' % i))
        test.must_exist(test.workpath('prereq%02d' % i))
        test.must_not_exist(test.workpath('ignore%02d' % i))
        test.must_exist(test.workpath('igreq%02d' % i))
        test.must_exist(test.workpath('withSE%02da' % i))
        test.must_exist(test.workpath('withSE%02db' % i))
        test.must_exist(test.workpath('withSE%02dc' % i))


sys.stdout.write('all --random\n')
for i in range(3):
    test.run(arguments = 'all --random',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)


sys.stdout.write('-j8 --random all\n')
for i in range(3):
    test.run(arguments = '-c all')

    test.run(arguments = '-j8 --random all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)


sys.stdout.write('-j8 -k --random all\n')
for i in range(3):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k --random all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)
    test.must_exist(test.workpath('side_effect'))
    for i in range(20):
        test.must_exist(test.workpath('ok%02da' % i))
        test.must_exist(test.workpath('ok%02db' % i))
        test.must_exist(test.workpath('ok%02dc' % i))
        test.must_exist(test.workpath('prereq%02d' % i))
        test.must_not_exist(test.workpath('ignore%02d' % i))
        test.must_exist(test.workpath('igreq%02d' % i))
        test.must_exist(test.workpath('withSE%02da' % i))
        test.must_exist(test.workpath('withSE%02db' % i))
        test.must_exist(test.workpath('withSE%02dc' % i))


sys.stdout.write('-j8 -k --random all interupt=yes\n')
for i in range(3):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k --random interrupt=yes all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
