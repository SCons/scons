#include "test2.hpp"

int
main(int argc, char *argv[])
{
    Foo* test = new Foo();
    test->print_function();
    test->print_function2();
    return 0;
}

int Foo::print_function()
{
    std::cout << "print_function";
    return 0;
}