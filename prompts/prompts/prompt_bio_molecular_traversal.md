# Prompt: Molecular Pathway Traversal & Bio-Heuristic Pruning with Aelfstone

## System Prompt for LLMs
Copy and paste this prompt into Claude, ChatGPT, or Cursor:

> "Write a Python verification script that benchmarks Aelfstone's Bio-Informatics engine at `https://civictechai.com/traverse`.
> The endpoint accepts a GraphPayload with `source_node`, `target_node`, `enable_pruning=True`, `pruning_threshold=100.0`, `nodes`, and `edges`.
> Edge metadata accepts dynamic chemical/genomic properties such as `base_cost`, `affinity`, and `decay`.
> The engine inverts affinity so high-binding pathways have minimal traversal costs and discards sub-threshold paths before RAM saturation.
> Generate a multi-protein interaction network, submit it via requests with Bearer auth, and output `edges_pruned_from_ram` along with `ram_conserved_mb`."
