import os

import pickle

from tree_parser import string_replace, proof_step

from adapt_utils import replace_symbols

import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt

from collections import defaultdict

#Snippet to collect context values from the database
# context_values = dict()
# for prop in database.propositions_list:
#     for k, v in prop.f.items():
#         if k in context_values:
#             if v.statement != context_values[k]:
#                 print(k, v.statement, context_values[k])
#                 break
#         else:
#             context_values[k] = v.statement

#Values collected loading 16080 theorems in the database
context_values = {
    'wph': ['ph'],
    'wps': ['ps'],
    'wch': ['ch'],
    'wth': ['th'],
    'wta': ['ta'],
    'wet': ['et'],
    'wze': ['ze'],
    'wsi': ['si'],
    'wrh': ['rh'],
    'wmu': ['mu'],
    'wla': ['la'],
    'wka': ['ka'],
    'vx.wal': ['x'],
    'vx.cv': ['x'],
    'cA.wceq': ['A'],
    'cB.wceq': ['B'],
    'vx.tru': ['x'],
    'vy.tru': ['y'],
    'vx': ['x'],
    'vy': ['y'],
    'vz': ['z'],
    'vw': ['w'],
    'vt': ['t'],
    'vu': ['u'],
    'vv': ['v'],
    'v.vs': ['s'],
    'wcel.cA': ['A'],
    'wcel.cB': ['B'],
    'cbvex4v.vf': ['f'],
    'cbvex4v.vg': ['g'],
    'cA': ['A'],
    'cB': ['B'],
    'cC': ['C'],
    'cD': ['D'],
    'cF': ['F'],
    'cG': ['G'],
    'cE': ['E'],
    'cV': ['V'],
    'cR': ['R'],
    'cS': ['S'],
    'cW': ['W'],
    'cH': ['H'],
    'vs': ['s'],
    'cX': ['X'],
    'cT': ['T'],
    'cQ': ['Q'],
    'cY': ['Y'],
    'va': ['a'],
    'cN': ['N'],
    'cU': ['U'],
    'cM': ['M'],
    'vi': ['i'],
    'vj': ['j'],
    'cZ': ['Z'],
    'vr': ['r'],
    'vb': ['b'],
    'vc': ['c'],
    'vd': ['d'],
    've': ['e'],
    'cP': ['P'],
    'vf': ['f'],
    'vp': ['p'],
    'vk': ['k'],
    'cI': ['I'],
    'vg': ['g'],
    'vm': ['m'],
    'cK': ['K'],
    'cL': ['L'],
    'cJ': ['J'],
    'c.pl': ['.+'],
    'cO': ['O'],
    'vn': ['n'],
    'vh': ['h'],
    'c.lt': ['.<'],
    'c.sm': ['.~'],
    'c.le': ['.<_'],
    'vq': ['q'],
    'c.pd': ['.+^'],
    'c.x': ['.x.'],
    'vl': ['l'],
    'c.0': ['.0.'],
    'c.as': ['.*'],
    'c.xp': ['.X.'],
    'c.xi': ['.,'],
    'vo': ['o'],
    'c.xb': ['.xb'],
    'c.pb': ['.+b'],
    'c.xo': ['.(x)'],
    'c.1': ['.1.']
 }


#wff_class_props = {p.label: p for p in database.propositions_list if p.vclass in ["wff", "class"]}
#pickle.dump(wff_class_props, open("wff_class_props.pkl", "wb"))

wff_class_props_file_places = [
    "wff_class_props.pkl",
    "../src/wff_class_props.pkl",
    "../../src/wff_class_props.pkl",
    "../../../src/wff_class_props.pkl",
]

wff_class_props = None
for p in wff_class_props_file_places:
    if os.path.exists(p):
        wff_class_props = pickle.load(open(p, "rb"))
        break

assert wff_class_props != None

