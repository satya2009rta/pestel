/*
 * pestel.cpp
 *
 *  A program to compute a winning strategy templates for (generalized) parity games
 *  It reuires stdin input as which is the description of a (generalized) parity game in extended HOA or pgsolver format; and outputs the result to stdout */

#include "FileHandler.hpp"

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
    std::cout << "- --localize              Print only a local template for each state in JSON format\n";
    std::cout << "- --print-actions         Print the template with actions instead of edges (only for games with labels on edges)\n";
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
        bool print_actions = false; // Flag to determine if labels should be printed
        bool localize = false; // Flag to determine if only local templates should be printed

        for (int i = 1; i < argc; ++i) {
            if (std::string(argv[i]) == "--print-game") {
                print_game = true;
            } else if (std::string(argv[i]) == "--print-template-size") {
                print_template_size = true;
            } else if (std::string(argv[i]) == "--print-game=pg") {
                print_game_pg = true;
            } else if (std::string(argv[i]) == "--print-actions") {
                print_actions = true;   
            } else if (std::string(argv[i]) == "--localize") {
                localize = true;
            } else if (std::string(argv[i]) == "--help") {
                printHelp();
                return 0;
            } else {
                printHelpN(std::string(argv[i]));
                return 0;
            }
        }

        /* construct games from stdin */
        mpa::MultiGame G = std2multigame();

        /* print the game if print_game or print_game_pg is true */
        if (print_game_pg){
            multigame2gpg(G);
            std::cout << "===================================================\n";
        } else if (print_game){
            multigame2std(G);
            std::cout << "\n===================================================\n";
        }
        
        /* compute the strat template */
        std::pair<std::set<size_t>, std::set<size_t>> winning_region;

        mpa::Template strat;
        winning_region = G.find_composition_template(strat);
        strat.clean();
        /* remove edge-states from result (needned for HOA formatted games) */
        G.filter_out_edge_states(winning_region, strat, print_actions);

        /* if localize is true then print only local templates in JSON format and exit */
        if (localize){
            G.print_local_templates(strat, winning_region.first, print_actions);
            return 0;
        }

        auto str_win = "Winning Region";
        if (G.n_games_ > 1) {
            str_win = "(Partial) Winning Region";
        }
        G.print_set(winning_region.first, str_win);

        /* print the strategy template with edges if print_actions is false else with labels */
        strat.print_template();
        std::cout << "*===================================================\n";
        
        /* print the size of the templates if print_template_size is true */
        if (print_template_size){
            std::cout << "\n#winning_vertices:"<< winning_region.first.size()<< "/"<<winning_region.first.size()+winning_region.second.size()<<"\n";
            strat.print_size();
            std::cout <<"**==================================================\n";
        }

        if (winning_region.first.find(G.init_vert_) != winning_region.first.end()){
            std::cout << "REALIZABLE!\n";
            return 0;
        }
        else{
            std::cout << "UNREALIZABLE!\n";
            return 1;
        }
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        printHelp();
        return -1;
    }
}

