// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

extern void ncurs_init();
extern void ncurs_cleanup();

int main() {
	ncurs_init();
	ncurs_cleanup();
}
