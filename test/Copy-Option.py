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
Test that setting Options in an Environment doesn't prevent the
Environment from being copied.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
gpib_options = ['NI_GPIB', 'NI_ENET']
gpib_include = '/'

#0.96 broke copying  ListOptions ???
opts = Options('config.py', ARGUMENTS)
opts.AddOptions(
    BoolOption('gpib', 'enable gpib support', 1),
    ListOption('gpib_options',
        'whether and what kind of gpib support shall be enabled',
        'all',
        gpib_options),
    )
env = Environment(options = opts, CPPPATH = ['#/'])
new_env=env.Clone()
""")

test.run(arguments = '.')

test.pass_test()
