import networkx as nx

from networkx.drawing.nx_pydot import graphviz_layout

from adapt_utils import replace_symbols

from collections import Counter

def is_label(token):

    if token not in [
        '$(',
        '$)',
        '${',
        '$}',
        '$c',
        '$d',
        '$v',
        '$f',
        '$e',
        '$a',
        '$p',
        '$=',
        '$[',
        '$]',
    ]:
        return True
    
    return False


class Step:
    def __init__(self, name):
        self.name = name
    #def __repr__(self):
        #return self.name

class ProofStep:
    def __init__(self, step_object, database):
        self._step_object = step_object
        self.label = self._step_object.prop.label
        self.statement = replace_symbols(self._step_object.tree.eval(database, self._step_object.context))

    def __repr__(self):
        return self.label
        
def get_proof_graph(p, database):
    """This version deduces directly the proof graph from the proof step list."""

    prop = database.propositions[p]

    proof_stack = list()

    G = nx.DiGraph()

    for step in prop.proof:
        step_obj = Step(step)#{"name": step}

        #If the step is in the database proposition, process it with other steps from the stack
        #At the end append the new step with their axes to the stack
        if step in database.propositions:
            step_prop = database.propositions[step]

            for hyp in reversed(step_prop.hyps):
                stack_elem = proof_stack.pop()
                if hyp.type == "e":
                    G.add_edge(step_obj, stack_elem)

        proof_stack.append(step_obj) 
        
    root = proof_stack[0]

    return G, root

def get_proof_steps_graph(p, database):
    """This version uses the property _prior_entails from proof steps to generate the proof graph."""

    prop = database.propositions[p]

    root = ProofStep(prop.entails_proof_steps[-1], database)

    G = nx.DiGraph()

    proof_stack = [root]

    while len(proof_stack) > 0:
        current_node = proof_stack.pop()

        for proof_step in current_node._step_object._prior_entails:
            proof_step_node = ProofStep(proof_step, database)

            G.add_edge(current_node, proof_step_node)

            proof_stack.append(proof_step_node)
            
    return G, root

def print_proof_props_graph(p, database):
    import matplotlib.pyplot as plt

    G, root = get_proof_graph(p, database)

    graph_nodes = list(nx.dfs_preorder_nodes(G, root, 9))
    #print(len(graph_nodes))

    graph_nodes_labels = {n:n.name for n in graph_nodes}

    #graph_nodes_labels = {n: " ".join(database.propositions[n.name].statement) for n in graph_nodes}

    plt.figure(figsize=(10, 5))
    pos = graphviz_layout(G.subgraph(graph_nodes), prog="dot")#twopi
    nx.draw(G.subgraph(graph_nodes), pos, labels=graph_nodes_labels, node_color="w", node_size=2000)
    plt.show()

def get_proof_steps(prop, depth=0, max_depth=3, cntr=None):
    
    cntr[prop.label] += 1
    
    proof_steps = {
        "theorem": prop.label, 
        "statement": replace_symbols(" ".join(prop.statement)),
        "steps": []
    }
     
    if depth < max_depth:
        for step in prop.entails_proof_steps:
            proof_step = get_proof_steps(step.prop, depth=depth+1, max_depth=max_depth, cntr=cntr)
            proof_steps["steps"].append(proof_step)
            
    return proof_steps 


def print_proof_steps(proof_steps, identation=0, cntr=None):
    print("".join([" | "] * identation) + "[" + str(cntr[proof_steps["theorem"]]) + "] " + proof_steps["theorem"] + " - " + proof_steps["statement"])
    for step in proof_steps["steps"]:
        print_proof_steps(step, identation=identation+1, cntr=cntr)     

def print_ident_proof(p, database, max_depth=1):
    occur_counter = Counter()
    proof_steps = get_proof_steps(database.propositions[p], max_depth=max_depth, cntr=occur_counter)
    print_proof_steps(proof_steps, cntr=occur_counter)

def print_proof_linear_steps(p, database):
    prop = database.propositions[p]
    for s in prop.entails_proof_steps:
        print("[{}]".format(s.prop.label), "|-", replace_symbols(s.tree.eval(database, prop)))


def print_proof_steps_graph(G, root, figsize=(30,10), node_size=3000):
    import matplotlib.pyplot as plt

    graph_nodes = list(nx.dfs_preorder_nodes(G, root, 9))

    graph_nodes_labels = {n:n.statement for n in graph_nodes}

    plt.figure(figsize=figsize)
    pos = graphviz_layout(G.subgraph(graph_nodes), prog="dot")#twopi
    nx.draw(G.subgraph(graph_nodes), pos, labels=graph_nodes_labels, node_color="w", node_size=node_size)
    plt.show()