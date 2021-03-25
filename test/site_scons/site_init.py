#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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
Verify various aspects of the handling of site_init.py.

And more ..
"""

import TestSCons
import sys
import os.path

test = TestSCons.TestSCons()

test.subdir('site_scons')


def _test_metadata():
    """Test site_init's module metadata.

    The following special variables should be predefined: __doc__,
    __file__ and __name__. No special variables should be transferred from
    SCons.Script.
    """
    test.write(['site_scons', 'site_init.py'], """\
import os.path
import re

special = []
for x in list(globals().keys()):
    if re.match("__[^_]+__", x):
        if x in ("__builtins__", "__package__",):
            # Ignore certain keywords, as they are known to be added by Python
            continue
        special.append(x)

print(sorted(special))
print(__doc__)
print(os.path.realpath(__file__))
print(__name__)
""")

    test.write('SConstruct', "\n")
    test.run(arguments = '-Q .',
             stdout = """\
['__doc__', '__file__', '__name__']
None
%s
site_init
scons: `.' is up to date.
""" % (os.path.realpath(os.path.join('site_scons', 'site_init.py')),))

_test_metadata()


"""
Verify site_scons/site_init.py file can define a tool, and it shows up
automatically in the SCons.Script namespace.
"""

if sys.platform == 'win32':
    cat_cmd='type'
else:
    cat_cmd='cat'

test.write(['site_scons', 'site_init.py'], """
def TOOL_FOO(env):
      env['FOO'] = '%s'
      bld = Builder(action = '$FOO ${SOURCE} > ${TARGET}',
				      suffix = '.tgt')
      env.Append(BUILDERS = {'Foo' : bld})

"""%cat_cmd)

test.write('SConstruct', """
e=Environment(tools=['default', TOOL_FOO])
e.Foo(target='foo.out', source='SConstruct')
""")

test.run(arguments = '-Q .',
         stdout = """%s SConstruct > foo.out\n"""%cat_cmd)


"""
Test errors in site_scons/site_init.py.
"""

test = TestSCons.TestSCons()

test.subdir('site_scons')

test.write(['site_scons', 'site_init.py'], """
raise Exception("Huh?")
""")

test.write('SConstruct', """
e=Environment(tools=['default', TOOL_FOO])
e.Foo(target='foo.out', source='SConstruct')
""")

test.run(arguments = '-Q .',
         stdout = "",
         stderr = r".*Error loading site_init file.*Huh\?.*",
         status=2,
         match=TestSCons.match_re_dotall)



test.pass_test()

# end of file

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
