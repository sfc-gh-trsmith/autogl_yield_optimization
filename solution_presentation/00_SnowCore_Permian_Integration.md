# Graph-Powered Post-Merger Integration for Energy: Achieve Unified Operations with Snowflake

**Midstream operators lose millions annually when acquired assets operate as blind spots.** Following a major acquisition, SnowCore Energy cannot predict how increased production from modern wells will impact legacy TeraField infrastructure—because critical data is trapped in incompatible SCADA systems and static PDF P&IDs.

---

## The Problem in Context

![The Integration Challenge](images/01_integration_challenge.svg)

- **Data fragmentation blocks synergy capture**: Two SCADA historians (OSIsoft PI vs. CygNet), two ERPs (SAP vs. Maximo), and two tagging conventions mean operators cannot query across the combined network.

- **Equipment mismatches create hidden risk**: SnowCore's modern separators operate at 1,000–1,500 PSI while acquired TeraField equipment is rated for only 500–800 PSI. Without visibility, pressure cascades trigger unplanned flaring.

- **Tribal knowledge is locked in documents**: Specifications for legacy TeraField valves exist only in PDF P&IDs and decade-old maintenance logs that engineers cannot search at decision time.

- **Reactive operations erode margins**: Controllers discover cross-network bottlenecks only after alarms sound, causing production deferment and SLA penalties.

---

## What We'll Achieve

![Business Outcomes](images/02_business_outcomes.svg)

| Outcome | KPI Target | Who Benefits |
|---------|------------|--------------|
| **Capture acquisition synergies** | $500M via optimized flow routing without new pipe | VP of Integration, Finance |
| **Reduce unplanned deferment** | 15% reduction by predicting cross-network pressure bottlenecks | ROC Controllers, Operations |
| **Accelerate decision-making** | Sub-second document retrieval for legacy equipment specs | Facilities Engineers |
| **Prevent equipment failures** | Zero pressure-mismatch incidents via proactive simulation | HSE, Maintenance |

---

## Why Snowflake

![Snowflake Architecture](images/03_snowflake_architecture.svg)

- **Unified data foundation**: A single governed platform unifies SnowCore and TeraField SCADA, ERP, and document data—so operators query the entire network with one SQL statement.

- **Performance that scales**: Elastic compute runs graph neural network inference and real-time simulations without capacity planning friction.

- **Collaboration without compromise**: Secure data sharing enables headquarters, field operations, and engineering contractors to work from the same trusted data.

- **Built-in AI/ML and app development**: Cortex AI services (Search, Analyst, Agent) and Snowpark ML enable graph learning and intelligent reasoning directly on data—no movement required.

---

## The Data (At a Glance)

![Data Flow](images/04_data_flow.svg)

**Domains**:
- **Assets & Topology**: Equipment master records from SAP and Maximo; GIS pipeline segments
- **Telemetry**: High-frequency sensor time-series from OSIsoft PI (SnowCore) and CygNet (TeraField)
- **Documents**: P&ID PDFs, maintenance logs, shift handover reports

**Freshness**:
- Telemetry ingested at 1-second (SnowCore) and 1-minute (TeraField) intervals
- Daily aggregates power dashboards; real-time feeds enable simulation

**Trust**:
- `SOURCE_SYSTEM` column preserves lineage across merged tables
- Row-level security ensures field operators see only their zone
- Full audit trail for regulatory compliance

---

## How It Comes Together

![Solution Architecture](images/05_solution_flow.svg)

| Step | What Happens | Snowflake Capability |
|------|--------------|----------------------|
| **1. Ingest & Unify** | Land SnowCore (PI) and TeraField (CygNet) telemetry into common schema with source lineage | Snowpipe, Dynamic Tables |
| **2. Enrich with Documents** | Parse P&ID PDFs and maintenance logs; extract equipment specs | Cortex Search, Document AI |
| **3. Build the Graph** | Construct network topology from asset master and GIS edge data | Snowpark DataFrames |
| **4. Predict Hidden Links** | Run AutoGL graph neural network to discover undocumented cross-network dependencies | Snowpark ML, External Access |
| **5. Score Risk** | Flag assets where predicted pressure exceeds documented ratings | Cortex Agent reasoning |
| **6. Simulate & Decide** | Let operators test routing scenarios before committing changes | Streamlit in Snowflake |
| **7. Monitor & Alert** | Continuous risk scoring with threshold-based notifications | Snowflake Alerts, Dashboards |

---

## The "Wow" Moment: Discovering TF-V-204

![Risk Discovery](images/06_risk_discovery.svg)

When an operator asks *"Can I route 5,000 extra barrels through Midland Hub?"*, the system:

1. **Runs AutoGL inference** → Draws a new edge connecting SnowCore PAD-42 to TeraField V-204
2. **Checks Cortex Search** → Extracts "MAWP: 600 PSIG" from the legacy P&ID PDF
3. **Projects pressure** → Calculates downstream impact of increased flow
4. **Returns a verdict** → "DENIED: Projected pressure (800 PSI) exceeds TF-V-204 limit (600 PSI)"

**Without this solution**, the risk was invisible because the cross-network connection wasn't documented in either system's asset registry.

---

## Demo Application: Permian Command Center

### Home Dashboard
Real-time KPIs, asset comparison, and data quality metrics across both networks.

![Dashboard Preview](images/07_dashboard_preview.svg)

### Network Discovery Map
Interactive geospatial visualization showing:
- SnowCore assets (blue)
- TeraField assets (red)
- Known pipelines (solid lines)
- AutoGL-predicted links (dashed purple)

### Simulation & Chat
- **Left panel**: Production increase sliders and routing controls
- **Right panel**: Cortex Agent chat for natural-language queries

---

## Call to Action

### Primary: Run the Demo in Your Account

1. Clone the repository and generate synthetic data:
   ```bash
   git clone https://github.com/snowflake-labs/autogl-yield-optimization
   cd autogl-yield-optimization
   python3 utils/generate_synthetic_data.py
   ```

2. Deploy to Snowflake:
   ```bash
   ./deploy.sh -c your_connection
   ```

3. Open Snowsight → Streamlit → Launch **AUTOGL_YIELD_OPTIMIZATION_APP**

4. Click "Run AutoGL Prediction" and watch the system discover hidden dependencies

---

### Secondary: Adapt for Your Network

- **Review the data model**: See how `ASSET_MASTER`, `NETWORK_EDGES`, and `SCADA_TELEMETRY` are structured
- **Customize the graph features**: Modify the AutoGL notebook to include your domain-specific node/edge attributes
- **Connect your documents**: Point Cortex Search at your P&ID repository
- **Book a working session**: Schedule time with the Snowflake team to map this pattern to your infrastructure

---

## Appendix: Technical Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `01_setup.sql` | Infrastructure (DB, WH, Network Rule) | `sql/` |
| `02_tables.sql` | DDL and data loading | `sql/` |
| `03_cortex_search.sql` | Document search service | `sql/` |
| `04_semantic_view.sql` | Cortex Analyst semantic model | `sql/` |
| `05_cortex_agent.sql` | AI agent deployment | `sql/` |
| `autogl_link_prediction.ipynb` | Graph neural network notebook | `notebooks/` |
| `streamlit_app.py` | Executive dashboard | `streamlit/` |
| `1_Network_Map.py` | Geospatial visualization | `streamlit/pages/` |
| `2_Simulation_Chat.py` | Simulation and AI chat | `streamlit/pages/` |

---

*SnowCore Permian Command Center — Powered by Snowflake Cortex AI + AutoGL Graph Neural Networks*

