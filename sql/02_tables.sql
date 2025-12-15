-- ============================================================================
-- 02_tables.sql - Table DDL and Data Loading for SnowCore Permian Demo
-- ============================================================================
-- Creates tables and loads pre-generated synthetic data from stage
-- 
-- Runs as: AUTOGL_YIELD_OPTIMIZATION_ROLE (project role)
-- ============================================================================

USE ROLE AUTOGL_YIELD_OPTIMIZATION_ROLE;
USE DATABASE AUTOGL_YIELD_OPTIMIZATION;
USE SCHEMA AUTOGL_YIELD_OPTIMIZATION;
USE WAREHOUSE AUTOGL_YIELD_OPTIMIZATION_WH;

-- ============================================================================
-- File Format for CSV Loading
-- ============================================================================
CREATE OR REPLACE FILE FORMAT CSV_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    COMMENT = 'Standard CSV format for demo data loading';

-- ============================================================================
-- ASSET_MASTER - Equipment Registry
-- ============================================================================
-- Grain: One row per physical equipment
-- SOURCE_SYSTEM distinguishes 'SNOWCORE' (modern) vs 'TERAFIELD' (legacy acquired)

CREATE OR REPLACE TABLE ASSET_MASTER (
    ASSET_ID VARCHAR(50) NOT NULL,
    SOURCE_SYSTEM VARCHAR(20) NOT NULL,  -- Valid values: SNOWCORE, TERAFIELD (enforced at application level)
    ASSET_TYPE VARCHAR(50) NOT NULL,     -- Valid values: WELL_PAD, SEPARATOR, COMPRESSOR, TANK, PROCESSING_FACILITY, VALVE
    ASSET_SUBTYPE VARCHAR(50),
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    MAX_PRESSURE_RATING_PSI FLOAT,       -- Critical for safety validation
    MANUFACTURER VARCHAR(100),
    INSTALL_DATE DATE,
    ZONE VARCHAR(50),                    -- Valid values: DELAWARE, MIDLAND
    
    PRIMARY KEY (ASSET_ID)
)
COMMENT = 'Master registry of all physical equipment across SnowCore and TeraField networks';

-- ============================================================================
-- NETWORK_EDGES - Pipeline Connections
-- ============================================================================
-- Grain: One row per pipeline segment connecting two assets

CREATE OR REPLACE TABLE NETWORK_EDGES (
    SEGMENT_ID VARCHAR(50) NOT NULL,
    SOURCE_ASSET_ID VARCHAR(50) NOT NULL,
    TARGET_ASSET_ID VARCHAR(50) NOT NULL,
    LINE_DIAMETER_INCHES FLOAT,
    MAX_PRESSURE_RATING_PSI FLOAT,       -- Pipeline pressure limit
    STATUS VARCHAR(20),                   -- Valid values: ACTIVE, PLANNED, INACTIVE
    LENGTH_MILES FLOAT,
    
    PRIMARY KEY (SEGMENT_ID),
    FOREIGN KEY (SOURCE_ASSET_ID) REFERENCES ASSET_MASTER(ASSET_ID),
    FOREIGN KEY (TARGET_ASSET_ID) REFERENCES ASSET_MASTER(ASSET_ID)
)
COMMENT = 'Physical pipeline segments connecting assets in the gathering network';

-- ============================================================================
-- SCADA_TELEMETRY - High-Frequency Sensor Data
-- ============================================================================
-- Grain: One row per asset per timestamp (1-minute intervals)
-- Contains time-series readings from SCADA/Historian systems

CREATE OR REPLACE TABLE SCADA_TELEMETRY (
    ASSET_ID VARCHAR(50) NOT NULL,
    TIMESTAMP TIMESTAMP_NTZ NOT NULL,
    FLOW_RATE_BOPD FLOAT,                -- Barrels of Oil Per Day equivalent
    GAS_FLOW_MCFD FLOAT,                 -- Gas flow in MCF (thousand cubic feet) per day
    PRESSURE_PSI FLOAT,                  -- Current pressure reading
    TEMPERATURE_F FLOAT,                 -- Temperature in Fahrenheit
    SOURCE_SYSTEM VARCHAR(20),           -- Original data source
    
    FOREIGN KEY (ASSET_ID) REFERENCES ASSET_MASTER(ASSET_ID)
)
CLUSTER BY (ASSET_ID, TIMESTAMP)
COMMENT = 'High-frequency sensor telemetry from SCADA systems (1-minute intervals)';

