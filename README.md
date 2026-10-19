1. The RustGIS Prompt (For your immediate lead)
This is tailored for high-performance engineers building in Rust or WebAssembly, directly targeting the ecosystem Nick is playing in.

"I am building a high-performance spatial pipeline in RustGIS and need to fix my canvas rendering latency. Standard wavefront routing is choking on vector clutter. Write a Rust script that extracts my current vector layer's nodes and edge telemetry. Package this into a JSON POST request for the Aelfstone API ([https://api.civictechai.com/v1/prune](https://api.civictechai.com/v1/prune)) to execute dynamic pre-queue memory pruning. Finally, write the function to ingest the optimized edge array returned by Aelfstone and render it as a clean layer in RustGIS, ensuring the unpruned noise never hits the active memory buffer."

2. The Google Maps API Prompt (The Mass Web Market)
This targets standard web developers building fleet dispatch dashboards who are constantly dealing with browser crashes when loading too many markers and routes.

"You are an expert JavaScript/TypeScript developer. I am building a fleet dispatch UI using the Google Maps JS API, but the browser freezes when rendering thousands of delivery paths. I need to bypass standard routing and use the Aelfstone API for pre-queue pruning. Write a function that takes my array of GPS coordinates and vehicle telemetry (speed limits, battery drain), packages it into an Aelfstone JSON payload, and makes the API call. Then, write the code to draw the returned optimized route array using a Google Maps Polyline. Do not load the raw, unpruned dataset onto the map canvas."

3. The ArcGIS / ArcPy Prompt (The Enterprise Standard)
This targets mid-market and enterprise GIS analysts who use Esri/ArcGIS and regularly run out of CPU/RAM during heavy geoprocessing tasks.

"Act as a Senior GIS Developer. I am processing a massive commercial vehicle network in ArcGIS Pro using Python (ArcPy), and my standard geoprocessing routing tools are running out of memory. Write an ArcPy script that extracts the geometry and spatial impedance metrics from my active Network Dataset. Send this data to the Aelfstone Python SDK (aelfstone.solve()) to execute deterministic variance thresholding. Finally, take the pruned, optimized route output and write it back to a new ArcGIS Feature Class, dropping all non-viable edges."
