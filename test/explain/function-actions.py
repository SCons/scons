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
Verify that --debug=explain correctly handles changes to actions
that contain a list of function Actions.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('SConstruct', """\
DefaultEnvironment(tools=[])
import shutil

env = Environment(tools=[])
mode = int(ARGUMENTS.get('mode'))
if mode:
    def DifferentCopy(target, source, env):
        tgt = str(target[0])
        src = str(source[0])
        shutil.copy(src, tgt)
    def AltCopyStage2(target, source, env):
        pass
    MyCopy = Builder(action = [DifferentCopy, AltCopyStage2])

    def ChangingCopy(target, source, env):
        tgt = str(target[0])
        src = str(source[0])
        shutil.copy(src, tgt)
    ChangingCopy = Builder(action = ChangingCopy)
else:
    MyCopy = Builder(action = Copy('$TARGET', '$SOURCE'))
    def ChangingCopy(target, source, env):
        tgt = str(target[0].get_abspath())
        src = str(source[0].get_abspath())
        shutil.copy(src, tgt)
    ChangingCopy = Builder(action = ChangingCopy)

env['BUILDERS']['MyCopy'] = MyCopy
env['BUILDERS']['ChangingCopy'] = ChangingCopy

env.MyCopy('f1.out', 'f1.in')
env.ChangingCopy('f2.out', 'f2.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")

test.run(arguments = "mode=0 .")

test.must_match('f1.out', "f1.in\n")
test.must_match('f2.out', "f2.in\n")

test.run(arguments = "--debug=explain mode=1 .",
         stdout = test.wrap_stdout("""\
scons: rebuilding `f1.out' because the build action changed:
               old: Copy("$TARGET", "$SOURCE")
               new: DifferentCopy(target, source, env)
                    AltCopyStage2(target, source, env)
DifferentCopy(["f1.out"], ["f1.in"])
AltCopyStage2(["f1.out"], ["f1.in"])
scons: rebuilding `f2.out' because the contents of the build action changed
               action: ChangingCopy(target, source, env)
ChangingCopy(["f2.out"], ["f2.in"])
"""))



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
