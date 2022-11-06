import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()

env.Append(CXXFLAGS = ["-std=c++20"])
env['CXXMODULEPATH'] = "cxx-scons-modules"
env.Program("scons-module-test", ["itest.cpp", "test.cpp", "main.cpp"])
""")

test.write('itest.cpp', """\
module test;

int i = 42;
""")

test.write('test.cpp', r"""\
module;

#include <iostream>
#include "incl.h"

export module test;
export void test()
{
	std::cout << "hello, world\n";
}

export template<unsigned int> struct fact;

export extern int i;

template<unsigned int n>
struct fact {
    static constexpr unsigned int value = n * fact<n-1>::value;
};

template<>
struct fact<0> {
    static constexpr unsigned int value = 1;
};
""")

test.write('incl.h', '')

test.write('main.cpp', """\
import test;

import <iostream>;

int main()
{
	std::cout << i << std::endl;
	test();
	int i = fact<4>::value;
	std::cout << i << std::endl;
	return 0;
}
""")

test.run(arguments = ".")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
