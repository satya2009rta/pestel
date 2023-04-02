/*
 * solvePUF.cpp
 *
 *  A program to find strategy template for 2-player games with permanent availability faults (PUF)
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

        /* print informations about the PUF game */
        std::cout << filename << "," << G.n_vert_ << "," << G.n_edge_ << "," << G.max_color_+1 << "," << num << "," << percentage << ",";
        

        /* generate the PUF edges */
        auto PUF_edges = G.generate_PUF_edges(num);
        // G.print_edges(PUF_edges);
        /* check if it needs re-computation */
        if (G.need_recomputation_PUF_parity(PUF_edges)){
            std::cout << "1\n";
            return 1;
        }
        std::cout << "0\n";
        return 0;
    }
    /* TODO: print the same output in the output file */
    catch (const std::exception &ex) {
        std::cout << ex.what() << "\n";
        return -1;
    }
}

