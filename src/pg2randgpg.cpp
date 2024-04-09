/*
 * pg2randgpg.cpp
 *
 *  A program to add random colors to a (pgsolver) game to 
 *  get a pgsolver format generalized parity game
 *  It requires stdin input which is the description of a parity game in extended HOA or pgsolver format; and outputs the result game in pgsolver format to stdout. */

#include <functional>

#include "MultiGame.hpp"
#include "FileHandler.hpp"

int main(int argc, char* argv[]) {
    try {
        /* sanity check: input filename should be provided by the user */
        if (argc <= 3) {
            throw std::runtime_error("Too few input arguments.\n");
        }
        mpa::MultiGame G;

        /* read filename */
        std::string filename(argv[1]);
        G.mergeGame(file2game(filename));
        
        int no_games = std::stoi(argv[2]); /* number of new color sets to be added */
        int rand_max_col = std::stoi(argv[3]); /* maximum color that can be generated */
        
        /* if there is fourth argument, then generate the no_games set of colors one by one and print it to files */
        if (argc > 4) {
            G.all_colors_.clear();
            G.n_games_ = 0;
            for (int i = 0; i < no_games; i++){
                G.randMultigame(1,rand_max_col,false);
                std::string output_file(argv[4]);
                output_file += filename+"-"+std::to_string(G.n_games_)+"-"+std::to_string(G.max_color_)+".gpg";
                std::ofstream file(output_file);
                multigame2gpg(G,file);
            }
        }
        else{
            /* randomly generate no_games set of colors <= max_color */
            G.randMultigame(no_games, rand_max_col);
            multigame2gpg(G);
        }
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return -1;
    }
}

