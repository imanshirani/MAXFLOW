# MAXFLOW - Node-Based Workflow for 3ds Max

MAXFLOW is an experimental, live node-based environment for Autodesk 3ds Max, built entirely with Python, PySide6, and NodeGraphQt. It brings procedural, node-driven logic to 3ds Max scenes, allowing users to extract properties, manipulate math logic, and dynamically inject and control modifiers in real-time.

> **⚠️ IMPORTANT: HIGHLY EXPERIMENTAL BETA ⚠️**
> **This project is in its early BETA stage.** It is highly experimental, heavily under construction, and *will* contain bugs. It is not yet ready for production pipelines. Things might break, nodes might disconnect, and scenes might behave unexpectedly. 
> 
> **Why release it now?** Because this is too big to build alone! We are releasing MAXFLOW into the wild to gather brilliant minds. If you are a pipeline developer, technical artist, or Python enthusiast, **we need your help** to mature this architecture, squash bugs, and build the ultimate node-based toolset for 3ds Max. 

---

https://github.com/imanshirani/MAXFLOW/blob/main/SC/PR.jpg

---

## 🚀 Current Features

MAXFLOW already establishes a strong foundation with a functional live-evaluation engine:

* **Live Viewport Evaluation:** Uses `registerRedrawViewsCallback` to evaluate node graphs in real-time as the 3ds Max scene updates.
* **Scene Integration Nodes:**
  * **Universal Object Node:** Pick and link directly to 3ds Max objects to drive Transform parameters (Position, Rotation, Scale) and base object properties.
  * **Get Property (Extractor):** Dynamically extract any property from a scene object (e.g., `pos.x`) to use mathematically in the graph.
* **Dynamic Modifier Control:**
  * Read, assign, and manipulate 3ds Max modifiers dynamically.
  * Automatically handles custom tagging (`[MF-xxxx]`) to keep track of procedurally generated modifiers without destroying user data.
  * Custom UI to search standard and advanced modifier parameters and jump directly to the max modify panel.
* **Math & Logic System:**
  * A suite of math nodes including Add, Subtract, Multiply, Divide, Power, Modulo, Min, Max, Sine, and Cosine.
* **Input Parameters:**
  * Custom Sliders for Floats and Integers, Booleans, Strings, and Axis pickers.
* **Workflow & UI Tools:**
  * Built on `NodeGraphQt` with a customized dark theme.
  * Extractor/Bypass node tools, Backdrop frames for organization, and an auto-cleaning memory module for rapid development and testing.

---

## 🛠️ Installation & Usage

1. Clone or download this repository.
2. Ensure you have PySide6 installed for your 3ds Max Python environment.
3. Run `main.py` directly from 3ds Max using the Scripting menu, or execute it via `pymxs`.
   
---
## 🤝 Call for Contributors!
We are actively looking for contributors to help shape the future of MAXFLOW! Whether you want to add new node types, optimize the GraphEvaluator, improve the UI, or fix memory leaks, your PRs are highly welcome.

How to get involved:

Fork the repository.

Explore the Code: Check out nodes/base_node.py and see how easy it is to register a new node.

Check the Issues: Look for tags like good first issue or help wanted.

Submit a Pull Request: We review all PRs! Don't worry if your code isn't perfect; we will figure it out together.

Let's bring a proper procedural node workflow to 3ds Max!
