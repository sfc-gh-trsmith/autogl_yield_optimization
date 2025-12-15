# SnowCore Permian Command Center

**Intelligent Yield & Graph-Based RCA Command Center** for the merged SnowCore/TeraField Permian Basin gathering network.

## Overview

Following the acquisition of TeraField Resources, this demo showcases how Snowflake's AI capabilities can unify disconnected gathering networks and predict systemic risks across the combined infrastructure.

### Key Features

- **🗺️ Unified Network Visualization**: Interactive geospatial map showing SnowCore (Blue) and TeraField (Red) assets with pipeline connections
- **🤖 AutoGL Link Prediction**: Graph neural network that discovers hidden dependencies between the two networks
- **💬 AI Integration Assistant**: Cortex Agent that bridges live SCADA data with legacy engineering specs
- **⚠️ Pressure Risk Detection**: Real-time alerts when routing decisions would exceed equipment limits

### The "Wow" Moment

Click "Run AutoGL Prediction" and watch the system:
1. Draw new edges connecting previously disconnected clusters
2. Flag **TF-V-204** as high risk
3. Explain: *"Increased flow from SnowCore Pad 42 will exceed the 600 PSI pressure rating of this legacy TeraField valve (detected via PDF extraction)"*

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTOGL_YIELD_OPTIMIZATION                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ASSET_MASTER │  │SCADA_       │  │NETWORK_     │  │GRAPH_      │ │
│  │             │  │TELEMETRY    │  │EDGES        │  │PREDICTIONS │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
│         │                │                │                │        │
│         └────────────────┴────────────────┴────────────────┘        │
│                                 │                                    │
│  ┌──────────────────────────────┼──────────────────────────────────┐│
│  │                     Snowflake Notebook                          ││
│  │   • PyTorch Geometric (via Network Rule)                        ││
│  │   • GraphSAGE for link prediction                               ││
│  │   • Anomaly scoring                                             ││
│  └──────────────────────────────┬──────────────────────────────────┘│
│                                 │                                    │
│  ┌──────────────────────────────┼──────────────────────────────────┐│
│  │                     Cortex AI Services                          ││
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            ││
│  │   │Cortex       │  │Cortex       │  │Cortex       │            ││
│  │   │Analyst      │  │Search       │  │Agent        │            ││
│  │   │(SQL/NL)     │  │(RAG/Docs)   │  │(Reasoning)  │            ││
│  │   └─────────────┘  └─────────────┘  └─────────────┘            ││
│  └──────────────────────────────┬──────────────────────────────────┘│
│                                 │                                    │
│  ┌──────────────────────────────┴──────────────────────────────────┐│
│  │                    Streamlit App                                 ││
│  │   • Network Map (Plotly Scattergeo)                             ││
│  │   • Simulation Controls                                          ││
│  │   • AI Chat Interface                                            ││
│  └──────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Snowflake account with ACCOUNTADMIN access
- Snowflake CLI (`snow`) installed and configured
- Python 3.11+ (for data generation only)

## Quick Start

### 1. Clone and Generate Data

```bash
cd autogl_yield_optimization

# Generate synthetic demo data (deterministic, seed=42)
python3 utils/generate_synthetic_data.py
```

### 2. Deploy to Snowflake

```bash
# Deploy all resources (uses default "demo" connection)
./deploy.sh

# Or specify a different Snowflake CLI connection
./deploy.sh -c myconnection

# Deploy to a specific environment (DEV, PROD)
./deploy.sh --prefix DEV
./deploy.sh --prefix PROD -c prod_connection

# Redeploy individual components (faster iteration)
./deploy.sh --only-streamlit      # Redeploy Streamlit app only
./deploy.sh --only-notebook       # Redeploy notebook only
./deploy.sh --only-data           # Reload data only
./deploy.sh --only-sql            # Run SQL setup only
```

