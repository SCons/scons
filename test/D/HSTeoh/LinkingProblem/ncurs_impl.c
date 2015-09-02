/* Ncurses wrappers */
#include <ncurses.h>

void ncurs_init() {
	initscr();
	cbreak();
	noecho();
	keypad(stdscr, TRUE);
}

void ncurs_cleanup() {
	endwin();
}
