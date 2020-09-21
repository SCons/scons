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

"""
Verify that use of --implicit-cache with the Python Value Nodes
used by the Configure subsystem generate the same .sconsign file
and don't cause it to grow without limit.

This was reported as issue 2033 in the tigris.org bug tracker, by the
Ardour project.  Prior to 0.98.4, the Value implementation would actually
return the repr() of its value as the str().  This was done because
it made saving a Value in a file and reading it back in kind of work,
because a print a string Value into a file (for example) would in fact
put quotes around it and be assignable in that file.

The problem is that this would get stored in a .sconsign file as its
repr(), with the specific problem being that Values with embedded newlines
would get stored as strings containing backslash+n digraphs *and* the
quotes at beginning and end of the string::

    '\n#include <math.h>\n\n': {<.sconsign info>}

Then, when we read that back in from the .sconsign file, we would store
that repr() as a string Value itself, escaping the backslashes and
including the quotes, so when we stored it the second time it would end
up looking like:

    "'\\n#include <math.h>\\n\\n'": {<.sconsign info>}

Every time that we would read this value and store it again (because
something else changed in the .sconf_temp directory), the string would
get longer and longer until it blew out the users's memory.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSConsign

test = TestSConsign.TestSConsign()

test.write('SConstruct', """
env = Environment(CPPPATH=['.'])
conf = Configure(env)
conf.CheckHeader( 'math.h' )
if ARGUMENTS.get('USE_FOO'):
    conf.CheckHeader( 'foo.h' )
env = conf.Finish()
""")

test.write('foo.h', "#define FOO 1\n")

# First run:  Have the configure subsystem only look for math.h, and
# squirrel away the .sconsign info for the conftest_0.c file that's
# generated from the Python Value Node that we're using for our test.

test.run(arguments = '.')

test.run_sconsign('-d .sconf_temp -e conftest_5a3fa36d51dd2a28d521d6cc0e2e1d04_0.c --raw .sconsign.dblite')
old_sconsign_dblite = test.stdout()

# Second run:  Have the configure subsystem also look for foo.h, so
# that there's a change in the .sconf_temp directory that will cause its
# .sconsign information to get rewritten from disk.  Squirrel away the
# .sconsign info for the conftest_0.c file.  The now-fixed bug would show
# up because the entry would change with the additional string-escaping
# described above.  The now-correct behavior is that the re-stored value
# for conftest_0.c doesn't change.

test.run(arguments = '--implicit-cache USE_FOO=1 .')

test.run_sconsign('-d .sconf_temp -e conftest_5a3fa36d51dd2a28d521d6cc0e2e1d04_0.c --raw .sconsign.dblite')
new_sconsign_dblite = test.stdout()

if old_sconsign_dblite != new_sconsign_dblite:
    print(".sconsign.dblite did not match:")
    print("FIRST RUN ==========")
    print(old_sconsign_dblite)
    print("SECOND RUN ==========")
    print(new_sconsign_dblite)
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
