import std.stdio;
import dmod;

extern (C) {
  int csqr(int arg);
}

void main() {
  print_msg();
  auto i = 17;
  writefln("The square of %d is %d", i, csqr(i));
}
