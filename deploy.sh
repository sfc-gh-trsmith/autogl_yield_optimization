#!/bin/bash
# ============================================================================
# deploy.sh - Deploy SnowCore Permian Command Center to Snowflake
# ============================================================================
# Prerequisites:
#   - Snowflake CLI (snow) installed and configured
#   - ACCOUNTADMIN role access (for initial infrastructure setup)
#   - Pre-generated data in data/synthetic/ directory
#
# Role Usage:
#   - ACCOUNTADMIN: Infrastructure setup (01_setup.sql) - roles, compute pools, etc.
#   - ${PROJECT_PREFIX}_ROLE: Schema-level operations (02-05 SQL files)
#
# Naming Convention (per SNOWFLAKE_DEPLOYMENT_SCRIPT_GUIDELINES.md):
#   DATABASE: ${ENV_PREFIX}_AUTOGL_YIELD_OPTIMIZATION (or AUTOGL_YIELD_OPTIMIZATION without prefix)
#   SCHEMA: AUTOGL_YIELD_OPTIMIZATION
#   ROLE: ${ENV_PREFIX}_AUTOGL_YIELD_OPTIMIZATION_ROLE
#   WAREHOUSE: ${ENV_PREFIX}_AUTOGL_YIELD_OPTIMIZATION_WH
#   COMPUTE_POOL: ${ENV_PREFIX}_AUTOGL_YIELD_OPTIMIZATION_COMPUTE_POOL
#
# Usage:
#   ./deploy.sh                        # Full deployment with default connection
#   ./deploy.sh -c myconnection        # Full deployment with specified connection
#   ./deploy.sh --prefix DEV           # Deploy with DEV_ prefix for dev environment
#   ./deploy.sh --only-streamlit       # Only redeploy the Streamlit app
#   ./deploy.sh --only-notebook        # Only redeploy the notebook
#   ./deploy.sh --only-data            # Only upload and load data
#   ./deploy.sh --only-sql             # Only run SQL setup scripts
# ============================================================================

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and change to it
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Default configuration
CONNECTION="demo"
ENV_PREFIX=""
ONLY_COMPONENT=""

# Read project name from .cursor/PROJECT_NAME.md
PROJECT_NAME_FILE="${SCRIPT_DIR}/.cursor/PROJECT_NAME.md"
DIR_BASENAME=$(basename "$SCRIPT_DIR")

if [ -f "$PROJECT_NAME_FILE" ]; then
    PROJECT_NAME=$(head -1 "$PROJECT_NAME_FILE" | tr -d '[:space:]')
else
    PROJECT_NAME=""
fi

# Validate project name
if [ -z "$PROJECT_NAME" ]; then
    echo -e "${YELLOW}[WARN] .cursor/PROJECT_NAME.md not found${NC}"
    echo "Using directory name: $DIR_BASENAME"
    read -p "Continue? (yes/no): " CONFIRM
    [ "$CONFIRM" != "yes" ] && exit 1
    PROJECT_NAME="$DIR_BASENAME"
elif [ "$PROJECT_NAME" != "$DIR_BASENAME" ]; then
    echo -e "${YELLOW}[WARN] Project name '$PROJECT_NAME' differs from directory '$DIR_BASENAME'${NC}"
    read -p "Continue with '$PROJECT_NAME'? (yes/no): " CONFIRM
    [ "$CONFIRM" != "yes" ] && exit 1
fi

# Convert to uppercase for Snowflake naming
PROJECT_PREFIX=$(echo "$PROJECT_NAME" | tr '[:lower:]' '[:upper:]')

# Display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy SnowCore Permian Command Center to Snowflake.

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  --only-streamlit         Deploy only the Streamlit app
  --only-notebook          Deploy only the notebook
  --only-data              Upload and load data only
  --only-sql               Run SQL setup scripts only
  -h, --help               Show this help message

Examples:
  $0                           # Full deployment
  $0 -c prod                   # Use 'prod' connection
  $0 --prefix DEV              # Deploy with DEV_ prefix
  $0 --prefix DEV -c dev_conn  # DEV environment with dev connection
  $0 --only-streamlit          # Redeploy Streamlit app only
EOF
    exit 0
}

# Error handler
error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--connection)
            CONNECTION="$2"
            shift 2
            ;;
        -p|--prefix)
            ENV_PREFIX="$2"
            shift 2
            ;;
        --only-streamlit)
            ONLY_COMPONENT="streamlit"
            shift
            ;;
        --only-notebook)
            ONLY_COMPONENT="notebook"
            shift
            ;;
        --only-data)
            ONLY_COMPONENT="data"
            shift
            ;;
        --only-sql)
            ONLY_COMPONENT="sql"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            error_exit "Unknown option: $1\nUse --help for usage information"
            ;;
    esac
