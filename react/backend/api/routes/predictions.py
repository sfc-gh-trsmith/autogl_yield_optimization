from fastapi import APIRouter, Query
from typing import Optional
from database import execute_query, get_connection

router = APIRouter()

@router.get("")
async def list_predictions(
    prediction_type: Optional[str] = Query(None),
    min_confidence: float = Query(0.5),
    limit: int = Query(100, le=500)
):
    type_filter = f"AND prediction_type = '{prediction_type}'" if prediction_type else ""
    
    sql = f"""
    SELECT 
        gp.entity_id as source_node,
        gp.related_entity_id as target_node,
        gp.prediction_type,
        gp.confidence,
        gp.score as risk_score,
        gp.explanation,
        src.asset_id as source_asset_name,
        src.asset_type as source_asset_type,
        src.latitude as source_lat,
        src.longitude as source_lon,
        tgt.asset_id as target_asset_name,
        tgt.asset_type as target_asset_type,
        tgt.latitude as target_lat,
        tgt.longitude as target_lon
    FROM GRAPH_PREDICTIONS gp
    LEFT JOIN ASSET_MASTER src ON gp.entity_id = src.asset_id
    LEFT JOIN ASSET_MASTER tgt ON gp.related_entity_id = tgt.asset_id
    WHERE gp.confidence >= {min_confidence}
    {type_filter}
    ORDER BY gp.confidence DESC
    LIMIT {limit}
    """
    return execute_query(sql)

@router.get("/link-discoveries")
async def get_link_discoveries(min_confidence: float = Query(0.5)):
    sql = f"""
    SELECT 
        gp.entity_id as source_node,
        gp.related_entity_id as target_node,
        gp.confidence,
        gp.score as risk_score,
        gp.explanation,
        src.asset_id as source_name,
        src.source_system as source_origin,
        src.latitude as source_lat,
        src.longitude as source_lon,
        tgt.asset_id as target_name,
        tgt.source_system as target_origin,
        tgt.latitude as target_lat,
        tgt.longitude as target_lon
    FROM GRAPH_PREDICTIONS gp
    JOIN ASSET_MASTER src ON gp.entity_id = src.asset_id
    JOIN ASSET_MASTER tgt ON gp.related_entity_id = tgt.asset_id
    WHERE UPPER(gp.prediction_type) = 'LINK_PREDICTION'
      AND gp.confidence >= {min_confidence}
    ORDER BY gp.confidence DESC
    """
    return execute_query(sql)

@router.get("/anomalies")
async def get_anomalies(min_risk: float = Query(0.6)):
    sql = f"""
    SELECT 
        gp.entity_id as asset_id,
        am.asset_id as asset_name,
        am.asset_type,
        am.source_system,
        am.latitude,
        am.longitude,
        gp.score as risk_score,
        gp.confidence as anomaly_score,
        gp.explanation
    FROM GRAPH_PREDICTIONS gp
    JOIN ASSET_MASTER am ON gp.entity_id = am.asset_id
    WHERE UPPER(gp.prediction_type) = 'NODE_ANOMALY'
      AND gp.score >= {min_risk}
    ORDER BY gp.score DESC
    """
    return execute_query(sql)

@router.get("/autogl-interpretation")
async def get_autogl_interpretation():
    link_sql = """
    SELECT 
        gp.entity_id as source, 
        gp.related_entity_id as target,
        gp.confidence, 
        gp.explanation,
        src.source_system as source_origin,
        tgt.source_system as target_origin
    FROM GRAPH_PREDICTIONS gp
    JOIN ASSET_MASTER src ON gp.entity_id = src.asset_id
    JOIN ASSET_MASTER tgt ON gp.related_entity_id = tgt.asset_id
    WHERE UPPER(gp.prediction_type) = 'LINK_PREDICTION'
    ORDER BY gp.confidence DESC
    LIMIT 10
    """
    links = execute_query(link_sql)
    
    cross_network = [l for l in links if l.get('source_origin') != l.get('target_origin')]
    same_network = [l for l in links if l.get('source_origin') == l.get('target_origin')]
    
    context = f"AutoGL discovered {len(links)} network connections:\n"
    context += f"- {len(cross_network)} cross-network (SnowCore <-> TeraField)\n"
    context += f"- {len(same_network)} same-network redundancies\n\n"
    
    for link in links[:5]:
        conf = link.get('confidence', 0)
        context += f"- {link.get('source')} -> {link.get('target')} ({conf:.0%} confidence)\n"
    
    prompt = f"""Provide a 2-3 sentence executive summary of these AutoGL graph neural network discoveries for pipeline network integration:

{context}

Focus on: business value, operational efficiency gains, and risk reduction potential."""

    escaped_prompt = prompt.replace("'", "''")
    sql = f"""SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{escaped_prompt}') as interpretation"""
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        interpretation = row[0] if row else "Analysis unavailable"
    except Exception as e:
        interpretation = f"Unable to generate interpretation: {str(e)}"
    
    return {
        "total_discoveries": len(links),
        "cross_network_count": len(cross_network),
        "same_network_count": len(same_network),
        "interpretation": interpretation
    }
