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
Test ValidateOptions() command.
"""

import TestSCons

test = TestSCons.TestSCons()
test.file_fixture('fixture/SConstruct-check-valid-options', 'SConstruct')

# Should see "This is in SConstruct"
test.run()
test.must_contain_single_instance_of(test.stdout(), ["This is in SConstruct"])

test.run(arguments="--testing=abc")
test.must_contain_single_instance_of(test.stdout(), ["This is in SConstruct"])

# Should not see "This is in SConstruct"
test.run(arguments="--garbage=xyz", status=2, stderr=".*SCons Error: no such option: --garbage.*", match=TestSCons.match_re_dotall)
test.fail_test(("This is in SConstruct" in test.stdout()), message='"This is in SConstruct" should not be output. This means ValidateOptions() did not error out before this was printed')




# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
