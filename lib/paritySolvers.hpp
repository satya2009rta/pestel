/* paritySolvers.hpp */

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
#include <functional>

#include "MultiGame.hpp"

///////////////////////////////////////////////////////////////
/// Printing informations
///////////////////////////////////////////////////////////////

/* print game informations */
int print_game(mpa::Game G){
    std::cout << "Game constructed! #vertices:"<<G.n_vert_<<"  #edges:"<<G.n_edge_<<"  #colors:"<<G.max_color_+1<<"\n";
    return 1;
}

/* print multi-game informations */
int print_game(mpa::MultiGame G){
    std::cout << "\nGame constructed! #vertices:"<<G.n_vert_<<"  #edges:"<<G.n_edge_<<"  #colors:"<<G.max_color_+1<<"  #games:"<<G.n_games_<<"\n";
    return 1;
}

/* print method completion informations */
template<class T>
int print_method(const T method,const int size,const size_t total_size,const int time,const int ptime = -1, bool init = false){
    if (size == -1){
        std::cout << "Method"<<method<<" Timed out!\n";
    }
    else if (ptime == -1){
        if (init){
            std::cout << "Method"<<method<<" completed! size = "<<size << "/"<<total_size<< "; time:"<<time<< "(INIT)\n";
        }
        else{
            std::cout << "Method"<<method<<" completed! size = "<<size << "/"<<total_size<< "; time:"<<time<< "\n";
        }
    }
    else{
        if (init){
            std::cout << "Method"<<method<<" completed! size = "<<size << "/"<<total_size<< "; time:"<<time<<"; ptime:"<<ptime<< "(INIT)\n";
        }
        else{
            std::cout << "Method"<<method<<" completed! size = "<<size << "/"<<total_size<< "; time:"<<time<<"; ptime:"<<ptime<< "\n";
        }
    }
    return 1;
}


/* compare time and size and print the informations */
template<class T>
int compareTime(const T method, const std::string time, const int actual_windom_size, int standard_time, const int windom_size, const int our_tool_time){
    if (method == 0){
        if (windom_size == -1){ 
            std::cout << ","<<"0"<<"," << std::stoi(time)*1000;
            standard_time = std::stoi(time)*1000;
        }
        else if (actual_windom_size == -1){
            std::cout << ","<<"0"<<"," << standard_time;
        }
        else if (windom_size < actual_windom_size){
            std::cout << ","<< "1" <<","<< standard_time;
        }
        else{
            std::cout << ","<< "0" <<","<< standard_time;
        }
    }
    else{
        if (windom_size == -1){
            std::cout << ","<< std::stoi(time)*1000 << ","<<"0";
            standard_time = std::stoi(time)*1000;
        }
        else if (actual_windom_size == -1){
            std::cout << ","<<"0"<<"," << standard_time;
        }
        else if (windom_size < actual_windom_size){
            std::cout << ","<< standard_time << ","<<"1";
        }
        else{
            std::cout << ","<< standard_time << ","<<"0";
        }
    }
    if (standard_time < our_tool_time){
        std::cout << ","<<"0";
    }
    else{
        std::cout << ","<<"1";
    }
    return windom_size;
}


///////////////////////////////////////////////////////////////
/// Operations for Perez genParity solvers
///////////////////////////////////////////////////////////////

/*! Read winning region from output of python file of generalized-parity solvers
* \param[in] filename  Name of the file */
template<class T>
int readGPGwin(const std::string& filename, T& win_size, T& init) {
    std::ifstream file;
    file.open(filename);
    std::string line;
    if (file.is_open()) {
        /* the data is in the next line*/
        std::getline(file,line);
        std::getline(file,line);
        // std::cout << line << "\n";
        if(std::getline(file,line)) {
            // std::cout<<"\n"<<line << "\n";
            /* if 0 in winning region */
            if(line.find("(INIT)")!=std::string::npos){
                init = 0;
            }
            else{
                init = 1;
            }
            
            std::istringstream stream(line);
            std::string str;
            stream >> str; /* "#winning_vertices:win/total" */
            str = str.substr(18,-1); /* win/total */
            std::stringstream ss(str);
            ss >> win_size;
        } else {
            return 0;
        }
        file.close();
        try {
            if (std::filesystem::remove(filename))
                return 1;
        }
        catch(const std::filesystem::filesystem_error& err) {
            std::cout << "filesystem error: " << err.what() << '\n';
        }
        return 1;
    } else {
        try {
            throw std::runtime_error("FileHandler:readGPGwin: Unable to open input file.");
        } catch (std::exception &e) {
            std::cout << e.what() << "\n";
            return 0;
        }
    }
}

/* run the genParity solvers */
int genParityMethods(const std::string filename, const std::string method,
                    const std::string path = "./lib/solveGenParity.py",
                    const int time = 300, 
                    const std::string output_file = "./log"){
    std::string script = "timeout "+std::to_string(time)+" python2 -u "+path+" \""+filename+"\" "+method+" > "+output_file;
    const char *cstr = script.c_str();

    system(cstr);
    int win_size;
    int init;
    if (readGPGwin(output_file, win_size, init))
        return win_size;
    return -1;
}
int genParityMethods(const std::string filename, const int int_method,
                    const std::string path = "./lib/solveGenParity.py",
                    const int time = 300, 
                    const std::string output_file = "./log"){
    std::string method = std::to_string(int_method);
    return genParityMethods(filename, method, path, time, output_file);
}
