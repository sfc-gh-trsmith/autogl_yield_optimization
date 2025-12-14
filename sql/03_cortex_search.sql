-- ============================================================================
-- 03_cortex_search.sql - Cortex Search Service for Unstructured Documents
-- ============================================================================
-- Creates search service for P&ID documents, maintenance logs, and operator notes
-- ============================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE AUTOGL_YIELD_OPTIMIZATION;
USE SCHEMA PUBLIC;
USE WAREHOUSE AUTOGL_WH;

-- ============================================================================
-- Documents Table for Cortex Search
-- ============================================================================
-- Stores document content and metadata for RAG retrieval

CREATE OR REPLACE TABLE LEGACY_DOCUMENTS (
    DOCUMENT_ID VARCHAR(100) NOT NULL,
    DOCUMENT_TYPE VARCHAR(50) NOT NULL,    -- P&ID, SHIFT_REPORT, MAINTENANCE_LOG, VENDOR_MANUAL
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

-- P&ID Document
INSERT INTO LEGACY_DOCUMENTS (DOCUMENT_ID, DOCUMENT_TYPE, DOCUMENT_NAME, TAG_ID, FACILITY, CONTENT, SOURCE_SYSTEM)
SELECT 
    'PID-TF-MID-001',
    'P&ID',
    'TeraField_Midland_Hub_Process_Flow.txt',
    'TF-V-204',
    'Midland Hub',
    $1,
    'TERAFIELD'
FROM @DOCS_STAGE/TeraField_Midland_Hub_Process_Flow.txt (FILE_FORMAT => (TYPE = 'CSV' FIELD_DELIMITER = NONE RECORD_DELIMITER = NONE));

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
FROM @DOCS_STAGE/Shift_Report_2023_10_12.txt (FILE_FORMAT => (TYPE = 'CSV' FIELD_DELIMITER = NONE RECORD_DELIMITER = NONE));

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
FROM @DOCS_STAGE/Maintenance_Log_V204.txt (FILE_FORMAT => (TYPE = 'CSV' FIELD_DELIMITER = NONE RECORD_DELIMITER = NONE));

-- ============================================================================
-- Cortex Search Service
-- ============================================================================
-- Creates a search service for semantic search over legacy documents

CREATE OR REPLACE CORTEX SEARCH SERVICE TERAFIELD_LEGACY_DOCS_SEARCH
    ON CONTENT
    ATTRIBUTES TAG_ID, DOCUMENT_TYPE, FACILITY
    WAREHOUSE = AUTOGL_WH
    TARGET_LAG = '1 hour'
    COMMENT = 'Semantic search over legacy TeraField P&IDs, maintenance logs, and operator notes'
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
SHOW CORTEX SEARCH SERVICES LIKE 'TERAFIELD_LEGACY_DOCS_SEARCH';

-- Test search query (find pressure ratings)
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'TERAFIELD_LEGACY_DOCS_SEARCH',
    '{
        "query": "What is the maximum pressure rating for V-204?",
        "columns": ["DOCUMENT_ID", "TAG_ID", "CONTENT"],
        "limit": 3
    }'
) AS SEARCH_RESULTS;

SELECT 'Cortex Search service created successfully!' AS STATUS;

