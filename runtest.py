#!/usr/bin/env python

import getopt
import os
import os.path
import re
import string
import sys

all = 0
build = None
debug = ''
tests = []
version = None

opts, tests = getopt.getopt(sys.argv[1:], "ab:dv:",
			    ['all','build=','debug','version='])

for o, a in opts:
    if o == '-a' or o == '--all': all = 1
    elif o == '-b' or o == '-build': build = a
    elif o == '-d' or o == '--debug': debug = "/usr/lib/python1.5/pdb.py"
    elif o == '-v' or o == '--version': version = a

cwd = os.getcwd()

if tests:
    map(os.path.abspath, tests)
elif all:
    def find_Test_py(arg, dirname, names):
	global tests
        n = filter(lambda n: n[-8:] == "Tests.py", names)
	n = map(lambda x,d=dirname: os.path.join(d, x), n)
	tests = tests + n
    os.path.walk('src', find_Test_py, 0)

    def find_py(arg, dirname, names):
	global tests
        n = filter(lambda n: n[-3:] == ".py", names)
	n = map(lambda x,d=dirname: os.path.join(d, x), n)
	tests = tests + n
    os.path.walk('test', find_py, 0)

if build == 'aegis':
    if not version:
	version = os.popen("aesub '$version'").read()[:-1]

    match = re.compile(r'^[CD]0*')

    def aegis_to_version(aever):
	arr = string.split(aever, '.')
	end = max(len(arr) - 1, 2)
	arr = map(lambda e: match.sub('', e), arr[:end])
	def rep(e):
	    if len(e) == 1:
		e = '0' + e
	    return e
	arr[1:] = map(rep, arr[1:])
	return string.join(arr, '.')

    version = aegis_to_version(version)

    build_test = os.path.join(cwd, "build", "test")
    scons_dir = os.path.join(build_test, "scons-" + version)

    os.environ['PYTHONPATH'] = string.join([scons_dir,
					    build_test],
					   os.pathsep)

else:

    scons_dir = os.path.join(cwd, 'src')

    os.environ['PYTHONPATH'] = string.join([os.path.join(cwd, 'src'),
					    os.path.join(cwd, 'etc')],
					   os.pathsep)

os.chdir(scons_dir)

fail = []

for path in tests:
    if os.path.isabs(path):
	abs = path
    else:
	abs = os.path.join(cwd, path)
    cmd = string.join(["python", debug, abs], " ")
    if all:
	print cmd
    if os.system(cmd):
	fail.append(path)

sys.exit(len(fail))
