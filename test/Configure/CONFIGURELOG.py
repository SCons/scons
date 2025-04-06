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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""
Test that the configure context log file name can be specified by
setting the $CONFIGURELOG construction variable.
"""

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

test.write(SConstruct_path, """\
DefaultEnvironment(tools=[])
def CustomTest(context):
  context.Message('Executing Custom Test ...')
  context.Result(1)

env = Environment(tools=[], CONFIGURELOG = 'custom.logfile')
conf = Configure(env, custom_tests = {'CustomTest' : CustomTest})
conf.CustomTest();
env = conf.Finish()
""")

test.run()

expect = """\
file %(SConstruct_path)s,line 7:
\tConfigure(confdir = .sconf_temp)
scons: Configure: Executing Custom Test ...
scons: Configure: (cached) yes


""" % locals()

test.must_match('custom.logfile', expect, mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
