-- ============================================================================
-- 04_semantic_view.sql - Deploy Cortex Analyst Semantic View
-- ============================================================================
-- Creates semantic view from YAML definition for natural language SQL queries
-- ============================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE AUTOGL_YIELD_OPTIMIZATION;
USE SCHEMA PUBLIC;
USE WAREHOUSE AUTOGL_WH;

-- ============================================================================
-- Deploy Semantic View from YAML
-- ============================================================================
-- The YAML file is uploaded to stage and deployed using SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML

CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  'AUTOGL_YIELD_OPTIMIZATION.PUBLIC',
$$
name: PERMIAN_ANALYTICS_VIEW
description: >
  Semantic view for analyzing SnowCore and TeraField asset performance,
  production metrics, and operational KPIs across the Permian Basin gathering network.
  Supports natural language queries about production, pressure, downtime, and asset comparisons.

tables:
  - name: SCADA_AGGREGATES
    description: Daily aggregated SCADA metrics by asset
    base_table:
      database: AUTOGL_YIELD_OPTIMIZATION
      schema: PUBLIC
      table: SCADA_AGGREGATES
    
    dimensions:
      - name: asset_id
        description: Unique identifier for the physical asset
        expr: ASSET_ID
        data_type: VARCHAR
        
      - name: record_date
        description: Date of the aggregated readings
        expr: RECORD_DATE
        data_type: DATE
        
      - name: source_system
        description: Origin system - SNOWCORE (modern) or TERAFIELD (legacy acquired)
        expr: SOURCE_SYSTEM
        data_type: VARCHAR
        synonyms:
          - acquisition cohort
          - data source
          - origin
          
      - name: zone
        description: Geographic zone - DELAWARE or MIDLAND basin
        expr: ZONE
        data_type: VARCHAR
        synonyms:
          - basin
          - area
          - region
          
      - name: asset_type
        description: Type of equipment (WELL_PAD, SEPARATOR, COMPRESSOR, etc.)
        expr: ASSET_TYPE
        data_type: VARCHAR
        synonyms:
          - equipment type
          - facility type

    time_dimensions:
      - name: date
        description: Date for time-based analysis
        expr: RECORD_DATE
        data_type: DATE

    measures:
      - name: total_production_bbl
        description: Total oil production in barrels
        expr: SUM(TOTAL_PRODUCTION_BBL)
        data_type: NUMBER
        synonyms:
          - oil production
          - barrels produced
          - output
          
      - name: avg_flow_rate_bopd
        description: Average flow rate in barrels of oil per day
        expr: AVG(AVG_FLOW_RATE_BOPD)
        data_type: NUMBER
        synonyms:
          - flow rate
          - production rate
          - BOPD
          
      - name: max_pressure_psi
        description: Maximum pressure reading in PSI
        expr: MAX(MAX_PRESSURE_PSI)
        data_type: NUMBER
        synonyms:
          - peak pressure
          - highest pressure
          
      - name: avg_pressure_psi
        description: Average pressure reading in PSI
        expr: AVG(AVG_PRESSURE_PSI)
        data_type: NUMBER
        synonyms:
          - mean pressure
          - pressure
          
      - name: pressure_variance
        description: Variance in pressure readings (indicator of stability)
        expr: AVG(PRESSURE_VARIANCE)
        data_type: NUMBER
        synonyms:
          - pressure fluctuation
          - pressure stability
          
      - name: downtime_hours
        description: Estimated hours of downtime based on missing readings
        expr: SUM(DOWNTIME_HOURS)
        data_type: NUMBER
        synonyms:
          - offline hours
          - outage time
          - unavailability
          
      - name: avg_temperature_f
        description: Average temperature in Fahrenheit
        expr: AVG(AVG_TEMPERATURE_F)
        data_type: NUMBER
        synonyms:
          - temperature
          - temp
          
      - name: reading_count
        description: Number of sensor readings (indicator of data quality)
        expr: SUM(READING_COUNT)
        data_type: NUMBER
        
      - name: asset_count
        description: Count of distinct assets
        expr: COUNT(DISTINCT ASSET_ID)
        data_type: NUMBER

  - name: ASSET_MASTER
    description: Master registry of all physical equipment
    base_table:
      database: AUTOGL_YIELD_OPTIMIZATION
      schema: PUBLIC
      table: ASSET_MASTER
    
    dimensions:
      - name: asset_id
        description: Unique identifier for the physical asset
        expr: ASSET_ID
        data_type: VARCHAR
        
      - name: source_system
        description: Origin system - SNOWCORE or TERAFIELD
        expr: SOURCE_SYSTEM
        data_type: VARCHAR
        
      - name: asset_type
        description: Type of equipment
        expr: ASSET_TYPE
        data_type: VARCHAR
        
      - name: asset_subtype
        description: Subtype of equipment
        expr: ASSET_SUBTYPE
        data_type: VARCHAR
        
      - name: manufacturer
        description: Equipment manufacturer
        expr: MANUFACTURER
        data_type: VARCHAR
        synonyms:
          - vendor
          - make
          
      - name: zone
        description: Geographic zone
        expr: ZONE
        data_type: VARCHAR

    measures:
      - name: max_pressure_rating_psi
        description: Maximum allowable working pressure for the asset
        expr: MAX(MAX_PRESSURE_RATING_PSI)
        data_type: NUMBER
        synonyms:
          - MAWP
          - design pressure
          - pressure limit
          - rated pressure
          
      - name: asset_count
        description: Count of assets
        expr: COUNT(*)
        data_type: NUMBER

  - name: GRAPH_PREDICTIONS
    description: ML model predictions for anomalies and link discovery
    base_table:
      database: AUTOGL_YIELD_OPTIMIZATION
      schema: PUBLIC
      table: GRAPH_PREDICTIONS
    
    dimensions:
      - name: prediction_type
        description: Type of prediction - NODE_ANOMALY or LINK_PREDICTION
        expr: PREDICTION_TYPE
        data_type: VARCHAR
        
      - name: entity_id
        description: Asset ID being predicted
        expr: ENTITY_ID
        data_type: VARCHAR
        
      - name: related_entity_id
        description: Related asset (for link predictions)
        expr: RELATED_ENTITY_ID
        data_type: VARCHAR

    measures:
      - name: anomaly_score
        description: Risk score from ML model (0-1, higher = more risk)
        expr: AVG(SCORE)
        data_type: NUMBER
        synonyms:
          - risk score
          - risk level
          
      - name: max_anomaly_score
        description: Maximum anomaly score
        expr: MAX(SCORE)
        data_type: NUMBER
        
      - name: confidence
        description: Model confidence in the prediction
        expr: AVG(CONFIDENCE)
        data_type: NUMBER
        
      - name: prediction_count
        description: Number of predictions
        expr: COUNT(*)
        data_type: NUMBER
$$
);

-- ============================================================================
-- Verify Semantic View
-- ============================================================================

SHOW VIEWS LIKE 'PERMIAN_ANALYTICS_VIEW' IN SCHEMA AUTOGL_YIELD_OPTIMIZATION.PUBLIC;

-- Test with Cortex Analyst
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-large2',
    'Based on the PERMIAN_ANALYTICS_VIEW semantic model, generate a SQL query to: Compare downtime between SNOWCORE and TERAFIELD assets. Return only the SQL, no explanation.'
) AS GENERATED_SQL;

SELECT 'Semantic view deployed successfully!' AS STATUS;

