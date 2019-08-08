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
Test writing XML output to a file.
"""

import os
import re

import TestCmd
import TestRuntest

test = TestRuntest.TestRuntest(match = TestCmd.match_re,
                               diff = TestCmd.diff_re)

pythonstring = re.escape(TestRuntest.pythonstring)
pythonflags = TestRuntest.pythonflags
test_fail_py = re.escape(os.path.join('test', 'fail.py'))
test_no_result_py = re.escape(os.path.join('test', 'no_result.py'))
test_pass_py = re.escape(os.path.join('test', 'pass.py'))

test.subdir('test')

test.write_fake_scons_source_tree()

test.write_failing_test(['test', 'fail.py'])

test.write_no_result_test(['test', 'no_result.py'])

test.write_passing_test(['test', 'pass.py'])

test.run(arguments = '--xml xml.out test', status=1)

expect = """\
  <results>
    <test>
      <file_name>%(test_fail_py)s</file_name>
      <command_line>%(pythonstring)s%(pythonflags)s %(test_fail_py)s</command_line>
      <exit_status>1</exit_status>
      <stdout>FAILING TEST STDOUT
</stdout>
      <stderr>FAILING TEST STDERR
</stderr>
      <time>\\d+\\.\\d</time>
    </test>
    <test>
      <file_name>%(test_no_result_py)s</file_name>
      <command_line>%(pythonstring)s%(pythonflags)s %(test_no_result_py)s</command_line>
      <exit_status>2</exit_status>
      <stdout>NO RESULT TEST STDOUT
</stdout>
      <stderr>NO RESULT TEST STDERR
</stderr>
      <time>\\d+\\.\\d</time>
    </test>
    <test>
      <file_name>%(test_pass_py)s</file_name>
      <command_line>%(pythonstring)s%(pythonflags)s %(test_pass_py)s</command_line>
      <exit_status>0</exit_status>
      <stdout>PASSING TEST STDOUT
</stdout>
      <stderr>PASSING TEST STDERR
</stderr>
      <time>\\d+\\.\\d</time>
    </test>
  <time>\\d+\\.\\d</time>
  </results>
""" % locals()

# Just strip carriage returns so the regular expression matching works.
contents = test.read('xml.out')
contents = contents.replace(b'\r', b'')
test.write('xml.out', contents)

test.must_match('xml.out', expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
