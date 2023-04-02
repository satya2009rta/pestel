/*
 * Class: MultiGame
 *
 * Class formalizing two parity games
 */

#ifndef MULTIGAME_HPP_
#define MULTIGAME_HPP_

#include "Game.hpp"
#include <chrono>
#include <random>

// #include "FileHandler.hpp"


namespace mpa {
class MultiGame: public Game {
public:
    /* number games */
    size_t n_games_;
    /* all_colors: the i-th vector represents i-th color set */
    std::vector<std::map<size_t, size_t>> all_colors_;
    
public:
    /* basic constructor from given explicit representation of multiple games */
    MultiGame(size_t n_vert,
        std::vector<size_t> vert_id,
        std::vector<std::unordered_set<size_t>> tr,
        size_t n_games,
        std::vector<std::vector<size_t>> all_colors): Game(n_vert, vert_id, tr, all_colors[0]), n_games_(n_games){
        /* compute the maximum color */
        max_color_ = 0;
        for (auto colors : all_colors){
            std::map<size_t, size_t> cols;
            for (size_t i = 0; i < n_vert_; i++){
                max_color_ = std::max(max_color_, colors[i]);
                cols.insert(std::make_pair(i, colors[i]));
            }
            all_colors_.push_back(cols);
        }
    }

    /* basic constructor from given explicit representation of a single game */
    MultiGame(size_t n_vert,
         std::vector<size_t> vert_id,
         std::vector<std::unordered_set<size_t>> tr,
         std::vector<size_t> colors): Game(n_vert, vert_id, tr, colors){
        n_games_ = 1;
        all_colors_.push_back(colors_);
    }

    /* copy constructor */
    MultiGame(const MultiGame& other): Game(other) {
        n_vert_ = other.n_vert_;
        n_edge_ = other.n_edge_;
        vertices_ = other.vertices_;
        edges_ = other.edges_;
        vert_id_ = other.vert_id_;
        max_color_ = other.max_color_;
        n_games_ = other.n_games_;
        all_colors_ = other.all_colors_;
    }

    /* default constructor */
    MultiGame(): Game() {}

    ///////////////////////////////////////////////////////////////
    ///MultiGame operators
    ///////////////////////////////////////////////////////////////

    /* merging a new game */
    void mergeGame(const Game newGame){
        if (n_vert_ == 0){/* current multigame is empty */
            n_vert_ = newGame.n_vert_;
            n_edge_ = newGame.n_edge_;
            vertices_ = newGame.vertices_;
            edges_ = newGame.edges_;
            vert_id_ = newGame.vert_id_;
            max_color_ = newGame.max_color_;
            n_games_ = 1;
            all_colors_.push_back(newGame.colors_);
            colors_ = newGame.colors_;
        }
        else{
            /* sanity check for two games having same game graph */
            // if (n_vert_ != newGame.n_vert_ || n_edge_ != newGame.n_edge_ || vert_id_ != newGame.vert_id_ || edges_ != newGame.edges_ || vertices_ != newGame.vertices_)
            //     std::cerr << "[ERROR] mergeGame: The game graph of the new game is different.\n";
            n_games_ += 1; /* number of games is increased by one */
            max_color_ = std::max(max_color_, newGame.max_color_); /* max_color is updated */
            all_colors_.push_back(newGame.colors_); /* colors is added to all_colors vector */
        }
    }

    /* find the n-th game */
    Game nthGame(const size_t n) const{
        mpa::Game game(*this);
        game.colors_ = all_colors_[n];
        game.max_color_ = max_col(game.colors_);
        return game;
    }

    /* replace the multigame */
    void copy(const MultiGame& other){
        n_vert_ = other.n_vert_;
        n_edge_ = other.n_edge_;
        vertices_ = other.vertices_;
        edges_ = other.edges_;
        vert_id_ = other.vert_id_;
        max_color_ = other.max_color_;
        colors_ = other.colors_;
        n_games_ = other.n_games_;
        all_colors_ = other.all_colors_;
    }

    ///////////////////////////////////////////////////////////////
    ///Game to multigame with random sets of colors
    ///////////////////////////////////////////////////////////////

