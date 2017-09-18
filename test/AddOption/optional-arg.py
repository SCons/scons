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
Verify use of the nargs='?' keyword argument to specify a long
command-line option with an optional argument value.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
AddOption('--install',
          nargs='?',
          dest='install',
          default='/default/directory',
          const='/called/default/directory',
          action='store',
          type='string',
          metavar='DIR',
          help='installation directory')
print(GetOption('install'))
""")

test.run('-Q -q',
         stdout="/default/directory\n")

test.run('-Q -q next-arg',
         stdout="/default/directory\n",
         status=1)

test.run('-Q -q . --install',
         stdout="/called/default/directory\n")

test.run('-Q -q . --install next-arg',
         stdout="/called/default/directory\n",
         status=1)

test.run('-Q -q . first-arg --install',
         stdout="/called/default/directory\n",
         status=1)

test.run('-Q -q . first-arg --install next-arg',
         stdout="/called/default/directory\n",
         status=1)

test.run('-Q -q . --install=/command/line/directory',
         stdout="/command/line/directory\n")

test.run('-Q -q . --install=/command/line/directory next-arg',
         stdout="/command/line/directory\n",
         status=1)

test.run('-Q -q . first-arg --install=/command/line/directory',
         stdout="/command/line/directory\n",
         status=1)

test.run('-Q -q . first-arg --install=/command/line/directory next-arg',
         stdout="/command/line/directory\n",
         status=1)


test.write('SConstruct', """\
AddOption('-X', nargs='?')
""")

expect = r"""
scons: \*\*\* option -X: nargs='\?' is incompatible with short options
File "[^"]+", line \d+, in \S+
"""

test.run(status=2, stderr=expect, match=TestSCons.match_re)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
