#include "myheader.hpp"

#include <iostream>

void myfunc()
{
	std::cout << __FUNCTION__ << std::endl << std::endl;
}

void yourfunc()
{
	std::cout << "whatever" << "\\n" << std::flush;
}
