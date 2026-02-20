import json
import os

nodes = []
edges = []

def add_node(node_type, node_id, **properties):
    nodes.append({
        "type": node_type,
        "id": node_id,
        **properties
    })
def add_edge(source, relation, target):
    edges.append({
        "source": source,
        "relation": relation,
        "target": target
    })

def extract_enhancements(control, parent_id):
    enhancements = control.get("controls", [])

    for enh in enhancements:
        enh_id = enh.get("id")
        enh_title = enh.get("title")

        # Add enhancement node
        add_node("Enhancement", enh_id, title=enh_title)
        add_edge(parent_id, "HAS_ENHANCEMENT", enh_id)

        #  Parameters inside enhancement
        for param in enh.get("params", []):
            param_id = param.get("id")
            add_node("Parameter", param_id)
            add_edge(enh_id, "HAS_PARAMETER", param_id)

        #  Parts inside enhancement
        for part in enh.get("parts", []):
            part_id = part.get("id")
            part_name = part.get("name")

            add_node("Part", part_id, name=part_name)
            add_edge(enh_id, "HAS_PART", part_id)

        # Recursive call
        extract_enhancements(enh, enh_id)

print("Current Working Directory:", os.getcwd())

file_path = "oscal-content/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"

with open(file_path, "r") as f:
    data = json.load(f)

catalog = data["catalog"]

print(" Catalog Loaded ")

catalog_id = catalog.get("uuid")
add_node("Catalog", catalog_id)

# -------------------------------
# Extract full structure
# -------------------------------
groups = catalog.get("groups", [])

for group in groups:
    group_id = group.get("id")
    group_title = group.get("title")

    # Add Group node
    add_node("Group", group_id, title=group_title)
    add_edge(catalog_id, "HAS_GROUP", group_id)

    for control in group.get("controls", []):
        control_id = control.get("id")
        control_title = control.get("title")

        # Add Control node
        add_node("Control", control_id, title=control_title)
        add_edge(group_id, "HAS_CONTROL", control_id)

        
        for param in control.get("params", []):
            param_id = param.get("id")
            add_node("Parameter", param_id)
            add_edge(control_id, "HAS_PARAMETER", param_id)

       
        for part in control.get("parts", []):
            part_id = part.get("id")
            part_name = part.get("name")

            add_node("Part", part_id, name=part_name)
            add_edge(control_id, "HAS_PART", part_id)

        
        extract_enhancements(control, control_id)

# -------------------------------
# Final Summary
# -------------------------------
print("\n================ GRAPH SUMMARY =================")
print("Total Nodes:", len(nodes))
print("Total Edges:", len(edges))

print("\nSample Nodes:", nodes[:5])
print("\nSample Edges:", edges[:5])

import csv

# Export nodes
with open("nodes.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "type"])
    writer.writeheader()

    for node in nodes:
        writer.writerow({
            "id": node["id"],
            "type": node["type"]
        })

# Export edges
with open("edges.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["source", "relation", "target"])
    writer.writeheader()

    for edge in edges:
        writer.writerow(edge)

print("\n✅ Exported nodes.csv and edges.csv")
