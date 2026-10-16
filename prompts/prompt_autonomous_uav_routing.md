# Prompt: Autonomous UAV Routing & Telemetry Pruning with Aelfstone

## System Prompt for LLMs
Copy and paste this prompt into Claude, ChatGPT, or Cursor:

> "Write a Python verification script that benchmarks Aelfstone's Spatial Telemetry engine at `https://civictechai.com/route`. 
> The endpoint accepts a GraphPayload with `source_node`, `target_node`, `nodes`, and `edges`. 
> Each edge metadata requires `spatial_distance` (float), `signal_entropy` (0.0 to 1.0), and `battery_cost` (float). 
> The engine automatically prunes any hazardous edges where `signal_entropy >= 0.95` or `battery_cost > 85.0` prior to RAM allocation. 
> Build a synthetic 50-node obstacle graph featuring both 'trap' corridors (short distance but fatal entropy) and 'safe' corridors. POST the payload with Bearer token authentication, and display `vcompute_conserved_pct`, engine execution latency in milliseconds, and verify the routing path successfully avoided the pruned traps."
