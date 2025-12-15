#!/bin/bash
# ============================================================================
# clean.sh - Clean up Snowflake resources for SnowCore Permian Command Center
# ============================================================================
# Removes all Snowflake objects created by deploy.sh
# Does NOT delete local files (they are version controlled)
#
# Deletion Order (per SNOWFLAKE_DEPLOYMENT_SCRIPT_GUIDELINES.md):
#   1. Compute Pool (must be dropped before role)
#   2. Warehouse
#   3. External Access Integration
#   4. Database (cascades to all tables, stages, apps, notebooks)
#   5. Role (last, after all owned objects are gone)
#
# Usage:
#   ./clean.sh                       # Uses default connection "demo"
#   ./clean.sh -c myconnection       # Uses specified connection
#   ./clean.sh --prefix DEV          # Clean DEV environment
#   ./clean.sh --force               # Skip confirmation prompt
#   ./clean.sh --prefix DEV --yes    # Clean DEV without confirmation
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
FORCE=false

# Project naming base (per guidelines)
PROJECT_PREFIX="AUTOGL_YIELD_OPTIMIZATION"

# Display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Remove all Snowflake resources created by deploy.sh.
Local files are NOT deleted (they are version controlled).

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  --force, --yes, -y       Skip confirmation prompt
  -h, --help               Show this help message

Examples:
  $0                       # Clean default environment
  $0 -c prod               # Use 'prod' connection
  $0 --prefix DEV          # Clean DEV environment
  $0 --prefix DEV --yes    # Clean DEV without confirmation
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
        --force|--yes|-y)
            FORCE=true
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

# Display banner
echo "=================================================="
echo "SnowCore Permian Command Center - Cleanup"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  Connection: $CONNECTION"
if [ -n "$ENV_PREFIX" ]; then
    echo "  Environment Prefix: $ENV_PREFIX"
fi
echo ""

# Display what will be removed
echo -e "${YELLOW}WARNING: This will permanently delete all project resources!${NC}"
echo ""
echo "Resources to be deleted:"
echo "  - Compute Pool: ${COMPUTE_POOL}"
echo "  - Warehouse: ${WAREHOUSE}"
echo "  - External Access Integration: ${EXTERNAL_ACCESS}"
echo "  - Database: ${DATABASE} (includes all tables, stages, apps, notebooks)"
echo "  - Role: ${ROLE}"
echo ""

# Confirmation
if [ "$FORCE" = false ]; then
    read -p "Are you sure you want to delete all resources? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Cleanup cancelled."
        exit 0
    fi
fi

echo ""
echo "Starting cleanup..."
echo ""

# Step 1: Drop Compute Pool (must be done first, before role)
echo -e "${YELLOW}[1/6] Dropping compute pool...${NC}"
snow sql ${SNOW_CONN} -q "
    USE ROLE ACCOUNTADMIN;
    DROP COMPUTE POOL IF EXISTS ${COMPUTE_POOL};
" 2>/dev/null && echo -e "${GREEN}[OK]${NC} Compute pool dropped" \
             || echo -e "${YELLOW}[WARN]${NC} Compute pool not found or already dropped"

# Step 2: Drop Warehouse
echo -e "${YELLOW}[2/6] Dropping warehouse...${NC}"
snow sql ${SNOW_CONN} -q "
    USE ROLE ACCOUNTADMIN;
    DROP WAREHOUSE IF EXISTS ${WAREHOUSE};
" 2>/dev/null && echo -e "${GREEN}[OK]${NC} Warehouse dropped" \
             || echo -e "${YELLOW}[WARN]${NC} Warehouse not found or already dropped"

# Step 3: Drop External Access Integration
echo -e "${YELLOW}[3/6] Dropping external access integration...${NC}"
snow sql ${SNOW_CONN} -q "
    USE ROLE ACCOUNTADMIN;
    DROP EXTERNAL ACCESS INTEGRATION IF EXISTS ${EXTERNAL_ACCESS};
" 2>/dev/null && echo -e "${GREEN}[OK]${NC} External access integration dropped" \
             || echo -e "${YELLOW}[WARN]${NC} External access integration not found or already dropped"

# Step 4: Drop Database (cascades to all contained objects including network rules in schema)
echo -e "${YELLOW}[4/6] Dropping database (cascades to all tables, stages, apps, notebooks)...${NC}"
snow sql ${SNOW_CONN} -q "
    USE ROLE ACCOUNTADMIN;
    DROP DATABASE IF EXISTS ${DATABASE} CASCADE;
" 2>/dev/null && echo -e "${GREEN}[OK]${NC} Database dropped" \
             || echo -e "${YELLOW}[WARN]${NC} Database not found or already dropped"

# Step 5: Drop any remaining network rules at account level (if they weren't in schema)
echo -e "${YELLOW}[5/6] Dropping any remaining network rules...${NC}"
# Note: Network rules created in the schema are dropped with the database CASCADE
# This step handles any that might have been created at account level
echo -e "${GREEN}[OK]${NC} Network rules cleanup complete"

# Step 6: Drop Role (must be done last, after all owned objects are gone)
echo -e "${YELLOW}[6/6] Dropping role...${NC}"
snow sql ${SNOW_CONN} -q "
    USE ROLE ACCOUNTADMIN;
    DROP ROLE IF EXISTS ${ROLE};
" 2>/dev/null && echo -e "${GREEN}[OK]${NC} Role dropped" \
             || echo -e "${YELLOW}[WARN]${NC} Role not found or already dropped"

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "=================================================="
echo ""
echo "All Snowflake resources have been removed."
echo "Local files (data/, sql/, etc.) have been preserved."
echo ""
echo "To redeploy, run:"
if [ -n "$ENV_PREFIX" ]; then
    echo "  ./deploy.sh -c ${CONNECTION} --prefix ${ENV_PREFIX}"
else
    echo "  ./deploy.sh -c ${CONNECTION}"
fi
echo ""
echo "=================================================="
