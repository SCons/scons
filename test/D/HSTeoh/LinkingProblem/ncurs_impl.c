/* Ncurses wrappers */
#include <ncurses.h>

int ncurs_init() {
	initscr();
	cbreak();
	noecho();
	keypad(stdscr, TRUE);
}

int ncurs_cleanup() {
	endwin();
}