def eval_tree(tree):
    if tree.value in context_values: 
        return context_values[tree.value]
    
    prop = wff_class_props[tree.value]
    assert len(tree.leaves)==len(prop.hyps)
    
    #find the replacement rules for the variables
    replacement_dict = {}
    for i in range(len(prop.hyps)):
        if prop.hyps[i].type == "f":
            replacement_dict[prop.hyps[i].variable] = eval_tree(tree.leaves[i])
    
    return string_replace(prop.statement[1:], replacement_dict)

def tree2str(tree, raw_symbols=False):
    evaluated_tree = eval_tree(tree)
    if raw_symbols:
        return " ".join(evaluated_tree)

    return replace_symbols(" ".join(evaluated_tree))


def get_step_replace_dict(step):
    
    repdict = {}
    
    #In case we are dealing with already hypothesis nodes, there no hypothesis to work with
    #since there is no hypotehsis of a hypothesis, we need to wrap the hyps within get_prop_hyps
    
    e_hyps = [h for h in get_prop_hyps(step.prop) if h.type == 'e']
    assert len(e_hyps) == len(step._prior_entails), print(len(e_hyps), len(step._prior_entails))

    #Populate with hypothesis
    for raw_hyp, rep_hyp in zip(e_hyps, step._prior_entails):

        raw_tree = raw_hyp.tree
        rep_tree = rep_hyp.tree

        for pos in raw_tree.breadth_first_position_list():
            raw_subtree = raw_tree.tree_at_position(pos)
            rep_subtree = rep_tree.tree_at_position(pos)
            if raw_subtree.value != rep_subtree.value:
                repdict[raw_subtree.value] = rep_subtree

    if len(e_hyps) == 0 or True:
        #Populate with conclusion (this is necessary when there is no hypothesis)
        raw_tree = step.prop.tree
        rep_tree = step.tree

        for pos in raw_tree.breadth_first_position_list():
            raw_subtree = raw_tree.tree_at_position(pos)
            rep_subtree = rep_tree.tree_at_position(pos)
            if raw_subtree.value != rep_subtree.value:
                if raw_subtree.value in repdict and rep_subtree != repdict[raw_subtree.value]:
                    print(rep_subtree, repdict[raw_subtree.value])
                    raise Exception("Different trees within same node!")
                else:
                    repdict[raw_subtree.value] = rep_subtree
        
    return repdict



def get_prop_hyps(prop):
    #We should use this function instead of direct checking for hypothesis
    #because if the prop is already a hypothesis, this property will not exist
    #which will raise an exception. This encapsulates and resolves this
    return prop.hyps if hasattr(prop, "hyps") else []
  


class PStep:
    def __init__(self, step):
        self._step = step
        self.is_hyp = step.prop.type == 'e'
        self._expanded_from = None

        self.depth = 0

        self.statement_depth = 0
        
        self.output = None
        self.inputs = []
    
    @property 
    def context(self):
        return self._step.context
    
    @property 
    def prop(self):
        return self._step.prop
    
    @property
    def label(self):
        return self._step.prop.label
    
    @property 
    def _prior_entails(self):
        return self._step._prior_entails
    
    @property 
    def tree(self):
        return self._step.tree
        
    def get_root_step(self):
        if self.output == None:
            return self
        return self.output.get_root_step() 
    
    def get_hyps(self, hyps=None):
        if hyps == None:
            hyps = []
            
        if self.is_hyp:
            assert len(self.inputs) == 0 #Sanity check
            hyps.append(self)
        else:
            for c in self.inputs:
                c.get_hyps(hyps)
        return hyps

    def get_steps_df(self, _ps_list=None):
        if _ps_list == None:
            _ps_list = []

        _ps_list.append(self)
        for child_step in self.inputs:
            child_step.get_steps_df(_ps_list)

        return _ps_list
    
    def copy(self):
        cp_psstep = PStep(self._step)

        cp_psstep.depth = self.depth
        cp_psstep.statement_depth = self.statement_depth
        cp_psstep._expanded_from = self._expanded_from

        for inp in self.inputs:
            cp_inp = inp.copy()
            cp_inp.output = cp_psstep
            cp_psstep.inputs.append(cp_inp)
        return cp_psstep
    
    def expand(self):
        if self.is_hyp:
            return self#.get_root_step()

        exp_self = expand_proof_step_ps(self)
        
        if exp_self == None: #No more expansions are possible
            return self#.get_root_step()

        exp_self._expanded_from = self

        for s in exp_self.get_steps_df():
            #Not so sure whether this is correct or not
            s._expanded_from = self
            s.depth = self.depth + 1
            s.statement_depth = self.statement_depth + 1

        #The step which calls the expand method should not have 
        #its statement depth increase since it is the same statement as the original step
        #so lets roll it back.
        exp_self.statement_depth = self.statement_depth
        
        #Replace the expanded step in the proof it belongs to
        #This means replace connections from the previous nodes with the newest nodes
        exp_self_in_proof = replace_expanded_step(self, exp_self)
        return exp_self_in_proof
        
    
    @property
    def statement(self):
        return tree2str(self.tree)

    @property
    def raw_statement(self):
        return tree2str(self.tree, True)

    @property
    def prop_statement(self):
        return tree2str(self.prop.tree)

    @property
    def raw_prop_statement(self):
        return tree2str(self.prop.tree, True)

    @property
    def prop_hyps(self):
        if self.is_hyp:
            return []

        return [tree2str(h.tree) for h in self.prop.hyps if h.type == 'e']
    
    def __repr__(self):
        obj_name = "PStep" if not self.is_hyp else "PHyp"
        return f"<{obj_name}:{self._step.prop.label} ⊢ {self.statement}>"
    
    def print_graph(self):
        print_proof_props_graph_pn(self)
    
    def print_linear(self, ident=0):
        print(" | " * ident, self)
        for cs in self.inputs:
            cs.print_linear(ident+1)
    
