from fastapi import APIRouter, Query
from database import execute_query

router = APIRouter()

@router.get("")
async def get_telemetry(
    asset_id: str = Query(...),
    hours: int = Query(24, le=168)
):
    sql = f"""
    SELECT 
        asset_id,
        record_date as timestamp,
        avg_pressure_psi as pressure_psi,
        avg_flow_rate_bopd as flow_rate_mcfd,
        avg_temperature_f as temperature_f,
        gas_oil_ratio
    FROM SCADA_AGGREGATES
    WHERE asset_id = %s
    ORDER BY record_date DESC
    LIMIT 30
    """
    return execute_query(sql, (asset_id,))

@router.get("/aggregates")
async def get_aggregates(
    asset_id: str = Query(None),
    period: str = Query("daily")
):
    asset_filter = f"AND asset_id = '{asset_id}'" if asset_id else ""
    
    sql = f"""
    SELECT 
        asset_id,
        'daily' as agg_period,
        record_date as agg_date,
        avg_pressure_psi as avg_pressure,
        max_pressure_psi as max_pressure,
        min_pressure_psi as min_pressure,
        avg_flow_rate_bopd as avg_flow_rate,
        total_production_bbl as total_volume,
        reading_count
    FROM SCADA_AGGREGATES
    WHERE 1=1 {asset_filter}
    ORDER BY record_date DESC
    LIMIT 30
    """
    return execute_query(sql)

@router.get("/kpis")
async def get_kpis():
    sql = """
    SELECT 
        COUNT(DISTINCT asset_id) as total_assets,
        SUM(avg_flow_rate_bopd) as total_throughput,
        AVG(avg_pressure_psi) as avg_network_pressure,
        COUNT(CASE WHEN max_pressure_psi > 1200 THEN 1 END) as high_pressure_events
    FROM SCADA_AGGREGATES
    WHERE record_date = (SELECT MAX(record_date) FROM SCADA_AGGREGATES)
    """
    results = execute_query(sql)
    return results[0] if results else {}
