import os
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from database import get_connection, execute_query, DATABASE, SCHEMA

router = APIRouter()

SEMANTIC_VIEW = f"{DATABASE}.{SCHEMA}.AUTOGL_YIELD_OPTIMIZATION_ANALYTICS_VIEW"

class AgentRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    context: Optional[str] = None

def get_asset_context(asset_id: str) -> dict:
    try:
        sql = f"""
        SELECT 
            am.asset_id,
            am.asset_type,
            am.source_system,
            am.zone,
            am.latitude,
            am.longitude,
            am.max_pressure_rating_psi,
            sa.avg_pressure_psi as current_pressure,
            sa.avg_flow_rate_bopd as throughput,
            gp.score as risk_score,
            gp.explanation as risk_explanation
        FROM {DATABASE}.{SCHEMA}.ASSET_MASTER am
        LEFT JOIN (
            SELECT asset_id, avg_pressure_psi, avg_flow_rate_bopd
            FROM {DATABASE}.{SCHEMA}.SCADA_AGGREGATES
            WHERE record_date = (SELECT MAX(record_date) FROM {DATABASE}.{SCHEMA}.SCADA_AGGREGATES)
        ) sa ON am.asset_id = sa.asset_id
        LEFT JOIN (
            SELECT entity_id, score, explanation
            FROM {DATABASE}.{SCHEMA}.GRAPH_PREDICTIONS
            WHERE UPPER(prediction_type) = 'NODE_ANOMALY'
        ) gp ON am.asset_id = gp.entity_id
        WHERE am.asset_id = '{asset_id}'
        """
        results = execute_query(sql)
        if results:
            return results[0]
    except Exception:
        pass
    return {}

def search_docs(query: str) -> str:
    try:
        sql = f"""
        SELECT 
            SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                '{DATABASE}.{SCHEMA}.AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH',
                '{query.replace("'", "''")}',
                {{
                    'columns': ['DOCUMENT_NAME', 'DOCUMENT_TYPE', 'CONTENT', 'TAG_ID', 'FACILITY'],
                    'limit': 3
                }}
            ) as results
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        if row and row[0]:
            return str(row[0])[:2000]
    except Exception:
        pass
    return ""

def query_analyst_via_sql(question: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        escaped_question = question.replace("'", "''").replace("\\", "\\\\")
        
        sql = f"""
        SELECT SNOWFLAKE.CORTEX.SEMANTIC_VIEW_ANSWER(
            '{SEMANTIC_VIEW}',
            '{escaped_question}'
        ) as answer
        """
        
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        
        if row and row[0]:
            result = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            return result
    except Exception as e:
        cursor.close()
        return {"error": str(e), "fallback": True}
    
    return {"error": "No response", "fallback": True}

def get_contextual_data(question: str) -> str:
    question_lower = question.lower()
    
    data_parts = []
    
    if any(kw in question_lower for kw in ['risk', 'anomaly', 'high-risk', 'dangerous', 'concern']):
        sql = f"""
        SELECT 
            gp.entity_id as asset_id,
            am.asset_type,
            am.source_system,
            am.zone,
            gp.score as risk_score,
            gp.explanation
        FROM {DATABASE}.{SCHEMA}.GRAPH_PREDICTIONS gp
        JOIN {DATABASE}.{SCHEMA}.ASSET_MASTER am ON gp.entity_id = am.asset_id
        WHERE UPPER(gp.prediction_type) = 'NODE_ANOMALY'
        AND gp.score > 0.5
        ORDER BY gp.score DESC
        LIMIT 10
        """
        try:
            results = execute_query(sql)
            if results:
                data_parts.append("HIGH-RISK ASSETS (from AutoGL anomaly detection):")
                for r in results:
                    data_parts.append(f"  - {r['asset_id']} ({r['asset_type']}, {r['source_system']}): Risk Score {r['risk_score']:.2f} - {r['explanation']}")
        except Exception:
            pass
    
    if any(kw in question_lower for kw in ['link', 'connection', 'discover', 'network', 'cross-network']):
        sql = f"""
        SELECT 
            gp.entity_id as source,
            gp.related_entity_id as target,
            gp.confidence,
            gp.explanation
        FROM {DATABASE}.{SCHEMA}.GRAPH_PREDICTIONS gp
        WHERE UPPER(gp.prediction_type) = 'LINK_PREDICTION'
        AND gp.confidence > 0.5
        ORDER BY gp.confidence DESC
        """
        try:
            results = execute_query(sql)
            if results:
                data_parts.append("\nDISCOVERED NETWORK LINKS (from AutoGL link prediction):")
                for r in results:
                    data_parts.append(f"  - {r['source']} <-> {r['target']}: Confidence {r['confidence']:.2f}")
        except Exception:
            pass
    
    if any(kw in question_lower for kw in ['asset', 'pipeline', 'pad', 'separator', 'compressor', 'all', 'list', 'show']):
        sql = f"""
        SELECT 
            am.asset_id,
            am.asset_type,
            am.source_system,
            am.zone,
            am.max_pressure_rating_psi,
            sa.avg_pressure_psi as current_pressure,
            sa.avg_flow_rate_bopd as throughput
        FROM {DATABASE}.{SCHEMA}.ASSET_MASTER am
        LEFT JOIN (
            SELECT asset_id, avg_pressure_psi, avg_flow_rate_bopd
            FROM {DATABASE}.{SCHEMA}.SCADA_AGGREGATES
            WHERE record_date = (SELECT MAX(record_date) FROM {DATABASE}.{SCHEMA}.SCADA_AGGREGATES)
        ) sa ON am.asset_id = sa.asset_id
        ORDER BY am.source_system, am.asset_type
        LIMIT 20
        """
        try:
            results = execute_query(sql)
            if results:
                data_parts.append("\nASSET INVENTORY:")
                snowcore = [r for r in results if r.get('source_system') == 'snowcore']
                terafield = [r for r in results if r.get('source_system') == 'terafield']
                
                if snowcore:
                    data_parts.append(f"  SnowCore Assets ({len(snowcore)}):")
                    for r in snowcore[:5]:
                        pressure_info = f", Pressure: {r['current_pressure']:.0f} PSI" if r.get('current_pressure') else ""
                        data_parts.append(f"    - {r['asset_id']} ({r['asset_type']}){pressure_info}")
                
                if terafield:
                    data_parts.append(f"  TeraField Assets ({len(terafield)}):")
                    for r in terafield[:5]:
                        pressure_info = f", Pressure: {r['current_pressure']:.0f} PSI" if r.get('current_pressure') else ""
                        data_parts.append(f"    - {r['asset_id']} ({r['asset_type']}){pressure_info}")
        except Exception:
            pass
    
    if any(kw in question_lower for kw in ['pressure', 'flow', 'operational', 'scada', 'reading', 'sensor']):
        sql = f"""
        SELECT 
            sa.asset_id,
            am.asset_type,
            sa.avg_pressure_psi,
            sa.max_pressure_psi,
            sa.avg_flow_rate_bopd,
            sa.record_date
        FROM {DATABASE}.{SCHEMA}.SCADA_AGGREGATES sa
        JOIN {DATABASE}.{SCHEMA}.ASSET_MASTER am ON sa.asset_id = am.asset_id
        WHERE sa.record_date = (SELECT MAX(record_date) FROM {DATABASE}.{SCHEMA}.SCADA_AGGREGATES)
        ORDER BY sa.avg_pressure_psi DESC
        LIMIT 10
        """
        try:
            results = execute_query(sql)
            if results:
                data_parts.append("\nOPERATIONAL DATA (Latest SCADA readings):")
                for r in results:
                    data_parts.append(f"  - {r['asset_id']} ({r['asset_type']}): Pressure {r['avg_pressure_psi']:.0f} PSI, Flow {r['avg_flow_rate_bopd']:.0f} BOPD")
        except Exception:
            pass
    
    return "\n".join(data_parts) if data_parts else ""

def generate_response_with_cortex(question: str, context_data: str, asset_context: str = "") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    
    system_prompt = """You are an AI assistant for SnowCore Permian Integration, helping analyze oil & gas pipeline networks.

