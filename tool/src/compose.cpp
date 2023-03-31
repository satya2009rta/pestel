/*
 * compose.cpp
 *
 *  A program to compute and compose strategy templates for two 2-player games
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
        
        /* compute the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        std::map<size_t, std::unordered_set<size_t>> colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region;
        
        if (G.n_vert_ < 10 && G.n_games_ == 2){/* when there is only two games */
            winning_region = G.nthGame(0).find_strategy_template_parity(unsafe_edges, colive_edge_set, live_group_set);
            G.print_set(winning_region.first, "Winning Region1");
            G.print_edges(unsafe_edges, "Unsafe edges", 1);
            G.print_edges(colive_edge_set, "Colive edges", 1);
            G.print_live_groups(live_group_set, "Live groups", 1);
            std::cout << "*=====================================================\n";
            
            winning_region = G.nthGame(1).find_strategy_template_parity(unsafe_edges, colive_edge_set, live_group_set);
            G.print_set(winning_region.first, "Winning Region2");
            G.print_edges(unsafe_edges, "Unsafe edges", 1);
            G.print_edges(colive_edge_set, "Colive edges", 1);
            G.print_live_groups(live_group_set, "Live groups", 1);
            std::cout << "**====================================================\n";
        }

        winning_region = G.find_composition_template(unsafe_edges, colive_edge_set, live_group_set);

        if (winning_region.first.size()<10){
            G.print_set(winning_region.first, "Winning Region");
            G.print_edges(unsafe_edges, "Unsafe edges", 1);
            G.print_edges(colive_edge_set, "Colive edges", 1);
            G.print_live_groups(live_group_set, "Live groups", 1);
            std::cout << "***===================================================\n";
        }
        
        std::cout << "\n#winning_vertices:"<< winning_region.first.size()<< "/"<<G.n_vert_<<"\n";
        std::cout << "#unsafe_edges:"<< unsafe_edges.size()<<"\n";
        std::cout << "#colive_edges:"<< colive_edge_set.size()<<"\n";
        std::cout << "#live_groups:"<< live_group_set.size()<<"\n";
        std::cout <<"****==================================================\n";

        // winning_region = G.gen_zielonka();
        // if (winning_region.first.size()<10){
        //     G.print_set(winning_region.first, "Actual Winning Region");
        // }
        // std::cout << "#actual_winning_vertices:"<< winning_region.first.size()<< "/"<<G.n_vert_<<"\n";
        return 1;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return 0;
    }
}

