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
#    f) Some sources are missing

test.write('SConstruct', """
def fail_action(target = None, source = None, env = None):
    return 2

failed0  = Command(target='failed00',  source='', action=fail_action)
ok0      = Command(target='ok00',      source='', action=Touch('${TARGET}'))
prereq0  = Command(target='prereq00',  source='', action=Touch('${TARGET}'))
ignore0  = Command(target='ignore00',  source='', action=Touch('${TARGET}'))
igreq0   = Command(target='igreq00',   source='', action=Touch('${TARGET}'))
missing0 = Command(target='missing00', source='MissingSrc', action=Touch('${TARGET}'))

prev_level  = failed0 + ok0 + ignore0
prev_prereq = prereq0
prev_ignore = ignore0
prev_igreq  = igreq0

for i in range(1,20):
    
    failed = Command(target='failed%02d' % i,  source='', action=fail_action)
    ok     = Command(target='ok%02d' % i,      source='', action=Touch('${TARGET}'))
    prereq = Command(target='prereq%02d' % i,  source='', action=Touch('${TARGET}'))
    ignore = Command(target='ignore%02d' % i,  source='', action=Touch('${TARGET}'))
    igreq  = Command(target='igreq%02d' % i,   source='', action=Touch('${TARGET}'))
    missing = Command(target='missing%02d' %i, source='MissingSrc', action=Touch('${TARGET}'))

    next_level = failed + ok + ignore + igreq + missing

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
(scons: \\*\\*\\* Source `MissingSrc' not found, needed by target `missing\\d+'\\.(  Stop\\.)?\\n)\
"""

re_errors = "(" + re_error + ")+"

test.run(arguments = 'all',
         status = 2,
         stderr = "scons: *** [failed19] Error 2\n")
test.must_not_exist(test.workpath('ok'))


for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j8 all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)


for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)
    for i in range(20):
        test.must_exist(test.workpath('ok%02d' % i))
        test.must_exist(test.workpath('prereq%02d' % i))
        test.must_not_exist(test.workpath('ignore%02d' % i))
        test.must_exist(test.workpath('igreq%02d' % i))


for i in range(5):
    test.run(arguments = 'all --random',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)
    test.must_not_exist(test.workpath('ok'))

for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j8 --random all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)

for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k --random all',
             status = 2,
             stderr = re_errors,
             match=TestSCons.match_re_dotall)
    for i in range(20):
        test.must_exist(test.workpath('ok%02d' % i))
        test.must_exist(test.workpath('prereq%02d' % i))
        test.must_not_exist(test.workpath('ignore%02d' % i))
        test.must_exist(test.workpath('igreq%02d' % i))

test.pass_test()
