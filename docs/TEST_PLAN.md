# Test Plan: SnowCore Permian Command Center

This document outlines the standard procedure for running a full test cycle of the project. It covers prerequisites, cleanup, deployment, execution, and verification steps.

## 1. Prerequisites

Before starting a test cycle, ensure the following are installed and configured:

- **Snowflake CLI (`snow`)**: Installed and authenticated with an account having `ACCOUNTADMIN` privileges.
- **Python 3.11+**: For generating synthetic data (if needed).
- **Git**: To clone the repository.
- **Connection**: A configured Snowflake connection (default: `demo`).

## 2. Test Scenarios

We support testing in different environments using prefixes.

| Scenario | Prefix | Command Flag | Description |
|----------|--------|--------------|-------------|
| Default | None | (none) | Deploys to `AUTOGL_YIELD_OPTIMIZATION` |
| Development | `DEV` | `--prefix DEV` | Deploys to `DEV_AUTOGL_YIELD_OPTIMIZATION` |
| Testing | `TEST` | `--prefix TEST` | Deploys to `TEST_AUTOGL_YIELD_OPTIMIZATION` |

## 3. Full Test Cycle Steps

### Step 1: Clean Up Previous Resources

Ensure a clean state by removing any existing resources.

```bash
# For default environment
./clean.sh

# For DEV environment
./clean.sh --prefix DEV
```

**Verification:**

- Script should report successful drop of Compute Pool, Warehouse, Database, Role, etc.
- If resources didn't exist, it should report them as "not found or already dropped" (which is acceptable).

### Step 2: Generate/Verify Data

Ensure local data files are present.

```bash
# Check if data exists
ls -l data/synthetic/

# If missing, generate it
python3 utils/generate_synthetic_data.py
```

**Verification:**

- `data/synthetic/` should contain `asset_master.csv`, `network_edges.csv`, `scada_telemetry.csv`, etc.

### Step 3: Deploy Application

Deploy the full stack to Snowflake.

```bash
# Default deployment
./deploy.sh

# DEV deployment
./deploy.sh --prefix DEV
```

**Verification:**

- Script should complete without errors.
- Output should list created resources (Database, Schema, Role, Warehouse, Streamlit, Notebook).
- **Critical Check:** Ensure `AUTOGL_YIELD_OPTIMIZATION_APP` and `AUTOGL_YIELD_OPTIMIZATION_NOTEBOOK` are listed.

### Step 4: Run Machine Learning Workflows

Execute the Snowflake Notebook to generate predictions.

```bash
# Run notebook for default env
./run.sh main

# Run notebook for DEV env
./run.sh --prefix DEV main
```

**Verification:**

- Script should indicate "Notebook execution complete".
- Prediction summary should show counts for `NODE_ANOMALY` or other prediction types.

### Step 5: Verify Deployment Status

Check the health of the deployed resources.

```bash
# Check status for default env
./run.sh status

# Check status for DEV env
./run.sh --prefix DEV status
```

**Verification:**

- Compute Pool and Warehouse should be active/visible.
- Table row counts should be non-zero for all tables.
- High-risk assets should be listed (if any exist).

### Step 6: User Interface Testing (Manual)

1. Get the Streamlit URL:
   ```bash
   ./run.sh streamlit
   # or
   ./run.sh --prefix DEV streamlit
   ```
2. Open the URL in a browser.
3. **Smoke Tests:**

   **Home Page:**
   - [ ] Page loads with problem statement and KPI cards.
   - [ ] Asset registry comparison displays SnowCore vs TeraField stats.
   - [ ] Network connectivity map renders with two clusters.

   **Network Discovery Map:**
   - [ ] Map loads successfully with asset markers.
   - [ ] "Before AutoGL" / "After AutoGL" toggle works.
   - [ ] "Show Predicted Links" displays ML-discovered edges.
   - [ ] Asset selector shows details when asset is selected.

   **Simulation & Chat:**
   - [ ] Asset selector filters to well pads.
   - [ ] Production slider adjusts simulation input.
   - [ ] "Run Simulation" returns APPROVED/DENIED result.
   - [ ] Chat interface accepts input (e.g., "What is the pressure rating for V-204?").

   **Telemetry Explorer:**
   - [ ] Time-series correlation chart loads (SC-PAD-42 flow vs TF-V-204 pressure).
   - [ ] Data quality comparison cards display SnowCore vs TeraField metrics.
   - [ ] Pressure profile chart shows critical flow path.
   - [ ] Asset selector deep dive shows multi-metric visualization.

   **Production Analytics:**
   - [ ] Synergy KPI scorecard displays $500M target and progress.
   - [ ] Daily production by system chart renders (stacked area).
   - [ ] Zone production donut chart and trend line display.
   - [ ] Gas-Oil Ratio trend chart loads.
   - [ ] Downtime analysis and asset ranking charts render.

   **Document Intelligence:**
   - [ ] AI-extracted cards show MAWP, operating limit, and work order.
   - [ ] P&ID document viewer displays with highlighted text.
   - [ ] Maintenance timeline shows TF-V-204 history.
   - [ ] Shift report viewer displays operator notes.
   - [ ] Document search returns results for sample queries.

   **About:**
   - [ ] Page loads with header, version badges, and overview section.
   - [ ] Business Impact section displays KPI cards ($500M, 15%, <5 min, N-Tier).
   - [ ] Data Architecture section shows 3-column layout (Internal/External/Model).
   - [ ] "How It Works" tabs switch between Executive, Technical, and Cortex views.
   - [ ] Technical Deep-Dive shows model architecture diagram and LaTeX formulas.
   - [ ] Cortex AI Integration tab displays agent workflow steps.
   - [ ] Application Pages section lists all 6 pages with descriptions.
   - [ ] Technology Stack displays visual badge pills.
   - [ ] Known Limitations section shows 6 caveats with warning styling.
   - [ ] Getting Started section displays workflow and reference tables.

### Step 7: Final Cleanup (Optional)

If the test is complete and the environment is no longer needed:

```bash
./clean.sh
# or
./clean.sh --prefix DEV
```

## 4. Component-Specific Testing

For rapid iteration, verify individual components using the `--only-` flags in `deploy.sh`.

- **Streamlit Only:** `deploy.sh --only-streamlit` -> Verify app changes.
- **Notebook Only:** `deploy.sh --only-notebook` -> Verify notebook logic.
- **SQL Only:** `deploy.sh --only-sql` -> Verify schema changes.
- **Data Only:** `deploy.sh --only-data` -> Verify data reloading.

## 5. Troubleshooting Common Issues

- **Connection Errors:** Verify `~/.snowflake/config.toml` has the correct connection defined. Use `snow connection test -c <connection_name>`.
- **Permission Errors:** Ensure the user running the scripts has `ACCOUNTADMIN` role (required for initial setup of Compute Pools and Roles).