    /* generate and add n_games sets of colors to get a multigame */
    void randMultigame(const size_t n_games, const size_t max_col, const bool clear = true){
        if (clear){/* remove all previous colors if clear is true */
            all_colors_.clear();
            n_games_ = 0;
        }
        /* update number of games */
        n_games_ += n_games;
        /* update max_color */
        max_color_ = max_col;
        /* add n_games set of random colors */
        for (size_t i = 0; i < n_games; i++){
            all_colors_.push_back(random_colors(max_col));
        }
    }

    /* generate a set of random colors <= max_col */
    std::map<size_t, size_t> random_colors(const size_t max_col){
        std::map<size_t, size_t> colors;
        
        /* a vector of all vertices */
        std::vector<size_t> vertices(vertices_.begin(), vertices_.end());
        
        size_t min_num = n_vert_/(2*max_col); /* each color has atleast this many vertices */
        std::vector<size_t> remaining_vert = vertices; /* remaining vertices to be colored (initially all) */
        size_t remaining_num = n_vert_-1; /* number of remaining vertices - 1 (initially n_vert_-1) */
            
        /* randomly choose min_num vertices for each color */
        for (size_t col = 0; col <= max_col; col++){
            for (size_t i = 0; i < min_num; i++){
                size_t rand_index = random_num(remaining_num); /* generate random index */
                size_t vertex = remaining_vert[rand_index]; /* vertex at rand_index in remaining vertices */
                
                colors.insert(std::make_pair(vertex, col)); /* set color of that vertex as col */
                remaining_vert.erase(remaining_vert.begin() + rand_index); /* remove that vertex from remaining vertices */
                remaining_num -= 1; /* update remaining number of vertices */
            }
        }
        /* randomly choose color for remaining vertices */
        for (auto vertex : remaining_vert){
            size_t rand_col = random_num(max_col); /* generate random color */
            colors.insert(std::make_pair(vertex, rand_col)); /* set color of vertex to rand_col */
        }
        return colors;
    }

    /* random number from [0,n] */
    size_t random_num(const size_t max) const {
        std::random_device rd; /* obtain a random number from hardware */
        std::mt19937 gen(rd()); /* seed the generator */
        std::uniform_int_distribution<> distr(0, max); /* define the range */

        return distr(gen); /* generate numbers */
    }


    ///////////////////////////////////////////////////////////////
    ///Compose templates of multiple games
    ///////////////////////////////////////////////////////////////
    
    /* compute the composition of permissive strategy template for two games */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> find_composition_template(std::map<size_t, std::unordered_set<size_t>>& unsafe_edges,
                                    std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                                    std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set) const {
        /* clear the template */
        colive_edge_set.clear();
        live_group_set.clear();

        /* solve the games without changing anything in the original game */
        MultiGame multigame_copy(*this); /* copy of the multi-game */
        auto winning_region = multigame_copy.recursive_composition_template(colive_edge_set, live_group_set);
        /* unsafe edges are the player 0's edges from winning region to losing region */
        unsafe_edges = edges_between(winning_region.first, set_complement(winning_region.first));
        /* return winning region */
        return winning_region;
    }

