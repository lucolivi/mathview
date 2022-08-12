import sys
sys.path.append("../src")

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

import glob

import random

from models_functions import get_props_features_xy

app = Flask(__name__, static_url_path='/static')

tdb = TheoremDatabase("../data/tdb")

edges_cnt = pickle.load(open("../data/edges_cnt.pkl", "rb"))

database = meta_math_database(file_contents("../data/set_mod.mm"), n=5000)

print("Loading model...")
model_name = "1660273773.971621"
ml_model = pickle.load(open(os.path.join("../data/trained_models", model_name, "model.pkl"), "rb"))

#Load test data
testdata = dict()
for f in glob.glob(os.path.join("../data/test_data", "*.txt")):
    f_rev = "".join(reversed(f))
    f_name = "".join(reversed(f_rev[4:f_rev.index("/")]))
    testdata[f_name] = [l[l.index("⊢"):-1] for l in open(f).readlines() if len(l) > 2]

print(testdata)

def get_theorem_complexity(theorem_name):
    theorem = tdb[theorem_name]
    
    if theorem == None:
        return 0
    
    if "complexity" not in theorem:
        print(theorem["theorem"])
        
        if len(theorem["steps"]) == 0:
            theorem["complexity"] = 1
        else:
            theorem["complexity"] = sum([get_theorem_complexity(tt["theorem"]) for tt in theorem["steps"]])
            
    return theorem["complexity"]


def get_prop_data(prop_proof):
    
    # prop = database.propositions[prop_label]
    
    # prop_proof = construct_proof(prop)

    prop_dataset = {
        'steps':[],
        'links':[]
    }

    #Populate step numbers
    next_step_n = 0
    for s in prop_proof.get_steps_df(): 
        next_step_n += 1
        s._step_num = next_step_n

    for s in prop_proof.get_steps_df():

        prop_dataset["steps"].append((
            s._step_num,
            s.label,
            s.raw_statement,
            s.raw_prop_statement,
            get_theorem_complexity(s.label), #Lemma complexity
            int(s.statement_depth == 0)
        ))

        for child_s in s.inputs:
            prop_dataset["links"].append((child_s._step_num, s._step_num))


    return prop_dataset




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/save")
# def save_database():

#     #pickle.dump(database, open("theorem_database.pkl", "wb"))
#     tdb.save()

#     return "Database saved."


@app.route("/debug_get")
def debug_get():
    return jsonify(request.args)

@app.route("/theorem_list")
def get_theorem_list_from_db():
    return "<br>".join([f'<a href="../graphtree_exp/{p.label}">{p.label}</a>'  for p in database.propositions_list if p.vclass == "|-"])


@app.route("/theorem_db_exp/<theorem>")
def get_theorem_from_db_exp(theorem):

    if theorem not in database.propositions:
        abort(404)
        #return "Theorem not found."

    prop = database.propositions[theorem]
    
    prop_proof = construct_proof(prop)

    #Get expansions ids
    expansion_ids = request.args.get('expansions_ids', None)
    if expansion_ids:
        expansions_ids = [int(i) for i in expansion_ids.split(";")]
    else:
        expansions_ids = []

    while True:
        proof_steps = prop_proof.get_steps_df()
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
            prop_proof = proof_steps_dict[next_exp_id].expand().get_root_step()


    #Get Ml Model prediction
    prop_features_x, _ = get_props_features_xy(get_prop_data(prop_proof))
    pred_y = ml_model.predict_proba(prop_features_x)[:,1]
    
    #Populate hyps
    hyps = []
    for ps in proof_steps:
        for child_step in ps.inputs:
            hyps.append([ps.step_num, child_step.step_num])

    steps = []
    for ps, ml_pred_y in zip(proof_steps, pred_y):
        pstep_expr = "⊢ " + ps.statement
        pstep_label = ps.label

        #This is used to highlight nodes that should not be hidden
        ground_truth_display = False
        if theorem in testdata:
            #if pstep_label + " " + pstep_expr in testdata[theorem]:
            if pstep_expr in testdata[theorem]:
                ground_truth_display = True    

        pstep_dict = {

            "expression": pstep_expr, 
            "prop_expression": ", ".join(ps.prop_hyps) + " ⊢ " + ps.prop_statement,
            "step": ps.step_num, 
            "theorem": pstep_label,
            "ground_truth": pstep_label + " " + pstep_expr,
            "ground_truth_display": ground_truth_display,
            "statement_depth": ps.statement_depth,

            #Granularity useful metrics
            #"step_prob": 1,#float(pstep.step_prob),
            #"step_obviousness": 1, #float(pstep.step_obviousness),
            #"step_complexity": 1.0, 
            "_thrs_random_value": round(random.random(),4),
            "_thrs_lemma_complexity": get_theorem_complexity(pstep_label), #tdb[pstep_label]["complexity"],
            #"lemma_log_complexity": math.log(tdb[pstep_label]["complexity"]), 
            #"log_complexity": 1.0, 
            #"norm_complexity": 1.0, 
            "_thrs_edge_count": len(ps.inputs),
            "_thrs_symbols_count": round(1 / len(pstep_expr.split(" ")), 5),
            "_thrs_statement_depth": -ps.statement_depth,
            "_thrs_ml_prediction": round(ml_pred_y, 5)
            #"edge_count_norm": 1.0, 
        } 

        steps.append(pstep_dict)

    theorem_obj = {
        "theorem": prop.label,
        "hyps": hyps,
        "expression": prop_proof.statement,
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

    expression = replace_symbols("⊢ " + " ".join(tree_to_string(prop.tree, database, prop)))

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
        "complexity": tdb[theorem]["complexity"],
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

    return render_template('graphtree_exp.html', theorem=theorem)


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



if __name__ == "__main__":
    app.run(debug=True, port=5002, host="0.0.0.0")