done

# Build connection string
SNOW_CONN="-c $CONNECTION"

# Compute full prefix (adds underscore only if prefix provided)
if [ -n "$ENV_PREFIX" ]; then
    FULL_PREFIX="${ENV_PREFIX}_${PROJECT_PREFIX}"
else
    FULL_PREFIX="${PROJECT_PREFIX}"
fi

# Derive all resource names
DATABASE="${FULL_PREFIX}"
SCHEMA="${PROJECT_PREFIX}"
ROLE="${FULL_PREFIX}_ROLE"
WAREHOUSE="${FULL_PREFIX}_WH"
COMPUTE_POOL="${FULL_PREFIX}_COMPUTE_POOL"
NETWORK_RULE="${FULL_PREFIX}_EGRESS_RULE"
EXTERNAL_ACCESS="${FULL_PREFIX}_EXTERNAL_ACCESS"
NOTEBOOK_NAME="${FULL_PREFIX}_NOTEBOOK"
STREAMLIT_NAME="${FULL_PREFIX}_APP"

# Helper function to check if a step should run
should_run_step() {
    local step_name="$1"
    # If no specific component requested, run all steps
    if [ -z "$ONLY_COMPONENT" ]; then
        return 0
    fi
    # Check if this step matches the requested component
    case "$ONLY_COMPONENT" in
        sql)
            [[ "$step_name" == "account_sql" || "$step_name" == "schema_sql" ]]
            ;;
        data)
            [[ "$step_name" == "upload_data" || "$step_name" == "upload_docs" || "$step_name" == "load_data" ]]
            ;;
        notebook)
            [[ "$step_name" == "notebook" ]]
            ;;
        streamlit)
            [[ "$step_name" == "streamlit" ]]
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to deploy Streamlit app with proper cleanup and file staging
deploy_streamlit() {
    local STREAMLIT_DIR="${SCRIPT_DIR}/streamlit"
    local STAGE_PATH="@${DATABASE}.${SCHEMA}.streamlit/${STREAMLIT_NAME}"
    
    # Step 1: Clean up stale output/bundle directory to prevent deployment issues
    echo -e "  ${YELLOW}Cleaning up stale bundle artifacts...${NC}"
    rm -rf "${STREAMLIT_DIR}/output"
    
    # Step 2: Run the standard deploy command to create/update the Streamlit object
    echo -e "  ${YELLOW}Creating Streamlit object...${NC}"
    cd "${STREAMLIT_DIR}"
    snow streamlit deploy --replace ${SNOW_CONN} --database ${DATABASE} --schema ${SCHEMA} --role ${ROLE}
    cd "${SCRIPT_DIR}"
    
    # Step 3: Manually upload all files to ensure they're properly staged
    echo -e "  ${YELLOW}Uploading Streamlit files to stage...${NC}"
    snow stage copy "${STREAMLIT_DIR}/streamlit_app.py" ${STAGE_PATH}/ --overwrite ${SNOW_CONN} --role ${ROLE}
    snow stage copy "${STREAMLIT_DIR}/pages/1_Network_Map.py" ${STAGE_PATH}/pages/ --overwrite ${SNOW_CONN} --role ${ROLE}
    snow stage copy "${STREAMLIT_DIR}/pages/2_Simulation_Chat.py" ${STAGE_PATH}/pages/ --overwrite ${SNOW_CONN} --role ${ROLE}
    snow stage copy "${STREAMLIT_DIR}/utils/__init__.py" ${STAGE_PATH}/utils/ --overwrite ${SNOW_CONN} --role ${ROLE}
    snow stage copy "${STREAMLIT_DIR}/utils/data_loader.py" ${STAGE_PATH}/utils/ --overwrite ${SNOW_CONN} --role ${ROLE}
    snow stage copy "${STREAMLIT_DIR}/environment.yml" ${STAGE_PATH}/ --overwrite ${SNOW_CONN} --role ${ROLE}
    
    # Step 4: Verify all files are staged
    echo -e "  ${YELLOW}Verifying staged files...${NC}"
    local FILE_COUNT=$(snow stage list-files ${STAGE_PATH} ${SNOW_CONN} --role ${ROLE} 2>/dev/null | grep -c "\.py\|\.yml" || echo "0")
    if [ "$FILE_COUNT" -lt 6 ]; then
        echo -e "  ${YELLOW}[WARN] Expected 6 files but found ${FILE_COUNT}. Check stage manually.${NC}"
    else
        echo -e "  ${GREEN}[OK]${NC} All ${FILE_COUNT} files verified on stage"
    fi
}

# Display configuration banner
echo "=================================================="
echo "SnowCore Permian Command Center - Deployment"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  Connection: $CONNECTION"
if [ -n "$ENV_PREFIX" ]; then
    echo "  Environment Prefix: $ENV_PREFIX"
