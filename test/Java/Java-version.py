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
Test globbing to find a JDK
"""

import os
import sys

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

if sys.platform == 'win32':
    test.subdir(['Program Files'])
    test.subdir(['Program Files', 'Java'])
    test.subdir(['Program Files', 'Java', 'jdk1.8.0_201'])
    test.subdir(['Program Files', 'Java', 'jdk1.8.0_201', 'bin'])
    test.subdir(['Program Files', 'Java', 'jdk-11.0.2'])
    test.subdir(['Program Files', 'Java', 'jdk-11.0.2', 'bin'])

    test.write(['Program Files', 'Java', 'jdk1.8.0_201', 'bin', 'javac.exe'], "echo Java 1.8")
    test.write(['Program Files', 'Java', 'jdk-11.0.2', 'bin', 'javac.exe'], "echo Java 11.0")
else:
    test.subdir(['jvm'])
    test.subdir(['jvm', 'java'])
    test.subdir(['jvm', 'java', 'bin'])
    test.subdir(['jvm', 'java-11-openjdk-11.0.2'])
    test.subdir(['jvm', 'java-11-openjdk-11.0.2', 'bin'])
    test.subdir(['jvm', 'java-1.8-openjdk-1.8.0'])
    test.subdir(['jvm', 'java-1.8-openjdk-1.8.0', 'bin'])

    test.write(['jvm', 'java', 'bin', 'javac'], "echo Java 1.8")
    test.write(['jvm', 'java-11-openjdk-11.0.2', 'bin', 'javac'], "echo Java 11.0")
    test.write(['jvm', 'java-1.8-openjdk-1.8.0', 'bin', 'javac'], "echo Java 1.8")

for version in (None, "1.8", "11.0"):
    if version:
        if sys.platform == 'win32':
            patterns = [
                'Program Files*/Java/jdk*%s*/bin' % version,
            ]
        else:
            patterns = [
                'jvm/*-%s*/bin' % version,
            ]
    else:
        if sys.platform == 'win32':
            patterns = [
                'Program Files*/Java/jdk*/bin',
            ]
        else:
            patterns = [
                'jvm/*/bin',
            ]
    java_path = test.paths(patterns)
    #print(java_path)
    if not java_path:
        msg = "glob pattern {%s} found no JDK matches" % patterns[0]
        test.fail_test(message=msg)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
