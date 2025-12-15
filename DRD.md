Demo Requirements Document (DRD): SnowCore Permian "One Field" Command Center

### 1. Strategic Overview

**Problem Statement:** Following the massive acquisition of "TeraField Resources" (proxy for Pioneer), SnowCore Energy now operates two distinct, disconnected gathering networks in the Permian Basin. Critical data regarding pipeline connectivity, pressure ratings, and maintenance history is trapped in incompatible legacy SCADA systems and static PDF P&IDs. This data fragmentation creates "blind spots," making it impossible to optimize flow across the combined network or predict how new drilling in SnowCore zones will impact downstream TeraField facilities.

**Target Business Goals (KPIs):**
* **Achieve $500M in Synergies:** By optimizing flow routing across the combined network without laying new pipe.
* **Reduce Unplanned Deferment by 15%:** By predicting "systemic" pressure bottlenecks that occur at the interface of SnowCore and TeraField assets.

**The "Wow" Moment:** The user views a geospatial map showing two disconnected clusters of assets (SnowCore in Blue, TeraField in Red). With one click, they execute the "AutoGL Link Prediction" job. The map dynamically draws new edges connecting the clusters, revealing hidden pipeline dependencies. A "High Risk" alert immediately pulses on a legacy TeraField valve. The user asks, "Why is this valve at risk?" and the system explains: *"Increased flow from SnowCore Pad A will exceed the pressure rating of this TeraField valve (detected via PDF extraction)."*

### 2. User Personas & Stories

| Persona Level | Role Title | Key User Story (Demo Flow) |
| :--- | :--- | :--- |
| **Strategic** | **VP of Permian Integration** | "As a VP, I want to see a unified 'Total Production' dashboard that merges SnowCore and TeraField volumes in real-time to track our post-merger synergy targets." |
| **Operational** | **ROC Controller** (Remote Ops) | "As a Controller, I want to simulate how opening a choke on a new SnowCore well will propagate pressure changes to downstream legacy facilities so I can prevent flaring." |
| **Technical** | **Facilities Engineer** | "As an Engineer, I want to find the original P&ID specification for a legacy TeraField compressor immediately when an alarm sounds, without searching through shared drives." |

### 3. Data Architecture & Snowpark ML (Backend)

**Structured Data (Inferred Schema):**
* **[ASSET_MASTER]:** `(ASSET_ID, SOURCE_SYSTEM_FLAG, ASSET_TYPE, LAT, LON)`
    * *Grain:* One row per physical equipment. `SOURCE_SYSTEM_FLAG` distinguishes 'SNOWCORE' vs 'TERAFIELD'.
* **[SCADA_TELEMETRY]:** `(ASSET_ID, TIMESTAMP, FLOW_RATE, SUCTION_PRESSURE, DISCHARGE_PRESSURE)`
    * *Grain:* High-frequency time-series (1-minute intervals) from distinct Historians (e.g., PI vs. CygNet).
* **[NETWORK_EDGES]:** `(SOURCE_ID, TARGET_ID, LINE_DIAMETER, MAX_PRESSURE_RATING)`
    * *Grain:* Physical pipeline segments connecting the assets.

**Unstructured Data (Tribal Knowledge):**
* **Source Material:** "Legacy TeraField" P&IDs (PDF Diagrams), Maintenance logs from the last 10 years, Vendor Manuals.
* **Purpose:** To bridge the "Knowledge Gap" where SnowCore engineers do not know the specs of the acquired equipment.

**ML Notebook Specification:**
* **Objective:** **Network State Prediction (Graph Regression)** & **Topology Reconstruction (Link Prediction)**.
* **Target Variable:** `pressure_anomaly_score` (Float) and `link_probability` (Float).
* **Algorithm Choice:** **AutoGL (Auto Graph Learning)** using a Spatial-Temporal Graph Neural Network (ST-GNN).
* **Inference Output:** A "Digital Twin" graph object stored in `[PERMIAN_GRAPH_PREDICTIONS]` table, utilized by the Streamlit app for visualization.

### 4. Cortex Intelligence Specifications

