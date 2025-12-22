#!/bin/bash
# ============================================================================
# run.sh - Runtime Operations for SnowCore Permian Command Center
# ============================================================================
# Prerequisites:
#   - deploy.sh has been run successfully (infrastructure exists)
#
# Commands:
#   main       - Execute the AutoGL notebook
#   status     - Check status of resources and show table counts
#   streamlit  - Get Streamlit app URL
#   notebook   - Get notebook URL in Snowsight
#
# Usage:
#   ./run.sh main                      # Execute notebook with default connection
#   ./run.sh status                    # Show resource status
#   ./run.sh streamlit                 # Get Streamlit URL
#   ./run.sh -c prod main              # Use 'prod' connection
#   ./run.sh --prefix DEV status       # Check DEV environment status
# ============================================================================

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
CONNECTION="demo"
ENV_PREFIX=""
COMMAND=""

# Display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND

Runtime operations for SnowCore Permian Command Center.

Commands:
  main       Execute the AutoGL notebook
  status     Check status of resources and show table counts
  streamlit  Get Streamlit app URL
  notebook   Get notebook URL in Snowsight

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  -h, --help               Show this help message

Examples:
  $0 main                      # Execute notebook
  $0 status                    # Check resource status
  $0 streamlit                 # Get Streamlit URL
  $0 -c prod main              # Use 'prod' connection
  $0 --prefix DEV status       # Check DEV environment
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
        -h|--help)
            usage
            ;;
        main|status|streamlit|notebook)
            COMMAND="$1"
            shift
            ;;
        *)
            error_exit "Unknown option or command: $1\nUse --help for usage information"
            ;;
    esac
done

# Require a command
if [ -z "$COMMAND" ]; then
    usage
fi

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
NOTEBOOK_NAME="${FULL_PREFIX}_NOTEBOOK"
STREAMLIT_NAME="${FULL_PREFIX}_APP"

###############################################################################
# Command: main - Execute notebook
###############################################################################
cmd_main() {
    echo "=================================================="
    echo "AutoGL Link Prediction - Notebook Execution"
    echo "=================================================="
    echo ""
    echo "Configuration:"
    echo "  Connection: $CONNECTION"
    if [ -n "$ENV_PREFIX" ]; then
        echo "  Environment Prefix: $ENV_PREFIX"
    fi
    echo "  Database: $DATABASE"
    echo "  Schema: $SCHEMA"
    echo "  Notebook: $NOTEBOOK_NAME"
    echo ""
    
    echo -e "${YELLOW}Executing notebook...${NC}"
    echo -e "  Running AutoGL Link Prediction (this may take 2-5 minutes)..."
    
    snow notebook execute ${NOTEBOOK_NAME} \
        ${SNOW_CONN} \
        --database ${DATABASE} \
        --schema ${SCHEMA} \
        --warehouse ${WAREHOUSE}
    
    echo -e "${GREEN}[OK]${NC} Notebook execution complete"
    
    # Show prediction summary
    echo ""
    echo -e "${YELLOW}Prediction Summary:${NC}"
    snow sql -q "
        SELECT 
            PREDICTION_TYPE,
            COUNT(*) AS COUNT,
            ROUND(AVG(SCORE), 3) AS AVG_SCORE,
            ROUND(MAX(SCORE), 3) AS MAX_SCORE
        FROM ${DATABASE}.${SCHEMA}.GRAPH_PREDICTIONS
        GROUP BY PREDICTION_TYPE;
    " ${SNOW_CONN} --database ${DATABASE} --schema ${SCHEMA} --warehouse ${WAREHOUSE} 2>/dev/null || echo "  (Unable to fetch summary - predictions may not exist yet)"
    
    echo ""
    echo "=================================================="
    echo -e "${GREEN}Notebook Run Complete!${NC}"
    echo "=================================================="
    echo ""
    echo "Results:"
    echo "  - Predictions written to: ${DATABASE}.${SCHEMA}.GRAPH_PREDICTIONS"
    echo ""
    echo "Next steps:"
    echo "  1. View the Streamlit app: ./run.sh streamlit"
    echo "  2. Check Network Map for discovered connections"
    echo "  3. Use Simulation Chat to ask about high-risk assets"
}

