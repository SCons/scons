// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

import std.stdio: writefln;
import amod: print_message;
import bmod: calculate_value;

void main() {
  print_message();
	writefln("The value is %d.", calculate_value());
}