    /* recursively compute the composition of strategy template for two games */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> recursive_composition_template(std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                                    std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set,
                                    const bool add_spec = false) {
        auto winning_region = std::make_pair(vertices_, std::unordered_set<size_t> {}); /* winning region of the games */
        std::vector<std::unordered_set<size_t>> i_winning_regions(n_games_); /* winning region of i-th game */
        std::vector<std::map<size_t, std::unordered_set<size_t>>> i_colive_edge_sets(n_games_); /* colive edges for i-th game */
        std::vector<std::vector<std::map<size_t, std::unordered_set<size_t>>>> i_live_group_sets(n_games_); /* live-groups for i-th game */
        std::unordered_set<size_t> colive_vertices; /* vertices with color 2d+1 */
        // size_t counter = 0; /* count thenumber of iteration */

        if (n_games_ == 1){ /* if there is only one game, solve in standard way */
            Game game = nthGame(0);
            winning_region =  game.recursive_strategy_template_parity(colive_edge_set,live_group_set);
            /* print to analyze the results */
            // std::cout << "couter:"<<counter<< "  colive:"<<colive_vertices.size()<<"  winning:"<<winning_region.first.size()<<"\n"; 
            return winning_region; /* return winning region */
        }

        bool new_spec = add_spec; /* another boolean variable for new/add_spec as we want to modify it later */
        while (true){/* iterate until there is no need to solve any game again */
            if (new_spec){ /* if a new_spec is added to previous game */    
                size_t i = n_games_-1;
                mpa::Game game = nthGame(i); /* i-th game */
                /* compute template and winning region of i-th game */
                i_winning_regions[i] = game.recursive_strategy_template_parity(i_colive_edge_sets[i], i_live_group_sets[i]).first;
            }
            else{ /* no new_spec, we start a new itearation */
                /* compute template for every game */
                #pragma omp parallel
                #pragma omp for 
                for (size_t i = 0; i < n_games_; i++){
                    size_t colive_color = max_odd(all_colors_[i]); /* minimum odd color >= max color */
                    for (const size_t v : colive_vertices){/* set color of all colive vertices colive_color */
                        all_colors_[i].at(v) = colive_color;
                    }
                    mpa::Game game = nthGame(i); /* i-th game */
                    
                    /* compute template and winning region of i-th game */
                    i_winning_regions[i] = game.recursive_strategy_template_parity(i_colive_edge_sets[i], i_live_group_sets[i]).first;
                }
            }

            /* compute intersection of all winning regions and merge the templates */
            for (size_t i = 0; i < n_games_; i++){
                if (new_spec){
                    i = n_games_-1;
                    new_spec = false; /* set new_spec to false */
                }
                winning_region.first = set_intersection(winning_region.first,i_winning_regions[i]);
                for (auto v : vertices_){
                    set_merge(colive_edge_set[v],i_colive_edge_sets[i][v]);
                }
                live_group_set.insert(live_group_set.end(), i_live_group_sets[i].begin(),i_live_group_sets[i].end());
                i_colive_edge_sets[i].clear();
                i_live_group_sets[i].clear();
            }
            winning_region.second = set_complement(winning_region.first); /* compute total losing region */
            colive_vertices.clear(); /* clear the colive vertices for new iteration */
            
            /* compute conflicts by colive edges (containing all outgoing edges of a vertex) */
            conflict_colive(colive_edge_set, winning_region, colive_vertices);
            /* compute conflicts by colive edges and live groups */
            conflict_live_colive(live_group_set, colive_edge_set, winning_region, colive_vertices);

            /* first remove losing region from everywhere */
            remove_vertices(winning_region.second);
            colive_vertices = set_difference(colive_vertices, winning_region.second);
                
            
            /* print to analyze the results */
            // counter += 1;
            // if (counter <= 2){
            //     std::cout << "couter:"<<counter<< "  colive:"<<colive_vertices.size()<<"  losing:"<<winning_region.second.size()<<"\n";
            // }
            

            /* check if there is no conflicts by live groups and colive edges */
            if (colive_vertices.empty()){/* if no conflicts by live colive edges, then check conflict by unsafe edges */
                /* check if there is no conflicts by unsafe edges */
                if (!conflict_unsafe(live_group_set, colive_edge_set, winning_region)){
                    /* remove the unsafe edges and edges from losing region from colive edge set */
                    map_remove_vertices(colive_edge_set, winning_region.second);
                    /* remove the restrictions on losing regions and colive edges from live group (as there is other choice from that source) */
                    for (auto& live_group : live_group_set){
                        map_remove_keys(live_group, winning_region.second);
                        map_remove(live_group, colive_edge_set);
                    }
                    /* remove duplicates in live_group_set */
                    vec_erase_duplicate(live_group_set);
                    break; /* break the loop as there is no more conflict */
                }
            }

            /* clear the template */
            colive_edge_set.clear();
            live_group_set.clear();
        }
        /* print to analyze the results */
        // std::cout << "couter:"<<counter<< "  colive:"<<colive_vertices.size()<<"  winning:"<<winning_region.first.size()<<"\n"; 
        return winning_region; /* return winning region */
    }
    
    /* Check if the unsafe edges create some conflict */
    bool conflict_unsafe(std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set,
                            std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                            const std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region) {
        for (auto v : winning_region.first){
            if (!edges_.at(v).empty() && check_set_inclusion(edges_.at(v), set_union(winning_region.second, colive_edge_set[v]))){
                return true; /* return true if there is a conflict */
            }
        }                
        for (auto& live_group : live_group_set){ /* iterate over all live groups to compute live_unsafe_region */
            for (auto v : winning_region.first){
            if (!live_group[v].empty() &&  check_set_inclusion(live_group[v], set_union(winning_region.second, colive_edge_set[v]))){
                    return true; /* return true if there is a conflict */
                }
            }
        }
        return false; /* return false if there is no conflict (no dead-ends) */
    }

