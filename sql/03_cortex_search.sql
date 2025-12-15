-- ============================================================================
-- 03_cortex_search.sql - Cortex Search Service for Unstructured Documents
-- ============================================================================
-- Creates search service for PID documents, maintenance logs, and operator notes
-- 
-- Runs as: AUTOGL_YIELD_OPTIMIZATION_ROLE (project role)
-- ============================================================================

USE ROLE AUTOGL_YIELD_OPTIMIZATION_ROLE;
USE DATABASE AUTOGL_YIELD_OPTIMIZATION;
USE SCHEMA AUTOGL_YIELD_OPTIMIZATION;
USE WAREHOUSE AUTOGL_YIELD_OPTIMIZATION_WH;

-- ============================================================================
-- Documents Table for Cortex Search
-- ============================================================================
-- Stores document content and metadata for RAG retrieval

CREATE OR REPLACE TABLE LEGACY_DOCUMENTS (
    DOCUMENT_ID VARCHAR(100) NOT NULL,
    DOCUMENT_TYPE VARCHAR(50) NOT NULL,    -- PID, SHIFT_REPORT, MAINTENANCE_LOG, VENDOR_MANUAL
    DOCUMENT_NAME VARCHAR(255) NOT NULL,
    TAG_ID VARCHAR(50),                    -- Equipment tag referenced (e.g., TF-V-204)
    FACILITY VARCHAR(100),
    CONTENT TEXT NOT NULL,                 -- Full document text content
    UPLOAD_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM VARCHAR(50),             -- TERAFIELD, SNOWCORE
    
    PRIMARY KEY (DOCUMENT_ID)
)
COMMENT = 'Legacy TeraField documents for Cortex Search RAG retrieval';

-- ============================================================================
-- Load Documents from Stage
-- ============================================================================

-- Create file format for reading text files as single blob
CREATE OR REPLACE FILE FORMAT TEXT_FILE_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = NONE
    RECORD_DELIMITER = NONE
    COMMENT = 'Format for reading entire text files as single blob';

-- PID Document
INSERT INTO LEGACY_DOCUMENTS (DOCUMENT_ID, DOCUMENT_TYPE, DOCUMENT_NAME, TAG_ID, FACILITY, CONTENT, SOURCE_SYSTEM)
SELECT 
    'PID-TF-MID-001',
    'PID',
    'TeraField_Midland_Hub_Process_Flow.txt',
    'TF-V-204',
    'Midland Hub',
    $1,
    'TERAFIELD'
FROM @DOCS_STAGE/TeraField_Midland_Hub_Process_Flow.txt (FILE_FORMAT => TEXT_FILE_FORMAT);

-- Shift Report
INSERT INTO LEGACY_DOCUMENTS (DOCUMENT_ID, DOCUMENT_TYPE, DOCUMENT_NAME, TAG_ID, FACILITY, CONTENT, SOURCE_SYSTEM)
SELECT 
    'SHIFT-2023-10-12',
    'SHIFT_REPORT',
    'Shift_Report_2023_10_12.txt',
    'TF-V-204',
    'Midland Hub',
    $1,
    'TERAFIELD'
FROM @DOCS_STAGE/Shift_Report_2023_10_12.txt (FILE_FORMAT => TEXT_FILE_FORMAT);

-- Maintenance Log
INSERT INTO LEGACY_DOCUMENTS (DOCUMENT_ID, DOCUMENT_TYPE, DOCUMENT_NAME, TAG_ID, FACILITY, CONTENT, SOURCE_SYSTEM)
SELECT 
    'MAINT-V204-LOG',
    'MAINTENANCE_LOG',
    'Maintenance_Log_V204.txt',
    'TF-V-204',
    'Midland Hub',
    $1,
    'TERAFIELD'
FROM @DOCS_STAGE/Maintenance_Log_V204.txt (FILE_FORMAT => TEXT_FILE_FORMAT);

-- ============================================================================
-- Cortex Search Service
-- ============================================================================
-- Creates a search service for semantic search over legacy documents

CREATE OR REPLACE CORTEX SEARCH SERVICE AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH
    ON CONTENT
    ATTRIBUTES TAG_ID, DOCUMENT_TYPE, FACILITY
    WAREHOUSE = AUTOGL_YIELD_OPTIMIZATION_WH
    TARGET_LAG = '1 hour'
    COMMENT = 'Semantic search over legacy TeraField PIDs, maintenance logs, and operator notes'
AS (
    SELECT 
        DOCUMENT_ID,
        DOCUMENT_TYPE,
        DOCUMENT_NAME,
        TAG_ID,
        FACILITY,
        CONTENT,
        SOURCE_SYSTEM
    FROM LEGACY_DOCUMENTS
);

-- ============================================================================
-- Verify Setup
-- ============================================================================

-- Check documents loaded
SELECT DOCUMENT_ID, DOCUMENT_TYPE, TAG_ID, FACILITY, LENGTH(CONTENT) AS CONTENT_LENGTH
FROM LEGACY_DOCUMENTS;

-- Show search service
SHOW CORTEX SEARCH SERVICES LIKE 'AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH';

-- Test search query (find pressure ratings)
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH',
    '{
        "query": "What is the maximum pressure rating for V-204?",
        "columns": ["DOCUMENT_ID", "TAG_ID", "CONTENT"],
        "limit": 3
    }'
) AS SEARCH_RESULTS;

SELECT 'Cortex Search service created successfully!' AS STATUS;
