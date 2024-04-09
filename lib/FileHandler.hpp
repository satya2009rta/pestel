/* FileHandler.hpp */

#include <filesystem>
#include <iostream>
#include <sstream>
#include <fstream>
#include <locale>
#include <vector>
#include <unordered_set>
#include <dirent.h>
#include <sys/stat.h>
#include <cstring>
#include <cstdlib>
#include <chrono>

#include "MultiGame.hpp"
#include "hoa_consumer_build_parity_game.hh"


///////////////////////////////////////////////////////////////
/// File/Folder operations
///////////////////////////////////////////////////////////////

/* Check if input is a .hoa file, then we use the hoa game constructor */
inline bool ends_with(std::string const & value, std::string const & ending)
{
    if (ending.size() > value.size()) return false;
    return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
}

/*! Ensures that a specified subdirectory exists.
*  \param[in]  dirName     Name of the desired subdirectory.
*/
template <class dir_type>
void checkMakeDir(dir_type dirName) {
    DIR* dir = opendir(dirName);
    if (dir) {
        closedir(dir);
    }
    else if (ENOENT == errno) {
        int result = mkdir(dirName, 0777);
        (void) result;
    }
 }

 /*! Create a file OR erase previous data written to a file
 * \param[in] filename  The name of the file*/
void create(const std::string& filename) {
    std::ofstream file;
    file.open(filename, std::ofstream::out | std::ofstream::trunc);
    if (file.is_open()) {
        file.close();
    }
}


///////////////////////////////////////////////////////////////
/// Read/Write different game formats
///////////////////////////////////////////////////////////////

/*! output a multigame to gpg format 
 * \param[in] Multigame  */
int multigame2gpg(const mpa::MultiGame G, std::ostream& ostr = std::cout){
    /* print first line */
    ostr<< "parity "<< G.n_vert_-1 <<";\n"; 
    for (size_t v = 0; v < G.n_vert_; v++){ /* print the following for each vertex */
        ostr << v << " "; /* vertex name (number) */

        ostr<<G.all_colors_[0].at(v); /* print color in 1st game separately to avoid comma */
        for (size_t i = 1; i < G.n_games_; i++){/* for each other game print color of v with comma */
            ostr<<","<<G.all_colors_[i].at(v);
        }
        
        ostr << " " << G.vert_id_.at(v) << " "; /* print vertex id (which player it belongs to) */
        
        if (!G.edges_.at(v).empty()){ /* if v has neighbours then print them */
            size_t counter = 0;
            for (auto u : G.edges_.at(v)){ /* print all neighbours */
                if (counter == 0){
                    ostr <<u;
                    counter = 1;
                }
                else{
                    ostr <<","<<u;
                }
            }
        }
        ostr<<"\n";
    }
    return 0;
}

/*! read a game in extended hoa format from a file/input and convert it to normal game
 * \param[in] filename  Name of the file OR
 * \param[in] issr input stream */
mpa::Game hoa2game(std::istream& issr){
    mpa::Game G;
    cpphoafparser::HOAConsumer::ptr consumer;
    cpphoafparser::parity_game_data data;
    consumer.reset(new cpphoafparser::HOAConsumerBuildParityGame(&data));
    cpphoafparser::HOAParser::parse(issr, consumer);

    G.n_vert_ = data.n_vert;
    G.n_edge_ = data.n_edge;
    G.vertices_ = data.vertices;
    G.edges_ = data.edges;
    G.vert_id_ = data.vert_id;
    G.max_color_ = data.max_color;
    G.colors_ = data.colors;

    return G;
}
mpa::Game hoa2game(const std::string filename){
    std::ifstream file(filename);
    return hoa2game(file);
    
}

/*! read a game in pgsolver format from a file and convert it to normal game */
mpa::Game pg2game(std::istream& file){
    size_t N;
    std::vector<size_t> V_ID;
    std::vector<std::unordered_set<size_t>> TR_final;
    std::vector<size_t> COL;
    std::vector<size_t> V_name;
    std::vector<std::unordered_set<size_t>> TR;
    std::vector<size_t> ICOL;
    size_t max_col=0;
        std::string line;
        /* go through all the lines until a match with arr_name is found */
        while(std::getline(file,line)) {
            std::stringstream line_stream(line);
            std::string name;
            line_stream >> name;
            /* check for the header line starting with "parity" */
            if (name == "parity"){
                break; /* break the loop when header line found */
            }
        }
        N=0; /* initialize number of vertics = 0 */
        while(std::getline(file,line)) {
            std::stringstream line_stream(line);
            N = N+1;
            /* first number is vertex id */
            size_t id;
            line_stream >> id;
            /* second number is color of that vertex */
            size_t color;
            line_stream >> color;
            /* third number is owner of that vertex */
            size_t owner_id;
            line_stream >> owner_id;
            /* set the color and owner of that vertex */
            V_name.push_back(id);
            V_ID.push_back(owner_id);
            COL.push_back(color);
            max_col = std::max(color,max_col);
            ICOL.push_back(color%2+1);
            
            std::string successors; /* string of successors of that vertex */
            line_stream >> successors;
            std::stringstream ss(successors);
            std::unordered_set<size_t> trans_list;
            /* update transitions of that vertex */
            for (size_t i; ss >> i; ++ i) {
                trans_list.insert(i);   
                // std::cout << i << ",";
                if (ss.peek() == ',')
                    ss.ignore();
            }
            TR.push_back(trans_list);
        }
        for (auto it = TR.begin(); it != TR.end(); ++ it){
            std::unordered_set<size_t> trans_list;
            std::unordered_set<size_t> set = *it;
            for (auto i : set){
                trans_list.insert(std::distance(V_name.begin(), find(V_name.begin(),V_name.end(),i)));
            }
            TR_final.push_back(trans_list);
        }
        // if (max_col==1){
            // COL = ICOL; /* buchi ehoa to buchi pgsolver */
        // }
        mpa::Game G(N, V_ID, TR_final, COL);
        return G;
}
mpa::Game pg2game(const std::string& filename){
    std::ifstream file(filename);
    return pg2game(file);
}

