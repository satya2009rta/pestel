/*
 * conflictsPUF.cpp
 *
 *  A program to find the conflicts for the strategy template for 2-player games with permanent availability faults (PUF)
 *  The input is to be given as a text file */

#include "FileHandler.hpp"

/* command line inputs:
 *
 *  [1]: input file name
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
        std::vector<size_t> COL;
        /* check if the file is a .gm (pgsolver) file  */
        if(ends_with(filename, ".gm")){
            /* covert pgsolver format to normal game */
            pg2game(filename, N, V_ID, TR, COL);
        }
        else { /* read the number of vertices and vertex id, etc. directly from file */
            std2game(filename, N, V_ID, TR, COL);
        }
        /* construct the game */
        mpa::MultiGame G(N, V_ID, TR, COL);

        /* read percentage of PUF edges */
        std::float_t percentage = std::atof(argv[2]);
        /* compute the number of PUF edges */
        size_t num = 1+G.n_edge_*percentage/100;
        
        /* read the number of repeatition */
        std::size_t max_iter = std::atof(argv[3]);

        /* number of conflicts */
        double conflicts_size = 0;
        /* compute the conflicts iteratively */
        for (size_t i = 0; i < max_iter; i++){
            /* generate the PUF edges */
            auto PUF_edges = G.generate_PUF_edges(num);
            /* compute the conflicts */
            std::unordered_set<size_t> conflicts;
            G.conflicts_recomputation_PUF_parity(PUF_edges, conflicts);   
            conflicts_size += conflicts.size();
        }
        auto avg = 100*conflicts_size/(G.n_vert_*max_iter);
        if (conflicts_size != 0){
            /* print informations about the PUF game */
            std::cout << filename << "," << G.n_vert_ << "," << G.n_edge_ << "," << G.max_color_+1 << "," << num << "," << percentage << "," << avg<< "\n";;
        }
        return 0;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return -1;
    }
}

