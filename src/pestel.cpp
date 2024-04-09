/*
 * pestel.cpp
 *
 *  A program to compute a winning strategy templates for (generalized) parity games
 *  It reuires stdin input as which is the description of a (generalized) parity game in extended HOA or pgsolver format; and outputs the result to stdout */

#include "FileHandler.hpp"
#include "MultiGame.hpp"

void printHelpN(const std::string str) {
        std::cout << "pestel " << str << " is not available.\n";
        std::cout << "Try pestel --help for more information.\n";
    }
void printHelp() {
    std::cout << "Usage: pestel [OPTION...]\n";
    std::cout << "Compute winning strategy templates for (generalized) parity games.\n";
    std::cout << "\nInputs/Outputs:\n";
    std::cout << "- STDIN: description of a parity game in extended-HOA/pgsolver format or description of a generalized parity game in pgsolver format\n";
    std::cout << "- STDOUT: a winning strategy template\n"; 
    std::cout << "\nThe possible OPTIONs are as follows:\n";
    std::cout << "- --help                  Print this help message\n";
    std::cout << "- --print-game            Print the parity game (same format as input)\n";
    std::cout << "- --print-game=pg         Print the parity game in pgsolver format\n";
    std::cout << "- --print-template-size   Print size of the templates\n";
    std::cout << "\nExample usage:\n";
    std::cout << "pestel --print-template-size < example.pg\n";
}

int main(int argc, char* argv[]) {
    try {
        bool print_game = false; // Flag to determine if game should be printed (same format as input)
        bool print_game_pg = false; // Flag to determine if game should be printed in pgsolver format
        bool print_template_size = false; // Flag to determine if template size should be printed

        for (int i = 1; i < argc; ++i) {
            if (std::string(argv[i]) == "--print-game") {
                print_game = true;
            } else if (std::string(argv[i]) == "--print-template-size") {
                print_template_size = true;
            } else if (std::string(argv[i]) == "--print-game=pg") {
                print_game_pg = true;
            } else if (std::string(argv[i]) == "--help") {
                printHelp();
                return 0;
            } else {
                printHelpN(std::string(argv[i]));
                return 0;
            }
        }

        /* construct the game */
        std::string game_str; /* game as a string*/
        mpa::MultiGame G = std2multgame(game_str);

        /* print the game if print_game or print_game_pg is true */
        if (print_game_pg){
            multigame2gpg(G);
            std::cout << "===================================================\n";
        } else if (print_game){
            std::cout << game_str;
            std::cout << "\n===================================================\n";
        }
        
        
        /* compute and print the strategy template */
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

        /* print the size of the templates if print_template_size is true */
        if (print_template_size){
            std::cout << "\n#" << "winning_vertices"<<part_win << ":"<< winning_region.first.size()<< "/"<<G.n_vert_<<"\n";
            std::cout << "#unsafe_edges:"<< unsafe_edges.size()<<"\n";
            std::cout << "#colive_edges:"<< colive_edge_set.size()<<"\n";
            std::cout << "#live_groups:"<< live_group_set.size()<<"\n";
            std::cout <<"**==================================================\n";
        }

        return 1;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        printHelp();
        return 0;
    }
}

