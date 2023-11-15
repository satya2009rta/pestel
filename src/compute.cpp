/*
 * compute.cpp
 *
 *  A program to find strategy template for 2-player games
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
        /* variables for game */
        size_t N;
        std::vector<size_t> V_ID;
        std::vector<std::unordered_set<size_t>> TR;
        std::vector<size_t> COL;
        if (argc <= 1) {
            pg2game(std::cin, N, V_ID, TR, COL);
        }
        else{
            /* read filename */
            std::string filename(argv[1]);
            /* print the filename */
            // std::cout << "\n********"<< filename << "********\n";
            /* check if the file is a .gm (pgsolver) file  */
            if(ends_with(filename, ".gm")){
                /* covert pgsolver format to normal game */
                pg2game(filename, N, V_ID, TR, COL);
            }
            else { /* read the number of vertices and vertex id, etc. directly from file */
                std2game(filename, N, V_ID, TR, COL);
            }
        }
        /* construct the game */
        mpa::Game G(N, V_ID, TR, COL);
        // print_game(G);

        /* compute the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        std::map<size_t, std::unordered_set<size_t>> colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        auto winning_region = G.find_strategy_template_parity(unsafe_edges, colive_edge_set, live_group_set);
        
        G.print_set(winning_region.first, "Winning Region");
        // if (winning_region.first.size()<10){
            G.print_edges(unsafe_edges, "Unsafe edges", 1);
            G.print_edges(colive_edge_set, "Colive edges", 1);
            G.print_live_groups(live_group_set, "Live groups", 1);
            std::cout <<"*==================================================\n";
        // }
        std::cout << "\n#winning_vertices:"<< winning_region.first.size()<< "/"<<G.n_vert_<<"\n";
        std::cout << "#unsafe_edges:"<< unsafe_edges.size()<<"\n";
        std::cout << "#colive_edges:"<< colive_edge_set.size()<<"\n";
        std::cout << "#live_groups:"<< live_group_set.size()<<"\n";
        std::cout <<"**==================================================\n";
        return 1;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 0;
    }
}

