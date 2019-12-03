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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Verify that targets in a batch builder are rebuilt when the
build action changes.
"""

import os

import TestSCons

# swap slashes because on py3 on win32 inside the generated build.py
# the backslashes are getting interpretted as unicode which is
# invalid.
python = TestSCons.python.replace('\\','//')
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

build_py_contents = """\
#!/usr/bin/env %s
import sys
sep = sys.argv.index('--')
targets = sys.argv[1:sep]
sources = sys.argv[sep+1:]
for t, s in zip(targets, sources):
    with open(t, 'wb') as ofp, open(s, 'rb') as ifp:
        ofp.write(bytearray('%s\\n', 'utf-8'))
        ofp.write(ifp.read())
sys.exit(0)
"""

test.write('build.py', build_py_contents % (python, 'one'))
os.chmod(test.workpath('build.py'), 0o755)

build_py_workpath = test.workpath('build.py')

# Provide IMPLICIT_COMMAND_DEPENDENCIES=2 so we take a dependency on build.py.
# Without that, we only scan the first entry in the action string.
test.write('SConstruct', """
env = Environment(IMPLICIT_COMMAND_DEPENDENCIES=2)
env.PrependENVPath('PATHEXT', '.PY')
bb = Action(r'%(_python_)s "%(build_py_workpath)s" $CHANGED_TARGETS -- $CHANGED_SOURCES',
            batch_key=True,
            targets='CHANGED_TARGETS')
env['BUILDERS']['Batch'] = Builder(action=bb)
env.Batch('f1.out', 'f1.in')
env.Batch('f2.out', 'f2.in')
env.Batch('f3.out', 'f3.in')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")

test.run(arguments = '.')

test.must_match('f1.out', "one\nf1.in\n")
test.must_match('f2.out', "one\nf2.in\n")
test.must_match('f3.out', "one\nf3.in\n")

test.up_to_date(arguments = '.')

test.write('build.py', build_py_contents % (python, 'two'))
os.chmod(test.workpath('build.py'), 0o755)

test.not_up_to_date(arguments = '.')

test.must_match('f1.out', "two\nf1.in\n")
test.must_match('f2.out', "two\nf2.in\n")
test.must_match('f3.out', "two\nf3.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
