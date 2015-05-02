/*
 * Simple D program that links to ncurses via a C wrapping file.
 */

extern(C) {
	void ncurs_init();
	void ncurs_cleanup();
}

void main() {
	ncurs_init();
	ncurs_cleanup();
}