fi
if [ -n "$ONLY_COMPONENT" ]; then
    echo "  Deploy Only: $ONLY_COMPONENT"
fi
echo "  Database: $DATABASE"
echo "  Schema: $SCHEMA"
echo "  Role: $ROLE"
echo "  Warehouse: $WAREHOUSE"
echo "  Compute Pool: $COMPUTE_POOL"
echo ""

# Step 1: Check prerequisites
echo -e "\n${YELLOW}[1/9] Checking prerequisites...${NC}"
echo "------------------------------------------------"

if ! command -v snow &> /dev/null; then
    error_exit "Snowflake CLI (snow) not found. Install with: pip install snowflake-cli"
fi
echo -e "${GREEN}[OK]${NC} Snowflake CLI found"

# Test Snowflake connection using a simple query
echo "Testing Snowflake connection..."
if ! snow sql ${SNOW_CONN} -q "SELECT 1" &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Failed to connect to Snowflake"
    snow connection test ${SNOW_CONN} 2>&1 || true
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Connection '$CONNECTION' verified"

if [ ! -d "${SCRIPT_DIR}/data/synthetic" ]; then
    error_exit "Synthetic data not found. Run 'python utils/generate_synthetic_data.py' first."
fi
echo -e "${GREEN}[OK]${NC} Prerequisites verified"

# Step 2: Run infrastructure setup (ACCOUNTADMIN required for account-level objects)
if should_run_step "account_sql"; then
    echo -e "\n${YELLOW}[2/9] Setting up infrastructure (as ACCOUNTADMIN)...${NC}"
    echo "------------------------------------------------"
    
    # Combine SET statements with SQL file using stdin
    {
        echo "-- Set session variables for account-level objects"
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_PREFIX = '${PROJECT_PREFIX}';"
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET PROJECT_WH = '${WAREHOUSE}';"
        echo "SET PROJECT_COMPUTE_POOL = '${COMPUTE_POOL}';"
        echo "SET PROJECT_SCHEMA = '${SCHEMA}';"
        echo "SET PROJECT_NETWORK_RULE = '${NETWORK_RULE}';"
        echo "SET PROJECT_EXTERNAL_ACCESS = '${EXTERNAL_ACCESS}';"
        echo ""
        cat "${SCRIPT_DIR}/sql/01_setup.sql"
    } | snow sql ${SNOW_CONN} -i --role ACCOUNTADMIN
    
    echo -e "${GREEN}[OK]${NC} Infrastructure created"
else
    echo -e "\n${YELLOW}[2/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 3: Upload synthetic data to stage (using project role)
if should_run_step "upload_data"; then
    echo -e "\n${YELLOW}[3/9] Uploading synthetic data to stage...${NC}"
    echo "------------------------------------------------"
    snow stage copy "${SCRIPT_DIR}/data/synthetic/*.csv" @${DATABASE}.${SCHEMA}.DATA_STAGE --overwrite ${SNOW_CONN} --role ${ROLE}
    echo -e "${GREEN}[OK]${NC} Data uploaded to DATA_STAGE"
else
    echo -e "\n${YELLOW}[3/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 4: Upload documents to stage (using project role)
if should_run_step "upload_docs"; then
    echo -e "\n${YELLOW}[4/9] Uploading documents to stage...${NC}"
    echo "------------------------------------------------"
    snow stage copy "${SCRIPT_DIR}/data/documents/*.txt" @${DATABASE}.${SCHEMA}.DOCS_STAGE --overwrite ${SNOW_CONN} --role ${ROLE}
    echo -e "${GREEN}[OK]${NC} Documents uploaded to DOCS_STAGE"
else
    echo -e "\n${YELLOW}[4/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 5: Create tables and load data (using project role)
if should_run_step "load_data" || should_run_step "schema_sql"; then
    echo -e "\n${YELLOW}[5/9] Creating tables and loading data...${NC}"
    echo "------------------------------------------------"
    snow sql -f "${SCRIPT_DIR}/sql/02_tables.sql" ${SNOW_CONN} --role ${ROLE} --database ${DATABASE} --schema ${SCHEMA} --warehouse ${WAREHOUSE}
    echo -e "${GREEN}[OK]${NC} Tables created and data loaded"
else
    echo -e "\n${YELLOW}[5/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 6: Create Cortex Search service (using project role)
if should_run_step "schema_sql"; then
    echo -e "\n${YELLOW}[6/9] Setting up Cortex Search...${NC}"
    echo "------------------------------------------------"
    snow sql -f "${SCRIPT_DIR}/sql/03_cortex_search.sql" ${SNOW_CONN} --role ${ROLE} --database ${DATABASE} --schema ${SCHEMA} --warehouse ${WAREHOUSE}
    echo -e "${GREEN}[OK]${NC} Cortex Search service created"
