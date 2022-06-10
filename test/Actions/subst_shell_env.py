#!/usr/bin/env python
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
#


"""
Verify that shell environment variables can be expanded per target/source
when executing actions on the command line.
"""
import os

import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture('subst_shell_env-fixture')

test.run(arguments = ['-Q'])
test.must_match('out.txt', f"I_got_expanded_to_out.txt{os.linesep}out.txt_is_from_expansion{os.linesep}$EXPAND_THIS{os.linesep}")
test.must_match('out2.txt', f"I_got_expanded_to_out2.txt{os.linesep}out2.txt_is_from_expansion{os.linesep}$EXPAND_THIS{os.linesep}")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
