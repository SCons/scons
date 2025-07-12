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