**Cortex Analyst (Structured Data / SQL)**
* **Semantic Model Scope:**
    * **Measures:** `Total_Barrels_Oil_Day (BOED)`, `Gas_Oil_Ratio (GOR)`, `Downtime_Hours`.
    * **Dimensions:** `Asset_Zone` (Delaware/Midland), `Acquisition_Cohort` (Legacy/New), `Facility_Type`.
* **Golden Query (Verification):**
    * **User Prompt:** "Compare the downtime frequency of Legacy assets vs. Acquired assets over the last 30 days."
    * **Expected SQL:** `SELECT SOURCE_SYSTEM_FLAG, AVG(DOWNTIME_HOURS) FROM SCADA_AGGREGATES ... GROUP BY 1`

**Cortex Search (Unstructured Data / RAG)**
* **Service Name:** `AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH`
* **Indexing Strategy:**
    * **Document Attribute:** Indexing by `Tag_ID` (e.g., 'V-101') and `Document_Type` (e.g., 'P&ID', 'Datasheet').
* **Sample RAG Prompt:** "What is the maximum pressure rating for Separator V-204 at the Midland Battery? Extract this from the P&ID."

**Cortex Agents (Reasoning)**
* **Role:** The "Integration Assistant." It bridges the gap between the live sensor data (Analyst) and the static engineering specs (Search).
* **Workflow:**
    1.  User asks: "Can I route 5k extra barrels through the Midland Hub?"
    2.  Agent checks **AutoGL Model**: "Model predicts pressure will rise to 600psi."
    3.  Agent checks **Cortex Search**: "Specs show Midland Hub piping is rated for only 500psi."
    4.  Agent Conclusion: "No. Routing denied. Pressure (600psi) exceeds safety rating (500psi)."

### 5. Streamlit Application UX/UI

**Layout Strategy:**
* **Page 1 (The "One Permian" Map):** A full-screen `pydeck` or `Kepler.gl` geospatial visualization.
    * *Layer 1:* SnowCore Assets (Blue dots).
    * *Layer 2:* Acquired TeraField Assets (Red dots).
    * *Layer 3 (The Graph):* Glowing lines representing the pipeline network inferred by AutoGL.
* **Page 2 (Simulation & Chat):** Split screen. Left side is a slider to "Increase Production." Right side is the Cortex Agent chat window.

**Component Logic:**
* **Visualizations:** A directed graph where edge thickness represents current `Flow_Rate` and color represents `Pressure_Risk`.
* **Chat Integration:** The user can click any Red node (Acquired Asset) and ask questions. The history is context-aware (e.g., the Agent knows which specific pump was clicked).

### 6. Success Criteria

* **Technical Validator:** The system successfully joins `SnowCore` and `TeraField` data schemas into a single graph representation and runs an AutoGL inference pass in < 5 minutes.
* **Business Validator:** The solution demonstrates a preventative catch: identifying an incompatible pressure rating between a new well and an old facility *before* a simulated workflow is approved.

### Demo Data Specification: SnowCore Permian Integration
**Target Scenario:** Merging "TeraField" (Legacy Pioneer) assets into the "SnowCore" (ExxonMobil) High-Performance Computing environment.

---

#### 1. OT / Time-Series Data (The "Pulse")
**Objective:** Simulate high-frequency sensor telemetry from two incompatible SCADA historians.
**Generation Method:** Python Script (Deterministic functions with noise injection).

**A. SnowCore Historian (Modern Standard)**
* **System Proxy:** OSIsoft PI (AVEVA) / Azure Data Explorer
* **Schema:** `SCADA_SNOWCORE_TAGS`
* **Naming Convention:** Hierarchical (ISA-95) -> `Site/Area/Unit/Device/Attribute`
* **Data Pattern:** High sampling rate (1 sec), clean signal, low noise.
* **Synthetic Logic:**
    * `tags`: ["DELAWARE/PAD_42/SEP_V101/PRESS_PV", "DELAWARE/PAD_42/SEP_V101/TEMP_PV"]
    * `values`: Sine wave centered on operating point (e.g., 500 psi) + Gaussian noise (sigma=2).