    /* check conflict when the union of all colive edge set contains all edges of some vertex */
    void conflict_colive(const std::map<size_t, std::unordered_set<size_t>> colive_edge_set, 
                        const std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region,
                        std::unordered_set<size_t>& colive_vertices) {
        for (auto it = colive_edge_set.begin(); it != colive_edge_set.end(); it++){
            auto v = it ->first;
            if (winning_region.first.find(v)!= winning_region.first.end() && !edges_.at(v).empty() && check_set_inclusion(edges_.at(v), it->second)){
                /* if all edges of a source is colive then add the source to colive vertices */
                colive_vertices.insert(v);
            }
        }      
    }

    /* solve the conflict when the intersection of colive edges and live groups is non-empty */
    void conflict_live_colive(std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set,
                                const std::map<size_t, std::unordered_set<size_t>> colive_edge_set,
                                const std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region,
                                std::unordered_set<size_t>& colive_vertices) {
        std::unordered_set<size_t> conflict_keys; /* sources of the possible conflict edges */
        for (auto& live_group : live_group_set){ /* iterate over all live groups */
            for (auto it = colive_edge_set.begin(); it != colive_edge_set.end(); it++){
            auto v = it ->first;
            if (winning_region.first.find(v)!= winning_region.first.end() && !live_group[v].empty() && check_set_inclusion(live_group[v], it->second)){
                    /* for any conflict source, if there is no other choice in the live group
                    then there is a conflict */
                    /* if there is conflict then add the source to colive vertices */
                    colive_vertices.insert(v);
                }
            }
        }
    }


    ///////////////////////////////////////////////////////////////
    ///Parity games with PUF (permanent unavailability fault)
    ///////////////////////////////////////////////////////////////

    /* randomly choose a % of PUF edges */
    std::map<size_t, std::unordered_set<size_t>> generate_PUF_edges(size_t num) const {
        /* initialize the PUF_edges set */
        std::map<size_t, std::unordered_set<size_t>>  PUF_edges;

        /* generate PUF edge *num* many times */
        for (size_t i = 1; i <= num; i++){
            /* generate random index (with max index as the current number of edges excluding PUF edges) of an edge to add it to PUF_edges */
            size_t rand_index = random_num(n_edge_-num);
            size_t counter = 0; /* counter for indices of edges */
            for (auto u : vertices_){
                for (auto v : edges_.at(u)){ /* iterate over all edges */
                    if (PUF_edges[u].find(v) == PUF_edges[u].end()){ /* if (u,v) is not PUF edge */
                        if (counter == rand_index){ /* if this is the edge at rand_index, then add it to PUF_edges */
                            PUF_edges[u].insert(v);
                        }
                        /* increase the counter as the this edge was not PUF earlier, and hence, not counter before */
                        counter += 1; 
                    }
                }
            }
        }
        return PUF_edges;
    }

    /* check if it needs re-computation for solving parity games with PUF  */
    bool need_recomputation_PUF_parity(std::map<size_t, std::unordered_set<size_t>>& PUF_colive_edge_set) const {
        /* initialize the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        auto colive_edge_set = PUF_colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        /* copy the game to not change the original game */
        MultiGame game_copy = *this; 

        /* compute the initial strategy template with initializing PUF edges as colive (to use it to check implementability) */
        auto winning_region = game_copy.recursive_strategy_template_parity(colive_edge_set, live_group_set);

        /* compute and add the dead-ends to losing region */
        game_copy.compute_dead_ends(PUF_colive_edge_set,winning_region);

        /* return true if the template is implementable else false */
        return game_copy.conflict_unsafe(live_group_set, colive_edge_set, winning_region);
    }

