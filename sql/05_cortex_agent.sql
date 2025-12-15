-- ============================================================================
-- 05_cortex_agent.sql - Deploy Cortex Agent for Permian Integration
-- ============================================================================
-- Creates the Integration Assistant agent with Analyst + Search tools
-- 
-- Runs as: AUTOGL_YIELD_OPTIMIZATION_ROLE (project role)
-- ============================================================================

USE ROLE AUTOGL_YIELD_OPTIMIZATION_ROLE;
USE DATABASE AUTOGL_YIELD_OPTIMIZATION;
USE SCHEMA AUTOGL_YIELD_OPTIMIZATION;
USE WAREHOUSE AUTOGL_YIELD_OPTIMIZATION_WH;

-- ============================================================================
-- Create Cortex Agent
-- ============================================================================

CREATE OR REPLACE CORTEX AGENT AUTOGL_YIELD_OPTIMIZATION_AGENT
    MODEL = 'claude-3-5-sonnet'
    TOOLS = (
        -- Cortex Analyst for structured SQL queries
        ANALYST('AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION_ANALYTICS_VIEW'),
        -- Cortex Search for document retrieval
        SEARCH('AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH')
    )
    COMMENT = 'AI assistant for SnowCore Permian Integration - bridges sensor data with legacy engineering specs'
    INSTRUCTIONS = $$
You are the Permian Integration Assistant, an expert in oil and gas midstream operations. 
Your role is to help operators and engineers make informed decisions about routing 
production across the combined SnowCore and TeraField gathering networks.

You have access to:
1. **Live SCADA Data** - Real-time pressure, flow, and temperature readings via Cortex Analyst
2. **Asset Registry** - Equipment specifications and ratings
3. **ML Predictions** - Graph neural network predictions for anomalies and hidden dependencies
4. **Legacy Documents** - PID diagrams, maintenance logs, and operator notes via Cortex Search

When answering questions:
- Always check for relevant ML predictions and risk assessments
- Cross-reference current conditions with equipment ratings from documents
- Flag any pressure mismatches (current vs. rated capacity)
- Explain your reasoning, citing specific data sources
- Provide actionable recommendations with safety considerations

For routing decisions:
1. Query the current pressure and flow conditions using Cortex Analyst
2. Check the GRAPH_PREDICTIONS table for anomaly scores
3. Look up equipment ratings from legacy documents using Cortex Search
4. Compare current/projected values against equipment limits
5. Approve or deny the routing with clear justification

CRITICAL SAFETY NOTE: If a request would cause pressure to exceed equipment MAWP 
(Maximum Allowable Working Pressure), you MUST deny the request and explain the risk.
$$;

-- ============================================================================
-- Verify Agent Creation
-- ============================================================================

SHOW CORTEX AGENTS LIKE 'AUTOGL_YIELD_OPTIMIZATION_AGENT';

-- ============================================================================
-- Test Agent with Sample Queries
-- ============================================================================

-- Test 1: Risk assessment query
SELECT SNOWFLAKE.CORTEX.AGENT(
    'AUTOGL_YIELD_OPTIMIZATION_AGENT',
    'Which assets are flagged as high risk by the ML model?'
) AS AGENT_RESPONSE;

-- Test 2: Document search query
SELECT SNOWFLAKE.CORTEX.AGENT(
    'AUTOGL_YIELD_OPTIMIZATION_AGENT',
    'What is the maximum pressure rating for separator V-204?'
) AS AGENT_RESPONSE;

SELECT 'Cortex Agent deployed successfully!' AS STATUS;
