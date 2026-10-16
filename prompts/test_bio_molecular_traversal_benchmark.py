#!/usr/bin/env python3
"""
Aelfstone Bio-Informatics Engine Benchmark: Molecular Binding & Affinity Pruning
Validates genomic/protein pathway traversal against /traverse.
"""

import json
import time
import requests

API_URL = "https://civictechai.com/traverse"
API_KEY = "aelf_test__584t94dWLgRhJesrgv9Nwg"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "source_node": "TARGET_PROTEIN_A",
    "target_node": "RECEPTOR_E",
    "enable_pruning": True,
    "pruning_threshold": 100.0,
    "nodes": [{"id": p, "metadata": {}} for p in ["TARGET_PROTEIN_A", "KINASE_B", "LIGAND_C", "INTERACTOR_D", "RECEPTOR_E"]],
    "edges": [
        # High affinity pathway (low dynamic traversal cost)
        {"source": "TARGET_PROTEIN_A", "target": "KINASE_B", "metadata": {"base_cost": 10.0, "affinity": 0.95, "decay": 1.0}},
        {"source": "KINASE_B", "target": "RECEPTOR_E", "metadata": {"base_cost": 12.0, "affinity": 0.88, "decay": 1.05}},
        
        # Low affinity pathways (cost > 100.0, pruned before RAM allocation)
        {"source": "TARGET_PROTEIN_A", "target": "LIGAND_C", "metadata": {"base_cost": 50.0, "affinity": 0.10, "decay": 1.5}},
        {"source": "LIGAND_C", "target": "INTERACTOR_D", "metadata": {"base_cost": 60.0, "affinity": 0.05, "decay": 2.0}},
        {"source": "INTERACTOR_D", "target": "RECEPTOR_E", "metadata": {"base_cost": 40.0, "affinity": 0.12, "decay": 1.2}}
    ]
}

start = time.perf_counter()
resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
elapsed_ms = (time.perf_counter() - start) * 1000.0

if resp.status_code == 200:
    data = resp.json()
    print("=== AELFSTONE BIO-INFORMATICS BENCHMARK ===")
    print(f"Network RTT:            {elapsed_ms:.2f} ms")
    print(f"Traversal Depth:        {data.get('traversal_depth')}")
    print(f"Edges Pruned from RAM:  {data.get('edges_pruned_from_ram')}")
    print(f"Optimized Path:         {' -> '.join(data.get('optimized_path', []))}")
    print("Engine Telemetry:", json.dumps(data.get("engine_telemetry"), indent=2))
else:
    print(f"Error {resp.status_code}: {resp.text}")
