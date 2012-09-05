/*
 * Simple D program that links to ncurses via a C wrapping file.
 */

extern(C) {
	int ncurs_init();
	int ncurs_cleanup();
}

void main() {
	ncurs_init();
	ncurs_cleanup();
}

