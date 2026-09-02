import json
import os

def list_files(directory):
    return os.listdir(directory)

print("start reading dict")
amr_dict_path = "./amr_panaroo_dict.json"
with open(amr_dict_path, 'r', encoding='utf-8') as file:
    # Read the JSON file and convert it to a dictionary
    data = json.load(file)
amr_keys = data.keys()

print("start reading file lists")
core_files_with_ref = list_files("./core_gene_sequences_with_ref/")
new_core_files_with_ref = [f.removesuffix('.aln.fas') for f in core_files_with_ref]
core_files_without_ref = list_files("./core_gene_sequences_without_ref/")
new_core_files_without_ref = [f.removesuffix('.aln.fas') for f in core_files_without_ref]
print(new_core_files_without_ref)
rare_files = list_files("./rare_gene_sequences/")
new_rare_files = [f.removesuffix('.aln.fas') for f in rare_files]
dispensable_files = list_files("./dispensable_gene_sequences/")
new_dispensable_files = [f.removesuffix('.aln.fas') for f in dispensable_files]

print("start counting")
core_count = 0
dis_count = 0
rare_count = 0
non_exiseting = []
for i in data:
    flags=0
    if i in new_core_files_with_ref or i in new_core_files_without_ref:
        core_count+=1
        flags=1
    else:
        v=data[i]
        if v in new_core_files_with_ref or v in new_core_files_without_ref:
            core_count+=1
            flags=1
    if i in new_rare_files:
        rare_count+=1
        flags=2
    else:
        v=data[i]
        if v in new_rare_files:
            rare_count+=1
            flags=2
    if i in new_dispensable_files and i not in new_rare_files:
        dis_count+=1
        flags=3
    else:
        v=data[i]
        if v in new_dispensable_files and v not in new_rare_files:
            dis_count+=1
            flags=3
    print(i)
    if flags==0:
        print("not exist")
        non_exiseting.append(i)
    elif flags==1:
        print("core")
    elif flags==2:
        print("rare")
    elif flags==3:
        print("dis")

print(core_count,dis_count,rare_count)
#Composition of 296 items: 22 core, 187 dispensable, 22 rare, and the remaining invalid. Total: 296.