    /* compute (and add it to losing region) the dead-ends created by the PUF edges and the unsafe edges */
    int compute_dead_ends(std::map<size_t, std::unordered_set<size_t>>& PUF_colive_edge_set, std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>>& winning_region) {
        bool need_iteration = true;
        while (need_iteration){
            winning_region.first = set_complement(winning_region.second);
            need_iteration = false;
            for (auto v : winning_region.first){
                if (!edges_.at(v).empty() && check_set_inclusion(edges_.at(v), set_union(winning_region.second, PUF_colive_edge_set[v]))){
                    winning_region.second.insert(v); /* add it to losing region if it is a dead-end */
                    need_iteration = true;
                }
            }  
        }
        return 1;              
    }


    /* compute the conflicted vertices due to PUF edges */
    int conflicts_recomputation_PUF_parity(std::map<size_t, std::unordered_set<size_t>>& PUF_colive_edge_set, std::unordered_set<size_t>& conflicts) const {
        /* initialize the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        auto colive_edge_set = PUF_colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        /* copy the game to not change the original game */
        MultiGame game_copy = *this; 

        /* compute the initial strategy template with initializing PUF edges as colive (to use it to check implementability) */
        auto winning_region = game_copy.recursive_strategy_template_parity(colive_edge_set, live_group_set);

        /* compute and add the dead-ends to losing region */
        game_copy.compute_dead_ends(PUF_colive_edge_set,winning_region);

        /* compute the final conflicts */
        return game_copy.compute_conflict_unsafe(live_group_set, colive_edge_set, winning_region, conflicts);
    }
    /* compute the conflicted vertices due to unsafe edges and colive edges */
    int compute_conflict_unsafe(std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set,
                            std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                            const std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region,
                            std::unordered_set<size_t>& conflicts) {
        ;
        for (auto v : winning_region.first){
            if (!edges_.at(v).empty() && check_set_inclusion(edges_.at(v), set_union(winning_region.second, colive_edge_set[v]))){
                conflicts.insert(v);
            }
        }                
        for (auto& live_group : live_group_set){ /* iterate over all live groups to compute live_unsafe_region */
            for (auto v : winning_region.first){
            if (!live_group[v].empty() &&  check_set_inclusion(live_group[v], set_union(winning_region.second, colive_edge_set[v]))){
                    conflicts.insert(v);
                }
            }
        }
        return 1;
    }

    


