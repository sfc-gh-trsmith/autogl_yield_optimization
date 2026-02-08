from fastapi import APIRouter, Query
from typing import Optional
from database import execute_query

router = APIRouter()

@router.get("")
async def list_assets(
    source_system: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    min_risk: Optional[float] = Query(None),
    limit: int = Query(500, le=2000)
):
    conditions = []
    if source_system:
        conditions.append(f"source_system = '{source_system}'")
    if asset_type:
        conditions.append(f"asset_type = '{asset_type}'")
    if zone:
        conditions.append(f"zone = '{zone}'")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
    SELECT 
        am.asset_id,
        am.asset_id as asset_name,
        am.asset_type,
        am.source_system,
        am.latitude,
        am.longitude,
        am.zone as basin,
        am.zone as field,
        am.max_pressure_rating_psi as design_pressure,
        COALESCE(gp.risk_score, 0) as risk_score,
        COALESCE(gp.anomaly_score, 0) as anomaly_score,
        sa.avg_pressure_psi as current_pressure,
        sa.avg_flow_rate_bopd as throughput
    FROM ASSET_MASTER am
    LEFT JOIN (
        SELECT entity_id, MAX(score) as risk_score, MAX(confidence) as anomaly_score
        FROM GRAPH_PREDICTIONS
        WHERE prediction_type = 'anomaly_detection'
        GROUP BY entity_id
    ) gp ON am.asset_id = gp.entity_id
    LEFT JOIN (
        SELECT asset_id, avg_pressure_psi, avg_flow_rate_bopd
        FROM SCADA_AGGREGATES
        WHERE record_date = (SELECT MAX(record_date) FROM SCADA_AGGREGATES)
    ) sa ON am.asset_id = sa.asset_id
    WHERE {where_clause}
    ORDER BY risk_score DESC NULLS LAST
    LIMIT {limit}
    """
    return execute_query(sql)

@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    sql = """
    SELECT 
        am.asset_id,
        am.asset_id as asset_name,
        am.asset_type,
        am.source_system,
        am.latitude,
        am.longitude,
        am.zone as basin,
        am.zone as field,
        am.max_pressure_rating_psi as design_pressure,
        am.manufacturer,
        am.install_date,
        COALESCE(gp.risk_score, 0) as risk_score,
        COALESCE(gp.anomaly_score, 0) as anomaly_score
    FROM ASSET_MASTER am
    LEFT JOIN (
        SELECT entity_id, MAX(score) as risk_score, MAX(confidence) as anomaly_score
        FROM GRAPH_PREDICTIONS
        WHERE prediction_type = 'anomaly_detection'
        GROUP BY entity_id
    ) gp ON am.asset_id = gp.entity_id
    WHERE am.asset_id = %s
    """
    results = execute_query(sql, (asset_id,))
    return results[0] if results else None

@router.get("/edges/all")
async def get_network_edges(include_predictions: bool = Query(True)):
    base_sql = """
    SELECT 
        SEGMENT_ID as edge_id,
        SOURCE_ASSET_ID as source_asset_id,
        TARGET_ASSET_ID as target_asset_id,
        'pipeline' as edge_type,
        CASE 
            WHEN SOURCE_ASSET_ID LIKE 'SC-%' THEN 'snowcore'
            ELSE 'terafield'
        END as source_system,
        1.0 as confidence,
        'existing' as discovery_method
    FROM NETWORK_EDGES
    WHERE STATUS = 'ACTIVE'
    """
    
    if include_predictions:
        base_sql += """
        UNION ALL
        SELECT 
            'pred_' || ROW_NUMBER() OVER (ORDER BY confidence DESC) as edge_id,
            entity_id as source_asset_id,
            related_entity_id as target_asset_id,
            'predicted' as edge_type,
            'autogl' as source_system,
            confidence,
            'autogl_gnn' as discovery_method
        FROM GRAPH_PREDICTIONS
        WHERE UPPER(prediction_type) = 'LINK_PREDICTION' AND confidence > 0.5
        """
    
    return execute_query(base_sql)