else
    echo -e "\n${YELLOW}[6/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 7: Deploy Semantic View (using project role)
if should_run_step "schema_sql"; then
    echo -e "\n${YELLOW}[7/9] Deploying Semantic View...${NC}"
    echo "------------------------------------------------"
    snow sql -f "${SCRIPT_DIR}/sql/04_semantic_view.sql" ${SNOW_CONN} --role ${ROLE} --database ${DATABASE} --schema ${SCHEMA} --warehouse ${WAREHOUSE}
    echo -e "${GREEN}[OK]${NC} Semantic View deployed"
else
    echo -e "\n${YELLOW}[7/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 8: Deploy Streamlit app (using project role)
if should_run_step "streamlit"; then
    echo -e "\n${YELLOW}[8/9] Deploying Streamlit app...${NC}"
    echo "------------------------------------------------"
    deploy_streamlit
    echo -e "${GREEN}[OK]${NC} Streamlit app deployed"
else
    echo -e "\n${YELLOW}[8/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Step 9: Deploy AutoGL notebook (using project role)
if should_run_step "notebook"; then
    echo -e "\n${YELLOW}[9/9] Deploying AutoGL notebook...${NC}"
    echo "------------------------------------------------"
    NOTEBOOK_DIR="${SCRIPT_DIR}/notebooks"
    
    # Upload the notebook file to stage
    echo -e "  ${YELLOW}Uploading notebook to stage...${NC}"
    snow stage copy "${NOTEBOOK_DIR}/autogl_link_prediction.ipynb" \
        @${DATABASE}.${SCHEMA}.NOTEBOOK_STAGE/ \
        --overwrite ${SNOW_CONN} --role ${ROLE}
    
    # Create or replace the notebook object with container runtime for PyTorch
    echo -e "  ${YELLOW}Creating notebook object...${NC}"
    snow sql -q "
        CREATE OR REPLACE NOTEBOOK ${DATABASE}.${SCHEMA}.${NOTEBOOK_NAME}
        FROM '@${DATABASE}.${SCHEMA}.NOTEBOOK_STAGE'
        MAIN_FILE = 'autogl_link_prediction.ipynb'
        QUERY_WAREHOUSE = ${WAREHOUSE}
        COMPUTE_POOL = ${COMPUTE_POOL}
        RUNTIME_NAME = 'SYSTEM\$BASIC_RUNTIME'
        EXTERNAL_ACCESS_INTEGRATIONS = (${EXTERNAL_ACCESS})
        COMMENT = 'AutoGL Link Prediction - Discovers hidden network connections and predicts pressure anomaly risks';
    " ${SNOW_CONN} --role ${ROLE} --database ${DATABASE} --schema ${SCHEMA} --warehouse ${WAREHOUSE}
    
    # Add live version so notebook can be executed via CLI
    echo -e "  ${YELLOW}Committing notebook live version...${NC}"
    snow sql -q "ALTER NOTEBOOK ${DATABASE}.${SCHEMA}.${NOTEBOOK_NAME} ADD LIVE VERSION FROM LAST" \
        ${SNOW_CONN} --role ${ROLE} --database ${DATABASE} --schema ${SCHEMA} --warehouse ${WAREHOUSE}
    echo -e "${GREEN}[OK]${NC} Notebook deployed"
else
    echo -e "\n${YELLOW}[9/9] Skipped (--only-$ONLY_COMPONENT)${NC}"
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================================="
echo ""

if [ -n "$ONLY_COMPONENT" ]; then
    echo "Deployed component: $ONLY_COMPONENT"
else
    echo "Resources created:"
    echo "  - Database: ${DATABASE}"
    echo "  - Schema: ${SCHEMA}"
    echo "  - Role: ${ROLE}"
    echo "  - Warehouse: ${WAREHOUSE}"
    echo "  - Compute Pool: ${COMPUTE_POOL}"
    echo "  - Tables: ASSET_MASTER, NETWORK_EDGES, SCADA_TELEMETRY, GRAPH_PREDICTIONS, SCADA_AGGREGATES"
    echo "  - Cortex Search: ${FULL_PREFIX}_DOCS_SEARCH"
    echo "  - Semantic View: ${FULL_PREFIX}_ANALYTICS_VIEW"
    echo "  - Streamlit App: ${STREAMLIT_NAME}"
    echo "  - Notebook: ${NOTEBOOK_NAME}"
    echo ""
    echo "Next steps:"
    echo "  1. Run the AutoGL notebook to generate ML predictions:"
    echo "     ./run.sh main"
    echo "  2. Open Snowsight and navigate to Streamlit apps"
    echo "  3. Launch '${STREAMLIT_NAME}'"
fi
echo ""
echo "=================================================="
