-- ============================================================================
-- 01_setup.sql - Infrastructure Setup for SnowCore Permian Command Center
-- ============================================================================
-- Creates role, database, warehouse, compute pool, network rules, and stages
-- 
-- This script runs as ACCOUNTADMIN to create account-level objects.
-- Subsequent scripts (02-05) run as the project role.
--
-- REQUIRED SESSION VARIABLES (set by deploy.sh before execution):
--   $FULL_PREFIX           - Full resource prefix (e.g., DEV_AUTOGL_YIELD_OPTIMIZATION)
--   $PROJECT_PREFIX        - Base project prefix (AUTOGL_YIELD_OPTIMIZATION)
--   $PROJECT_ROLE          - Role name (e.g., DEV_AUTOGL_YIELD_OPTIMIZATION_ROLE)
--   $PROJECT_WH            - Warehouse name
--   $PROJECT_COMPUTE_POOL  - Compute pool name
--   $PROJECT_SCHEMA        - Schema name (always PROJECT_PREFIX, unprefixed)
--   $PROJECT_NETWORK_RULE  - Network rule name
--   $PROJECT_EXTERNAL_ACCESS - External access integration name
--
-- Naming Convention (per SNOWFLAKE_DEPLOYMENT_SCRIPT_GUIDELINES.md):
--   DATABASE: $FULL_PREFIX (e.g., DEV_AUTOGL_YIELD_OPTIMIZATION or AUTOGL_YIELD_OPTIMIZATION)
--   SCHEMA: $PROJECT_SCHEMA (always AUTOGL_YIELD_OPTIMIZATION - unprefixed)
--   ROLE: $PROJECT_ROLE
--   WAREHOUSE: $PROJECT_WH
--   COMPUTE_POOL: $PROJECT_COMPUTE_POOL
--   NETWORK_RULE: $PROJECT_NETWORK_RULE
--   EXTERNAL_ACCESS: $PROJECT_EXTERNAL_ACCESS
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- Role
-- ============================================================================
CREATE ROLE IF NOT EXISTS IDENTIFIER($PROJECT_ROLE)
    COMMENT = 'Role for AutoGL Yield Optimization project';

-- Grant role to current user and ACCOUNTADMIN for management
SET MY_USER = (SELECT CURRENT_USER());
GRANT ROLE IDENTIFIER($PROJECT_ROLE) TO USER IDENTIFIER($MY_USER);
GRANT ROLE IDENTIFIER($PROJECT_ROLE) TO ROLE ACCOUNTADMIN;

-- ============================================================================
-- Database and Schema
-- ============================================================================
CREATE DATABASE IF NOT EXISTS IDENTIFIER($FULL_PREFIX);

-- Build fully qualified schema name for creation
SET FQ_SCHEMA = $FULL_PREFIX || '.' || $PROJECT_SCHEMA;
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($FQ_SCHEMA);

-- Set context for subsequent operations
-- Note: USE statements can't use IDENTIFIER(), so we use literals derived from session context
SELECT 'Setting context for database: ' || $FULL_PREFIX AS STATUS;

-- Grant database and schema ownership to project role
GRANT OWNERSHIP ON DATABASE IDENTIFIER($FULL_PREFIX) 
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;
GRANT OWNERSHIP ON SCHEMA IDENTIFIER($FQ_SCHEMA) 
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- ============================================================================
-- Warehouse
-- ============================================================================
CREATE WAREHOUSE IF NOT EXISTS IDENTIFIER($PROJECT_WH)
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for AutoGL Yield Optimization project';

-- Grant warehouse privileges to project role
GRANT USAGE ON WAREHOUSE IDENTIFIER($PROJECT_WH) TO ROLE IDENTIFIER($PROJECT_ROLE);
GRANT OPERATE ON WAREHOUSE IDENTIFIER($PROJECT_WH) TO ROLE IDENTIFIER($PROJECT_ROLE);

-- ============================================================================
-- Network Rule for PyPI Access (Required for pip install in notebooks)
-- ============================================================================
-- Network rules must be created in a schema context
-- We'll create it in the project schema
SET FQ_NETWORK_RULE = $FULL_PREFIX || '.' || $PROJECT_SCHEMA || '.' || $PROJECT_NETWORK_RULE;

CREATE OR REPLACE NETWORK RULE IDENTIFIER($FQ_NETWORK_RULE)
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = (
        'pypi.org:443',
        'files.pythonhosted.org:443',
        'download.pytorch.org:443'
    )
    COMMENT = 'Allow access to PyPI and PyTorch for package installation';