/* read a game from std::cin */
mpa::Game std2game(std::istream& file = std::cin){
    size_t pg = 2; /* determine if the format is psolver (default: 2 = undecided) */
    /* construct the game from stdin */
    std::string str, line;
    while (std::getline(file, line)){
        str += "\n" + line;
        if (pg == 2){
            std::stringstream line_stream(line);
            std::string name;
            line_stream >> name;
            /* check for the header line starting with "parity" then it is pgsolver format */
            if (name == "parity"){
                pg = 1;
            }
            /* check for the header line starting with "HOA:" then it is hoa format */
            else if (name == "HOA:"){
                pg = 0;
            }
        }
        if (pg == 0){
            if (line.find("END") != std::string::npos){
                break;
            }
        }
    }
    std::istringstream issr(str);
    if (pg == 1){
        return pg2game(issr);
    }
    return hoa2game(issr);
}

/*! read a game in pgsolver/ehoa format from a file and convert it to normal game
 * \param[in] filename  Name of the file */
mpa::Game file2game(const std::string& filename){
    std::ifstream file(filename);
    return std2game(file);
}





/*! read a generalized parity game in gpgsolver format from a file and convert it to normal game
 * \param[in] file  filestream or Name of the file
*/
mpa::MultiGame gpg2multgame(std::istream& file){
    size_t N;
    std::vector<size_t> V_ID;
    std::vector<std::unordered_set<size_t>> TR_final;
    size_t N_GAME;
    std::vector<std::vector<size_t>> ALL_COL;
    std::vector<size_t> V_name;
    std::vector<std::unordered_set<size_t>> TR;
        std::string line;
        /* go through all the lines until a match with arr_name is found */
        while(std::getline(file,line)) {
            std::stringstream line_stream(line);
            std::string name;
            line_stream >> name;
            /* check for the header line starting with "parity" */
            if (name == "parity"){
                break; /* break the loop when header line found */
            }
        }
        N=0; /* initialize number of vertics = 0 */
        N_GAME = 0; /* initialize number of games = 0 */
        bool n_games_set = false; /* if the number of games is known */
        while(std::getline(file,line)) {
            std::stringstream line_stream(line);
            N = N+1;
            /* first number is vertex id */
            size_t id;
            line_stream >> id;
            /* second string is colors of that vertex */
            std::string colors; /* string of colors of that vertex */
            line_stream >> colors;
            std::stringstream ss_col(colors);
            /* add the colors of that vertex */
            if (!n_games_set){ /* first time when number of games is not known */
                for (size_t i; ss_col >> i; ++ i) {
                    N_GAME += 1;
                    ALL_COL.push_back(std::vector<size_t>(1,i)); /* insert a new vector of colors with first color i */
                    if (ss_col.peek() == ',')
                        ss_col.ignore();
                }
                n_games_set = true;
            }
            else{
                size_t counter_games = 0; /* number of colors seen - 1 */
                for (size_t i; ss_col >> i; ++ i) {
                    ALL_COL[counter_games].push_back(i);
                    counter_games += 1;
                    if (ss_col.peek() == ',')
                        ss_col.ignore();
                }
            }
            /* third number is owner of that vertex */
            size_t owner_id;
            line_stream >> owner_id;
            /* set the owner of that vertex */
            V_name.push_back(id);
            V_ID.push_back(owner_id);
            
            std::string successors; /* string of successors of that vertex */
            line_stream >> successors;
            std::stringstream ss(successors);
            std::unordered_set<size_t> trans_list;
            /* update transitions of that vertex */
            for (size_t i; ss >> i; ++ i) {
                trans_list.insert(i);   
                // std::cout << i << ",";
                if (ss.peek() == ',')
                    ss.ignore();
            }
            TR.push_back(trans_list);
        }
        for (auto it = TR.begin(); it != TR.end(); ++ it){
            std::unordered_set<size_t> trans_list;
            std::unordered_set<size_t> set = *it;
            for (auto i : set){
                trans_list.insert(std::distance(V_name.begin(), find(V_name.begin(),V_name.end(),i)));
            }
            TR_final.push_back(trans_list);
        }
        mpa::MultiGame G(N, V_ID, TR_final, N_GAME, ALL_COL);
        return G;
}
mpa::MultiGame gpg2multgame(const std::string& filename){
        std::ifstream file(filename);
        return gpg2multgame(file);
}
mpa::MultiGame std2multgame(std::istream& file = std::cin){
    size_t pg = 2; /* determine if the format is psolver (default: 2 = undecided) */
    /* construct the game from stdin */
    std::string str, line;
    while (std::getline(file, line)){
        str += "\n" + line;
        if (pg == 2){
            std::stringstream line_stream(line);
            std::string name;
            line_stream >> name;
            /* check for the header line starting with "parity" then it is pgsolver format */
            if (name == "parity"){
                pg = 1;
            }
            /* check for the header line starting with "HOA:" then it is hoa format */
            else if (name == "HOA:"){
                pg = 0;
            }
        }
        if (pg == 0){
            if (line.find("END") != std::string::npos){
                break;
            }
        }
    }
    std::istringstream issr(str);
    if (pg == 1){
        return gpg2multgame(issr);
    }
    mpa::MultiGame G;
    G.mergeGame(hoa2game(issr));
    return G;
}
mpa::MultiGame file2multgame(const std::string& filename){
    std::ifstream file(filename);
    return std2multgame(file);
}


