#include "stuff.h"

X::X() {
    this->i = 1;
}
int X::y(){
    return this->i;
}

X *SomeX() {
    return new X(); 
}
