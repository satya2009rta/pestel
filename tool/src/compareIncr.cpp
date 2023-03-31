/*
 * addSpecPGenParity.cpp
 *
 *  A program to solve generalized parity game using pre-computed template and compare with other methods by Perez..
 *  The input is to be given as a text file */

#include "FileHandler.hpp"
#include "paritySolvers.hpp"

/* command line inputs:
 *
 *  [1]: input file name
 *  [2]: output file name (optional, if not provided then the result is only displayed on the std I/O)
 */

/* function that solves and compares with other algo */
int solveGenParityMethods(const int method, const std::string time, const mpa::MultiGame G, const std::string path, const size_t actual_windom_size, const int our_tool_time){
    
    int windom_size = G.n_vert_;

    mpa::MultiGame multigame_copy(G);
    int standard_time = 0;
    std::string filename = "new.gpg";
    size_t iterate = G.n_games_;
    while (iterate > 0){
        std::ofstream file(filename);
        multigame2gpg(multigame_copy, file);
        file.close();
        auto t1 = std::chrono::high_resolution_clock::now();
        windom_size = std::min(windom_size, genParityMethods(filename, method, path, std::stoi(time)));
        auto t2 = std::chrono::high_resolution_clock::now();
        standard_time += std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();

        multigame_copy.n_games_ -= 1;
        iterate -= 1;
        multigame_copy.all_colors_.pop_back();
    }
    std::filesystem::remove(filename);

    return compareTime(method, time, actual_windom_size, standard_time, windom_size, our_tool_time);
}


int main(int argc, char* argv[]) {
    try {
        /* sanity check: input filename should be provided by the user */
        if (argc <= 1) {
            throw std::runtime_error("Too few input arguments.\n");
        }
        std::string time = "300"; /* default timeout time */
        if (argc > 2){ /* timeout time in argument */ 
            std::string str_time(argv[2]);
            time = str_time;
        }
        /* read filename */
        std::string filename(argv[1]);
        size_t N;
        std::vector<size_t> V_ID;
        std::vector<std::unordered_set<size_t>> TR;
        size_t N_GAMES;
        std::vector<std::vector<size_t>> ALL_COLS;
        /* convert the gpgsolver format to normal multi-game */
        gpg2game(filename, N, V_ID, TR, N_GAMES, ALL_COLS);
        
        /* construct the MultiGame */
        mpa::MultiGame G(N, V_ID, TR, N_GAMES, ALL_COLS);

        /* initialize size and time for our algo */
        int new_windom_size = -1;
        int new_time_count = std::stoi(time)*1000;

        if (argc <= 4){ /* python file path */ 
            auto t3 = std::chrono::high_resolution_clock::now();
            new_windom_size = G.solve_gen_parity_add_spec(G.n_games_).first.size();
            auto t4 = std::chrono::high_resolution_clock::now();
            new_time_count = std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t3).count();
            if (new_time_count > std::stoi(time)*1000){
                new_time_count = std::stoi(time)*1000;
            }
        }

        
        
        std::string path = "./tool/lib/solveGenParity.py";
        if (argc > 3){ /* python file path */ 
            std::string str_path(argv[3]);
            path = str_path;
        }

        /* print size of the MultiGame */
        std::cout << filename << "," << G.n_vert_ <<"," << G.n_edge_ << ","<< G.max_color_ << "," << G.n_games_;
        /* print time taken by our algo */
        std::cout << ","<<new_time_count;

        /* solve using generalized zielonka */
        int actual_windom_size = solveGenParityMethods(0, time, G, path, new_windom_size, new_time_count);

        /* solve with partial algos */
        solveGenParityMethods(1, time, G, path, actual_windom_size, new_time_count);
        solveGenParityMethods(2, time, G, path, actual_windom_size, new_time_count);
        solveGenParityMethods(3, time, G, path, actual_windom_size, new_time_count);
        std::cout << "\n";

        return actual_windom_size;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 0;
    }
}