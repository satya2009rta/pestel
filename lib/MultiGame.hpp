/*
 * Class: MultiGame
 *
 * Class formalizing generalized (multi-objective) parity games
 */

#ifndef MULTIGAME_HPP_
#define MULTIGAME_HPP_

#include "Game.hpp"
#include <random>

// #include "FileHandler.hpp"


namespace mpa {
class MultiGame: public Game {
public:
    /* all maximum of colors */
    std::vector<size_t> all_max_color_;
    /* all_colors: the i-th vector represents i-th color set (for i=1,2)*/
    std::vector<std::map<size_t, size_t>> all_colors_;
    /* number of objectives (0th one for player 0, rest for player 1)*/
    size_t n_games_;
    
public:
    /* default constructor */
    MultiGame(): Game() {
        n_games_ = 2;
        all_max_color_ = std::vector<size_t>(2,0);
        all_colors_ = std::vector<std::map<size_t, size_t>>(2,std::map<size_t, size_t>());
    }

    /* copy a normal game */
    MultiGame(const Game other): Game(other){
        n_games_ = 1;
        all_max_color_.push_back(max_color_);
        all_colors_.push_back(colors_);
    }

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
            all_max_color_.push_back(max_color_);
            colors_ = newGame.colors_;
        }
        else{
            /* sanity check for two games having same game graph */
            // if (n_vert_ != newGame.n_vert_ || n_edge_ != newGame.n_edge_ || vert_id_ != newGame.vert_id_ || edges_ != newGame.edges_ || vertices_ != newGame.vertices_)
            //     std::cerr << "[ERROR] mergeGame: The game graph of the new game is different.\n";
            n_games_ += 1; /* number of games is increased by one */
            max_color_ = std::max(max_color_, newGame.max_color_); /* max_color is updated */
            all_colors_.push_back(newGame.colors_); /* colors is added to all_colors vector */
            all_max_color_.push_back(newGame.max_color_); /* max_color is added to all_max_color vector */
        }
    }

    /* find the n-th game */
    Game nthGame(const size_t n) const{
        mpa::Game game;
        game.n_vert_ = n_vert_;
        game.n_edge_ = n_edge_;
        game.vertices_ = vertices_;
        game.init_vert_ = init_vert_;
        game.vert_id_ = vert_id_;
        game.edges_ = edges_;
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
        all_max_color_ = other.all_max_color_;
    }


    ///////////////////////////////////////////////////////////////
    ///Product of two games
    ///////////////////////////////////////////////////////////////

    /* compute product of two games */
    int product_games(const Game& game1, const Game& game2, const bool hoa = true) {
        *this = MultiGame(); /* clear the game */
        n_games_ = 2; /* number of objective is two */

        std::map<std::pair<size_t,size_t>,size_t> product_verts; /* map of product of vertices to new vertieces */

        /* if one game is empty then return empty */
        if (game1.n_vert_ == 0 || game2.n_vert_ == 0){
            return 1;
        }
        /* update the aps : ids of aps in all 3 games */
        std::vector<std::vector<size_t>> common_aps; /* ids of common aps */
        std::vector<std::vector<size_t>> first_aps; /* only first ap-ids */
        std::vector<std::vector<size_t>> second_aps; /* only second ap-ids */
        std::map<size_t,size_t> second_aps_map; /* map for second aps to update controllable_aps */
        std::map<size_t,size_t> first_aps_map; /* map for first aps to update controllable_aps */
        std::set<size_t> common_in_second; /* id of commons aps in second game -- need to compute second_aps */
        for (size_t i = 0; i < game1.ap_id_.size(); i++){
            bool common = false; /* if i-th vertex is common in both game */
            for (size_t j = 0; j < game2.ap_id_.size(); j++){
                if (game1.ap_id_.at(i) == game2.ap_id_.at(j)){ /* i-th vertex is common */
                    common_aps.push_back(std::vector<size_t>{ap_id_.size(),i,j}); /* add it in common_aps vector with ids in all games */
                    second_aps_map[j] = ap_id_.size();
                    common_in_second.insert(j); 
                    common = true; /* set common to true */
                    break;
                }
            }
            if (!common){/* if not common then add it to first_aps */
                first_aps.push_back(std::vector<size_t>{ap_id_.size(),i});
            }
            /* add this ap and its label to new game */
            first_aps_map[i] = ap_id_.size();
            ap_id_[ap_id_.size()] = game1.ap_id_.at(i);
        }
        for (size_t j = 0; j < game2.ap_id_.size(); j++){ /* iterate over all aps of 2nd game */
            if (common_in_second.find(j) == common_in_second.end()){ /* if it is not common then add it to second_aps and new game */
                second_aps.push_back(std::vector<size_t>{ap_id_.size(),j});
                ap_id_[ap_id_.size()] = game2.ap_id_.at(j);
                second_aps_map[j] = ap_id_.size();
            }
        }

        /* update the controllable_aps */
        for (size_t a : game1.controllable_ap_){
            controllable_ap_.insert(first_aps_map.at(a));
        }
        for (size_t a : game2.controllable_ap_){
            controllable_ap_.insert(second_aps_map.at(a));
        }
        

        /* initial vertex should be of same player in both games */
        if (game1.vert_id_.at(game1.init_vert_) != game2.vert_id_.at(game2.init_vert_)){
            std::cerr << "Error: vertex ids of both games are not same!\n";
        }
        /* insert initial vertex and update all variables */
        n_vert_ = 1;
        size_t org_vert = 1; /* counter for normal vertices */
        size_t edge_vert = (game1.n_vert_-game1.n_edge_/2)*(game2.n_vert_-game2.n_edge_/2); /* counter for edge-vertices */
        vertices_.insert(0); 
        init_vert_ = 0;
        vert_id_[0] = game1.vert_id_.at(game1.init_vert_);
        all_colors_[0][0] = game1.colors_.at(game1.init_vert_);
        all_colors_[1][0] = game2.colors_.at(game2.init_vert_);
        product_verts.insert({std::make_pair(game1.init_vert_,game2.init_vert_),0});

        /* maintain a stack to explore new (product) vertices */
        std::stack<std::vector<size_t>> stack_list;
        /* initialize the stack with initial vertex */
        stack_list.push(std::vector<size_t>{0,game1.init_vert_,game2.init_vert_});

        /* explore until the stack list is empty */
        while (!stack_list.empty()){
            std::vector<size_t> curr = stack_list.top(); /* current pair of vertices */
            stack_list.pop(); /* pop the top element from stack list */
            for (auto u : game1.edges_.at(curr[1])){ /* for each edge-neighbour of 1st vertex */
                for (auto v : game2.edges_.at(curr[2])){ /* for each edge-neihbour of 2nd vertex */
                    bool valid = true; /* if product of these two edges is possible */
                    std::vector<size_t> temp_common(ap_id_.size(),2); /* needed if possible, temporarily store the ids of this new edge */
                    for (auto ap : common_aps){ /* first go through common aps */
                        if (game1.labels_.at(u)[ap[1]]+game2.labels_.at(v)[ap[2]] == 1){
                            valid = false; /* one of the id of this ap is 1 and other is 0, so not valid product */
                            break;
                        }
                        /* if this ap is consistent in both edges then add its label to temp_common */
                        else if (game1.labels_.at(u)[ap[1]] == 0 || game2.labels_.at(v)[ap[2]] == 0){
                            temp_common[ap[0]] = 0;
                        }
                        else if (game1.labels_.at(u)[ap[1]] == 1 || game2.labels_.at(v)[ap[2]] == 1){
                            temp_common[ap[0]] = 1;
                        }
                    }
                    if (valid){ /* if the product-edge is valid */
                        /* update its temp_common to all ids */
                        for (auto ap : first_aps){
                            temp_common[ap[0]] = game1.labels_.at(u)[ap[1]];
                        }
                        for (auto ap : second_aps){
                            temp_common[ap[0]] = game2.labels_.at(v)[ap[1]];
                        }
                        size_t newId = org_vert; 
                        if (hoa){
                            newId = edge_vert;/* new state for product-edges : use edge_vert counter */
                            edge_vert += 1;
                        }
                        else{
                            org_vert += 1;
                        }
                        /* update all variables for new game */
                        n_vert_ += 1;
                        n_edge_ += 2;
                        vertices_.insert(newId);
                        vert_id_[newId] = 2;
                        edges_[curr[0]].insert(newId);
                        labels_[newId] = temp_common;
                        all_colors_[0][newId] = game1.colors_.at(u);
                        all_colors_[1][newId] = game2.colors_.at(v);

                        /* product of end-states of these edges */
                        std::pair<size_t,size_t> new_succ = std::make_pair(*game1.edges_.at(u).begin(),*game2.edges_.at(v).begin());
                        if (product_verts.find(new_succ) != product_verts.end()){ /* if the product of end-states of edges are already present add the edge */
                            edges_[newId].insert(product_verts.at(new_succ));
                            pre_edges_[product_verts.at(new_succ)].insert(newId);
                        }
                        else{ /* if the product of end-states of edges are not present */
                            size_t succId = org_vert; /* new state for the product-successor-states : use org_vert counter */
                            /* update all variables in the new game */
                            org_vert += 1;
                            n_vert_ += 1;
                            vertices_.insert(succId);
                            vert_id_[succId] = game1.vert_id_.at(new_succ.first);
                            edges_[newId].insert(succId);
                            pre_edges_[succId].insert(newId);
                            all_colors_[0][succId] = game1.colors_.at(new_succ.first);
                            all_colors_[1][succId] = game2.colors_.at(new_succ.second);
                            product_verts[new_succ] = succId;
                            stack_list.push(std::vector<size_t>{succId,new_succ.first,new_succ.second});
                        }
                    }
                }
            }
        }
        /* update max_color */
        all_max_color_[0] = max_col(all_colors_[0]); 
        all_max_color_[1] = max_col(all_colors_[1]); 
        return 1;
    }


    ///////////////////////////////////////////////////////////////
    ///Game to MultiGame with random sets of colors
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
    size_t random_num(const size_t max, const size_t min = 0){
        std::random_device rd; /* obtain a random number from hardware */
        std::mt19937 gen(rd()); /* seed the generator */
        std::uniform_int_distribution<> distr(min, max); /* define the range */

        return distr(gen); /* generate numbers */
    }


    ///////////////////////////////////////////////////////////////
    ///Compose templates of multiple games
    ///////////////////////////////////////////////////////////////
    
    /* compute the composition of permissive strategy template for two games */
    std::pair<std::set<size_t>, std::set<size_t>> find_composition_template(Template& strat) const {
        /* clear the template */
        strat.clear();

        /* solve the games without changing anything in the original game */
        MultiGame multigame_copy(*this); /* copy of the multi-game */
        auto winning_region = multigame_copy.recursive_composition_template(strat);
        /* unsafe edges are the player 0's edges from winning region to losing region */
        strat.unsafe_edges_ = edges_between(winning_region.first, set_complement(winning_region.first));
        /* return winning region */
        return winning_region;
    }

    /* recursively compute the composition of strategy template for two games */
    std::pair<std::set<size_t>, std::set<size_t>> recursive_composition_template(Template& strat) {
        auto winning_region = std::make_pair(vertices_, std::set<size_t> {}); /* winning region of the games */
        std::vector<std::set<size_t>> losing_regions(n_games_); /* losing region of i-th game */
        std::vector<Template> i_templates(n_games_); /* templates of i-th game */
        std::set<size_t> colive_vertices; /* vertices with color 2d+1 */
        // size_t counter = 0; /* count thenumber of iteration */
        
        if (n_games_ == 1){ /* if there is only one game, solve in standard way */
            Game game = nthGame(0);
            winning_region =  game.recursive_strategy_template_parity(strat);
            return winning_region; /* return winning region */
        }

        while (true){/* iterate until there is no need to solve any game again */
            // /* print to analyze the results */
            // std::cout << "couter begins:"<<counter<< "  colive:"<<colive_vertices.size()<<"  winning:"<<winning_region.first.size()<<"\n"; 
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
                losing_regions[i] = nthGame(i).recursive_strategy_template_parity(i_templates[i]).second;
            }
            
            /* compute the overall winning region */
            winning_region.second = nthGame(0).solve_reachability_game(set_union(losing_regions),{}).first; 
            winning_region.first = set_complement(winning_region.second);

            /* merge all templates */
            strat.merge_live_colive(i_templates);

            /* clear the colive vertices for new iteration */
            colive_vertices.clear(); 
            
            /* compute conflicts by colive edges (containing all outgoing edges of a vertex) */
            conflict_colive(strat.colive_edges_, winning_region, colive_vertices);
            /* compute conflicts by colive edges and live groups */
            conflict_live_colive(strat.live_groups_, strat.colive_edges_, winning_region, colive_vertices);

            /* first remove losing region from everywhere */
            remove_vertices(winning_region.second);
            colive_vertices = set_difference(colive_vertices, winning_region.second);
                
            
            /* print to analyze the results */
            // counter += 1;
            // if (counter <= 5){
            //     std::cout << "couter:"<<counter<< "  colive:"<<colive_vertices.size()<<"  losing:"<<winning_region.second.size()<<"\n";
            // }
            

            /* check if there is no conflicts by live groups and colive edges */
            if (colive_vertices.empty()){/* if no conflicts by live colive edges, then check conflict by unsafe edges */
                /* check if there is no conflicts by unsafe edges */
                if (!conflict_unsafe(strat.live_groups_, strat.colive_edges_, winning_region)){
                    /* remove the unsafe edges and edges from losing region from colive edge set */
                    map_remove_vertices(strat.colive_edges_, winning_region.second);
                    /* remove the restrictions on losing regions and colive edges from live group (as there is other choice from that source) */
                    for (auto& live_group : strat.live_groups_){
                        map_remove_keys(live_group, winning_region.second);
                        map_remove(live_group, strat.colive_edges_);
                    }
                    break; /* break the loop as there is no more conflict */
                }
            }

            /* clear the template */
            strat.clear();
            for (size_t i = 0; i < n_games_; i++){
                i_templates[i].clear();
            }
        }
        // /* print to analyze the results */
        // std::cout << "couter:"<<counter<< "  colive:"<<colive_vertices.size()<<"  winning:"<<winning_region.first.size()<<"\n"; 
        return winning_region; /* return winning region */
    }
    
    /* Check if the unsafe edges create some conflict */
    bool conflict_unsafe(std::vector<std::map<size_t, std::set<size_t>>>& live_group_set,
                            std::map<size_t, std::set<size_t>>& colive_edge_set,
                            const std::pair<std::set<size_t>, std::set<size_t>>& winning_region) {
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
    void conflict_colive(const std::map<size_t, std::set<size_t>>& colive_edge_set,
                        const std::pair<std::set<size_t>, std::set<size_t>>& winning_region,
                        std::set<size_t>& colive_vertices) {
        for (auto it = colive_edge_set.begin(); it != colive_edge_set.end(); it++){
            auto v = it ->first;
            if (winning_region.first.find(v)!= winning_region.first.end() && !edges_.at(v).empty() && check_set_inclusion(edges_.at(v), it->second)){
                /* if all edges of a source is colive then add the source to colive vertices */
                colive_vertices.insert(v);
            }
        }      
    }

    /* solve the conflict when the intersection of colive edges and live groups is non-empty */
    void conflict_live_colive(std::vector<std::map<size_t, std::set<size_t>>>& live_group_set,
                                const std::map<size_t, std::set<size_t>>& colive_edge_set,
                                const std::pair<std::set<size_t>, std::set<size_t>>& winning_region,
                                std::set<size_t>& colive_vertices) {
        std::set<size_t> conflict_keys; /* sources of the possible conflict edges */
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
    std::pair<std::set<size_t>, std::set<size_t>> find_composed_strategy_template_parity(Template& strat) const {
        mpa::MultiGame copy(*this);
        copy.parityToMultigame();
        return copy.find_composition_template(strat);
    }
    
    /* solve parity game using composition of small games */
    std::pair<std::set<size_t>, std::set<size_t>> solve_composed_parity() const {
        /* initialize the strategy template */
        Template strat;
        return find_composed_strategy_template_parity(strat);
    }

    
    ///////////////////////////////////////////////////////////////
    ///Basic functions
    ///////////////////////////////////////////////////////////////

    /* function: max_odd
     *
     * return minimum odd color that is greater than or equal to max_color */
    size_t max_odd(const std::map<size_t, size_t>& colors) const {
        size_t odd_col = 1;
        for (auto const & col : colors){
            if (col.second%2 == 1 && col.second > odd_col)
                odd_col = col.second;
            else if (col.second%2 == 0 && col.second > odd_col)
                odd_col = col.second+1;
        }
        return odd_col;
    }
    size_t max_odd(size_t max_color) const {
        if (max_color%2 == 1){
            return max_color;
        }
        else{
            return max_color+1;
        }
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
    
    void remove_vertices(const std::set<size_t>& set) {
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
    
    MultiGame subgame(const std::set<size_t>& set) const{
        MultiGame game = *this;
        game.n_vert_ = set.size();
        game.vertices_= set;

        std::set<size_t> complement = set_complement(set);
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
    
    void map_remove(std::map<size_t, std::set<size_t>>& map2, const std::map<size_t, std::set<size_t>>& map1) const {
        for (auto v = map1.begin(); v != map1.end(); v++){
            map2[v->first] = set_difference(map2[v->first], v->second);
        }
    }

    /* print game informations */
    int print_game(){
        if (labels_.empty()){
            std::cout << "Game constructed! #vertices:"<<n_vert_<<"  #edges:"<<n_edge_;
            if (n_games_ == 2){
                std::cout << "  #colors0:"<<all_max_color_[0]+1<<"  #colors1:"<<all_max_color_[1]+1<<"\n";
                return 0;
            }
            size_t max_color = 0;
            for (size_t i = 1; i<n_games_; i++){
                max_color = std::max(max_color,all_max_color_[i]);
            }
            std::cout << "  #games:"<<n_games_<< "  #colors0:"<<all_max_color_[0]+1<<"  #colors1:"<<max_color+1<<"\n";
            return 1;
        }
        std::cout << "Game constructed! #vertices:"<<n_vert_-n_edge_/2<<"  #edges:"<<n_edge_/2<<"  #colors0:"<<all_max_color_[0]+1<<"  #colors1:"<<all_max_color_[1]+1<<"\n";
        return 1;
    }
    
}; /* close class definition */
} /* close namespace */

#endif
