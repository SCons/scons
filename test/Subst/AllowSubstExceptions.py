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
XXX Put a description of the test here.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import SCons.Errors

# Avoid tools= initialization in both the default and local construction
# environments, so we don't get substitution exceptions from platform-
# specific Tool modules.
DefaultEnvironment(tools = [])
env = Environment(tools = [], INDEX = [0, 1])

assert env.subst('$NAME') == ''
assert env.subst('${NAME}') == ''
assert env.subst('${INDEX[999]}') == ''

assert env.subst_list('$NAME') == [[]]
assert env.subst_list('${NAME}') == [[]]
assert env.subst_list('${INDEX[999]}') == [[]]

AllowSubstExceptions()

try: env.subst('$NAME')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

try: env.subst('${NAME}')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

try: env.subst('${INDEX[999]}')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

try: env.subst_list('$NAME')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

try: env.subst_list('${NAME}')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

try: env.subst_list('${INDEX[999]}')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")



try: env.subst('${1/0}')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

try: env.subst_list('${1/0}')
except SCons.Errors.UserError as e: print(e)
else: raise Exception("did not catch expected SCons.Errors.UserError")

AllowSubstExceptions(ZeroDivisionError)

assert env.subst('${1/0}') == ''
assert env.subst_list('${1/0}') == [[]]
""")

test.run()
#print test.stdout()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
