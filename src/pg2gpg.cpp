/*
 * pg2gpg.cpp
 *
 *  A program to convert a pgsolver file into pgsolver format generalized parity game.
 *  It requires stdin input which is the description of a parity game in extended HOA or pgsolver format; and outputs the result game in pgsolver format to stdout. */

#include <functional>

#include "MultiGame.hpp"
#include "FileHandler.hpp"

int main(int argc, char* argv[]) {
    try {
        mpa::MultiGame G;

        if (argc <= 1) {
            G.mergeGame(std2game());
        }
        else{
            /* read filename */
            std::string filename(argv[1]);
            G.mergeGame(file2game(filename));
        }

        /* convert it to generalized parity game (multi-game) */
        G.parityToMultigame();
        
        /* output to gpg formtat */
        multigame2gpg(G);
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return -1;
    }
}

