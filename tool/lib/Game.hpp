/*
 * Class: Game
 *
 *  Class formalizing a basic two player (parity) game
 */

#ifndef GAME_HPP_
#define GAME_HPP_

#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_set>
#include <map>
#include <queue>
#include <algorithm>

#define V0 0 /* vertices belonging to player 0 */
#define V1 1 /* vertices belonging to player 1 */

namespace mpa {
class Game {
public:
    /* number of vertices */
    size_t n_vert_;
    /* number of edges */
    size_t n_edge_;
    /* vertices */
    std::unordered_set<size_t> vertices_;
    /* vertex id: V0, when the vertex belongs to player 0 and V1 when it belongs to player 1 */
    std::map<size_t, size_t> vert_id_;
    /* edges as a map from vertices to set of its neighbours */
    std::map<size_t, std::unordered_set<size_t>> edges_;
    /* number of colors */
    size_t max_color_;
    /* colors of vertices */
    std::map<size_t, size_t> colors_;
public:
    /* default constructor */
    Game() {
        n_vert_ = 0;
        n_edge_ = 0;
    }
    /* basic constructor from given explicit representation of the game graph */
    Game(size_t n_vert,
         std::vector<size_t> vert_id,
         std::vector<std::unordered_set<size_t>> tr,
         std::vector<size_t> colors): n_vert_(n_vert){
        /* sanity check for vertex id-s */
        // for (auto i = vert_id_.begin(); i != vert_id_.end(); ++i) {
        //     if ((*i != V0) && (*i != V1)) {
        //         std::cerr << "[WARNING] Invalid assignment of vertices to player 0 and player 1.\n";
        //     }
        // }
        
        n_edge_ = 0; /* initialize number of edges = 0 */
        /* populate everything for each vertex */
        max_color_ = 0;
        for (size_t i = 0; i < n_vert_; i++){
            vertices_.insert(i);
            vert_id_.insert(std::make_pair(i, vert_id[i]));
            colors_.insert(std::make_pair(i, colors[i]));
            max_color_ = std::max(max_color_, colors[i]);

            edges_.insert(std::make_pair(i, tr[i]));
            n_edge_ += tr[i].size();
        }
    }

    /* copy constructor */
    Game(const Game& other){
        n_vert_ = other.n_vert_;
        n_edge_ = other.n_edge_;
        vertices_ = other.vertices_;
        edges_ = other.edges_;
        vert_id_ = other.vert_id_;
        max_color_ = other.max_color_;
        colors_ = other.colors_;
    }

    ///////////////////////////////////////////////////////////////
    /// Solving all types of games
    ///////////////////////////////////////////////////////////////

    /* solve reachability game for player i (default is player 0)
     * input: target
     * output: Reach_i(target) */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_reachability_game(const std::unordered_set<size_t> target,
                                                    const std::unordered_set<size_t> players = {V0}) const {
        std::unordered_set<size_t> losing; /* vertices from which targets might not be reachable */
        std::unordered_set<size_t> winning = target; /* vertices from which targets are currently reachable */
        while (true)
        {
            losing = set_complement(winning); /* complement of vertices from which targets are currently reachable */
            std::unordered_set<size_t> new_winning; /* new vertices from which targets are currently reachable */
            for (size_t v: losing){ /* new_winning =  cpre_i(winning) */
                if(players.find(vert_id_.at(v)) != players.end() && check_set_intersection(edges_.at(v),winning))
                    new_winning.insert(v);
                else if(check_set_inclusion(edges_.at(v),winning) && edges_.find(v) != edges_.end())
                    new_winning.insert(v);
            }
            if (new_winning.empty()){ /* if there is no new winning vertex then return winning */
                losing = set_complement(winning);
                return std::make_pair(winning, losing);
            }
            set_merge(winning, new_winning); /* include the new targets in winning */
        }
    }

