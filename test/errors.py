#!/usr/bin/env python

__revision__ = "test/errors.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct1', """
a ! int(2.0)
""")
test.run(arguments='-f SConstruct1')
test.fail_test(test.stderr() != """  File "SConstruct1", line 2

    a ! int(2.0)

      ^

SyntaxError: invalid syntax

""")


test.write('SConstruct2', """
raise UserError, 'Depends() require both sources and targets.'
""")
test.run(arguments='-f SConstruct2')
test.fail_test(test.stderr() != """
SCons error: Depends() require both sources and targets.
File "SConstruct2", line 2, in ?
""")


test.write('SConstruct3', """
raise InternalError, 'error inside'
""")
test.run(arguments='-f SConstruct3')
expect = r"""Traceback \((most recent call|innermost) last\):
  File ".*scons\.py", line \d+, in \?
    main\(\)
  File ".*scons\.py", line \d+, in main
    exec f in globals\(\)
  File "SConstruct3", line \d+, in \?
    raise InternalError, 'error inside'
InternalError: error inside
"""
test.fail_test(not test.match_re(test.stderr(), expect))

test.pass_test()
