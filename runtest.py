#!/usr/bin/env python

import getopt, os, os.path, re, string, sys

opts, tests = getopt.getopt(sys.argv[1:], "dv:")

debug = ''
version = None

for o, a in opts:
    if o == '-d': debug = "/usr/lib/python1.5/pdb.py"
    if o == '-v': version = a

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

cwd = os.getcwd()

map(os.path.abspath, tests)

build_test = os.path.join(cwd, "build", "test")
scons_ver = os.path.join(build_test, "scons-" + version)

os.chdir(scons_ver)

os.environ['PYTHONPATH']  = scons_ver + ':' + build_test

exit = 0

for path in tests:
    if not os.path.isabs(path):
	path = os.path.join(cwd, path)
    if os.system("python " + debug + " " + path):
	exit = 1

sys.exit(exit)
