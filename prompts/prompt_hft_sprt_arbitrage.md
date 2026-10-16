# Prompt: High-Frequency Trading & SPRT Pruning with Aelfstone

## System Prompt for LLMs
Copy and paste this prompt into Claude, ChatGPT, or Cursor:

> "Write a Python verification script that benchmarks Aelfstone's Quantitative Finance engine at `https://civictechai.com/evaluate`.
> The endpoint accepts a GraphPayload with `source_node`, `target_node`, `nodes`, and `edges`.
> Each edge metadata requires `pricing_volatility` (float), `mean_delta` (float), and `liquidity_depth` (float).
> The engine uses Sequential Probability Ratio Testing (SPRT) to prune anomalous, low-variance vectors where `pricing_volatility < 0.0005` and `mean_delta > 0.001` (LLR score > 5.2).
> Build a synthetic order book arbitrage graph, POST it with Bearer token authentication, and display `vcompute_conserved_pct`, execution latency in milliseconds, and the pruned arbitrage hops."
