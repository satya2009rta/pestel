/*
 * pg2gpg.cpp
 *
 *  A program to convert a pgsolver file into gpg format (generalized parity game)
 *  The input is to be given as a text file */

#include <functional>

#include "MultiGame.hpp"
#include "FileHandler.hpp"

/* command line inputs:
 *
 *  [1]: input file name
 * 
 */

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
        if (argc > 2) {
            std::string output_file(argv[2]);
            std::ofstream file(output_file);
            multigame2gpg(G,file);
        }
        else{
            multigame2gpg(G);
        }
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return -1;
    }
}

