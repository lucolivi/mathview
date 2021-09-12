import requests
from bs4 import BeautifulSoup

import json

import pickle

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
    return jsonify(tdb[theorem])

@app.route("/graph/<theorem>")
def get_theorem_graph(theorem):

    return render_template('theorem.html', theorem=theorem)


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