    ///////////////////////////////////////////////////////////////
    ///Solve generalized parity games using multi-games
    ///////////////////////////////////////////////////////////////
    /* solve generalized parity game  */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_gen_parity() const {
        /* initialize the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        std::map<size_t, std::unordered_set<size_t>> colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        return find_composition_template(unsafe_edges, colive_edge_set, live_group_set);
    }

    /* solve generalized parity game by adding specs iteratively */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_gen_parity_add_spec(const int iterate = 2) const {
        /* initialize the strategy template */
        std::map<size_t, std::unordered_set<size_t>> colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        
        MultiGame multigame_copy(*this); /* copy of the multi-game */
        return multigame_copy.recursive_gen_parity_add_spec(iterate, colive_edge_set, live_group_set);
    }

    /* recursive version of solve_gen_parity_add_spec */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> recursive_gen_parity_add_spec(const int iterate,
                                std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                                std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set) {
        // std::cout <<"R\n";
        if (n_games_ < 2 || iterate == 1){ /* base case */
            // std::cout <<"B\n";
            return recursive_composition_template(colive_edge_set, live_group_set);
        }
        std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> winning_region;
        /* store the last color to add later */
        std::map<size_t,size_t> colors = all_colors_[all_colors_.size()-1];
    
        /* remove the last set of color */
        n_games_ -= 1;
        all_colors_.pop_back();
        
        winning_region = recursive_gen_parity_add_spec(iterate-1, colive_edge_set, live_group_set);
        /* now add the last set of color and solve game using pre-computed template */
        all_colors_.push_back(colors);
        n_games_ += 1;
        remove_vertices(winning_region.second);
        // std::cout <<"F\n";
        winning_region = recursive_composition_template(colive_edge_set, live_group_set, true);
        /* return winning region */
        return winning_region;
    }

    ///////////////////////////////////////////////////////////////
    ///Solve generalized parity games using GenZielonka
    ///////////////////////////////////////////////////////////////
    // std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> gen_zielonka() const {
    //     mpa::MultiGame copy(*this);
    //     copy.complement();
    //     std::vector<size_t> maxValues;
    //     for (size_t i = 0; i < n_games_; i++){
    //         maxValues.push_back(max_odd(all_colors_[i]));
    //     }
    //     return copy.disj_parity_win(maxValues, 0);
    // }

    // void complement(){
    //     for (size_t v = 0; v < n_vert_; v++){
    //         for (size_t i = 0; i < n_games_; i++){
    //             all_colors_[i].at(v) += 1;
    //         }
    //     }
    //     max_color_ += 1;
    // }

    // std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> disj_parity_win(const std::vector<size_t> maxValues, const int u){
    //     /* sanity check: max value of each priority to be odd! */
    //     for (size_t i = 0; i < n_games_; i++){
    //         if (maxValues[i] % 2 == 0){
    //             std::cerr << "Error::disj_parity_win: maxValues are not all odd \n";
    //         }
    //     }

    //     if (maxValues == std::vector<size_t>(n_games_,1) || vertices_.empty()){
    //         return std::make_pair(vertices_, std::unordered_set<size_t>{});
    //     }
    //     MultiGame G1;
    //     MultiGame H1;
    //     for (size_t i = 0; i < n_games_; i++){
    //         if (maxValues[i] != 1){
    //             auto attMaxOdd = solve_reachability_game(i_priority_node_function_j(maxValues[i],i), {V0});
                
    //             G1.copy(subgame(attMaxOdd.second));
    //             auto attMaxEven = G1.solve_reachability_game(i_priority_node_function_j(maxValues[i]-1, i), {V1});
                
    //             H1.copy(G1.subgame(attMaxEven.second));
                
    //             while (true){
    //                 std::vector<size_t> copy_maxValues = maxValues;
    //                 copy_maxValues[i] -= 2;

    //                 /* sanity check */
    //                 if (copy_maxValues[i] < 0 || copy_maxValues[i] != maxValues[i]-2){
    //                     std::cout << "Error::disj_parity_win: copy_maxValues is not correct. \n";
    //                 }

    //                 auto W1 = H1.disj_parity_win(copy_maxValues, u+1);
                    
    //                 if (G1.n_vert_ == 0 || W1.second.size() == H1.n_vert_){
    //                     if (W1.second.size() == H1.n_vert_ && G1.n_vert_ > 0){
    //                         auto B = solve_reachability_game(G1.vertices_, {V1});
                            
    //                         MultiGame newGame(subgame(B.second));
    //                         return newGame.disj_parity_win(maxValues, u+1);
    //                     }
    //                     else{
    //                         break;
    //                     }
    //                 }

    //                 auto T = G1.solve_reachability_game(W1.first, {V0});
    //                 G1.remove_vertices(T.second);
    //                 auto E = G1.solve_reachability_game(i_priority_node_function_j(maxValues[i]-1, i), {V1});
                    
    //                 H1.copy(G1.subgame(E.second));
    //             }
    //         }
    //     }
    //     return std::make_pair(vertices_, std::unordered_set<size_t>{});
    // }

    // std::unordered_set<size_t> i_priority_node_function_j(size_t i, size_t j){
    //     std::unordered_set<size_t> result;
    //     for (auto v : vertices_){
    //         if (all_colors_[j].at(v) == i){
    //             result.insert(v);
    //         }
    //     }
    //     return result;
    // }

    

    ///////////////////////////////////////////////////////////////
    ///Solve parity games using multiple {0,1,2,3}-parity games
    ///////////////////////////////////////////////////////////////

    /* convert the parity game to multiple small games */
    void parityToMultigame(){
        /* sanity check: number of games should be 1 */
        if (n_games_ != 1 || all_colors_.size() != 1){
            std::cerr << "[ERROR] parityToMultigame: Only one game is needed.\n";
        }
        /* clear the multigame parts except gamegraph (all_colors, n_games) */
        all_colors_.clear();
        n_games_ = 0;

        /* for every odd color create a new color_vector for new game */
        for (size_t odd_col = 1; odd_col <= max_color_; odd_col+= 2){
            std::map<size_t, size_t> colors; /* new color vector */
            for (auto vertex : vertices_){/* loop through each vertex */
                if (colors_[vertex] < odd_col){ 
                    colors.insert(std::make_pair(vertex,0)); /* new color of vertices with color < odd_col is 0 */
                }
                else if (colors_[vertex] == odd_col){
                    colors.insert(std::make_pair(vertex,1)); /* new color of vertices with color = odd_col is 1 */
                }
                else{
                    if (colors_[vertex]%2 == 0){
                        colors.insert(std::make_pair(vertex,2)); /* new color of vertices with even color > odd_col is 2 */
                    }
                    else{
                        colors.insert(std::make_pair(vertex,1)); /* new color of vertices with odd color > odd_col is 1 */
                    }
                } 
            }
            all_colors_.push_back(colors);
            n_games_ += 1;
        }
    }

    /* find strategy template for parity game after converting it to multiple small games */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> find_composed_strategy_template_parity(std::map<size_t, std::unordered_set<size_t>>& unsafe_edges,
                                    std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                                    std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set) const {
        mpa::MultiGame copy(*this);
        copy.parityToMultigame();
        return copy.find_composition_template(unsafe_edges, colive_edge_set, live_group_set);
    }
    
    /* solve parity game using composition of small games */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_composed_parity() const {
        /* initialize the strategy template */
        std::map<size_t, std::unordered_set<size_t>> unsafe_edges;
        std::map<size_t, std::unordered_set<size_t>> colive_edge_set;
        std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set;
        return find_composed_strategy_template_parity(unsafe_edges, colive_edge_set, live_group_set);
    }

    
    ///////////////////////////////////////////////////////////////
    ///Basic functions
    ///////////////////////////////////////////////////////////////

    /* function: max_odd
     *
     * return minimum odd color that is greater than or equal to max_color */
    size_t max_odd(const std::map<size_t, size_t> colors) const {
        size_t odd_col = 1;
        for (auto const & col : colors){
            if (col.second%2 == 1 && col.second > odd_col)
                odd_col = col.second;
            else if (col.second%2 == 0 && col.second > odd_col)
                odd_col = col.second+1;
        }
        return odd_col;
    }

    /* function: vec_erase_duplicate
     *
     * erase duplicates in a vector */
    template<class T>
    void vec_erase_duplicate(std::vector<T>& vec) const {
        std::vector<T> new_vec;
        for (auto element : vec){
            if (std::find(new_vec.begin(), new_vec.end(), element) == new_vec.end()){
                new_vec.push_back(element);
            }
        }
        vec = new_vec;
    }


    /* function: remove_vertices
     *
     * remove vertices from the game */
    
    void remove_vertices(const std::unordered_set<size_t> set) {
        vertices_= set_complement(set);
        n_vert_ = vertices_.size();
        
        map_remove_keys(vert_id_, set);
        
        for (auto& colors: all_colors_){
            map_remove_keys(colors, set);
            max_color_ = std::max(max_color_, max_col(colors));
        }
        colors_ = all_colors_[0];

        map_remove_keys(edges_, set);
        n_edge_ = 0;
        for (auto v : vertices_){
            edges_.at(v) = set_difference(edges_.at(v),set);
            n_edge_ += edges_.at(v).size();
        }
        /* sanity check */
        // valid_game();
    }

    /* function: subgame
     *
     * returns a subgame restricted to this set */
    
    MultiGame subgame(const std::unordered_set<size_t> set) const{
        MultiGame game(*this);
        game.n_vert_ = set.size();
        game.vertices_= set;

        std::unordered_set<size_t> complement = set_complement(set);
        map_remove_keys(game.vert_id_, complement);
        
        for (auto& colors: game.all_colors_){
            map_remove_keys(colors, set);
            game.max_color_ = std::max(game.max_color_, max_col(colors));
        }
        game.colors_ = game.all_colors_[0];

        map_remove_keys(game.edges_, set);
        game.n_edge_ = 0;
        for (auto v : game.vertices_){
            game.edges_.at(v) = set_difference(game.edges_.at(v),complement);
            game.n_edge_ += game.edges_.at(v).size();
        }
        /* sanity check */
        // game.valid_game();

        return game;
    }

    /* function: map_remove
     *
     * remove set of values from one map (set of edges) */
    
    void map_remove(std::map<size_t, std::unordered_set<size_t>>& map2, const std::map<size_t, std::unordered_set<size_t>> map1) const {
        for (auto v = map1.begin(); v != map1.end(); v++){
            map2[v->first] = set_difference(map2[v->first], v->second);
        }
    }

    
}; /* close class definition */
} /* close namespace */

#endif