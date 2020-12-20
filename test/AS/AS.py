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
Verify the ability to set the $AS construction variable to a different
assembler (a wrapper we create).
"""


import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.file_fixture('mylink.py')
test.file_fixture(['fixture', 'myas.py'])

test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  AS = r'%(_python_)s myas.py',
                  CC = r'%(_python_)s myas.py')
env.Program(target = 'test1', source = 'test1.s')
env.Program(target = 'test2', source = 'test2.S')
env.Program(target = 'test3', source = 'test3.asm')
env.Program(target = 'test4', source = 'test4.ASM')
env.Program(target = 'test5', source = 'test5.spp')
env.Program(target = 'test6', source = 'test6.SPP')
""" % locals())

test.write('test1.s', r"""This is a .s file.
#as
#link
""")

test.write('test2.S', r"""This is a .S file.
#as
#link
""")

test.write('test3.asm', r"""This is a .asm file.
#as
#link
""")

test.write('test4.ASM', r"""This is a .ASM file.
#as
#link
""")

test.write('test5.spp', r"""This is a .spp file.
#as
#link
""")

test.write('test6.SPP', r"""This is a .SPP file.
#as
#link
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1' + _exe, "This is a .s file.\n")

test.must_match('test2' + _exe, "This is a .S file.\n")

test.must_match('test3' + _exe, "This is a .asm file.\n")

test.must_match('test4' + _exe, "This is a .ASM file.\n")

test.must_match('test5' + _exe, "This is a .spp file.\n")

test.must_match('test6' + _exe, "This is a .SPP file.\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
