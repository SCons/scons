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
Test that the --debug=json option works.
"""

import json
import re
import sys

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

test.file_fixture('fixture/SConstruct_debug_count', 'SConstruct')
test.write('file.in', "file.in\n")


# Just check that object counts for some representative classes
# show up in the output.

def find_object_count(s, stdout):
    re_string = r'\d+ +\d+   %s' % re.escape(s)
    return re.search(re_string, stdout)

def check_json_file(filename):
    with open(filename,'r') as jf:
        stats_info = json.load(jf)
        if 'Build_Info' not in stats_info:
            test.fail_test(message='No Build_Info in json')
        if 'Object counts' not in stats_info:
            test.fail_test(message='No "Object counts" in json')

        for o in objects:
            if o not in stats_info['Object counts']:
                test.fail_test(message=f"Object counts missing {o}")

        if stats_info['Build_Info']['PYTHON_VERSION'][
            'major'] != sys.version_info.major:
            test.fail_test(message=f"Build Info PYTHON_VERSION incorrect")


objects = [
    'Action.CommandAction',
    'Builder.BuilderBase',
    'Environment.Base',
    'Executor.Executor',
    'Node.FS.File',
    'Node.FS.Base',
    'Node.Node',
]

test.run(arguments='--debug=count,json')
test.must_exist('scons_stats.json')
check_json_file('scons_stats.json')

test.run(arguments='--debug=count,json  JSON=build/output/stats.json')
test.must_exist('build/output/stats.json')
check_json_file('build/output/stats.json')

# TODO: Not sure how to do this in a reasonable way on windows, so just skip for now
if not IS_WINDOWS:
    test.run(arguments='--debug=count,json  JSON=/cant/write/here/dumb.json', status=2, stderr=None)
    test.must_not_exist('/cant/write/here/dumb.json')
    test.pass_test('scons: *** Unable to create directory for JSON debug output file:' in test.stderr())


test.pass_test()
