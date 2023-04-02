/*
 * approxPGenParity.cpp
 *
 *  A program to find strategy template and approximate winning region 
 *  for 2-player generalized parity game using multiGames
 *  The input is to be given as a text file */

#include "FileHandler.hpp"
#include "paritySolvers.hpp"

/* command line inputs:
 *
 *  [1]: input file name
 *  [2]: output file name (optional, if not provided then the result is only displayed on the std I/O)
 */

/* function that solves and compares with other algo */
int solveGenParityMethods(const int method, const std::string time, const std::string filename, const std::string path, const int actual_windom_size, const int our_tool_time){
    auto t1 = std::chrono::high_resolution_clock::now();
    int windom_size = genParityMethods(filename, method, path, std::stoi(time));
    auto t2 = std::chrono::high_resolution_clock::now();
    auto standard_time = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();

    return compareTime(method, time, actual_windom_size, standard_time, windom_size, our_tool_time);
}


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
        size_t N_GAMES;
        std::vector<std::vector<size_t>> ALL_COLS;
        mpa::MultiGame G;
    
        /* convert the gpgsolver format to normal multi-game */
        gpg2game(filename, N, V_ID, TR, N_GAMES, ALL_COLS);
        G.copy(mpa::MultiGame(N, V_ID, TR, N_GAMES, ALL_COLS));
        
        int methodN = 1; /* new method not timedout? */
        if (argc > 2){ /* timeout time in argument */ 
            std::string no_timeout(argv[2]);
            if (no_timeout == "0"){
                methodN = 0;
            }
            else if (no_timeout == "124"){
                methodN = 124;
            }
            else{
                methodN = 1;
            }
        }
        int new_time_count = -1;
        int new_windom_size = -1;

        std::string time = "10"; /* default timeout time */
        if (argc > 3){ /* timeout time in argument */ 
            std::string str_time(argv[3]);
            time = str_time;
        }

        /* first time check methodN timeout */
        if (methodN == 0){
            auto t3 = std::chrono::high_resolution_clock::now();
            new_windom_size = G.solve_gen_parity().first.size();
            auto t4 = std::chrono::high_resolution_clock::now();
            new_time_count = std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t3).count();
            int mstime = std::stoi(time)*1000;
            if (new_time_count > mstime){
                return 124;
            }
            else{
                return 1;
            }
        }
        /* compute the winning set if not timedout before */
        else if (methodN == 1){
            auto t3 = std::chrono::high_resolution_clock::now();
            new_windom_size = G.solve_gen_parity().first.size();
            auto t4 = std::chrono::high_resolution_clock::now();
            new_time_count = std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t3).count();
        }
        else if (methodN == 124){
            /* if timed out */
            new_time_count = std::stoi(time)*1000;
        }


        std::string path = "./lib/solveGenParity.py";
        if (argc > 4){ /* python file path */ 
            std::string str_path(argv[4]);
            path = str_path;
        }

        /* print size of the MultiGame */
        std::cout << filename << "," << G.n_vert_ <<"," << G.n_edge_ << ","<< G.max_color_ << "," << G.n_games_;
        /* print time taken by our algo */
        std::cout << ","<<new_time_count;

        /* solve using generalized zielonka */
        int actual_windom_size = solveGenParityMethods(0, time, filename, path, new_windom_size, new_time_count);

        /* solve with partial algos */
        solveGenParityMethods(1, time, filename, path, actual_windom_size, new_time_count);
        solveGenParityMethods(2, time, filename, path, actual_windom_size, new_time_count);
        solveGenParityMethods(3, time, filename, path, actual_windom_size, new_time_count);
        std::cout << "\n";

        return actual_windom_size;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 0;
    }
}