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
Verify the "exclude" parameter usage of the Glob() function.
  - with or without subdir
  - with or without returning strings
  - a file in a subdir is not excluded by a pattern without this subdir
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=[]) 

def concatenate(target, source, env):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())

env['BUILDERS']['Concatenate'] = Builder(action=concatenate)

env.Concatenate('fa.out', sorted(Glob('f*.in'   , exclude=['f2.in', 'f4.*']   , strings=False), key=lambda t: t.get_internal_path()))
env.Concatenate('fb.out', sorted(Glob('f*.in'   , exclude=['f2.in', 'f4.*']   , strings=True)))
env.Concatenate('fc.out', sorted(Glob('d?/f*.in', exclude=['d?/f1.*', 'f2.in'], strings=False), key=lambda t: t.get_internal_path()))
env.Concatenate('fd.out', sorted(Glob('d?/f*.in', exclude=['d?/f1.*', 'f2.in'], strings=True)))
env.Concatenate('fe.out', sorted(Glob('f*.in',    exclude='f1.in'             , strings=True)))
env.Concatenate('ff.out', sorted(Glob('f*.in',    exclude='other'             , strings=True)))
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")
test.write('f5.in', "f5.in\n")

test.subdir('d1', 'd2')
test.write(['d1', 'f1.in'], "d1/f1.in\n")
test.write(['d1', 'f2.in'], "d1/f2.in\n")
test.write(['d1', 'f3.in'], "d1/f3.in\n")
test.write(['d2', 'f1.in'], "d2/f1.in\n")
test.write(['d2', 'f2.in'], "d2/f2.in\n")
test.write(['d2', 'f3.in'], "d2/f3.in\n")

test.run(arguments = '.')

test.must_match('fa.out', "f1.in\nf3.in\nf5.in\n")
test.must_match('fb.out', "f1.in\nf3.in\nf5.in\n")
test.must_match('fc.out', "d1/f2.in\nd1/f3.in\nd2/f2.in\nd2/f3.in\n")
test.must_match('fd.out', "d1/f2.in\nd1/f3.in\nd2/f2.in\nd2/f3.in\n")
test.must_match('fe.out', "f2.in\nf3.in\nf4.in\nf5.in\n")
test.must_match('ff.out', "f1.in\nf2.in\nf3.in\nf4.in\nf5.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