def construct_proof(prop):
    root_step = prop.entails_proof_steps[-1]
    return _construct_proof_recursive(root_step)
    
def _construct_proof_recursive(s):
    ps = PStep(s)
    for child_s in s._prior_entails:
        child_ps = _construct_proof_recursive(child_s)
        ps.inputs.append(child_ps)
        child_ps.output = ps
    return ps

def replace_expanded_step(step, expanded_step):
    # Replace root node
    if step.output != None:
        expanded_step.output = step.output
        step_output_index = step.output.inputs.index(step)
        step.output.inputs[step_output_index] = expanded_step
        
    # Replace hyps
    ## Get hyps out nodes (this is necessary because hyp nodes must be replaced and not connected)
    #expanded_step_hyps = [h.output for h in expanded_step.get_hyps()]
    expanded_step_hyps = expanded_step.get_hyps()
    
    #Since there may be use of the same declared hypothesis twice (like in bitri proof)
    #We need to handle this assigning hyps to a dict
    exp_hyps_dict = defaultdict(list)
    
    #We have to take the list of hypothesis this way so we can make sure the 
    #proper order is maintained with the original step inputs order.
    #Using the order returned by the depth first search in expanded_step.get_hyps() 
    #may return problematic orders like in the case of mp2 proposition in the impbii proof
    #This will also work as a sanity checker since we are getting hypothesis labels from diferent
    #places that are expected to match.
    exp_hyps_list = [h.label for h in step._step.prop.hyps if h.type == "e"]
    
    for exp_hyp in expanded_step_hyps:
        exp_hyps_dict[exp_hyp.label].append(exp_hyp)
    
    assert len(step.inputs) == len(exp_hyps_list), f"{len(step.inputs)} {step.inputs} {len(exp_hyps_list)} {exp_hyps_list} {len(exp_hyps_dict)} {exp_hyps_dict}"
     
    for step_input, exp_hyp_label in zip(step.inputs, exp_hyps_list):
        for exp_hyp in exp_hyps_dict[exp_hyp_label]:
            #We have to do this to copy branches where the hypothesis are used twice
            #This will increase the size of the tree however will prevent node crossing
            #while visualizing them, which will help us debug, which is the main goal of this project.
            step_input_cp = step_input.copy()
            step_input_cp.output = exp_hyp.output #(this is necessary because hyp nodes must be replaced and not connected)
            exp_hyp_index = exp_hyp.output.inputs.index(exp_hyp)
            exp_hyp.output.inputs[exp_hyp_index] = step_input_cp
        
    #Return new proof
    #Maybe it is a good idea to perform a deepcopy of every step
    return expanded_step#.get_root_step() 

