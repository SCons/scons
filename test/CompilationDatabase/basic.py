import sys
import TestSCons


test = TestSCons.TestSCons()

if sys.platform == 'win32':
    test.file_fixture('mylink_win32.py', 'mylink.py')
else:
     test.file_fixture('mylink.py')

test.file_fixture('mygcc.py')

test.verbose_set(1)
test.file_fixture('fixture/SConstruct')
test.file_fixture('test_main.c')
test.run()
test.must_exist('compile_commands.json')

# Now test with absolute paths
test.run(arguments='ABSPATH=1')
test.must_exist('compile_commands_abs.json')
