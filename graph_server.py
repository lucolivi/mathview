import requests
from bs4 import BeautifulSoup

from collections import defaultdict

import json

import pickle

import math

from theorem_database import TheoremDatabase

import os

from tree_parser import meta_math_database, file_contents, tree_to_string

from adapt_utils import replace_symbols

from expanding import construct_proof

from flask import Flask, jsonify, abort, render_template, request, send_from_directory

app = Flask(__name__, static_url_path='/static')

tdb = TheoremDatabase("tdb")

edges_cnt = pickle.load(open("edges_cnt.pkl", "rb"))

database = meta_math_database(file_contents("set.mm"),n=3500)

#Load test data
testdata = dict()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/save")
def save_database():

    #pickle.dump(database, open("theorem_database.pkl", "wb"))
    tdb.save()

    return "Database saved."


def get_proof_steps_list_df(root_step, _ps_list=None):
    if _ps_list == None:
        _ps_list = []

    _ps_list.append(root_step)
    for child_step in root_step.inputs:
        get_proof_steps_list_df(child_step, _ps_list)

    return _ps_list


@app.route("/debug_get")
def debug_get():
    return jsonify(request.args)

@app.route("/theorem_db_exp/<theorem>")
def get_theorem_from_db_exp(theorem):

    if theorem not in database.propositions:
        abort(404)
        #return "Theorem not found."

    prop = database.propositions[theorem]
    
    prop_proof = construct_proof(prop)

    #Perform required expansions
    # num_expansions = int(request.args.get('expansions', 0))
    # for _ in range(num_expansions):
    #     prop_proof = prop_proof.expand()

    #Get expansions ids
    expansion_ids = request.args.get('expansions_ids', None)
    if expansion_ids:
        expansions_ids = [int(i) for i in expansion_ids.split(";")]
    else:
        expansions_ids = []

    while True:
        proof_steps = get_proof_steps_list_df(prop_proof)
        proof_steps_dict = {}

        #Populate step numbers
        step_i = 0
        for ps in proof_steps:
            step_i += 1
            ps.step_num = step_i
            proof_steps_dict[ps.step_num] = ps

        #Check if there is expansions to perform, otherwise exit loop
        if len(expansions_ids) == 0:
            break
        else: #Expand step and goes around the loop to recompute steps ids
            next_exp_id = expansions_ids.pop(0)
            prop_proof = proof_steps_dict[next_exp_id].expand()

    
    #Populate hyps
    hyps = []
    for ps in proof_steps:
        for child_step in ps.inputs:
            hyps.append([ps.step_num, child_step.step_num])

    steps = []
    for ps in proof_steps:
        pstep_expr = "⊢ " + ps.statement
        pstep_label = ps.label

        #This is used to highlight nodes that should not be hidden
        ground_truth_display = False
        if theorem in testdata:
            if pstep_label + " " + pstep_expr in testdata[theorem]:
                ground_truth_display = True    

        pstep_dict = {
            "edge_count": len(ps.inputs),
            "edge_count_norm": 1.0, 
            "expression": pstep_expr, 
            "lemma_complexity": 1.0, 
            "lemma_log_complexity": 1.0, 
            "log_complexity": 1.0, 
            "norm_complexity": 1.0, 
            "step": ps.step_num, 
            "step_complexity": 1.0, 
            "step_prob": 1,#float(pstep.step_prob),
            "step_obviousness": 1, #float(pstep.step_obviousness),
            "theorem": pstep_label,
            "ground_truth": pstep_label + " " + pstep_expr,
            "ground_truth_display": ground_truth_display
        } 

        steps.append(pstep_dict)

    theorem_obj = {
        "theorem": prop.label,
        "hyps": hyps,
        "expression": prop_proof.statement,
        "complexity": 1.0,
        "steps": steps
    }

    return jsonify(theorem_obj)

