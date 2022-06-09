import pickle
import requests

from bs4 import BeautifulSoup

class TheoremDatabase:
    def __init__(self, database_file):
        self.database_file = database_file
        try:
            self.database = pickle.load(open(f"{database_file}.pkl", "rb"))
        except:
            print("Database not found. Creating new database.")
            self.database = {}

    def __getitem__(self, theorem):
        if theorem not in self.database:
            req = requests.get(f"http://us.metamath.org/mpeuni/{theorem}.html")

            if req.status_code == 404:
                self.database[theorem] = None
                return None

            if req.status_code != 200:
                return None
    
            html_text = req.text

            parsed_theorem = self._parse_theorem(html_text)

            self.database[theorem] = parsed_theorem

        return self.database[theorem]

    def _parse_theorem(self, htmltext):
        soup = BeautifulSoup(htmltext, "html.parser")

        nodes = []
        edges = []

        theorem_info = soup.find("table", summary="Assertion").find_all("td")
        theorem_name = theorem_info[0].text.strip()
        theorem_expression = " ".join(theorem_info[1].text.split())

        proof_table = soup.find("table", summary="Proof of theorem")
        if proof_table:
            for row in proof_table.find_all("tr"):
                row_data = row.find_all("td")
                if len(row_data) != 4:
                    continue
                
                step, hyp, ref, expression = row_data
                
                step = step.text
                hyps = hyp.text.strip().split(", ")
                ref = ref.find("a").text if ref.find("a") else ref.text #In case of hypothesis the reference is not placed within "a" tags
                expression = " ".join(expression.find(class_="math").text.split())
                
                nodes.append({
                    "step": step,
                    "theorem": ref,
                    "expression": expression
                })
                
                for i, h in enumerate(hyps):
                    if h:
                        edges.append((step, h, i))

        return {"theorem":theorem_name, "expression":theorem_expression, "steps": nodes, "hyps": edges}

    def save(self):
        pickle.dump(self.database, open(f"{self.database_file}.pkl", "wb"))