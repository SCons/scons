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

import sys
import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments='-Q --tree=prune',
         stdout="""scons: `.' is up to date.
+-.
  +-SConstruct
""")

test.run(arguments='-Q --tree=foofoo',
         stderr="""usage: scons [OPTION] [TARGET] ...

SCons Error: `foofoo' is not a valid --tree option type, try:
    all, derived, prune, status, linedraw
""",
         status=2)


# Test that unicode characters can be printed (escaped) with the --tree option
test.write('SConstruct', """\
env = Environment()
env.Tool("textfile")
name = "français"
env.Textfile("Foo", name)
""")

uchar = chr(0xe7)

expected = """Creating 'Foo.txt'
+-.
  +-Foo.txt
  | +-fran%sais
  +-SConstruct
""" % uchar

test.run(arguments='-Q --tree=all', stdout=expected, status=0)

# Test the "linedraw" option: same basic test as previous.
# With "--tree=linedraw" must default to "all", and use line-drawing chars.
test.write('SConstruct', """\
env = Environment()
env.Tool("textfile")
name = "français"
env.Textfile("LineDraw", name)
""")

expected = """Creating 'LineDraw.txt'
└─┬.
  ├─┬LineDraw.txt
  │ └─fran%sais
  └─SConstruct
""" % uchar


test.run(arguments='-Q --tree=linedraw', stdout=expected, status=0)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
