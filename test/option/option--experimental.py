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
Test the --experimental option.
"""

import TestSCons

test = TestSCons.TestSCons()

test.file_fixture('fixture/SConstruct__experimental', 'SConstruct')

tests = [
    ('.', []),
    ('--experimental=ninja', ['ninja']),
    ('--experimental=tm_v2', ['tm_v2']),
    ('--experimental=all', ['ninja', 'tm_v2', 'transporter', 'warp_speed']),
    ('--experimental=none', []),
]

for args, exper in tests:
    read_string = """All Features=ninja,tm_v2,transporter,warp_speed
Experimental=%s
""" % (exper)
    test.run(arguments=args,
             stdout=test.wrap_stdout(read_str=read_string, build_str="scons: `.' is up to date.\n"))

test.run(arguments='--experimental=warp_drive',
         stderr="""usage: scons [OPTIONS] [VARIABLES] [TARGETS]

SCons Error: option --experimental: invalid choice: 'warp_drive' (choose from 'all','none','ninja','tm_v2','transporter','warp_speed')
""",
         status=2)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
