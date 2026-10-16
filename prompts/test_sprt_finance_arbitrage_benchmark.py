#!/usr/bin/env python3
"""
Aelfstone Finance Engine Benchmark: SPRT Log-Likelihood Ratio Pruning
Validates arbitrage pathing against /evaluate under high-frequency market shifts.
"""

import json
import time
import requests

API_URL = "https://civictechai.com/evaluate"
API_KEY = "aelf_test__584t94dWLgRhJesrgv9Nwg"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "source_node": "USD",
    "target_node": "EUR",
    "nodes": [{"id": curr, "metadata": {}} for curr in ["USD", "BTC", "ETH", "SOL", "EUR"]],
    "edges": [
        # Viable high-liquidity arbitrage corridor
        {"source": "USD", "target": "BTC", "metadata": {"pricing_volatility": 0.02, "mean_delta": 0.0005, "liquidity_depth": 500.0}},
        {"source": "BTC", "target": "ETH", "metadata": {"pricing_volatility": 0.015, "mean_delta": 0.0002, "liquidity_depth": 350.0}},
        {"source": "ETH", "target": "EUR", "metadata": {"pricing_volatility": 0.01, "mean_delta": 0.0001, "liquidity_depth": 800.0}},
        
        # Poisoned / Anomalous corridor (triggers SPRT pruning threshold: LLR > 5.2)
        {"source": "USD", "target": "SOL", "metadata": {"pricing_volatility": 0.0002, "mean_delta": 0.0025, "liquidity_depth": 1200.0}},
        {"source": "SOL", "target": "EUR", "metadata": {"pricing_volatility": 0.0001, "mean_delta": 0.0030, "liquidity_depth": 900.0}}
    ]
}

start = time.perf_counter()
resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
elapsed_ms = (time.perf_counter() - start) * 1000.0

if resp.status_code == 200:
    data = resp.json()
    print("=== AELFSTONE QUANTITATIVE FINANCE BENCHMARK ===")
    print(f"Network RTT:            {elapsed_ms:.2f} ms")
    print(f"Hops Cleared:           {data.get('execution_hops')}")
    print(f"Tokens Charged:         {data.get('tokens_charged')}")
    print(f"Optimal Path:           {' -> '.join(data.get('optimized_execution_path', []))}")
    print("Engine Telemetry:", json.dumps(data.get("engine_telemetry"), indent=2))
else:
    print(f"Error {resp.status_code}: {resp.text}")
