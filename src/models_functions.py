import numpy as np

def get_props_features_xy(p):
    prop_features_x = []
    prop_features_y = []
    features2remove = ["prop", "statement", 'prop_statement', "y", "inputs", "output"]
    
    for s in get_prop_parameters(p).values():
        
        feature_names = sorted(s.keys()) #Sort keys is important to ensure feature order

        s_features = []
        for f in feature_names:
            if f not in features2remove:
                s_features.append(s[f])
            
        prop_features_x.append(s_features)
        prop_features_y.append(s["y"])

    return prop_features_x, prop_features_y

def get_prop_parameters(target_prop):
    steps_dict = {s[0]:{
        "prop": s[1], 
        "statement":s[2], 
        "prop_statement":s[3], 
        "lemma_complexity":max(s[4], 1), #Ensure there is no 0 complexity value
        "y":s[5]
    } for s in target_prop["steps"]}

    #Add neighbors refs
    for s in steps_dict.values():
        s["inputs"] = []
        s["output"] = None
    for s, d in target_prop["links"]:
        steps_dict[d]["inputs"].append(s)
        steps_dict[s]["output"] = d
        
    #Add number of neighbors
    for s in steps_dict.values():   
        s["n_neighbors"] = len(s["inputs"]) + (1 if s["output"] != None else 0)
    
    #Add number of symbols in the statement
    for s in steps_dict.values():
        s["ns"] = len(s["statement"].split(" "))

    #Add number of distinct symbols in the statement
    for s in steps_dict.values():
        s["nds"] = len(set(s["statement"].split(" ")))
        
    #Add ratio between # of symbols and # of distinct symbols
    for s in steps_dict.values():
        s["ns_nds_ratio"] = s["ns"] / s["nds"]
        
    #Add number of symbols in the statement normalize with the largest
    largest_ns = max([s["ns"] for s in steps_dict.values()])

    for s in steps_dict.values():
        s["ns_norm"] = s["ns"] / largest_ns

    #Add number of distinct symbols in the statement normalize with the largest
    largest_nds = max([s["nds"] for s in steps_dict.values()])

    for s in steps_dict.values():
        s["nds_norm"] = s["nds"] / largest_nds
        
    #Normalize lemma complexities with the largest
    largest_lc = max([s["lemma_complexity"] for s in steps_dict.values()])
    for s in steps_dict.values():
        s["lemma_complexity_norm"] = s["lemma_complexity"] / largest_lc
    
        
    #Add neighbors summarized parameters
    neighbors_params = ["ns", "nds", "ns_norm", "nds_norm", "ns_nds_ratio", "lemma_complexity", "lemma_complexity_norm"]

    for s in steps_dict.values():
        for p in neighbors_params:
            neighbors_values = []
            if s["output"] != None:
                neighbors_values.append(steps_dict[s["output"]][p])
            for inp in s["inputs"]:
                neighbors_values.append(steps_dict[inp][p])

            s[f"neighbor_{p}_max"] = max(neighbors_values)
            s[f"neighbor_{p}_min"] = min(neighbors_values)
            s[f"neighbor_{p}_avg"] = np.mean(neighbors_values)
            
            s[f"neighbor_{p}_max_ratio"] = s[p] / s[f"neighbor_{p}_max"]
            s[f"neighbor_{p}_min_ratio"] = s[p] / s[f"neighbor_{p}_min"]
            s[f"neighbor_{p}_avg_ratio"] = s[p] / s[f"neighbor_{p}_avg"]
            
            
    #Add jaccard similarity between node statement symbols and its neighbors statement symbols
    for s in steps_dict.values():
        jacc_simm_values = []
        ratio_over_unions = []
        ratio_over_intersections = []
        
        neighbors_refs = []
        
        if s["output"] != None:
            neighbors_refs.append(steps_dict[s["output"]])
        
        for inp in s["inputs"]:
            neighbors_refs.append(steps_dict[inp])
            
        s_symbols = set(s["statement"].split(" "))
            
        for n in neighbors_refs:
            n_symbols = set(n["statement"].split(" "))
            
            jacc_val = len(s_symbols.intersection(n_symbols)) / len(s_symbols.union(n_symbols))
            jacc_simm_values.append(jacc_val)
            
            ratio_over_unions.append(len(s_symbols)/len(s_symbols.union(n_symbols)))
            ratio_over_intersections.append(len(s_symbols.intersection(n_symbols))/len(s_symbols))
            
        s["neighbors_jacc_sim_min"] = min(jacc_simm_values)
        s["neighbors_jacc_sim_max"] = max(jacc_simm_values)
        s["neighbors_jacc_sim_avg"] = np.mean(jacc_simm_values)
        
        s["neighbors_ratio_union_min"] = min(ratio_over_unions)
        s["neighbors_ratio_union_max"] = max(ratio_over_unions)
        s["neighbors_ratio_union_avg"] = np.mean(ratio_over_unions)
        
        s["neighbors_ratio_intersection_min"] = min(ratio_over_intersections)
        s["neighbors_ratio_intersection_max"] = max(ratio_over_intersections)
        s["neighbors_ratio_intersection_avg"] = np.mean(ratio_over_intersections)
        
    #Include whether some of its neighbors has been hidden or not
    #This may be helpful while working with the iterative algorithm to determine whether or not some node should be hidden
            
    return steps_dict
    