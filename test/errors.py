#!/usr/bin/env python

__revision__ = "test/t0003.py __REVISION__ __DATE__ __DEVELOPER__"

from TestCmd import TestCmd

test = TestCmd(program = 'scons.py',
               workdir = '',
               interpreter = 'python')

test.write('SConstruct1', """
a ! int(2.0)
""")
test.run(chdir = '.', arguments='-f SConstruct1')
test.fail_test(test.stderr() != """  File "SConstruct1", line 2

    a ! int(2.0)

      ^

SyntaxError: invalid syntax

""")


test.write('SConstruct2', """
raise UserError, 'Depends() require both sources and targets.'
""")
test.run(chdir = '.', arguments='-f SConstruct2')
test.fail_test(test.stderr() != """
SCons error: Depends() require both sources and targets.
File "SConstruct2", line 2, in ?
""")


import os
sconspath = os.path.join(os.getcwd(), 'scons.py')

test.write('SConstruct3', """
raise InternalError, 'error inside'
""")
test.run(chdir = '.', arguments='-f SConstruct3')
expect = r"""Traceback \((most recent call|innermost) last\):
  File "%s", line 163, in \?
    main\(\)
  File "%s", line 153, in main
    execfile\(file\)
  File "SConstruct3", line 2, in \?
    raise InternalError, 'error inside'
InternalError: error inside
""" % (sconspath, sconspath)
test.fail_test(not test.match_re(test.stderr(), expect))

test.pass_test()
