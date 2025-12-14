-- ============================================================================
-- 01_setup.sql - Infrastructure Setup for SnowCore Permian Command Center
-- ============================================================================
-- Creates database, warehouse, network rule for PyPI access, and stages
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- Database and Schema
-- ============================================================================
CREATE DATABASE IF NOT EXISTS AUTOGL_YIELD_OPTIMIZATION;
USE DATABASE AUTOGL_YIELD_OPTIMIZATION;

CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- ============================================================================
-- Warehouse
-- ============================================================================
CREATE WAREHOUSE IF NOT EXISTS AUTOGL_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for AutoGL Yield Optimization demo';

USE WAREHOUSE AUTOGL_WH;

-- ============================================================================
-- Network Rule for PyPI Access (Required for pip install in notebooks)
-- ============================================================================
CREATE OR REPLACE NETWORK RULE PYPI_NETWORK_RULE
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
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION PYPI_ACCESS_INTEGRATION
    ALLOWED_NETWORK_RULES = (PYPI_NETWORK_RULE)
    ENABLED = TRUE
    COMMENT = 'External access integration for pip installs in Snowflake Notebooks';

-- ============================================================================
-- Internal Stages
-- ============================================================================

-- Stage for synthetic data CSVs
CREATE OR REPLACE STAGE DATA_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for loading synthetic demo data';

-- Stage for unstructured documents (P&IDs, logs)
CREATE OR REPLACE STAGE DOCS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for P&ID documents and operator logs';

-- Stage for notebooks
CREATE OR REPLACE STAGE NOTEBOOKS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for Snowflake Notebooks';

-- ============================================================================
-- Verify Setup
-- ============================================================================
SHOW DATABASES LIKE 'AUTOGL_YIELD_OPTIMIZATION';
SHOW WAREHOUSES LIKE 'AUTOGL_WH';
SHOW NETWORK RULES LIKE 'PYPI_NETWORK_RULE';
SHOW EXTERNAL ACCESS INTEGRATIONS LIKE 'PYPI_ACCESS_INTEGRATION';
SHOW STAGES;

SELECT 'Infrastructure setup complete!' AS STATUS;

