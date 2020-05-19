import TestSCons

test = TestSCons.TestSCons()
test.file_fixture('fixture/SConstruct')
test.file_fixture('test_main.c')
test.run()
test.must_exist('compile_commands.jxson')