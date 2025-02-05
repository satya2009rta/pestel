/*
 * hoa2pg.cpp
 *
 *  A program to convert a parity game in extended HOA format to pgsolver format.
 *  It requires stdin input which is the description of a parity game in extended HOA or pgsolver format; and outputs the result game in pgsolver format to stdout. */

#include <functional>

#include "FileHandler.hpp"

int main() {
    try {
        mpa::Game G = std2game();

        /* output to pg formtat */
        game2pg(G);
        return 0;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 1;
    }
}

