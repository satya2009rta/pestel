/*
 * pg2randgpg.cpp
 *
 *  A program to add random colors to a (pgsolver) game to 
 *  get a pgsolver format generalized parity game
 *  It requires stdin input which is the description of a parity game in extended HOA or pgsolver format; and outputs the result game in pgsolver format to stdout. */

#include <functional>

#include "FileHandler.hpp"

void printHelp() {
    std::cout << "Usage: pg2randgpggpg [num_obj] [max_col]\n";
    std::cout << "Convert a parity game to generalized parity game by adding a number of random parity objectives.\n";
    std::cout << "\nInputs/Outputs:\n";
    std::cout << "- num_obj: number of parity objectives to be generated\n";
    std::cout << "- max_col: maximum priority of the parity objectives\n";
    std::cout << "- STDIN: description of a parity game in extended-HOA/pgsolver format\n";
    std::cout << "- STDOUT:  a generalized parity game (in pgsolver format)\n"; 
    std::cout << "\nExample usage:\n";
    std::cout << "pg2randgpg 4 2 < .example.pg\n";
}

int main(int argc, char* argv[]) {
    try {
        /* sanity check: input filename should be provided by the user */
        if (argc <= 2) {
            throw std::runtime_error("Too few input arguments.\n");
            printHelp();
            return 0;
        }

        mpa::MultiGame G(std2game());
        
        int no_games = std::stoi(argv[1]); /* number of new color sets to be added */
        int rand_max_col = std::stoi(argv[2]); /* maximum color that can be generated */
        
       /* randomly generate no_games set of colors <= max_color */
        G.randMultigame(no_games, rand_max_col);
        multigame2gpg(G);

        return 0;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        printHelp();
        return 1;
    }
}