###############################################################################
# Command: status - Check resource status
###############################################################################
cmd_status() {
    echo "=================================================="
    echo "SnowCore Permian Command Center - Status"
    echo "=================================================="
    echo ""
    echo "Configuration:"
    echo "  Connection: $CONNECTION"
    if [ -n "$ENV_PREFIX" ]; then
        echo "  Environment Prefix: $ENV_PREFIX"
    fi
    echo "  Database: $DATABASE"
    echo ""
    
    echo -e "${YELLOW}Checking resources...${NC}"
    echo ""
    
    # Check compute pool
    echo "Compute Pool:"
    snow sql ${SNOW_CONN} -q "SHOW COMPUTE POOLS LIKE '${COMPUTE_POOL}';" 2>/dev/null | head -5 || echo "  Not found or no access"
    echo ""
    
    # Check warehouse
    echo "Warehouse:"
    snow sql ${SNOW_CONN} -q "SHOW WAREHOUSES LIKE '${WAREHOUSE}';" 2>/dev/null | head -5 || echo "  Not found or no access"
    echo ""
    
    # Check table row counts
    echo "Table Row Counts:"
    snow sql ${SNOW_CONN} -q "USE ROLE ${ROLE}; USE DATABASE ${DATABASE}; USE SCHEMA ${SCHEMA}; SELECT 'ASSET_MASTER' AS TABLE_NAME, COUNT(*) AS ROWS FROM ASSET_MASTER UNION ALL SELECT 'NETWORK_EDGES', COUNT(*) FROM NETWORK_EDGES UNION ALL SELECT 'SCADA_TELEMETRY', COUNT(*) FROM SCADA_TELEMETRY UNION ALL SELECT 'GRAPH_PREDICTIONS', COUNT(*) FROM GRAPH_PREDICTIONS UNION ALL SELECT 'SCADA_AGGREGATES', COUNT(*) FROM SCADA_AGGREGATES;" 2>/dev/null || echo "  [WARN] Error querying tables"
    echo ""
    
    # Check high-risk assets
    echo "High Risk Assets (score > 0.7):"
    snow sql ${SNOW_CONN} -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        SELECT ENTITY_ID, ROUND(SCORE, 3) AS RISK_SCORE, EXPLANATION
        FROM GRAPH_PREDICTIONS
        WHERE PREDICTION_TYPE = 'NODE_ANOMALY' AND SCORE > 0.7
        ORDER BY SCORE DESC
        LIMIT 5;
    " 2>/dev/null || echo "  [WARN] No predictions found or error querying"
    
    echo ""
    echo "=================================================="
}

###############################################################################
# Command: streamlit - Get Streamlit URL
###############################################################################
cmd_streamlit() {
    echo "=================================================="
    echo "SnowCore Permian Command Center - Streamlit App"
    echo "=================================================="
    echo ""
    
    # Try to get URL
    URL=$(snow streamlit get-url ${STREAMLIT_NAME} \
        ${SNOW_CONN} \
        --database ${DATABASE} \
        --schema ${SCHEMA} \
        --role ${ROLE} 2>/dev/null) || true
    
    if [ -n "$URL" ]; then
        echo "Streamlit Dashboard URL:"
        echo ""
        echo "  $URL"
    else
        echo "Could not retrieve URL automatically."
        echo ""
        echo "To open the dashboard:"
        echo "1. Go to Snowsight (https://app.snowflake.com)"
        echo "2. Navigate to: Projects > Streamlit"
        echo "3. Open: ${STREAMLIT_NAME}"
    fi
    echo ""
    echo "=================================================="
}

###############################################################################
# Command: notebook - Get notebook URL
###############################################################################
cmd_notebook() {
    echo "=================================================="
    echo "SnowCore Permian Command Center - Notebook"
    echo "=================================================="
    echo ""
    echo "Notebook: ${NOTEBOOK_NAME}"
    echo ""
    echo "To open the notebook:"
    echo "1. Go to Snowsight (https://app.snowflake.com)"
    echo "2. Navigate to: Projects > Notebooks"
    echo "3. Open: ${NOTEBOOK_NAME}"
    echo ""
    echo "Or execute headlessly:"
    echo "  ./run.sh main"
    echo ""
    echo "=================================================="
}

###############################################################################
# Execute command
###############################################################################
case $COMMAND in
    main)
        cmd_main
        ;;
    status)
        cmd_status
        ;;
    streamlit)
        cmd_streamlit
        ;;
    notebook)
        cmd_notebook
        ;;
    *)
        error_exit "Unknown command: $COMMAND"
        ;;
esac
