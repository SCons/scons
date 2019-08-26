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
Verify operation of Visual C/C++ batch builds.

This uses a fake compiler and linker script, fake command lines, and
explicit suffix settings so that the test should work when run on any
platform.
"""

import os
import TestSCons

test = TestSCons.TestSCons()

_python_ = TestSCons._python_

test.write('fake_cl.py', """\
import os
import sys
input_files = sys.argv[2:]
if sys.argv[1][-1] in (os.sep, '\\\\'):
    # The output (/Fo) argument ends with a backslash, indicating an
    # output directory.  We accept ending with a slash as well so this
    # test runs on non-Windows systems.  Strip either character and
    # record the directory name.
    sys.argv[1] = sys.argv[1][:-1]
    dir = sys.argv[1][3:]
else:
    dir = None
    output = sys.argv[1][3:]
# Delay writing the .log output until here so any trailing slash or
# backslash has been stripped, and the output comparisons later in this
# script don't have to account for the difference.
with open('fake_cl.log', 'a') as ofp:
    ofp.write(" ".join(sys.argv[1:]) + '\\n')
for infile in input_files:
    if dir:
        outfile = os.path.join(dir, infile.replace('.c', '.obj'))
    else:
        outfile = output
    with open(outfile, 'w') as ofp:
        with open(infile, 'r') as ifp:
            ofp.write(ifp.read())
""")

test.write('fake_link.py', """\
import sys
with open(sys.argv[1], 'w') as ofp:
    for infile in sys.argv[2:]:
        with open(infile, 'r') as ifp:
            ofp.write(ifp.read())
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
cccom = r'%(_python_)s fake_cl.py $_MSVC_OUTPUT_FLAG $CHANGED_SOURCES'
linkcom = r'%(_python_)s fake_link.py ${TARGET.windows} $SOURCES'
env = Environment(tools=['msvc', 'mslink'],
                  CCCOM=cccom, 
                  LINKCOM=linkcom,
                  PROGSUFFIX='.exe',
                  OBJSUFFIX='.obj',
                  MSVC_BATCH=ARGUMENTS.get('MSVC_BATCH'))
p = env.Object('prog.c')
f1 = env.Object('f1.c')
f2 = env.Object('f2.c')
env.Program(p + f1 + f2)
""" % locals())

test.write('prog.c', "prog.c\n")
test.write('f1.c', "f1.c\n")
test.write('f2.c', "f2.c\n")



test.run(arguments = 'MSVC_BATCH=1 .')

test.must_match('prog.exe', "prog.c\nf1.c\nf2.c\n", mode='r')
test.must_match('fake_cl.log', """\
/Fo.%s prog.c f1.c f2.c
"""%os.sep, mode='r')

test.up_to_date(options = 'MSVC_BATCH=1', arguments = '.')



test.write('f1.c', "f1.c 2\n")

test.run(arguments = 'MSVC_BATCH=1 .')

test.must_match('prog.exe', "prog.c\nf1.c 2\nf2.c\n", mode='r')
test.must_match('fake_cl.log', """\
/Fo.%s prog.c f1.c f2.c
/Fo.%s f1.c
"""%(os.sep, os.sep), mode='r')

test.up_to_date(options = 'MSVC_BATCH=1', arguments = '.')



test.run(arguments = '-c .')

test.unlink('fake_cl.log')



test.run(arguments = '. MSVC_BATCH=0')

test.must_match('prog.exe', "prog.c\nf1.c 2\nf2.c\n", mode='r')
test.must_match('fake_cl.log', """\
/Fof1.obj f1.c
/Fof2.obj f2.c
/Foprog.obj prog.c
""", mode='r')

test.run(arguments = '-c .')
test.unlink('fake_cl.log')


test.run(arguments = '. MSVC_BATCH=False')

test.must_match('prog.exe', "prog.c\nf1.c 2\nf2.c\n", mode='r')
test.must_match('fake_cl.log', """\
/Fof1.obj f1.c
/Fof2.obj f2.c
/Foprog.obj prog.c
""", mode='r')



test.write('f1.c', "f1.c 3\n")

test.run(arguments = '. MSVC_BATCH=0')

test.must_match('prog.exe', "prog.c\nf1.c 3\nf2.c\n", mode='r')
test.must_match('fake_cl.log', """\
/Fof1.obj f1.c
/Fof2.obj f2.c
/Foprog.obj prog.c
/Fof1.obj f1.c
""", mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
