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
        /* sanity check: input filename should be provided by the user */
        if (argc <= 1) {
            throw std::runtime_error("Too few input arguments.\n");
        }
        /* read filename */
        std::string filename(argv[1]);
        size_t N;
        std::vector<size_t> V_ID;
        std::vector<std::unordered_set<size_t>> TR;
        std::vector<size_t> COL;
        mpa::MultiGame G;
        
        /* covert pgsolver format to normal game */
        pg2game(filename, N, V_ID, TR, COL);
        
        /* construct the game */
        G.mergeGame(mpa::Game(N, V_ID, TR, COL));

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

