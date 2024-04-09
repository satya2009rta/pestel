/*
 * pestel.cpp
 *
 *  A program to compute and compose strategy templates for two 2-player games
 *  It reuires stdin input as which is the description of a (generalized) parity game in extended HOA or pgsolver format; and outputs the result to stdout */

#include "FileHandler.hpp"
#include "MultiGame.hpp"

int main(int argc, char* argv[]) {
    try {
        mpa::MultiGame G;
        if (argc <= 1) {
            G = std2multgame();
        }
        else{
            /* read filename */
            std::string filename(argv[1]);
            G = file2multgame(filename);
        }
        
        /* compute the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        std::map<size_t, std::unordered_set<size_t>> colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region;
        std::string part_win;

        if (G.n_games_ == 1){
            winning_region = G.find_strategy_template_parity(unsafe_edges, colive_edge_set, live_group_set);
        }
        else{
            winning_region = G.find_composition_template(unsafe_edges, colive_edge_set, live_group_set);
            part_win = "(partial)";
        }

        G.print_set(winning_region.first, "Winning Region"+part_win);
        G.print_edges(unsafe_edges, "Unsafe edges", 1);
        G.print_edges(colive_edge_set, "Colive edges", 1);
        G.print_live_groups(live_group_set, "Live groups", 1);
        std::cout << "*===================================================\n";

        
        std::cout << "\n#" << "winning_vertices"<<part_win << ":"<< winning_region.first.size()<< "/"<<G.n_vert_<<"\n";
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

