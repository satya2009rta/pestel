/*
 * Class: Game
 *
 *  Class formalizing a basic two player (parity) game
 */

#ifndef GAME_HPP_
#define GAME_HPP_

#include "Template.hpp"

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
    std::set<size_t> vertices_;
    /* initial vertex */
    size_t init_vert_;
    /* vertex id: V0, when the vertex belongs to player 0 and V1 when it belongs to player 1 */
    std::map<size_t, size_t> vert_id_;
    /* edges as a map from vertices to set of its neighbours */
    std::map<size_t, std::set<size_t>> edges_;
    /* maximum of colors */
    size_t max_color_;
    /* colors of vertices */
    std::map<size_t, size_t> colors_;

    /* variables needed for ehoa formatted games */
    /* pre of edges for original vertices (incoming edges) */
    std::map<size_t, std::set<size_t>> pre_edges_;
    /* ids of atomic proposition */
    std::map<size_t, std::string> ap_id_;
    /* labels of mid-state */
    std::map<size_t, std::vector<size_t>> labels_;
    /* controllable APs */
    std::set<size_t> controllable_ap_;
    /* name of states */
    std::map<size_t, std::string> state_names_;
    /* minimum color added for hoa games */
    size_t min_col_;
public:
    /* default constructor */
    Game() {
        n_vert_ = 0;
        n_edge_ = 0;
    }


    ///////////////////////////////////////////////////////////////
    /// Solving all types of games
    ///////////////////////////////////////////////////////////////

    /* solve reachability game for player i (default is player 0)
     * input: target
     * output: Reach_i(target) */
    std::pair<std::set<size_t>, std::set<size_t>> solve_reachability_game(const std::set<size_t>& target,
                                                    const std::set<size_t>& players = {V0}) const {
        std::set<size_t> losing; /* vertices from which targets might not be reachable */
        std::set<size_t> winning = target; /* vertices from which targets are currently reachable */
        while (true)
        {
            losing = set_complement(winning); /* complement of vertices from which targets are currently reachable */
            std::set<size_t> new_winning; /* new vertices from which targets are currently reachable */
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
    std::pair<std::set<size_t>, std::set<size_t>> solve_buchi_game(const std::set<size_t>& target) const {
        Game subgame = *this; /* copy the game */
        std::set<size_t> non_target = set_complement(target); /* vertices which are not target */
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
    std::pair<std::set<size_t>, std::set<size_t>> solve_cobuchi_game(const std::set<size_t>& target) const {
        Game subgame = *this; /* copy the game */
        std::set<size_t> non_target = set_complement(target); /* vertices which are not target */
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
    std::pair<std::set<size_t>, std::set<size_t>> solve_parity_game() const {
        Game game_copy(*this); /* copy of the game as we will change it */
        return game_copy.recursive_zielonka_parity();
    }
    /* recursive zielonka's algorithm */
    std::pair<std::set<size_t>, std::set<size_t>> recursive_zielonka_parity() const {
        if (n_vert_ == 0) /* if current region is empty, nothing to do, return empty */
            return std::make_pair(vertices_, vertices_);
        /* vertices with maximum color */
        std::set<size_t> max_col_vertices = vertex_with_color(max_color_);
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
    std::pair<std::set<size_t>, std::set<size_t>> find_strategy_template_buchi(const std::set<size_t>& target, Template& strat) const {
        /* initialize the template */
        strat.clear();

        /* first compute the winning region */
        auto winning_region = solve_buchi_game(target);
        /* unsafe edges are the player 0's edges from winning region to losing region */
        strat.unsafe_edges_ = edges_between(winning_region.first, winning_region.second);
        /* copy the subgame restricted to winning region */
        Game game_copy(subgame(winning_region.first));
        game_copy.find_live_groups_reach(target, winning_region.first, strat);
        return winning_region;
    }

    void find_live_groups_reach(const std::set<size_t>& target,
                                const std::set<size_t>& winning_region,
                                Template& strat) const {
        std::set<size_t> curr_target = target;
        /* keep finding live groups until convergence to the winning region */
        while (1) {
            /* vertices from which no player can stop reaching cuurent winning region */
            auto curr_winning_region = solve_reachability_game(curr_target, {});
            if (curr_winning_region.first.size() == winning_region.size()) {
                break;
            }
            curr_target = curr_winning_region.first; /* current target is the winnign region of last reachability game */
            /* add live group containing player0 edges from outiside to winning region; and add their sources to curr_target */
            strat.live_groups_.push_back(edges_between(curr_winning_region.second, curr_winning_region.first, curr_target));
        }
    }


    ///////////////////////////////////////////////////////////////
    ///Parity games
    ///////////////////////////////////////////////////////////////

    /* compute the permissive strategy template for parity game */
    std::pair<std::set<size_t>, std::set<size_t>> find_strategy_template_parity(Template& strat) const {
        /* clear the template */
        strat.clear();

        /* compute template recursively */
        auto winning_region = recursive_strategy_template_parity(strat);
        /* unsafe edges are the player 0's edges from winning region to losing region */
        strat.unsafe_edges_ = edges_between(winning_region.first, winning_region.second);
        /* remove unsafe edges from colive edges set */
        map_remove_vertices(strat.colive_edges_, winning_region.second);
        return winning_region;
    }

    /* compute the set of live groups and colive edges recursively */
    std::pair<std::set<size_t>, std::set<size_t>> recursive_strategy_template_parity(
                                    Template& strat,
                                    const size_t& u = 0) const {
        // std::cout << u<<"\n";
        if (n_vert_ == 0) /* if current region is empty, nothing to do, return empty */
            return std::make_pair(vertices_, vertices_);
        /* vertices with maximum color */
        std::set<size_t> max_col_vertices = vertex_with_color(max_color_);
        if (max_color_ % 2 == 1){ /* when max_color_ is odd */
            /* vertices from which player 1 can force to visit max_col_vertices (odd) */
            auto regionA = solve_reachability_game(max_col_vertices, {V1});
            /* complement of regionA */
            Game gameCA(subgame(regionA.second)); /* game with regionA removed */
            /* solve the gameCA */
            auto winCA = gameCA.recursive_strategy_template_parity(strat,u+1);
            if (winCA.first.empty()) /* if winning region is empty in gameCA then return everything empty */
                return std::make_pair(winCA.first, vertices_);
            else {
                /* vertices from which player 0 can force to reach winning region of gameCA */
                auto regionB = solve_reachability_game(winCA.first, {V0});
                /* edges from winning region of gameCA to regionB (all are player 0's) are colive */
                edges_between(winCA.first,set_complement(winCA.first), strat.colive_edges_);
                /* live groups needed to reach winCA from regionB */
                find_live_groups_reach(winCA.first,regionB.first,strat);

                Game gameCB(subgame(regionB.second)); /* game with regionB removed */
                /* solve gameCB */
                auto winCB = gameCB.recursive_strategy_template_parity(strat,u+1);
                return std::make_pair(set_union(winCB.first, regionB.first), winCB.second); /* winning region is regionB \cup winning region of gameCB */
            }
        }
        else{ /* max_color_ is even */
            /* vertices from which player 0 can force to visit max_col_vertices (even) */
            auto regionA = solve_reachability_game(max_col_vertices, {V0});
            /* complement of regionA */
            Game gameCA(subgame(regionA.second)); /* game with regionA removed */
            /* solve the gameCA with output in new template */
            Template& stratCA = strat;
            auto winCA = gameCA.recursive_strategy_template_parity(stratCA,u+1);
            if (winCA.second.empty()){ /* if losing region is empty */
                /* output template gameCA is merged with actual template */
                strat = stratCA;
                /* live groups needed to reach max even color from regionA */
                find_live_groups_reach(max_col_vertices,regionA.first,strat);
                return std::make_pair(vertices_, winCA.second); /* winning region is whole set */
            }
            else {
                /* vertices from which player 1 can force to reach losing region of gameCA */
                auto regionB = solve_reachability_game(winCA.second, {V1});
                Game gameCB(subgame(regionB.second)); /* game with regionB removed */
                /* solve gameCB */
                auto winCB = gameCB.recursive_strategy_template_parity(strat,u+1);
                return std::make_pair(winCB.first, set_union(winCB.second, regionB.first)); 
            }
        }
    }

    ///////////////////////////////////////////////////////////////
    /// Filter all edge-states out (needed for HOA formatted games)
    ///////////////////////////////////////////////////////////////

    /* print_action_edge depending on print_actions and if label exists */
    std::string print_action_edge(size_t state, bool print_actions) const {
        if (print_actions && !labels_.empty()) {
            return "\"" + print_label(state, true) + "\"";
        }
        if (labels_.empty()) {
            return std::to_string(state);
        }
        return std::to_string(*edges_.at(state).begin());
    }

    /* update string parts of the template by replacing edge-states by its label or its(only) successor in a set of edges */
    int filter_edges(const std::map<size_t, std::set<size_t>>& edges, std::map<size_t, std::set<std::string>>& edge_string, const bool print_actions=false) const {
        edge_string.clear();
        for (auto& pair : edges){
            std::set<std::string> new_succs;
            for (auto succ : pair.second){
                new_succs.insert(print_action_edge(succ, print_actions));
            }
            edge_string.insert(std::make_pair(pair.first, new_succs));
        }
        return 1;
    }

    /* filter out edge-states in a template */
    int filter_templates(Template& assump, const std::set<size_t>& org_vertices, const bool print_actions=false) const {
        filter_edges(assump.unsafe_edges_, assump.unsafe_strings_, print_actions);
        filter_edges(assump.colive_edges_, assump.colive_strings_, print_actions);
        for (auto& live_group : assump.live_groups_){
            std::map<size_t, std::set<std::string>> live_strings;
            filter_edges(live_group, live_strings, print_actions);
            assump.live_groups_strings_.push_back(live_strings);
        }
        for (auto& live_groups : assump.cond_live_groups_){
            std::vector<std::map<size_t, std::set<std::string>>> cond_live_strings;
            for (auto& live_group : live_groups){
                std::map<size_t, std::set<std::string>> live_strings;
                filter_edges(live_group, live_strings, print_actions);
                cond_live_strings.push_back(live_strings);
            }
            assump.cond_live_groups_strings_.push_back(cond_live_strings);
        }
        for (auto& cond_sets : assump.cond_sets_){
            cond_sets = set_intersection(cond_sets, org_vertices);
        }
        
        return 1;
    }

    /* filter out edge-states from a winning region, assumption and strategy template */
    int filter_out_edge_states(std::pair<std::set<size_t>, std::set<size_t>>& winning_region, Template& strat, const bool print_actions=false) const {
        if (labels_.empty()){
            return 0;
        }
        std::set<size_t> org_vertices;
        for (auto v : vertices_){
            if (vert_id_.at(v) != 2){
                org_vertices.insert(v);
            }
        }
        winning_region.first = set_intersection(winning_region.first, org_vertices);
        winning_region.second = set_intersection(winning_region.second, org_vertices);
        
        filter_templates(strat, org_vertices, print_actions);
        return 1;
    }


    ///////////////////////////////////////////////////////////////
    /// Convert to local templates for each state and print
    ///////////////////////////////////////////////////////////////

    /* construct a map from state id to its LocalTemplate */
    std::map<size_t, LocalTemplate> template2local(Template& temp, const std::set<size_t>& winning_states, const bool print_actions=false) const {

        // create a map to hold the local templates
        std::map<size_t, LocalTemplate> map_local_templates;

        // iterate through each state in the game
        for (auto state : winning_states){
            if (vert_id_.at(state) != 0){/* only consider player 0 states */
                continue;
            }
            auto id = state;
            std::string name = "";
            if (!state_names_.empty()){
                name = state_names_.at(state);
            }
            

            std::set<size_t> unrestricted;
            std::set<std::string> all_actions;
            std::set<std::string> unsafe_actions;
            std::set<std::string> colive_actions;
            std::set<std::string> live_actions;
            std::set<std::string> unrestricted_actions;
            std::set<std::string> preferred_actions;
            for (const auto& succ : edges_.at(state)){
                all_actions.insert(print_action_edge(succ,print_actions));
                unrestricted.insert(succ);
            }
            for (const auto& succ : temp.unsafe_edges_[state]){
                unsafe_actions.insert(print_action_edge(succ,print_actions));
                unrestricted.erase(succ);
            }
            for (const auto& succ : temp.colive_edges_[state]){
                colive_actions.insert(print_action_edge(succ,print_actions));
                unrestricted.erase(succ);
            }
            for (auto& live_group : temp.live_groups_){
                for (const auto& succ : live_group[state]){
                    live_actions.insert(print_action_edge(succ,print_actions));
                    unrestricted.erase(succ);
                }
            }
            for (const auto& succ : unrestricted){
                unrestricted_actions.insert(print_action_edge(succ,print_actions));
            }
            /* preferred actions are live actions (if any else unrestricted) */
            preferred_actions = live_actions;
            if (preferred_actions.size() == 0){
                preferred_actions = unrestricted_actions;
            }
            map_local_templates[state] = LocalTemplate(id, name, all_actions, unsafe_actions, colive_actions, live_actions, unrestricted_actions, preferred_actions);
        }
        return map_local_templates;
    }

    /* print the local templates */
    void print_local_templates(Template& temp, const std::set<size_t>& winning_states, const bool print_actions=false) {
        auto map_local_templates = template2local(temp, winning_states, print_actions);
        std::cout << "[\n";
        size_t counter = 0;
        for (const auto& pair : map_local_templates){
            pair.second.print_local_template();
            counter += 1;
            if (counter < map_local_templates.size()){
                std::cout << ",\n";
            }
            else{
                std::cout << "\n";
            }
        }
        std::cout << "]\n";
    }


    ///////////////////////////////////////////////////////////////
    ///Basic functions
    ///////////////////////////////////////////////////////////////
    
    /* function: set_difference
     *
     * compute set difference of two sets*/
    
    std::set<size_t> set_difference(const std::set<size_t>& set2, const std::set<size_t>& set1) const {
        std::set<size_t> set3; /* set2 - set1 */
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
    
    std::set<size_t> set_complement(const std::set<size_t>& set1) const {
        return set_difference(vertices_, set1);
    }

    /* function: check_set_inclusion
     *
     * check if set1 is included in set2 */
    template<class T>
    bool check_set_inclusion(const std::set<T>& set1, const std::set<T>& set2) const {
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
    bool check_set_intersection(const std::set<T>& set1, const std::set<T>& set2) const {
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
    
    void set_merge(std::set<size_t>& set1, const std::set<size_t>& set2) const {
        set1.insert(set2.begin(), set2.end());
    }

    /* function: vertex_with_color
     *
     * returns the set of vertices (in a set) with color c */
    std::set<size_t> vertex_with_color(const size_t c) const {
        std::set<size_t> result;
        for (auto v : vertices_){
            if (colors_.at(v) == c){
                result.insert(v);
            }
        }
        return result;
    }
    std::set<size_t> vertex_with_color(const size_t c, const std::set<size_t>& set) const {
        std::set<size_t> result;
        for (auto v : set){
            if (colors_.at(v) == c){
                result.insert(v);
            }
        }
        return result;
    }

    /* function: map_remove_values
     *
     * remove set of values from one map (set of edges) */
    
    void map_remove_values(std::map<size_t, std::set<size_t>>& map, const std::set<size_t>& values) const {
        for (auto v = map.begin(); v != map.end(); v++){
            v->second = set_difference(v->second, values);
        }
    }

    void map_remove_values(std::map<size_t, size_t>& map, std::set<size_t>& values) const {
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
    void map_remove_keys(std::map<size_t, T>& map, const std::set<size_t>& keys) const {
        for (auto const & key : keys){
            map.erase(key);
        }
    }

    /* function: map_remove_vertices
     *
     * remove set of keys and values from one map */
    void map_remove_vertices(std::map<size_t, std::set<size_t>>& map, const std::set<size_t>& keys) const {
        map_remove_keys(map, keys);
        map_remove_values(map,keys);
    }

    /* function: max_col
     *
     * compute the max_color the game */
    size_t max_col(std::map<size_t,size_t>& colors) const {
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
    
    void remove_vertices(const std::set<size_t>& set) {
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
    
    Game subgame(const std::set<size_t>& set) const{
        Game game(*this);
        game.n_vert_ = set.size();
        game.vertices_= set;

        std::set<size_t> complement = set_complement(set);
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
    std::set<size_t> set_intersection(const std::set<size_t>& set1, const std::set<size_t>& set2, const std::set<size_t>& set3 = std::set<size_t>{}) const {
        std::set<size_t> set4;
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
     * compute union of two or more sets */
    std::set<size_t> set_union(const std::set<size_t>& set1, const std::set<size_t>& set2) const {
        std::set<size_t> result = set1;
        result.insert(set2.begin(), set2.end());
        return result;
    }

    std::set<size_t> set_union(const std::vector<std::set<size_t>>& sets) const {
        std::set<size_t> result;
        for (auto set: sets){
            set_merge(result,set);
        }
        return result;
    }

    /* function: edges_between
     *
     * return all plyaer 0's edges from source to target */
    
    std::map<size_t, std::set<size_t>>  edges_between(const std::set<size_t>& source, const std::set<size_t>& target) const {
        std::map<size_t, std::set<size_t>> result_edges;
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
    void edges_between(const std::set<size_t>& source,
                       const std::set<size_t>& target,
                       std::map<size_t, std::set<size_t>>& result_edges) const {
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
    std::map<size_t, std::set<size_t>> edges_between(const std::set<size_t>& source,
                        const std::set<size_t>& target,
                        std::set<size_t>& new_sources) const {
        std::map<size_t, std::set<size_t>> result_edges;
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

    /* function: co_edges_between
     *
     * add all plyaer i's edges that are from source but not to target (and there is an edge from that source to target) */
    std::map<size_t, std::set<size_t>> co_edges_between(const std::set<size_t>& source,
                        const std::set<size_t>& target,
                        std::set<size_t>& new_sources,
                        std::map<size_t, std::set<size_t>>& result_edges,
                        const std::set<size_t>& players = {V0}) const {
        /* include every player i edge from source but not to target when there is an edge from source to target */
        for (auto v : source){
            bool colive_source = false; /* if there is an edge from this source to target */
            std::set<size_t> colive_neighbours; /* all neighbours of this source that is not a target */
            if (players.find(vert_id_.at(v)) != players.end()){
                for (auto u : edges_.at(v)){
                    if (target.find(u) == target.end()){
                        colive_neighbours.insert(u);
                    }
                    else{
                        colive_source = true;
                    }
                }
                if(colive_source){ /* if there is an edge from source to target then add the edges to colive_neighbours */
                    set_merge(result_edges[v], colive_neighbours);
                    new_sources.insert(v);
                }
            }
        }
        return result_edges;
    }



    ///////////////////////////////////////////////////////////////
    ///Print functions
    ///////////////////////////////////////////////////////////////
    
    /* print game informations */
    int print_game(){
        if (labels_.empty()){
            std::cout << "Game constructed! #vertices:"<<n_vert_<<"  #edges:"<<n_edge_<<"  #colors:"<<max_color_+1<<"\n";
            return 0;
        }
        std::cout << "Game constructed! #vertices:"<<n_vert_-n_edge_/2<<"  #edges:"<<n_edge_/2<<"  #colors:"<<max_color_+1<<"\n";
        return 1;
    }

    /* function: print_set
     *
     * print out all elements of the set*/
    void print_set (const std::set<size_t> set, const std::string note = "set") const {
        std::cout << "\n" << note << ": ";
        for (auto u=set.begin(); u != set.end();){
            std::cout << *u;
            ++u;
            if (u != set.end())
                std::cout << ", ";
        }
        std::cout << "\n";
    }

    /* function: print_label
    *
    * print out the label of state */
    std::string print_label(size_t u, const bool num = true) const {
        std::string output;
        std::string output_num;
        size_t start = 1;
        for (size_t i = 0; i < ap_id_.size(); i++){
            if (labels_.at(u)[i] == 0){
                if (start == 1){
                    start = 0;
                    output += "!"+ap_id_.at(i);
                    output_num += "!" + std::to_string(i);
                }
                else{
                    output += " & !"+ap_id_.at(i);
                    output_num += "&!" + std::to_string(i);
                }
            }
            else if (labels_.at(u)[i] == 1){
                if (start == 1){
                    start = 0;
                    output += ap_id_.at(i);
                    output_num += std::to_string(i);
                }
                else{
                    output += " & "+ ap_id_.at(i);
                    output_num += "&"+std::to_string(i);
                }
            }
        }
        if (output.empty()){
            output = "*";
            output_num = "t";
        }
        if (!num){
            return output;
        }
        return output_num;
    }

}; /* close class definition */
} /* close namespace */

#endif