**B. TeraField Historian (Legacy Brownfield)**
* **System Proxy:** CygNet / Rockwell
* **Schema:** `SCADA_TERAFIELD_FLAT`
* **Naming Convention:** Flat / Cryptic -> `FACILITY_DEVICE_ATTRIBUTE`
* **Data Pattern:** Lower sampling rate (1 min), "deadband" artifacts, stuck values (nulls).
* **Synthetic Logic:**
    * `tags`: ["TF_MID_HUB_V204_P", "TF_MID_HUB_V204_T", "TF_MID_LP_COMP_A_VIBE"]
    * `values`: Step functions (simulating discrete polls) + random "communication failure" gaps (NULLs).

**C. The "Anomaly" Injection (The Plot Twist)**
* **Trigger:** At `T_event`, SnowCore `PAD_42` ramps up flow (Flow = Flow * 1.5).
* **Response:** 5 minutes later, TeraField `TF_MID_HUB_V204_P` spikes (Pressure = Pressure + 50psi).
* **Goal:** AutoGL must learn this time-lagged correlation despite the different tag names.

---

#### 2. IT / Transactional Data (The "Nodes")
**Objective:** Master Data defining *what* the equipment is.

**A. SnowCore Asset Registry (SAP ERP)**
* **Table:** `SAP_EQUI_MASTER`
* **Columns:**
    * `EQUI_ID` (PK): `SC-10042`
    * `OBJECT_TYPE`: `SEPARATOR_3PHASE`
    * `MANUFACTURER`: `Schlumberger`
    * `MAX_RATING_PSI`: `1440` (High Pressure Standard)
    * `INSTALL_DATE`: `2022-01-15`

**B. TeraField Asset List (Legacy Maximo)**
* **Table:** `MAXIMO_ASSET_DUMP`
* **Columns:**
    * `ASSETNUM` (PK): `TF-V-204`
    * `DESCRIPTION`: `Legacy 2-Phase Vert Sep`
    * `VENDOR`: `Natco`
    * `SPEC_RATING`: `NULL` (Crucial missing data!)
    * `INSTALL_DATE`: `2014-06-10`

---

#### 3. Unstructured / "Dark" Data (The "Context")
**Objective:** Source documents for Cortex Search to fill the gaps in the structured data.

**A. P&ID PDFs (The "Map")**
* **File:** `TeraField_Midland_Hub_Process_Flow.pdf`
* **Content:** A CAD drawing showing `TF-V-204` connected to `Pipeline-Seg-88`.
* **Visual Text:** Includes a text annotation box: *"V-204 MAWP: 600 PSIG"*.
* **Role:** Cortex AI Extract must read "600 PSIG" from this PDF to flag the risk when SnowCore pushes 800 PSI.

**B. Shift Handover Logs (The "Human Element")**
* **File:** `Shift_Report_2023_10_12.txt`
* **Content:** *"Operator Note: Bypass valve on V-204 sticks when pressure exceeds 550. Recommend replacement."*
* **Role:** Cortex Analyst queries this to explain *why* the node is flagged Red.

---

#### 4. Graph Topology Data (The "Edges")
**Objective:** The physical connections.

**A. GIS Edge List (Geo-Spatial)**
* **Table:** `PIPELINE_NETWORK_GIS`
* **Columns:**
    * `SEGMENT_ID`: `PIPE-88`
    * `START_NODE_GEO`: `(31.9, -102.1)` (SnowCore Pad)
    * `END_NODE_GEO`: `(31.8, -101.9)` (TeraField Hub)
    * `STATUS`: `ACTIVE`
* **Note:** This table exists but is *disconnected* from the Asset Registries until the Graph model runs.

---

#### 5. Summary of the "Golden Record" Join
For the demo to work, the Python Data Generator must enforce this hidden truth:

1.  **SnowCore Pad 42** feeds **Pipeline 88**.
2.  **Pipeline 88** feeds **TeraField V-204**.
3.  **V-204** has a hidden limit of **600 PSI** (found in PDF).
4.  **Pad 42** ramps to **800 PSI** (found in Sensor Data).

**Outcome:** The system flags a "Design Mismatch" alert.

**Would you like me to generate the Python script that creates these CSVs and the dummy PDF text content?**


