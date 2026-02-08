from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import execute_query, execute_scalar

router = APIRouter()

class SimulationRequest(BaseModel):
    source_asset_id: str
    target_asset_ids: List[str]
    pressure_change_psi: float = -50.0
    scenario_name: Optional[str] = "pressure_cascade"

class SimulationResult(BaseModel):
    scenario_id: str
    source_asset: dict
    affected_assets: List[dict]
    pressure_cascade: List[dict]
    recommended_actions: List[str]
    estimated_impact_mcfd: float

@router.post("/pressure-cascade")
async def simulate_pressure_cascade(request: SimulationRequest) -> SimulationResult:
    source_sql = """
    SELECT asset_id, asset_id as asset_name, asset_type, latitude, longitude, 
           MAX_PRESSURE_RATING_PSI as design_pressure_psi, source_system
    FROM ASSET_MASTER
    WHERE asset_id = %s
    """
    source_results = execute_query(source_sql, (request.source_asset_id,))
    if not source_results:
        raise HTTPException(status_code=404, detail="Source asset not found")
    source_asset = source_results[0]
    
    target_ids = ",".join([f"'{t}'" for t in request.target_asset_ids])
    targets_sql = f"""
    SELECT 
        am.asset_id, 
        am.asset_id as asset_name, 
        am.asset_type, 
        am.latitude, 
        am.longitude,
        am.MAX_PRESSURE_RATING_PSI as design_pressure_psi,
        am.source_system,
        COALESCE(sa.AVG_PRESSURE_PSI, am.MAX_PRESSURE_RATING_PSI * 0.8) as current_pressure,
        COALESCE(sa.AVG_FLOW_RATE_BOPD, 0) as flow_rate
    FROM ASSET_MASTER am
    LEFT JOIN (
        SELECT asset_id, AVG(AVG_PRESSURE_PSI) as AVG_PRESSURE_PSI, AVG(AVG_FLOW_RATE_BOPD) as AVG_FLOW_RATE_BOPD
        FROM SCADA_AGGREGATES
        WHERE record_date >= CURRENT_DATE - 7
        GROUP BY asset_id
    ) sa ON am.asset_id = sa.asset_id
    WHERE am.asset_id IN ({target_ids})
    """
    affected_assets = execute_query(targets_sql)
    
    pressure_cascade = []
    time_offset = 0
    cumulative_change = request.pressure_change_psi
    
    for i, asset in enumerate(affected_assets):
        time_offset += 15 + (i * 5)
        propagation_factor = 0.85 ** i
        delta = cumulative_change * propagation_factor
        current = asset.get('current_pressure') or 800
        design = asset.get('design_pressure_psi') or 1200
        new_pressure = max(0, current + delta)
        
        risk_level = 'low'
        if new_pressure < design * 0.3:
            risk_level = 'critical'
        elif new_pressure < design * 0.5:
            risk_level = 'high'
        elif new_pressure < design * 0.7:
            risk_level = 'medium'
        
        pressure_cascade.append({
            'asset_id': asset['asset_id'],
            'asset_name': asset['asset_name'],
            'time_offset_min': time_offset,
            'pressure_delta': round(delta, 1),
            'new_pressure': round(new_pressure, 1),
            'original_pressure': round(current, 1),
            'risk_level': risk_level,
            'latitude': asset['latitude'],
            'longitude': asset['longitude']
        })
    
    high_risk_count = sum(1 for p in pressure_cascade if p['risk_level'] in ['high', 'critical'])
    total_flow = sum(a.get('flow_rate') or 0 for a in affected_assets)
    
    recommended_actions = []
    if high_risk_count > 0:
        recommended_actions.append(f"Alert: {high_risk_count} assets entering high-risk pressure state")
    if any(p['risk_level'] == 'critical' for p in pressure_cascade):
        recommended_actions.append("CRITICAL: Initiate emergency pressure relief protocol")
        recommended_actions.append("Notify field operations for manual valve inspection")
    recommended_actions.append(f"Monitor downstream pressure for {time_offset + 30} minutes")
    recommended_actions.append("Consider rerouting flow through alternate pipelines if available")
    
    return SimulationResult(
        scenario_id=f"sim_{request.source_asset_id}_{len(request.target_asset_ids)}",
        source_asset=source_asset,
        affected_assets=affected_assets,
        pressure_cascade=pressure_cascade,
        recommended_actions=recommended_actions,
        estimated_impact_mcfd=round(total_flow * 0.15, 1)
    )

@router.get("/routing-options")
async def get_routing_options(source_asset_id: str, target_asset_id: str):
    sql = """
    WITH RECURSIVE paths AS (
        SELECT 
            source_asset_id as start_node,
            target_asset_id as current_node,
            ARRAY_CONSTRUCT(source_asset_id, target_asset_id) as path,
            1 as depth
        FROM NETWORK_EDGES
        WHERE source_asset_id = %s
        
        UNION ALL
        
        SELECT 
            p.start_node,
            e.target_asset_id,
            ARRAY_APPEND(p.path, e.target_asset_id),
            p.depth + 1
        FROM paths p
        JOIN NETWORK_EDGES e ON p.current_node = e.source_asset_id
        WHERE p.depth < 5
          AND NOT ARRAY_CONTAINS(e.target_asset_id::VARIANT, p.path)
    )
    SELECT path, depth
    FROM paths
    WHERE current_node = %s
    ORDER BY depth
    LIMIT 5
    """
    return execute_query(sql, (source_asset_id, target_asset_id))