    /* solve Buechi game 
     * input: target
     * output: winning region for player 0 */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_buchi_game(const std::unordered_set<size_t> target) const {
        Game subgame = *this; /* copy the game */
        std::unordered_set<size_t> non_target = set_complement(target); /* vertices which are not target */
        /* in the subgame (copy of the game), target vertices has color 2 
        and non-target vertices have color 1 */
        for (size_t v: target) 
            subgame.colors_.at(v) = 2;
        for (size_t v: non_target)
            subgame.colors_.at(v) = 1;
        return subgame.solve_parity_game(); /* solve the 2-color parity game using parity algo */
    }

    /* solve Co-Buechi game 
     * input: target (Eventually Always [target])
     * output: winning region for player 0 */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_cobuchi_game(const std::unordered_set<size_t> target) const {
        Game subgame = *this; /* copy the game */
        std::unordered_set<size_t> non_target = set_complement(target); /* vertices which are not target */
        /* in the subgame (copy of the game), target vertices has color 2 
        and non-target vertices have color 1 */
        for (size_t v: target)
            subgame.colors_.at(v) = 0;
        for (size_t v: non_target)
            subgame.colors_.at(v) = 1;
        return subgame.solve_parity_game(); /* solve the 2-color parity game using parity algo */
    }


    /* solve parity game using Zielonka's algorithm
     * input: game with colors
     * output: winning region for player 0 */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> solve_parity_game() const {
        Game game_copy(*this); /* copy of the game as we will change it */
        return game_copy.recursive_zielonka_parity();
    }
    /* recursive zielonka's algorithm */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> recursive_zielonka_parity() const {
        if (n_vert_ == 0) /* if current region is empty, nothing to do, return empty */
            return std::make_pair(vertices_, vertices_);
        /* vertices with maximum color */
        std::unordered_set<size_t> max_col_vertices = vertex_with_color(max_color_);
        if (max_color_ % 2 == 1){ /* when max_color_ is odd */
            /* vertices from which player 1 can force to visit max_col_vertices (odd) */
            auto regionA = solve_reachability_game(max_col_vertices, {V1});
            /* complement of regionA */
            Game gameCA(subgame(regionA.second)); /* game with regionA removed */
            /* solve the gameCA */
            auto winCA = gameCA.recursive_zielonka_parity();
            if (winCA.first.empty()) /* if winning region is empty in gameCA then return everything empty */
                return std::make_pair(winCA.first, vertices_);
            else {
                /* vertices from which player 0 can force to reach winning region of gameCA */
                auto regionB = solve_reachability_game(winCA.first, {V0});
                Game gameCB(subgame(regionB.second)); /* game with regionB removed */
                /* solve gameCB */
                auto winCB = gameCB.recursive_zielonka_parity();
                return std::make_pair(set_union(winCB.first, regionB.first), winCB.second); /* winning region is regionB \cup winning region of gameCB */
            }
        }
        else{ /* max_color_ is even */
            /* vertices from which player 0 can force to visit max_col_vertices (even) */
            auto regionA = solve_reachability_game(max_col_vertices, {V0});
            /* complement of regionA */
            Game gameCA(subgame(regionA.second)); /* game with regionA removed */
            /* solve the gameCA */
            auto winCA = gameCA.recursive_zielonka_parity();
            if (winCA.second.empty()){ /* if losing region is empty */
                return std::make_pair(vertices_, winCA.second); /* winning region is whole set */
            }
            else {
                /* vertices from which player 1 can force to reach losing region of gameCA */
                auto regionB = solve_reachability_game(winCA.second, {V1});
                Game gameCB(subgame(regionB.second)); /* game with regionB removed */
                /* solve gameCB */
                auto winCB = gameCB.recursive_zielonka_parity();
                return std::make_pair(winCB.first, set_union(winCB.second, regionB.first)); /* winning region is winning region of gameCB */
            }
        }
    }


    ///////////////////////////////////////////////////////////////
    ///Buechi games
    ///////////////////////////////////////////////////////////////
    
