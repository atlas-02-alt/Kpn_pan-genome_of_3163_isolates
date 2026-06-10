import os
import json

rgi_root = "./both-align-results-strict-adv/rgi_results/"

mutation_models = set()

for root, dirs, files in os.walk(rgi_root):
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(root, file)) as f:
                data = json.load(f)

            for orf in data:
                for hsp in data[orf]:
                    hit = data[orf][hsp]

                    model_type = str(hit.get("model_type_id"))

                    if model_type in ["40293", "40295"]:
                        model_name = hit.get("model_name")
                        aro = hit.get("ARO_accession")

                        mutation_models.add((model_name, aro))

print("Total unique functional mutation models:", len(mutation_models))

with open("all_functional_mutations.txt", "w") as out:
    for m in sorted(mutation_models):
        out.write(f"{m[0]}\t{m[1]}\n")