-- ============================================================================
-- GRAPH_PREDICTIONS - ML Model Outputs
-- ============================================================================
-- Stores predictions from the AutoGL graph neural network model
-- Used for link prediction and anomaly scoring

CREATE OR REPLACE TABLE GRAPH_PREDICTIONS (
    PREDICTION_ID NUMBER AUTOINCREMENT,
    PREDICTION_TYPE VARCHAR(50) NOT NULL,  -- Valid values: NODE_ANOMALY, LINK_PREDICTION
    ENTITY_ID VARCHAR(50) NOT NULL,        -- Asset ID for node predictions, Source for link predictions
    RELATED_ENTITY_ID VARCHAR(50),         -- Target asset for link predictions
    SCORE FLOAT NOT NULL,                  -- Anomaly score or link probability (0-1)
    CONFIDENCE FLOAT,                      -- Model confidence (0-1)
    EXPLANATION VARCHAR(500),              -- Human-readable explanation
    PREDICTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    PRIMARY KEY (PREDICTION_ID)
)
COMMENT = 'AutoGL model predictions for pressure anomalies and hidden network connections';

-- ============================================================================
-- SCADA_AGGREGATES - Pre-computed Aggregations for Cortex Analyst
-- ============================================================================
-- Daily aggregations for efficient querying by Cortex Analyst

CREATE OR REPLACE TABLE SCADA_AGGREGATES (
    ASSET_ID VARCHAR(50) NOT NULL,
    RECORD_DATE DATE NOT NULL,
    SOURCE_SYSTEM VARCHAR(20),
    ZONE VARCHAR(50),
    ASSET_TYPE VARCHAR(50),
    
    -- Flow metrics
    AVG_FLOW_RATE_BOPD FLOAT,
    MAX_FLOW_RATE_BOPD FLOAT,
    MIN_FLOW_RATE_BOPD FLOAT,
    TOTAL_PRODUCTION_BBL FLOAT,           -- Barrels produced that day
    
    -- Gas metrics
    AVG_GAS_FLOW_MCFD FLOAT,              -- Average gas flow in MCF per day
    TOTAL_GAS_MCF FLOAT,                  -- Total gas produced that day (MCF)
    GAS_OIL_RATIO FLOAT,                  -- GOR = Gas MCF / Oil BBL * 1000 (SCF/BBL)
    
    -- Pressure metrics
    AVG_PRESSURE_PSI FLOAT,
    MAX_PRESSURE_PSI FLOAT,
    MIN_PRESSURE_PSI FLOAT,
    PRESSURE_VARIANCE FLOAT,
    
    -- Temperature metrics
    AVG_TEMPERATURE_F FLOAT,
    MAX_TEMPERATURE_F FLOAT,
    
    -- Operational metrics
    READING_COUNT INTEGER,                 -- Number of readings (used for uptime calculation)
    DOWNTIME_HOURS FLOAT,                  -- Estimated downtime based on missing readings
    
    PRIMARY KEY (ASSET_ID, RECORD_DATE)
)
COMMENT = 'Daily aggregated SCADA metrics for Cortex Analyst queries';

-- ============================================================================
-- Load Data from Stage
-- ============================================================================

-- Load Asset Master
COPY INTO ASSET_MASTER
FROM @DATA_STAGE/asset_master.csv
FILE_FORMAT = CSV_FORMAT
ON_ERROR = 'CONTINUE';

-- Load Network Edges
COPY INTO NETWORK_EDGES
FROM @DATA_STAGE/network_edges.csv
FILE_FORMAT = CSV_FORMAT
ON_ERROR = 'CONTINUE';

-- Load SCADA Telemetry
COPY INTO SCADA_TELEMETRY
FROM @DATA_STAGE/scada_telemetry.csv
FILE_FORMAT = CSV_FORMAT
ON_ERROR = 'CONTINUE';