    /* compute the permissive strategy template for Buechi game */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> find_strategy_template_buchi(const std::unordered_set<size_t> target,
                                std::map<size_t, std::unordered_set<size_t>>& unsafe_edges,
                                std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set) const {
        /* initialize the template */
        live_group_set.clear();

        /* first compute the winning region */
        auto winning_region = solve_buchi_game(target);
        /* unsafe edges are the player 0's edges from winning region to losing region */
        unsafe_edges = edges_between(winning_region.first, winning_region.second);
        /* copy the subgame restricted to winning region */
        Game game_copy(subgame(winning_region.first));
        game_copy.find_live_groups_reach(target, winning_region.first, live_group_set);
        return winning_region;
    }

    void find_live_groups_reach(const std::unordered_set<size_t> target,
                                const std::unordered_set<size_t> winning_region,
                                std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set) const {
        std::unordered_set<size_t> curr_target = target;
        /* keep finding live groups until convergence to the winning region */
        while (1) {
            /* vertices from which no player can stop reaching cuurent winning region */
            auto curr_winning_region = solve_reachability_game(curr_target, {});
            if (curr_winning_region.first.size() == winning_region.size()) {
                break;
            }
            curr_target = curr_winning_region.first; /* current target is the winnign region of last reachability game */
            /* add live group containing player0 edges from outiside to winning region; and add their sources to curr_target */
            live_group_set.push_back(edges_between(curr_winning_region.second, curr_winning_region.first, curr_target));
        }
    }



    ///////////////////////////////////////////////////////////////
    ///Parity games
    ///////////////////////////////////////////////////////////////

    /* compute the permissive strategy template for parity game */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> find_strategy_template_parity(std::map<size_t, std::unordered_set<size_t>>& unsafe_edges,
                std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set) const {
        /* clear the template */
        colive_edge_set.clear();
        live_group_set.clear();

        /* compute template recursively */
        auto winning_region = recursive_strategy_template_parity(colive_edge_set, live_group_set);
        /* unsafe edges are the player 0's edges from winning region to losing region */
        unsafe_edges = edges_between(winning_region.first, winning_region.second);
        /* remove unsafe edges from colive edges set */
        map_remove_vertices(colive_edge_set, winning_region.second);
        return winning_region;
    }