@app.route("/theorem_db/<theorem>")
def get_theorem_from_db(theorem):

    if theorem not in database.propositions:
        return "Theorem not found."

    prop = database.propositions[theorem]
    #set_prop_probs(prop)
    #set_prop_obviousness(prop)

    expression = replace_symbols("|- " + " ".join(tree_to_string(prop.tree, database, prop)))

    #List all
    all_steps = []

    #Populate step numbers and hyps
    hyps = []
    step_i = 0
    for pstep in prop.entails_proof_steps:
        if pstep not in all_steps:
            all_steps.append(pstep)

        if not hasattr(pstep, "step_num"):
            step_i += 1
            pstep.step_num = step_i
            #print(pstep.prop.label, step_i)
        
        for prior_pstep in pstep._prior_entails:
            if prior_pstep not in all_steps:
                all_steps.append(prior_pstep)

            if not hasattr(prior_pstep, "step_num"):
                step_i += 1
                prior_pstep.step_num = step_i
                #print(prior_pstep.prop.label, step_i)

            hyps.append([pstep.step_num, prior_pstep.step_num])

    steps = []
    for pstep in all_steps:
        pstep_expr = replace_symbols("⊢ " + " ".join(tree_to_string(pstep.tree, database, prop)))
        pstep_label = pstep.prop.label

        ground_truth_display = False
        if theorem in testdata:
            if pstep_label + " " + pstep_expr in testdata[theorem]:
                ground_truth_display = True    

        pstep_dict = {
            "edge_count": len(pstep._prior_entails),
            "edge_count_norm": 1.0, 
            "expression": pstep_expr, 
            "lemma_complexity": 1.0, 
            "lemma_log_complexity": 1.0, 
            "log_complexity": 1.0, 
            "norm_complexity": 1.0, 
            "step": pstep.step_num, 
            "step_complexity": 1.0, 
            "step_prob": 1,#float(pstep.step_prob),
            "step_obviousness": 1, #float(pstep.step_obviousness),
            "theorem": pstep_label,
            "ground_truth": pstep_label + " " + pstep_expr,
            "ground_truth_display": ground_truth_display
        } 

        steps.append(pstep_dict)

    theorem_obj = {
        "theorem": prop.label,
        "hyps": hyps,
        "expression": expression,
        "complexity": 1.0,
        "steps": steps
    }

    return jsonify(theorem_obj)

@app.route("/theorem/<theorem>")
def get_theorem(theorem):
    #return get_theorem_from_website(theorem)
    #return get_theorem_from_db(theorem)
    return get_theorem_from_db_exp(theorem)

@app.route("/theorem_website/<theorem>")
def get_theorem_from_website(theorem):

    # force = bool(request.args.get("force", default = 0))

    # if theorem not in database or force:
    #     req = requests.get(f"http://us.metamath.org/mpeuni/{theorem}.html")

    #     if req.status_code != 200:
    #         abort(req.status_code)
    
    #     html_text = req.text

    #     database[theorem] = parse_theorem(html_text)
    #     save_database()

    # #return render_template('theorem.html', theorem_obj=json.dumps(theorem_obj))
    theorem_obj = tdb[theorem].copy()

    hyps_dict = defaultdict(list)
    for source, target, _ in theorem_obj["hyps"]:
        hyps_dict[source].append(target)

    steps_dict = dict()
    for step in theorem_obj["steps"]:
        steps_dict[step["step"]] = step

    for step in theorem_obj["steps"]:
        get_step_complexity(step, hyps_dict, steps_dict)

    #Generate log complexities
    for step in theorem_obj["steps"]:
        if step["step_complexity"] > 0:
            step["log_complexity"] = round(math.log(step["step_complexity"]), 5)
        else:
            step["log_complexity"] = 0

    #Generate norm complexities
    final_complexity = theorem_obj["complexity"]
    for step in theorem_obj["steps"]:
        step["norm_complexity"] = round(step["step_complexity"] / final_complexity, 5)

    #Insert lemma complexities
    for step in theorem_obj["steps"]:
        if tdb[step["theorem"]]:
            step["lemma_complexity"] = tdb[step["theorem"]]["complexity"]
            step["lemma_log_complexity"] = round(math.log(step["lemma_complexity"]), 5)

    #Insert edges counts
    #Since target theorems do not repeat, store the edge count values using them as keys
    theorem_edges_cnt = defaultdict(int)
    for source, targets in hyps_dict.items():
        source_theorem = steps_dict[source]["theorem"]
        for target in targets:
            target_theorem = steps_dict[target]["theorem"]
            e_cnt = max(edges_cnt[(source_theorem, target_theorem)], 1) #Put minimum of 1 here to prevent return null edges
            #print("ecnt", e_cnt)
            theorem_edges_cnt[target] = e_cnt
            #print(source_theorem, target_theorem, e_cnt)

    theorem_edges_cnt_sum = sum(theorem_edges_cnt.values())

    for step in theorem_obj["steps"]:
        step["edge_count"] = theorem_edges_cnt[step["step"]]
        step["edge_count_norm"] = theorem_edges_cnt[step["step"]] / theorem_edges_cnt_sum
    
    #print(theorem_edges_cnt)

    #print(hyps_dict.values())
    #print(steps_dict)
    #target_dict = dict()
    #for source, target, _ in theorem_obj["hyps"]:
    #    target_dict
    #    hyps_dict[source].append(target)


    return jsonify(theorem_obj)