This creates:
- Database: `AUTOGL_YIELD_OPTIMIZATION`
- Schema: `AUTOGL_YIELD_OPTIMIZATION`
- Role: `AUTOGL_YIELD_OPTIMIZATION_ROLE`
- Warehouse: `AUTOGL_YIELD_OPTIMIZATION_WH`
- Compute Pool: `AUTOGL_YIELD_OPTIMIZATION_COMPUTE_POOL`
- Tables: `ASSET_MASTER`, `NETWORK_EDGES`, `SCADA_TELEMETRY`, `GRAPH_PREDICTIONS`, `SCADA_AGGREGATES`
- Cortex Search: `AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH`
- Semantic View: `AUTOGL_YIELD_OPTIMIZATION_ANALYTICS_VIEW`
- Streamlit App: `AUTOGL_YIELD_OPTIMIZATION_APP`
- Notebook: `AUTOGL_YIELD_OPTIMIZATION_NOTEBOOK`

### 3. Run the AutoGL Notebook

**Option A: Command Line (Headless)**
```bash
./run.sh main                    # Execute notebook
./run.sh status                  # Check resource status
./run.sh streamlit               # Get Streamlit app URL
./run.sh --prefix DEV status     # Check DEV environment
```

**Option B: Interactive (Snowsight)**
1. Open Snowsight → Notebooks
2. Open `AUTOGL_YIELD_OPTIMIZATION_NOTEBOOK`
3. The `AUTOGL_YIELD_OPTIMIZATION_EXTERNAL_ACCESS` integration is already attached
4. Run all cells to generate predictions

### 4. Launch the Dashboard

1. Open Snowsight → Streamlit
2. Launch `AUTOGL_YIELD_OPTIMIZATION_APP`
3. Explore the Network Map and Simulation Chat

## Directory Structure

```
autogl_yield_optimization/
├── data/
│   ├── synthetic/           # Pre-generated CSVs (version controlled)
│   │   ├── asset_master.csv
│   │   ├── network_edges.csv
│   │   ├── scada_telemetry.csv
│   │   └── graph_predictions.csv
│   └── documents/           # Mock P&ID text files
│       ├── TeraField_Midland_Hub_Process_Flow.txt
│       ├── Shift_Report_2023_10_12.txt
│       └── Maintenance_Log_V204.txt
├── sql/
│   ├── 01_setup.sql         # Infrastructure (DB, WH, Network Rule)
│   ├── 02_tables.sql        # DDL + data loading
│   ├── 03_cortex_search.sql # Search service
│   ├── 04_semantic_view.sql # Semantic view
│   └── 05_cortex_agent.sql  # Agent deployment
├── notebooks/
│   └── autogl_link_prediction.ipynb
├── semantic_views/
│   └── permian_analytics.yaml
├── agents/
│   └── integration_assistant.json
├── streamlit/
│   ├── snowflake.yml
│   ├── environment.yml
│   ├── streamlit_app.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_loader.py    # Parallel query utility
│   └── pages/
│       ├── 1_Network_Map.py
│       └── 2_Simulation_Chat.py
├── utils/
│   └── generate_synthetic_data.py
├── deploy.sh
├── clean.sh
└── README.md
```

## Demo Script

### Scenario: "Can we route 5,000 extra barrels through Midland Hub?"

1. **Open Simulation & Chat page**

2. **Ask the AI Assistant:**
   > "What is the pressure rating for separator V-204?"
   
   Response: *"Based on the P&ID, TF-V-204 has a MAWP of 600 PSIG..."*

3. **Check Risk Scores:**
   > "Which assets are flagged as high risk?"
   
   Response: *"TF-V-204 has risk score 0.92..."*

4. **Run Simulation:**
   - Select `SC-PAD-42` as source
   - Set production increase to 5,000 BOPD
   - Click "Run Simulation"
   
   Result: **DENIED** - Projected pressure (800 PSI) exceeds TF-V-204 limit (600 PSI)

5. **Show the Hidden Dependency:**
   - View Network Map
   - Enable "Show Predicted Links"
   - See the dashed purple line connecting SC-SEP-101 to TF-V-204

## Cleanup

```bash
# Remove all Snowflake resources (uses default "demo" connection)
./clean.sh

# Or specify a different connection
./clean.sh -c myconnection

# Clean a specific environment
./clean.sh --prefix DEV
./clean.sh --prefix DEV --yes    # Skip confirmation
```

This removes all Snowflake resources. Local files are preserved.

## Author

Tripp Smith - [linkedin.com/in/smithtripp/](https://linkedin.com/in/smithtripp/)

## License

MIT License - See [LICENSE](LICENSE) for details.