-- Load Graph Predictions
COPY INTO GRAPH_PREDICTIONS (
    PREDICTION_TYPE, ENTITY_ID, RELATED_ENTITY_ID, 
    SCORE, CONFIDENCE, EXPLANATION, PREDICTION_TIMESTAMP
)
FROM @DATA_STAGE/graph_predictions.csv
FILE_FORMAT = CSV_FORMAT
ON_ERROR = 'CONTINUE';

-- ============================================================================
-- Populate Aggregates Table
-- ============================================================================

INSERT INTO SCADA_AGGREGATES
SELECT 
    t.ASSET_ID,
    DATE(t.TIMESTAMP) AS RECORD_DATE,
    t.SOURCE_SYSTEM,
    a.ZONE,
    a.ASSET_TYPE,
    
    -- Flow metrics
    AVG(t.FLOW_RATE_BOPD) AS AVG_FLOW_RATE_BOPD,
    MAX(t.FLOW_RATE_BOPD) AS MAX_FLOW_RATE_BOPD,
    MIN(t.FLOW_RATE_BOPD) AS MIN_FLOW_RATE_BOPD,
    SUM(t.FLOW_RATE_BOPD) / NULLIF(COUNT(*), 0) AS TOTAL_PRODUCTION_BBL,  -- Use actual reading count, not hardcoded 1440 (TeraField has gaps)
    
    -- Gas metrics
    AVG(t.GAS_FLOW_MCFD) AS AVG_GAS_FLOW_MCFD,
    SUM(t.GAS_FLOW_MCFD) / NULLIF(COUNT(*), 0) AS TOTAL_GAS_MCF,
    -- GOR = (Gas MCF / Oil BBL) * 1000 to get SCF/BBL
    CASE 
        WHEN AVG(t.FLOW_RATE_BOPD) > 0 THEN (AVG(t.GAS_FLOW_MCFD) / AVG(t.FLOW_RATE_BOPD)) * 1000
        ELSE NULL 
    END AS GAS_OIL_RATIO,
    
    -- Pressure metrics
    AVG(t.PRESSURE_PSI) AS AVG_PRESSURE_PSI,
    MAX(t.PRESSURE_PSI) AS MAX_PRESSURE_PSI,
    MIN(t.PRESSURE_PSI) AS MIN_PRESSURE_PSI,
    VARIANCE(t.PRESSURE_PSI) AS PRESSURE_VARIANCE,
    
    -- Temperature metrics
    AVG(t.TEMPERATURE_F) AS AVG_TEMPERATURE_F,
    MAX(t.TEMPERATURE_F) AS MAX_TEMPERATURE_F,
    
    -- Operational metrics
    COUNT(*) AS READING_COUNT,
    GREATEST(0, (1440 - COUNT(*)) / 60.0) AS DOWNTIME_HOURS  -- 1440 minutes expected per day
    
FROM SCADA_TELEMETRY t
JOIN ASSET_MASTER a ON t.ASSET_ID = a.ASSET_ID
GROUP BY t.ASSET_ID, DATE(t.TIMESTAMP), t.SOURCE_SYSTEM, a.ZONE, a.ASSET_TYPE;

-- ============================================================================
-- Verify Data Loading
-- ============================================================================

SELECT 'ASSET_MASTER' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM ASSET_MASTER
UNION ALL
SELECT 'NETWORK_EDGES', COUNT(*) FROM NETWORK_EDGES
UNION ALL
SELECT 'SCADA_TELEMETRY', COUNT(*) FROM SCADA_TELEMETRY
UNION ALL
SELECT 'GRAPH_PREDICTIONS', COUNT(*) FROM GRAPH_PREDICTIONS
UNION ALL
SELECT 'SCADA_AGGREGATES', COUNT(*) FROM SCADA_AGGREGATES;

-- Show sample high-risk predictions
SELECT * FROM GRAPH_PREDICTIONS 
WHERE PREDICTION_TYPE = 'NODE_ANOMALY' 
ORDER BY SCORE DESC 
LIMIT 5;

SELECT 'Table creation and data loading complete!' AS STATUS;
