import requests
from bs4 import BeautifulSoup

from collections import defaultdict

import json

import pickle

import math

from theorem_database import TheoremDatabase


from flask import Flask, jsonify, abort, render_template, request

app = Flask(__name__, static_url_path='/static')

tdb = TheoremDatabase("tdb")

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/save")
def save_database():

    #pickle.dump(database, open("theorem_database.pkl", "wb"))
    tdb.save()

    return "Database saved."

@app.route("/theorem/<theorem>")
def get_theorem(theorem):

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
        step["log_complexity"] = round(math.log(step["step_complexity"]), 5)

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

        else:
            step["step_complexity"] = 0

    return step["step_complexity"]


@app.route("/graph/<theorem>")
def get_theorem_graph(theorem):

    theorem_complexity = tdb[theorem]["complexity"]
    theorem_log_completixy = math.log(theorem_complexity)

    return render_template('theorem.html', theorem=theorem, complexity=theorem_complexity, log_complexity=theorem_log_completixy)


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
    app.run(debug=True)