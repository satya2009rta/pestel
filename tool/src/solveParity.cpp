/*
 * solveParity.cpp
 *
 *  A program to find strategy template and approximate winning region 
 *  for 2-player parity game using multiGames
 *  The input is to be given as a text file */

#include "FileHandler.hpp"
#include "paritySolvers.hpp"

/* command line inputs:
 *
 *  [1]: input file name
 *  [2]: output file name (optional, if not provided then the result is only displayed on the std I/O)
 */

int main(int argc, char* argv[]) {
    try {
        /* sanity check: input filename should be provided by the user */
        if (argc <= 1) {
            throw std::runtime_error("Too few input arguments.\n");
        }
        /* read filename */
        std::string filename(argv[1]);
        std::string method = "N";
        if (argc > 2){
            std::string str_method(argv[2]);
            method = str_method;
        }

        size_t N;
        std::vector<size_t> V_ID;
        std::vector<std::unordered_set<size_t>> TR;
        std::vector<size_t> COL;
        mpa::MultiGame G;
        
        /* check if the file is a .gm (pgsolver) file  */
        if(ends_with(filename, ".gm")){
            /* covert pgsolver format to normal game */
            pg2game(filename, N, V_ID, TR, COL);
        }
        else { /* read the number of vertices and vertex id, etc. directly from file */
            std2game(filename, N, V_ID, TR, COL);
        }
        /* construct the game */
        G.mergeGame(mpa::Game(N, V_ID, TR, COL));
        print_game(G);
        
        int windom_size;
        auto t1 = std::chrono::high_resolution_clock::now();
        if (method == "Z"){
            windom_size = G.solve_parity_game().first.size();
        }
        else{
            windom_size = G.solve_composed_parity().first.size();
        }
        auto t2 = std::chrono::high_resolution_clock::now();
        auto standard_time = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
        print_method(method, windom_size, G.n_vert_, standard_time);

        return 1;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 0;
    }
}