def get_step_complexity(step, hyps_dict, steps_dict):
    """Returns the step complexity which is the sum of the complexities of all its predecessors hypothesis."""

    if "step_complexity" not in step:

        step_theorem = tdb[step["theorem"]]

        if step_theorem:
            #step["step_complexity"] = step_theorem["complexity"]
            _step_complexity = step_theorem["complexity"]
            for child_step_num in hyps_dict[step["step"]]:
                child_step = steps_dict[child_step_num]
                _step_complexity += get_step_complexity(child_step, hyps_dict, steps_dict)
        
            step["step_complexity"] =  _step_complexity
            step["lemma_complexity"] = step_theorem["complexity"]

        else:
            step["step_complexity"] = 0
            step["lemma_complexity"] = 0

    return step["step_complexity"]


@app.route("/graph/<theorem>")
def get_theorem_graph(theorem):

    theorem_complexity = tdb[theorem]["complexity"]
    theorem_log_completixy = math.log(theorem_complexity)

    return render_template('theorem.html', theorem=theorem, complexity=theorem_complexity, log_complexity=theorem_log_completixy)

@app.route("/graphtree/<theorem>")
def get_theorem_graph_tree(theorem):

    theorem_complexity = tdb[theorem]["complexity"]
    theorem_log_completixy = math.log(theorem_complexity)

    return render_template('graphtree.html', theorem=theorem, complexity=theorem_complexity, log_complexity=theorem_log_completixy)


@app.route("/graphtree_exp/<theorem>")
def get_theorem_graph_tree_exp(theorem):

    theorem_complexity = 10 #tdb[theorem]["complexity"]
    theorem_log_completixy = math.log(theorem_complexity)

    return render_template('graphtree_exp.html', theorem=theorem, complexity=theorem_complexity, log_complexity=theorem_log_completixy)


@app.route("/linear/<theorem>")
def get_theorem_linear(theorem):

    theorem_complexity = tdb[theorem]["complexity"]
    theorem_log_completixy = math.log(theorem_complexity)

    return render_template('linear.html', theorem=theorem, complexity=theorem_complexity, log_complexity=theorem_log_completixy)

@app.route("/natural/<theorem>")
def get_theorem_natural(theorem):

    theorem_complexity = tdb[theorem]["complexity"]
    theorem_log_completixy = math.log(theorem_complexity)

    return render_template('natural.html', theorem=theorem, complexity=theorem_complexity, log_complexity=theorem_log_completixy)


# def parse_theorem(htmltext):
#     soup = BeautifulSoup(htmltext)

#     nodes = []
#     edges = []

#     theorem_info = soup.find("table", summary="Assertion").find_all("td")
#     theorem_name = theorem_info[0].text
#     theorem_expression = theorem_info[1].text

#     proof_table = soup.find("table", summary="Proof of theorem")
#     if proof_table:
#         for row in proof_table.find_all("tr"):
#             row_data = row.find_all("td")
#             if len(row_data) != 4:
#                 continue
            
#             step, hyp, ref, expression = row_data
            
#             step = step.text
#             hyps = hyp.text.strip().split(", ")
#             ref = ref.find("a").text if ref.find("a") else ref.text #In case of hypothesis the reference is not placed within "a" tags
#             expression = " ".join(expression.find(class_="math").text.split())
            
#             nodes.append({
#                 "step": step,
#                 "theorem": ref,
#                 "expression": expression
#             })
            
#             for i, h in enumerate(hyps):
#                 if h:
#                     edges.append((step, h, i))

#     if len(nodes) == 0:
#         complexity = 1
#     else:
#         complexity = 0


#     return {"theorem":theorem_name, nodes": nodes, "edges": edges, "complexity": complexity}



if __name__ == "__main__":
    app.run(debug=True, port=5002)