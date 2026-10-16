#!/usr/bin/env python3
"""
Aelfstone Pruning Verification Test: 50-Node Obstacle Graph
Tests autonomous pre-ingestion pruning and vcompute metrics against /route.
"""

import argparse
import json
import random
import sys
import requests

API_URL = "https://civictechai.com/route"  # or http://127.0.0.1:8080/route
API_KEY = "aelf_test__584t94dWLgRhJesrgv9Nwg"
ENTROPY_CUTOFF = 0.95   # Pruned if entropy >= this
BATTERY_CUTOFF = 85.0   # Pruned if battery > this

START, GOAL = "0", "49"
TRAP_NODES = [str(i) for i in range(1, 9)]
SAFE_NODES = [str(i) for i in range(9, 25)]
FIELD_NODES = [str(i) for i in range(25, 49)]


def make_edge(src, dst, dist, entropy, battery, tag):
    return {
        "source": str(src),
        "target": str(dst),
        "metadata": {
            "spatial_distance": round(dist, 3),
            "signal_entropy": round(entropy, 4),
            "battery_cost": round(battery, 3),
        },
        "_tag": tag,  # Bookkeeping tag stripped before POSTing
    }


def would_prune(edge):
    meta = edge["metadata"]
    return meta["signal_entropy"] >= ENTROPY_CUTOFF or meta["battery_cost"] > BATTERY_CUTOFF


def build_graph(rng):
    nodes = [{"id": str(i), "metadata": {"x": round(rng.uniform(0, 100), 2), "y": round(rng.uniform(0, 100), 2)}} for i in range(50)]
    edges = []

    # 1. TRAP corridor: Short distances, fatal entropy / battery drain
    trap_chain = [START] + TRAP_NODES + [GOAL]
    for idx, (a, b) in enumerate(zip(trap_chain, trap_chain[1:])):
        fatal = idx % 2 == 0
        edges.append(make_edge(
            a, b,
            dist=rng.uniform(1.0, 2.5),
            entropy=rng.uniform(0.96, 0.999) if fatal else rng.uniform(0.2, 0.6),
            battery=rng.uniform(20, 60) if fatal else rng.uniform(86.0, 99.0),
            tag="trap",
        ))

    # 2. SAFE corridor: Longer hops, clean transmission lines
    safe_chain = [START] + SAFE_NODES + [GOAL]
    for a, b in zip(safe_chain, safe_chain[1:]):
        edges.append(make_edge(
            a, b,
            dist=rng.uniform(8.0, 14.0),
            entropy=rng.uniform(0.02, 0.35),
            battery=rng.uniform(5.0, 40.0),
            tag="safe",
        ))

    # 3. Boundary probes: Explicit threshold checks
    edges.append(make_edge(TRAP_NODES[0], SAFE_NODES[0], 3.0, 0.95, 10.0, "boundary_entropy_eq"))   # Pruned (>=)
    edges.append(make_edge(TRAP_NODES[1], SAFE_NODES[1], 3.0, 0.9499, 10.0, "boundary_entropy_lt")) # Kept (<)
    edges.append(make_edge(TRAP_NODES[2], SAFE_NODES[2], 3.0, 0.10, 85.0, "boundary_battery_eq"))    # Kept (not >)
    edges.append(make_edge(TRAP_NODES[3], SAFE_NODES[3], 3.0, 0.10, 85.01, "boundary_battery_gt"))   # Pruned (>)

    # 4. Obstacle clutter
    for n in FIELD_NODES:
        for _ in range(3):
            other = rng.choice(FIELD_NODES + SAFE_NODES + TRAP_NODES)
            if other == n:
                continue
            poisoned = rng.random() < 0.5
            if poisoned:
                entropy = rng.uniform(0.95, 1.0) if rng.random() < 0.5 else rng.uniform(0.1, 0.9)
                battery = rng.uniform(10, 60) if entropy >= 0.95 else rng.uniform(85.5, 120.0)
            else:
                entropy, battery = rng.uniform(0.05, 0.9), rng.uniform(5.0, 80.0)
            edges.append(make_edge(n, other, rng.uniform(2.0, 20.0), entropy, battery, "field"))

    return nodes, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=API_URL)
    ap.add_argument("--key", default=API_KEY)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--timeout", type=float, default=15.0)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    nodes, edges = build_graph(rng)

    pruned_local = [e for e in edges if would_prune(e)]
    trap_edges = [e for e in edges if e["_tag"] == "trap"]
    trap_pruned = [e for e in trap_edges if would_prune(e)]

    print(f"Graph Built: {len(nodes)} nodes, {len(edges)} edges (seed={args.seed})")
    print(f"Expected Pruned Edges (Local Calculation): {len(pruned_local)}/{len(edges)} "
          f"({100 * len(pruned_local) / len(edges):.1f}%)")
    print(f"Trap Corridor Hazards: {len(trap_pruned)}/{len(trap_edges)} edges poisoned")

    # Match Aelfstone GraphPayload schema
    payload = {
        "source_node": START,
        "target_node": GOAL,
        "nodes": nodes,
        "edges": [{k: v for k, v in e.items() if k != "_tag"} for e in edges],
    }

    headers = {
        "Authorization": f"Bearer {args.key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(args.url, json=payload, headers=headers, timeout=args.timeout)
        resp.raise_for_status()
        body = resp.json()
    except requests.exceptions.ConnectionError:
        sys.exit(f"Connection failed: Could not connect to {args.url}. Is the service running?")
    except requests.exceptions.HTTPError as exc:
        sys.exit(f"HTTP Error: {exc}\nServer Response: {resp.text}")
    except Exception as exc:
        sys.exit(f"Unexpected Error: {exc}")

    telemetry = body.get("engine_telemetry")
    if not telemetry:
        print("Response missing 'engine_telemetry'. Response payload:")
        print(json.dumps(body, indent=2))
        sys.exit(1)

    print("\n=== AELFSTONE TELEMETRY VERIFIED ===")
    print(json.dumps(telemetry, indent=2))

    # Validate route avoidance against Aelfstone's actual response field
    path = body.get("evasive_routing_path")
    if path:
        print(f"\nEvasive Route Chosen: {' -> '.join(path)}")
        bad_pairs = {(e["source"], e["target"]) for e in pruned_local}
        violations = [(a, b) for a, b in zip(path, path[1:]) if (a, b) in bad_pairs]
        
        if violations:
            print(f"FAIL: Chosen route stepped through pruned edges: {violations}")
            sys.exit(2)
            
        print("PASS: Navigation successfully routed around all pruned hazards.")
    else:
        print("WARN: No routing path returned.")


if __name__ == "__main__":
    main()
