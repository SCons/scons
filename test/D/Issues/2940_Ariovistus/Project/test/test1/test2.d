import std.stdio;

struct X {
}

extern(C) int _ZN1X1yEv(X* _this);
extern(C) X* _Z5SomeXv();

void main() {
    X *x = _Z5SomeXv();
    int i = _ZN1X1yEv(x);
    writeln("i: ", i);
}