    /* compute the set of live groups and colive edges recursively */
    std::pair<std::unordered_set<size_t>, std::unordered_set<size_t>> recursive_strategy_template_parity(
                                    std::map<size_t, std::unordered_set<size_t>>& colive_edge_set,
                                    std::vector<std::map<size_t, std::unordered_set<size_t>>>& live_group_set,
                                    const size_t& u = 0) const {
        // std::cout << u<<"\n";
        if (n_vert_ == 0) /* if current region is empty, nothing to do, return empty */
            return std::make_pair(vertices_, vertices_);
        /* vertices with maximum color */
        std::unordered_set<size_t> max_col_vertices = vertex_with_color(max_color_);
        if (max_color_ % 2 == 1){ /* when max_color_ is odd */
            /* vertices from which player 1 can force to visit max_col_vertices (odd) */
            auto regionA = solve_reachability_game(max_col_vertices, {V1});
            /* complement of regionA */
            Game gameCA(subgame(regionA.second)); /* game with regionA removed */
            /* solve the gameCA */
            auto winCA = gameCA.recursive_strategy_template_parity(colive_edge_set, live_group_set,u+1);
            if (winCA.first.empty()) /* if winning region is empty in gameCA then return everything empty */
                return std::make_pair(winCA.first, vertices_);
            else {
                /* vertices from which player 0 can force to reach winning region of gameCA */
                auto regionB = solve_reachability_game(winCA.first, {V0});
                /* edges from winning region of gameCA to regionB (all are player 0's) are colive */
                edges_between(winCA.first,set_complement(winCA.first), colive_edge_set);
                /* live groups needed to reach winCA from regionB */
                find_live_groups_reach(winCA.first,regionB.first,live_group_set);

                Game gameCB(subgame(regionB.second)); /* game with regionB removed */
                /* solve gameCB */
                auto winCB = gameCB.recursive_strategy_template_parity(colive_edge_set,live_group_set,u+1);
                return std::make_pair(set_union(winCB.first, regionB.first), winCB.second); /* winning region is regionB \cup winning region of gameCB */
            }
        }
        else{ /* max_color_ is even */
            /* vertices from which player 0 can force to visit max_col_vertices (even) */
            auto regionA = solve_reachability_game(max_col_vertices, {V0});
            /* complement of regionA */
            Game gameCA(subgame(regionA.second)); /* game with regionA removed */
            /* solve the gameCA with output in new template */
            std::map<size_t, std::unordered_set<size_t>> colive_edge_setCA = colive_edge_set;
            std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_setCA = live_group_set;
            auto winCA = gameCA.recursive_strategy_template_parity(colive_edge_setCA,live_group_setCA,u+1);
            if (winCA.second.empty()){ /* if losing region is empty */
                /* output template gameCA is merged with actual template */
                live_group_set = live_group_setCA;
                colive_edge_set = colive_edge_setCA;
                /* live groups needed to reach max even color from regionA */
                find_live_groups_reach(max_col_vertices,regionA.first,live_group_set);
                return std::make_pair(vertices_, winCA.second); /* winning region is whole set */
            }
            else {
                /* vertices from which player 1 can force to reach losing region of gameCA */
                auto regionB = solve_reachability_game(winCA.second, {V1});
                Game gameCB(subgame(regionB.second)); /* game with regionB removed */
                /* solve gameCB */
                auto winCB = gameCB.recursive_strategy_template_parity(colive_edge_set,live_group_set,u+1);
                return std::make_pair(winCB.first, set_union(winCB.second, regionB.first)); 
            }
        }
    }
    
public:

    ///////////////////////////////////////////////////////////////
    ///Basic functions
    ///////////////////////////////////////////////////////////////
    
    /* function: set_difference
     *
     * compute set difference of two sets*/
    
    std::unordered_set<size_t> set_difference(const std::unordered_set<size_t> set2, const std::unordered_set<size_t> set1) const {
        std::unordered_set<size_t> set3; /* set2 - set1 */
        for (auto u : set2){
            if (set1.find(u) == set1.end()){
                set3.insert(u);
            }
        }
        return set3;
    }

    /* function: set_complement
     *
     * compute complement of a set*/
    
    std::unordered_set<size_t> set_complement(const std::unordered_set<size_t> set1) const {
        return set_difference(vertices_, set1);
    }

    /* function: check_set_inclusion
     *
     * check if set1 is included in set2 */
    template<class T>
    bool check_set_inclusion(const std::unordered_set<T> set1, const std::unordered_set<T> set2) const {
        if (set2.empty()){
            return false;
        }
        for (auto a = set1.begin(); a != set1.end(); ++a) {
            if (set2.find(*a) == set2.end()) {
                return false;
            }
        }
        return true;
    }

    /* function: check_set_intersection
     *
     * check if there is nonempty intersection between the two sets */
    template<class T>
    bool check_set_intersection(const std::unordered_set<T> set1, const std::unordered_set<T> set2) const {
        for (auto a = set1.begin(); a != set1.end(); ++a) {
            if (set2.find(*a) != set2.end()) {
                return true;
            }
        }
        return false;
    }


    /* function: set_merge
     *
     * merge one set into another */
    
    void set_merge(std::unordered_set<size_t>& set1, const std::unordered_set<size_t> set2) const {
        set1.insert(set2.begin(), set2.end());
    }

    /* function: vertex_with_color
     *
     * returns the set of vertices with color c */
    
    std::unordered_set<size_t> vertex_with_color(size_t c) const {
        std::unordered_set<size_t> result;;
        for (auto const &pair : colors_) {
            if (pair.second == c) {
                result.insert(pair.first);
            }
        }
        return result;
    }