-- ============================================================================
-- External Access Integration for Notebooks
-- ============================================================================
-- Note: External access integrations reference network rules by fully qualified name
-- We need to use a string literal for ALLOWED_NETWORK_RULES, so construct it dynamically
SET EXT_ACCESS_RULE_REF = $FULL_PREFIX || '.' || $PROJECT_SCHEMA || '.' || $PROJECT_NETWORK_RULE;

-- Create external access integration using dynamic SQL
-- This is necessary because ALLOWED_NETWORK_RULES expects a literal, not a variable
-- Use scripting block to avoid 256-byte session variable limit
EXECUTE IMMEDIATE $$
DECLARE
    create_eai_sql VARCHAR;
BEGIN
    create_eai_sql := 'CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ' || $PROJECT_EXTERNAL_ACCESS ||
        ' ALLOWED_NETWORK_RULES = (' || $EXT_ACCESS_RULE_REF || ')' ||
        ' ENABLED = TRUE' ||
        ' COMMENT = ''External access integration for pip installs''';
    EXECUTE IMMEDIATE create_eai_sql;
END;
$$;

-- Grant external access integration usage to project role
GRANT USAGE ON INTEGRATION IDENTIFIER($PROJECT_EXTERNAL_ACCESS) TO ROLE IDENTIFIER($PROJECT_ROLE);

-- ============================================================================
-- Compute Pool for Container Runtime Notebooks
-- ============================================================================
CREATE COMPUTE POOL IF NOT EXISTS IDENTIFIER($PROJECT_COMPUTE_POOL)
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_SUSPEND_SECS = 300
    COMMENT = 'Compute pool for AutoGL notebooks with PyTorch';

-- Grant compute pool usage to project role
GRANT USAGE ON COMPUTE POOL IDENTIFIER($PROJECT_COMPUTE_POOL) TO ROLE IDENTIFIER($PROJECT_ROLE);

-- ============================================================================
-- Additional Grants for Cortex AI Services
-- ============================================================================
-- Grant privileges needed for Cortex services (Search, Analyst, Agent)
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE IDENTIFIER($PROJECT_ROLE);

-- ============================================================================
-- Future Grants for Tables Created by Other Roles
-- ============================================================================
-- Ensures that tables created in this schema (e.g., by notebooks running as
-- ACCOUNTADMIN) automatically grant SELECT to the project role
GRANT SELECT ON FUTURE TABLES IN SCHEMA IDENTIFIER($FQ_SCHEMA) 
    TO ROLE IDENTIFIER($PROJECT_ROLE);

-- ============================================================================
-- Internal Stages (created by project role after ownership transfer)
-- ============================================================================
-- Switch to project role for schema-level objects
-- Use the warehouse to ensure we have compute for subsequent operations
USE ROLE IDENTIFIER($PROJECT_ROLE);

-- Execute dynamic USE statements for database/schema context
USE DATABASE IDENTIFIER($FULL_PREFIX);
USE SCHEMA IDENTIFIER($PROJECT_SCHEMA);
USE WAREHOUSE IDENTIFIER($PROJECT_WH);

-- Stage for synthetic data CSVs
CREATE OR REPLACE STAGE DATA_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for loading synthetic demo data';

-- Stage for unstructured documents (PIDs, logs)
CREATE OR REPLACE STAGE DOCS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for PID documents and operator logs';

-- Stage for notebooks
CREATE OR REPLACE STAGE NOTEBOOK_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for Snowflake Notebooks';

-- ============================================================================
-- Verify Setup
-- ============================================================================
SELECT 'Database: ' || $FULL_PREFIX AS RESOURCE, 'Created' AS STATUS
UNION ALL
SELECT 'Schema: ' || $FQ_SCHEMA, 'Created'
UNION ALL
SELECT 'Role: ' || $PROJECT_ROLE, 'Created'
UNION ALL
SELECT 'Warehouse: ' || $PROJECT_WH, 'Created'
UNION ALL
SELECT 'Compute Pool: ' || $PROJECT_COMPUTE_POOL, 'Created'
UNION ALL
SELECT 'Network Rule: ' || $PROJECT_NETWORK_RULE, 'Created'
UNION ALL
SELECT 'External Access: ' || $PROJECT_EXTERNAL_ACCESS, 'Created';

SELECT 'Infrastructure setup complete!' AS STATUS;
