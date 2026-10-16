
#!/usr/bin/env python3
"""
Aelfstone Spatial Telemetry — synthetic graph verification benchmark.

Install:
    python -m pip install requests

Run:
    export AELFSTONE_TOKEN="your-bearer-token"
    python verify_aelfstone.py

Optional:
    export AELFSTONE_URL="https://civictechai.com/route"
    export AELFSTONE_TIMEOUT="30"
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import Any

import requests


ENDPOINT = os.getenv(
    "AELFSTONE_URL",
    "https://civictechai.com/route",
)
TOKEN = os.getenv("AELFSTONE_TOKEN", "")
TIMEOUT = float(os.getenv("AELFSTONE_TIMEOUT", "30"))

NODE_COUNT = 50
ENTROPY_LIMIT = 0.95
BATTERY_LIMIT = 85.0
SEED = 20261016


def is_hazardous(edge: dict[str, Any]) -> bool:
    """Mirror the pruning rules specified for the engine."""
    metadata = edge["metadata"]
    return (
        metadata["signal_entropy"] >= ENTROPY_LIMIT
        or metadata["battery_cost"] > BATTERY_LIMIT
    )


def make_edge(
    source: str,
    target: str,
    distance: float,
    entropy: float,
    battery: float,
    corridor: str,
) -> dict[str, Any]:
    return {
        "source": source,
        "target": target,
        "metadata": {
            "spatial_distance": float(distance),
            "signal_entropy": float(entropy),
            "battery_cost": float(battery),
            "corridor": corridor,
        },
    }


def build_graph() -> dict[str, Any]:
    """
    Create 50 nodes with:
      * A guaranteed safe route from source to target.
      * Short, hazardous trap edges competing with safe edges.
      * Additional safe links and hazardous decoy links.
    """
    rng = random.Random(SEED)
    nodes = [
        {
            "id": f"n{i:02d}",
            "x": float(i % 10),
            "y": float(i // 10),
            "obstacle": i in {12, 13, 22, 23, 32, 33},
        }
        for i in range(NODE_COUNT)
    ]

    edges: list[dict[str, Any]] = []

    # Guaranteed safe backbone: n00 -> n01 -> ... -> n49.
    for i in range(NODE_COUNT - 1):
        edges.append(
            make_edge(
                f"n{i:02d}",
                f"n{i + 1:02d}",
                distance=rng.uniform(8.0, 15.0),
                entropy=rng.uniform(0.05, 0.45),
                battery=rng.uniform(10.0, 45.0),
                corridor="safe_backbone",
            )
        )

    # Shortcuts that look attractive by distance but must be pruned.
    for i in range(0, NODE_COUNT - 4, 4):
        edges.append(
            make_edge(
                f"n{i:02d}",
                f"n{i + 4:02d}",
                distance=0.25,
                entropy=0.99,
                battery=10.0,
                corridor="trap_high_entropy",
            )
        )

    # Independent hazardous edges for the battery threshold.
    for i in range(2, NODE_COUNT - 2, 7):
        edges.append(
            make_edge(
                f"n{i:02d}",
                f"n{i + 2:02d}",
                distance=0.50,
                entropy=0.20,
                battery=90.0,
                corridor="trap_high_battery",
            )
        )

    # Safe cross-links offer alternate routing options.
    for i in range(NODE_COUNT - 3):
        if i % 3 == 0:
            edges.append(
                make_edge(
                    f"n{i:02d}",
                    f"n{i + 3:02d}",
                    distance=rng.uniform(12.0, 22.0),
                    entropy=rng.uniform(0.10, 0.60),
                    battery=rng.uniform(15.0, 60.0),
                    corridor="safe_crosslink",
                )
            )

    return {
        "source_node": "n00",
        "target_node": "n49",
        "nodes": nodes,
        "edges": edges,
    }


def extract_route(data: dict[str, Any]) -> list[str]:
    """
    Adapt this function if the API returns a different route representation.

    Accepted examples:
      {"path": ["n00", "n01", ...]}
      {"route": {"nodes": ["n00", "n01", ...]}}
      {"route": ["n00", "n01", ...]}
    """
    route = data.get("path", data.get("route"))

    if isinstance(route, dict):
        route = route.get("nodes")

    if not isinstance(route, list) or not all(
        isinstance(node, str) for node in route
    ):
        raise ValueError(
            "No supported route list found in the response. "
            "Expected 'path', 'route', or 'route.nodes'. "
            f"Response keys: {list(data.keys())}"
        )

    return route


def verify_route(
    payload: dict[str, Any],
    route: list[str],
) -> tuple[bool, list[str]]:
    """
    Check every consecutive route hop against the submitted graph.

    A hop is considered safe only if a corresponding directed edge
    exists and is not hazardous.
    """
    edges_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for edge in payload["edges"]:
        pair = (edge["source"], edge["target"])
        edges_by_pair.setdefault(pair, []).append(edge)

    issues: list[str] = []

    if not route:
        return False, ["The returned route is empty."]

    if route[0] != payload["source_node"]:
        issues.append(
            f"Wrong route start: expected {payload['source_node']}, "
            f"got {route[0]}."
        )

    if route[-1] != payload["target_node"]:
        issues.append(
            f"Wrong route destination: expected {payload['target_node']}, "
            f"got {route[-1]}."
        )

    known_nodes = {node["id"] for node in payload["nodes"]}
    for node_id in route:
        if node_id not in known_nodes:
            issues.append(f"Unknown node in route: {node_id}")

    for source, target in zip(route, route[1:]):
        candidates = edges_by_pair.get((source, target), [])

        if not candidates:
            issues.append(
                f"Route hop {source} -> {target} has no matching "
                "directed edge in the submitted graph."
            )
            continue

        if all(is_hazardous(edge) for edge in candidates):
            issues.append(
                f"Route uses a pruned hazardous edge: {source} -> {target}"
            )

    return not issues, issues


def main() -> int:
    if not TOKEN:
        print(
            "ERROR: Set AELFSTONE_TOKEN to your API Bearer token.",
            file=sys.stderr,
        )
        return 2

    payload = build_graph()

    hazardous = [e for e in payload["edges"] if is_hazardous(e)]
    safe = [e for e in payload["edges"] if not is_hazardous(e)]

    print("Aelfstone Spatial Telemetry benchmark")
    print("=" * 42)
    print(f"Endpoint:          {ENDPOINT}")
    print(f"Nodes:             {len(payload['nodes'])}")
    print(f"Edges submitted:   {len(payload['edges'])}")
    print(f"Safe edges:        {len(safe)}")
    print(f"Hazardous edges:   {len(hazardous)}")
    print(f"Source:            {payload['source_node']}")
    print(f"Target:            {payload['target_node']}")

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        started = time.perf_counter()
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
        latency_ms = (time.perf_counter() - started) * 1000.0

        print(f"\nHTTP status:       {response.status_code}")
        print(f"Request latency:   {latency_ms:.2f} ms")

        response.raise_for_status()

        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise ValueError(
                "Endpoint returned a non-JSON response."
            ) from exc

        print("\nEngine response:")
        print(json.dumps(result, indent=2))

        # Required metric: don't silently substitute a fabricated value.
        conserved = result.get("vcompute_conserved_pct")
        if isinstance(conserved, (int, float)) and not isinstance(
            conserved, bool
        ):
            print(f"\nvcompute_conserved_pct: {conserved:.4f}%")
        else:
            print(
                "\nWARNING: vcompute_conserved_pct is missing or "
                "is not numeric."
            )

        route = extract_route(result)
        passed, issues = verify_route(payload, route)

        print(f"\nReturned route ({len(route)} nodes):")
        print(" -> ".join(route))

        print("\nVerification:")
        if passed:
            print("PASS: route endpoints and all route hops verified.")
            print("PASS: no route hop relies exclusively on a pruned edge.")
        else:
            print("FAIL: route verification found issues.")
            for issue in issues:
                print(f"  - {issue}")

        # Report whether the submitted graph actually exercised both
        # pruning rules, independently of the returned route.
        entropy_traps = sum(
            e["metadata"]["signal_entropy"] >= ENTROPY_LIMIT
            for e in payload["edges"]
        )
        battery_traps = sum(
            e["metadata"]["battery_cost"] > BATTERY_LIMIT
            for e in payload["edges"]
        )

        print("\nPruning test coverage:")
        print(f"High-entropy edges: {entropy_traps}")
        print(f"High-battery edges: {battery_traps}")

        return 0 if passed and conserved is not None else 1

    except requests.exceptions.Timeout:
        print(
            f"ERROR: request timed out after {TIMEOUT} seconds.",
            file=sys.stderr,
        )
        return 2
    except requests.exceptions.HTTPError as exc:
        print(f"ERROR: HTTP request failed: {exc}", file=sys.stderr)
        print(response.text[:2000], file=sys.stderr)
        return 2
    except (requests.exceptions.RequestException, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