    /* function: map_remove_values
     *
     * remove set of values from one map (set of edges) */
    
    void map_remove_values(std::map<size_t, std::unordered_set<size_t>>& map, std::unordered_set<size_t> values) const {
        for (auto v = map.begin(); v != map.end(); v++){
            v->second = set_difference(v->second, values);
        }
    }
    void map_remove_values(std::map<size_t, size_t>& map, std::unordered_set<size_t> values) const {
        for (auto e = map.begin(); e != map.end();) {
            if (values.find(e->second) != values.end())
                map.erase(e++);
            else
                ++e;
        }
    }

    /* function: map_remove_keys
     *
     * remove set of keys from one map  */
    template<class T>
    void map_remove_keys(std::map<size_t, T>& map, std::unordered_set<size_t> keys) const {
        for (auto const & key : keys){
            map.erase(key);
        }
    }

    /* function: map_remove_vertices
     *
     * remove set of keys and values from one map */
    void map_remove_vertices(std::map<size_t, std::unordered_set<size_t>>& map, const std::unordered_set<size_t> keys) const {
        map_remove_keys(map, keys);
        map_remove_values(map,keys);
    }

    /* function: update_max_col
     *
     * re-compute and update the max_color the game */
    
    size_t max_col(std::map<size_t,size_t> colors) const {
        size_t max_color = 0;
        for (auto pair : colors){
            if (pair.second > max_color)
                max_color = pair.second;
        }
        return max_color;
    }

    /* function: remove_vertices
     *
     * remove vertices from the game */
    
