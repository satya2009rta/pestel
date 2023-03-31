/*
 * solveGenParity.cpp
 *
 *  A program to solve generalized parity game
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
        if (method != "N" && method != "Z"){
            std::string path = "./tool/lib/solveGenParity.py";
            if (argc > 3){ /* python file path */ 
                std::string str_path(argv[2]);
                path = str_path;
            }
            
            auto t1 = std::chrono::high_resolution_clock::now();
            int win_size = genParityMethods(filename, method, path);
            auto t2 = std::chrono::high_resolution_clock::now();
            auto standard_time = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
            print_method(method, win_size, 0, standard_time);
            return 0;
        }
        else{
            size_t N;
            std::vector<size_t> V_ID;
            std::vector<std::unordered_set<size_t>> TR;
            size_t N_GAMES;
            std::vector<std::vector<size_t>> ALL_COLS;
            /* print the filename */
            std::cout << "\n********"<< filename << "********\n";
            /* check if the file is a .gm (pgsolver) file  */
            if(ends_with(filename, ".gpg")){
                /* convert the gpgsolver format to normal multi-game */
                gpg2game(filename, N, V_ID, TR, N_GAMES, ALL_COLS);
            }
            else { /* read the number of vertices and vertex id, etc. directly from file */
                std2multigame(filename, N, V_ID, TR, N_GAMES, ALL_COLS);
            }
            /* construct the MultiGame */
            mpa::MultiGame G(N, V_ID, TR, N_GAMES, ALL_COLS);
            print_game(G);
            std::cout << "======================================================\n";

            /* compute the winning set */
            int windom_size;
            auto t1 = std::chrono::high_resolution_clock::now();
            if (method == "N"){
                windom_size = G.solve_gen_parity().first.size();
            }
            else{
                windom_size = G.gen_zielonka().first.size();
            }
            auto t2 = std::chrono::high_resolution_clock::now();
            auto standard_time = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
            print_method(method, windom_size, G.n_vert_, standard_time);
            return 0;
        }
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return -1;
    }
}