class Step:
    def __init__(self, name):
        self.name = name

def get_proof_graph_pn(pn, node_label="label"):
    G = nx.DiGraph()
    return _get_proof_graph_pn_recursive(pn, G, node_label), G

def _get_proof_graph_pn_recursive(pn, G, node_label="label"):
    if node_label == "label+statement":
        pn_gstep = Step(f"[{pn.label}] {pn.statement}")
    else:
        pn_gstep = Step(pn.label)

    G.add_node(pn_gstep) #We need to add node this way in case it have o children
        
    for pni in pn.inputs:
        pni_gstep = _get_proof_graph_pn_recursive(pni, G, node_label)
        G.add_edge(pn_gstep, pni_gstep)
    return pn_gstep

def print_proof_props_graph_pn(pn, node_label="label"):
    
    root, G = get_proof_graph_pn(pn, node_label)

    graph_nodes = list(nx.dfs_preorder_nodes(G, root, 9))

    graph_nodes_labels = {n:n.name for n in graph_nodes}

    plt.figure(figsize=(10, 5))
    pos = graphviz_layout(G.subgraph(graph_nodes), prog="dot")#twopi
    nx.draw(G.subgraph(graph_nodes), pos, labels=graph_nodes_labels, node_color="w", node_size=2000)
    plt.show()



def expand_proof_step_ps(root_step_ps):
    
    root_step = root_step_ps._step
    
    expanded_steps = []
    
    if not hasattr(root_step, "replace_dict_list"):
        root_step.replace_dict_list = [get_step_replace_dict(root_step)]
        
    step2exp = dict() #Store references from steps to expanded steps to populate
    
    #Get all steps (This is necessary because entails_proof_step does not return hypothesis)
    all_steps = []
    for s in root_step.prop.entails_proof_steps:
        if s not in all_steps:
            all_steps.append(s)
        for s_child in s._prior_entails:
            if s_child not in all_steps:
                all_steps.append(s_child)
    
    
    for child_step in all_steps:
        #Take the original prop tree
        exp_tree = child_step.prop.tree.copy()
        
        #Take the step transformation that was used to the raw step to the replace step
        replace_dict_list = [get_step_replace_dict(child_step)]
            
        #Get the root step replace dicts so we can iterativelly expand the steps
        replace_dict_list.extend(root_step.replace_dict_list)
        
        for rep_dict in replace_dict_list:
            exp_tree = exp_tree.replace(rep_dict)
        
        prior_statements = child_step.prior_statements if hasattr(child_step, "prior_statements") else []
        
        exp_step = proof_step(exp_tree, root_step.context, child_step.prop, prior_statements)
        exp_step.replace_dict_list = replace_dict_list
        
        expanded_steps.append(exp_step)
        
        step2exp[child_step] = exp_step
        
    #Populate _prior_entails
    for child_step in all_steps:
        step2exp[child_step]._prior_entails = [step2exp.get(cc, cc) for cc in child_step._prior_entails]
    
    
    #Create PStep wrappers and populate inputs and outputs
    expanded_steps_dict = {}
    for es in expanded_steps:
        expanded_steps_dict[es] = PStep(es)
    
    for es, es_ps in expanded_steps_dict.items():
        for child_es in es._prior_entails:
            if child_es not in expanded_steps_dict:
                continue
            child_es_ps = expanded_steps_dict[child_es]
            es_ps.inputs.append(child_es_ps)
            child_es_ps.output = es_ps
            
    if len(list(expanded_steps_dict.values())) == 0:
        return None
        
    return list(expanded_steps_dict.values())[0].get_root_step()


#Expand every depth 0 nodes
def expand_all_nodes_with_depth(root, target_depth=0):
    if root.depth == target_depth:
        root = root.expand()
    
    for i in root.inputs:
        expand_all_nodes_with_depth(i, target_depth)
        
    return root