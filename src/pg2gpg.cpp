/*
 * pg2gpg.cpp
 *
 *  A program to convert a pgsolver file into pgsolver format generalized parity game.
 *  It requires stdin input which is the description of a parity game in extended HOA or pgsolver format; and outputs the result game in pgsolver format to stdout. */

#include <functional>

#include "FileHandler.hpp"

int main() {
    try {
        mpa::MultiGame G(std2game());

        /* convert it to generalized parity game (multi-game) */
        G.parityToMultigame();
        
        /* output to gpg formtat */
        multigame2gpg(G);
        return 0;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 1;
    }
}