Context:
- Two merged companies: SnowCore (modern OSIsoft PI data) and TeraField (legacy CygNet data)
- AutoGL (Graph Neural Networks) discovers hidden connections between these networks
- GRAPH_PREDICTIONS contains ML predictions about network anomalies and link discoveries
- ASSET_MASTER contains all pipeline assets with locations and specifications
- SCADA_AGGREGATES contains sensor readings (pressure, flow rates)

Your role is to help users:
1. Understand asset conditions and risks based on the data provided
2. Explain AutoGL network discoveries
3. Provide operational insights

Be concise and data-driven. Reference specific asset IDs and metrics when available."""

    full_context = context_data
    if asset_context:
        full_context = f"Currently selected asset:\n{asset_context}\n\n{context_data}"
    
    escaped_prompt = f"{system_prompt}\n\nRelevant Data:\n{full_context}\n\nUser Question: {question}".replace("'", "''")
    
    sql = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'claude-3-5-sonnet',
        '{escaped_prompt}'
    ) as response
    """
    
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        cursor.close()
        return f"Error generating response: {str(e)}"
    
    return "I couldn't generate a response. Please try rephrasing your question."

async def stream_agent_response(message: str, thread_id: Optional[str] = None, context: Optional[str] = None) -> AsyncGenerator[str, None]:
    try:
        yield f"data: {json.dumps({'type': 'reasoning', 'text': 'Analyzing your question...'})}\n\n"
        
        asset_context = ""
        if context:
            yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': 'Asset Lookup', 'input': context})}\n\n"
            asset_data = get_asset_context(context)
            if asset_data:
                asset_context = json.dumps(asset_data, default=str)
            yield f"data: {json.dumps({'type': 'tool_end', 'tool_name': 'Asset Lookup', 'output': 'Retrieved asset details'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': 'Data Query', 'input': message[:50] + '...'})}\n\n"
        context_data = get_contextual_data(message)
        yield f"data: {json.dumps({'type': 'tool_end', 'tool_name': 'Data Query', 'output': f'Retrieved {len(context_data)} chars of context'})}\n\n"
        
        keywords = ['maintenance', 'repair', 'history', 'document', 'log', 'report', 'manual', 'procedure']
        if any(kw in message.lower() for kw in keywords):
            yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': 'Document Search', 'input': message[:30] + '...'})}\n\n"
            doc_results = search_docs(message)
            if doc_results:
                context_data += f"\n\nRELEVANT DOCUMENTATION:\n{doc_results}"
            yield f"data: {json.dumps({'type': 'tool_end', 'tool_name': 'Document Search', 'output': 'Searched documents'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'reasoning', 'text': 'Generating response...'})}\n\n"
        
        response = generate_response_with_cortex(message, context_data, asset_context)
        
        yield f"data: {json.dumps({'type': 'text_delta', 'text': response})}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_msg = str(e)
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        yield "data: [DONE]\n\n"

@router.post("/run")
async def run_agent(request: AgentRequest):
    return StreamingResponse(
        stream_agent_response(request.message, request.thread_id, request.context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/status")
async def agent_status():
    return {
        "status": "active", 
        "agent": "CORTEX_COMPLETE_WITH_DATA",
        "model": "claude-3-5-sonnet",
        "capabilities": ["Asset Analysis", "Document Search", "AutoGL Insights", "Data Query"]
    }
