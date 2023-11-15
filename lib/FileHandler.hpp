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

#define NOF_VERTEX   "NOF_VERTEX"
#define VERTEX_ID   "VERTEX_ID"
#define TRANSITIONS   "TRANSITIONS"
#define NOF_GAMES "NOF_GAMES"
#define COLORS  "COLORS"


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
/// Reading something from file
///////////////////////////////////////////////////////////////

/*! Read a member from a file. (A member is an attribute whose value is a scalar.)
 * \param[in] filename  Name of the file
 * \param[in] member_value  Reference to the variable that will contain the read member value
 * \param[in] member_name     The name of the member whose value is to be read
 * \param[out] out_flag          A flag that is 0 when reading was unsuccessful, and is 1 when reading was successful*/
template<class T>
int readMember(const std::string& filename, T& member_value, const std::string& member_name) {
    std::ifstream file;
    file.open(filename);
    std::string line;
    if (file.is_open()) {
        while(std::getline(file,line)) {
            /* check if a match is found with the member_name */
            if(line.find(member_name)!=std::string::npos) {
                /* the data is in the next line*/
                if(std::getline(file,line)) {
                  std::istringstream stream(line);
                  stream >> member_value;
                } else {
                    try {
                        throw std::runtime_error("FileHandler:readMember: Unable to read data member");
                    } catch (std::exception &e) {
                        std::cout << e.what() << "\n";
                        return 0;
                    }
                }
                file.close();
                return 1;
            }
        }
        /* while loop exited and data member was not found */
        try {
            throw std::runtime_error("FileHandler:readMember: Member not found.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    } else {
        try {
            throw std::runtime_error("FileHandler:readMember: Unable to open input file.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    }
}


/*! Read 1-dimensional vector from file
 * \param[in] filename  Name of the file
 * \param[in] v                  Reference to the vector that will contain the read vector value
 * \param[in] no_elem     The size of the vector
 * \param[in] vec_name     The name of the vector whose value is to be read
 * \param[out] out_flag          A flag that is 0 when reading was unsuccessful, and is 1 when reading was successful*/
template<class T>
int readVec(const std::string& filename, std::vector<T>& vec, size_t no_elem, const std::string& vec_name) {
    std::ifstream file;
    file.open(filename);
    if (file.is_open()) {
        std::string line;
        /* go through all the lines until a match with arr_name is found */
        while(std::getline(file,line)) {
            if(line.find(vec_name)!=std::string::npos) {
                for (size_t i=0; i<no_elem; i++) {
                    if(std::getline(file,line)) {
                        std::stringstream line_stream(line);
                        /* first character should be the index of the vector element */
                        size_t index;
                        line_stream >> index;
                        // if (index >= no_elem) {
                        //     try {
                        //         throw std::runtime_error("FileHandler:readVecSet: Index out of bound.");
                        //     } catch (std::exception &e) {
                        //         std::cout << e.what() << "\n";
                        //         return 0;
                        //     }
                        // }
                        // /* add empty elements for all the missing indices */
                        // for (size_t j = i; j < index; j++, i++) {
                        //     T t;
                        //     vec.push_back(t);
                        // }
                        if (index != i) {
                            try {
                                throw std::runtime_error("FileHandler:readVec: Missing index.");
                            } catch (std::exception &e) {
                                std::cout << e.what() << "\n";
                                return 0;
                            }
                        }
                        /* ignore all the characters until a colon is seen */
                        line_stream.ignore(std::numeric_limits<std::streamsize>::max(), ':');
                        /* add the next element and ignore the rest of the line */
                        T t;
                        line_stream >> t;
                        vec.push_back(t);
                    } else {
                        try {
                            throw std::runtime_error("FileHandler:readVec: Unable to read vector.");
                        } catch (std::exception &e) {
                            std::cout << e.what() << "\n";
                            return 0;
                        }
                    }
                }
                file.close();
                return 1;
            }
        }
        /* while loop exited and the vec was not found */
        try {
            throw std::runtime_error("FileHandler:readVecSet: Vector not found.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    } else {
        try {
            throw std::runtime_error("FileHandler:readVecSet: Unable to open input file.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    }
}

/*! Read 1-dimensional integer set (unordered) from file
 * NOTE: NO LINE BREAK IS ALLOWED!
 * \param[in] filename  Name of the file
 * \param[in] s                  Reference to the set that will contain the read set value
 * \param[in] no_elem     The size of the set
 * \param[in] set_name     The name of the set whose value is to be read
 * \param[out] out_flag          A flag that is 0 when reading was unsuccessful, and is 1 when reading was successful*/
template<class T>
int readSet(const std::string& filename, std::unordered_set<T>& s, size_t no_elem, const std::string& set_name) {
    std::ifstream file;
    file.open(filename);
    if (file.is_open()) {
        std::string line;
        while(std::getline(file,line)) {
            if(line.find(set_name)!=std::string::npos) {
                for (size_t i=0; i<no_elem; i++) {
                    if(std::getline(file,line)) {
                        std::stringstream stream(line);
                        std::locale loc;
                        if (!std::isdigit(line[0],loc)) {
                            try {
                                throw std::runtime_error("FileHandler:readSet: Number of rows do not match with number of elements.");
                            } catch (std::exception &e) {
                                std::cout << e.what() << "\n";
                                return 0;
                            }
                        } else {
                            T val;
                            stream >> val;
                            s.insert(val);
                        }
                    } else {
                        try {
                            throw std::runtime_error("FileHandler:readSet: Unable to read set.");
                        } catch (std::exception &e) {
                            std::cout << e.what() << "\n";
                            return 0;
                        }
                    }
                }
                file.close();
                return 1;
            }
        }
        /* while loop exited and the set was not found */
        try {
            throw std::runtime_error("FileHandler:readSet: Set not found.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    } else {
        try {
            throw std::runtime_error("FileHandler:readSet: Unable to open input file.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    }
}

/*! Read vector of pointers to unordered sets (can be thought of as a 2-d table) from file
 *  NOTE: NO LINE BREAK IS ALLOWED!
 * \param[in] filename  Name of the file
 * \param[in] vec             Reference to the vector that will contain the read vector value
 * \param[in] no_elem     The size of the vector
 * \param[in] vec_name     The name of the vector whose value is to be read
 * \param[out] out_flag          A flag that is 0 when reading was unsuccessful, and is 1 when reading was successful*/
template<class T>
int readVecSet(const std::string& filename, std::vector<std::unordered_set<T>>& vec, size_t no_elem, const std::string& vec_name) {
    std::ifstream file;
    file.open(filename);
    if (file.is_open()) {
        std::string line;
        /* go through all the lines until a match with arr_name is found */
        while(std::getline(file,line)) {
            if(line.find(vec_name)!=std::string::npos) {
                for (size_t i=0; i<no_elem; i++) {
                    if(std::getline(file,line)) {
                        if (line == "") { /* the line is empty */
                            /* no more members, fill the remaining positions with empty sets */
                            for (size_t j = i; j < no_elem; j++, i++) {
                                std::unordered_set<T> set;
                                vec.push_back(set);
                            }
                        } else {
                            std::stringstream line_stream(line);
                            /* first character should be the index of the vector element */
                            size_t index;
                            line_stream >> index;
                            if (index >= no_elem) {
                                try {
                                    throw std::runtime_error("FileHandler:readVecSet: Index out of bound.");
                                } catch (std::exception &e) {
                                    std::cout << e.what() << "\n";
                                    return 0;
                                }
                            }
                            if (index < i) {
                                try {
                                    throw std::runtime_error("FileHandler:readVecSet: Repeated index.");
                                } catch (std::exception &e) {
                                    std::cout << e.what() << "\n";
                                    return 0;
                                }
                            }
                            /* add empty sets for all the missing indices */
                            for (size_t j = i; j < index; j++, i++) {
                                std::unordered_set<T> set;
                                vec.push_back(set);
                            }
                            /* ignore all the characters until a colon is seen */
                            line_stream.ignore(std::numeric_limits<std::streamsize>::max(), ':');
                            /* create a set for the current index */
                            std::unordered_set<T> set;
                            while (line_stream.good()) {
                                T x;
                                line_stream >> x;
                                if (!line_stream.fail()) {
                                    set.insert(x);
                                }
                            }
                            vec.push_back(set);
                        }
                    } else {
                        try {
                            throw std::runtime_error("FileHandler:readVecSet: Unable to read vector.");
                        } catch (std::exception &e) {
                            std::cout << e.what() << "\n";
                            return 0;
                        }
                    }
                }
                file.close();
                return 1;
            }
        }
        /* while loop exited and the vec was not found */
        try {
            throw std::runtime_error("FileHandler:readVecSet: Vector not found.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    } else {
        try {
            throw std::runtime_error("FileHandler:readVecSet: Unable to open input file.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
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

/*! read a game in pgsolver format from a file and convert it to normal game
 * \param[in] file  filestream or Name of the file
 * \param[out] N     Number of vertices
 * \param[out] V_ID  Vector containing owner of the vertices
 * \param[out] TR_final    Transition vector
 * \param[out] COL   Vector of colors */
int pg2game(std::istream& file,
                size_t& N,
                std::vector<size_t>& V_ID,
                std::vector<std::unordered_set<size_t>>& TR_final,
                std::vector<size_t>& COL){
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
        return 1;
}
int pg2game(const std::string& filename,
                size_t& N,
                std::vector<size_t>& V_ID,
                std::vector<std::unordered_set<size_t>>& TR_final,
                std::vector<size_t>& COL){

    std::ifstream file(filename);
    return pg2game(file,N,V_ID,TR_final,COL);
}



/*! read a generalized parity game in gpgsolver format from a file and convert it to normal game
 * \param[in] file  filestream or Name of the file
 * \param[out] N     Number of vertices
 * \param[out] V_ID  Vector containing owner of the vertices
 * \param[out] TR_final    Transition vector
 * \param[out] N_GAME   Number of games
 * \param[out] ALL_COL   Vectors of all colors */
int gpg2game(std::istream& file,
                size_t& N,
                std::vector<size_t>& V_ID,
                std::vector<std::unordered_set<size_t>>& TR_final,
                size_t& N_GAME,
                std::vector<std::vector<size_t>>& ALL_COL){
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
        return 1;
}
int gpg2game(const std::string& filename,
                size_t& N,
                std::vector<size_t>& V_ID,
                std::vector<std::unordered_set<size_t>>& TR_final,
                size_t& N_GAME,
                std::vector<std::vector<size_t>>& ALL_COL){
        std::ifstream file(filename);
        return gpg2game(file,N,V_ID,TR_final,N_GAME,ALL_COL);
}



/*! read a generalized parity game in standard format from a file and convert it to normal game
 * \param[in] filename  Name of the file
 * \param[out] N     Number of vertices
 * \param[out] V_ID  Vector containing owner of the vertices
 * \param[out] TR    Transition vector
 * \param[out] COL   Vectors of all colors */
int std2game(const std::string& filename,
                size_t& N,
                std::vector<size_t>& V_ID,
                std::vector<std::unordered_set<size_t>>& TR,
                std::vector<size_t> & COL){
    if (!readMember(filename, N, NOF_VERTEX)) {
        throw std::runtime_error("Missing/badly entered number of vertices.\n");
    }
    if (!readVec(filename, V_ID, N, VERTEX_ID)) {
        throw std::runtime_error("Missing/badly entered player id-s of vertices.\n");
    }
    if (!readVecSet(filename, TR, N, TRANSITIONS)) {
        throw std::runtime_error("Missing/badly entered transition matrix.\n");
    }
    
    if (!readVec(filename, COL, N, COLORS)) {
        throw std::runtime_error("Missing/badly entered colors of the vertices.\n");
    }
    return 1;
}

/*! read a generalized parity game in standard format from a file and convert it to normal game
 * \param[in] filename  Name of the file
 * \param[out] N     Number of vertices
 * \param[out] V_ID  Vector containing owner of the vertices
 * \param[out] TR    Transition vector
 * \param[out] N_GAME   Number of games
 * \param[out] ALL_COL   Vectors of all colors */
int std2multigame(const std::string& filename,
                size_t& N,
                std::vector<size_t>& V_ID,
                std::vector<std::unordered_set<size_t>>& TR,
                size_t& N_GAME,
                std::vector<std::vector<size_t>>& ALL_COL){
    if (!readMember(filename, N, NOF_VERTEX)) {
        throw std::runtime_error("Missing/badly entered number of vertices.\n");
    }
    if (!readVec(filename, V_ID, N, VERTEX_ID)) {
        throw std::runtime_error("Missing/badly entered player id-s of vertices.\n");
    }
    if (!readVecSet(filename, TR, N, TRANSITIONS)) {
        throw std::runtime_error("Missing/badly entered transition matrix.\n");
    }
    std::vector<size_t> COL;
    if (!readVec(filename, COL, N, COLORS)){
        throw std::runtime_error("Missing/badly entered colors of the vertices.\n");
    }
    ALL_COL.push_back(COL);
    if (!readMember(filename, N_GAME, NOF_GAMES)) {
        std::cout<<"Number of games is assumed to be 2 as it is not provided.\n";
        std::vector<size_t> COL;
        if (!readVec(filename, COL, N, COLORS + std::to_string(2))){
            std::cout<<"Number of games is assumed to be 1 one set of colors provided.\n";
            N_GAME = 1;
        }
        else{
            ALL_COL.push_back(COL);
            N_GAME = 2;
        }
    }
    for (size_t i = 2; i <= N_GAME; i++){
        std::vector<size_t> COL;
        if (!readVec(filename, COL, N, COLORS + std::to_string(i))){
            throw std::runtime_error("Missing/badly entered colors of the vertices.\n");
        }
        ALL_COL.push_back(COL);
    }
    return 1;
}