    void remove_vertices(const std::unordered_set<size_t> set) {
        vertices_= set_complement(set);
        n_vert_ = vertices_.size();
        map_remove_keys(vert_id_, set);
        
        map_remove_keys(colors_, set);
        max_color_ = max_col(colors_);
        
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
    
    Game subgame(const std::unordered_set<size_t> set) const{
        Game game(*this);
        game.n_vert_ = set.size();
        game.vertices_= set;

        std::unordered_set<size_t> complement = set_complement(set);
        map_remove_keys(game.vert_id_, complement);
        map_remove_keys(game.colors_, complement);
        game.max_color_ = max_col(game.colors_);
        

        
        map_remove_keys(game.edges_, complement);
        game.n_edge_ = 0;
        for (auto v : game.vertices_){
            game.edges_.at(v) = set_difference(game.edges_.at(v),complement);
            game.n_edge_ += game.edges_.at(v).size();
        }
        /* sanity check */
        // game.valid_game();
        
        return game;
    }

    /* check valid_game */
    void valid_game() const {
        if (n_vert_ != vertices_.size() || n_vert_ != edges_.size() || n_vert_ != vert_id_.size() || n_vert_ != colors_.size()){
            std::cerr << "ERROR: Invalid Game ###############.\n";
            std::cout << "vertex:"<<n_vert_ <<"," << vertices_.size()<<"   edges"<< n_edge_ <<","<<edges_.size()<< "  vert_id:" << vert_id_.size() << " color:"<<colors_.size()<<"\n";
        }
    }
    
    /* function: set_intersetion
     *
     * compute intersection of sets */
    std::unordered_set<size_t> set_intersection(const std::unordered_set<size_t> set1, const std::unordered_set<size_t> set2, const std::unordered_set<size_t> set3 = std::unordered_set<size_t>{}) const {
        std::unordered_set<size_t> set4;
        if (set3.empty()){
            for (auto a : set1) {
                if (set2.find(a) != set2.end()) {
                    set4.insert(a);
                }
            }
        }
        else{
            for (auto a : set1) {
                if (set2.find(a) != set2.end() && set3.find(a) != set3.end()) {
                    set4.insert(a);
                }
            }
        }
        return set4;
    }

    /* function: set_union
     *
     * compute union of two sets */
    std::unordered_set<size_t> set_union(const std::unordered_set<size_t> set1, const std::unordered_set<size_t> set2) const {
        std::unordered_set<size_t> result = set1;
        result.insert(set2.begin(), set2.end());
        return result;
    }

    /* function: edges_between
     *
     * return all plyaer 0's edges from source to target */
    
    std::map<size_t, std::unordered_set<size_t>>  edges_between(const std::unordered_set<size_t> source,
                        const std::unordered_set<size_t> target) const {
        std::map<size_t, std::unordered_set<size_t>> result_edges;
        /* include every player 0 edge from source to target */
        for (auto v : source){
            if (vert_id_.at(v) == V0){
                for (auto u : edges_.at(v)){
                    if (target.find(u) != target.end()){
                        result_edges[v].insert(u);
                    }
                }
            }
        }
        return result_edges;
    }
    void edges_between(const std::unordered_set<size_t> source,
                        const std::unordered_set<size_t> target,
                        std::map<size_t, std::unordered_set<size_t>>& result_edges) const {
        /* include every player 0 edge from source to target */
        for (auto v : source){
            if (vert_id_.at(v) == V0){
                for (auto u : edges_.at(v)){
                    if (target.find(u) != target.end()){
                        result_edges[v].insert(u);
                    }
                }
            }
        }
    }
    std::map<size_t, std::unordered_set<size_t>> edges_between(const std::unordered_set<size_t> source,
                        const std::unordered_set<size_t> target,
                        std::unordered_set<size_t>& new_sources) const {
        std::map<size_t, std::unordered_set<size_t>> result_edges;
        /* include every player 0 edge from source to target */
        for (auto v : source){
            if (vert_id_.at(v) == V0){
                for (auto u : edges_.at(v)){
                    if (target.find(u) != target.end()){
                        result_edges[v].insert(u);
                        new_sources.insert(v);
                    }
                }
            }
        }
        return result_edges;
    }



    ///////////////////////////////////////////////////////////////
    ///Print functions
    ///////////////////////////////////////////////////////////////
    

    /* function: print_set
     *
     * print out all elements of the set*/
    void print_set (const std::unordered_set<size_t> set, const std::string note = "set") const {
        std::cout << "\n" << note << ": ";
        for (auto u=set.begin(); u != set.end();){
            std::cout << *u;
            ++u;
            if (u != set.end())
                std::cout << ", ";
        }
        std::cout << "\n";
    }

    /* function: print_edges
     *
     * print out all edges of the map */
    void print_edges (std::map<size_t, std::unordered_set<size_t>>& map, const std::string note = "edges", const int print_empty = 1) const {
        if (print_empty == 1 || map.size()!=0){
            std::cout << "\n" << note << ": \n";
            for (auto v = map.begin(); v != map.end();){
                if (v->second.empty()){
                    map.erase(v++);
                }
                else{
                    for (auto u : v->second){
                        std::cout << v->first << " -> " << u << "\n";
                    }
                    ++v;
                }
            }
        }
    }
    /* function: print_live_groups
     *
     * print out all live_groups of the live_group_set */
    void print_live_groups (const std::vector<std::map<size_t, std::unordered_set<size_t>>> live_group_set, const std::string note = "live groups", const int print_empty = 1) const {
        if (print_empty == 1 || live_group_set.size()!=0){
            std::cout << "\n" << note << ": \n";
            for (auto live_group : live_group_set){
                std::cout << "{";
                size_t counter = 0;
                for (auto v = live_group.begin(); v != live_group.end(); v++){
                    for (auto u : v->second){
                        if (counter == 0){
                            std::cout << "("<<v->first << " -> " << u<<")";
                            counter += 1;
                        }
                        else{
                            std::cout << ", " <<"("<< v->first << " -> " << u<<")";
                        }
                    }
                }
                std::cout << "}\n";
            }
        }
    }
}; /* close class definition */
} /* close namespace */

#endif
