#!/usr/bin/env python3
"""
generate_synthetic_data.py - Synthetic Data Generator for SnowCore Permian Demo

Generates deterministic demo data with a hidden pattern:
- SnowCore Pad 42 feeds TeraField V-204 via Pipeline-88
- V-204 has 600 PSI limit (documented in P&ID)
- Pad 42 ramps to 800 PSI, triggering "Design Mismatch" alert

Usage:
    python utils/generate_synthetic_data.py

Output:
    data/synthetic/*.csv (version controlled)
"""

import csv
import math
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"

# Time range for telemetry data
START_TIME = datetime(2024, 1, 1, 0, 0, 0)
END_TIME = datetime(2024, 1, 7, 23, 59, 0)  # 7 days of data
INTERVAL_MINUTES = 1

# Anomaly event timing (Day 5, 10:00 AM)
ANOMALY_EVENT_TIME = datetime(2024, 1, 5, 10, 0, 0)

# Geographic bounds (Permian Basin - West Texas)
LAT_MIN, LAT_MAX = 31.5, 32.5
LON_MIN, LON_MAX = -103.5, -101.5


# ============================================================================
# Asset Definitions
# ============================================================================

def generate_asset_master():
    """Generate ASSET_MASTER table data.
    
    Creates a mix of SnowCore (modern) and TeraField (legacy acquired) assets.
    """
    assets = []
    
    # SnowCore Assets (Modern - High pressure ratings)
    snowcore_assets = [
        # Pads (Well Pads)
        {"id": "SC-PAD-42", "type": "WELL_PAD", "subtype": "MULTI_WELL", "lat": 32.1, "lon": -102.8, "max_psi": 1500, "manufacturer": "Schlumberger"},
        {"id": "SC-PAD-43", "type": "WELL_PAD", "subtype": "MULTI_WELL", "lat": 32.15, "lon": -102.75, "max_psi": 1500, "manufacturer": "Schlumberger"},
        {"id": "SC-PAD-44", "type": "WELL_PAD", "subtype": "SINGLE_WELL", "lat": 32.2, "lon": -102.7, "max_psi": 1440, "manufacturer": "Halliburton"},
        {"id": "SC-PAD-45", "type": "WELL_PAD", "subtype": "MULTI_WELL", "lat": 32.05, "lon": -102.85, "max_psi": 1500, "manufacturer": "Schlumberger"},
        
        # Separators
        {"id": "SC-SEP-101", "type": "SEPARATOR", "subtype": "3PHASE", "lat": 32.08, "lon": -102.6, "max_psi": 1440, "manufacturer": "Schlumberger"},
        {"id": "SC-SEP-102", "type": "SEPARATOR", "subtype": "3PHASE", "lat": 32.12, "lon": -102.55, "max_psi": 1440, "manufacturer": "Exterran"},
        
        # Compressors
        {"id": "SC-COMP-A", "type": "COMPRESSOR", "subtype": "RECIPROCATING", "lat": 32.0, "lon": -102.5, "max_psi": 1200, "manufacturer": "Ariel"},
        {"id": "SC-COMP-B", "type": "COMPRESSOR", "subtype": "CENTRIFUGAL", "lat": 31.95, "lon": -102.45, "max_psi": 1000, "manufacturer": "Solar Turbines"},
        
        # Central Processing Facility
        {"id": "SC-CPF-01", "type": "PROCESSING_FACILITY", "subtype": "CENTRAL", "lat": 31.9, "lon": -102.3, "max_psi": 1440, "manufacturer": "Wood Group"},
    ]
    
    # TeraField Assets (Legacy Acquired - Lower pressure ratings, some missing specs)
    terafield_assets = [
        # Legacy Separators (lower ratings)
        {"id": "TF-V-204", "type": "SEPARATOR", "subtype": "2PHASE_VERTICAL", "lat": 31.8, "lon": -101.9, "max_psi": 600, "manufacturer": "Natco"},  # CRITICAL: Low pressure limit!
        {"id": "TF-V-205", "type": "SEPARATOR", "subtype": "2PHASE_VERTICAL", "lat": 31.75, "lon": -101.85, "max_psi": 650, "manufacturer": "Natco"},
        {"id": "TF-H-301", "type": "SEPARATOR", "subtype": "2PHASE_HORIZONTAL", "lat": 31.85, "lon": -102.0, "max_psi": 720, "manufacturer": "Cameron"},
        
        # Legacy Compressors
        {"id": "TF-COMP-LP-A", "type": "COMPRESSOR", "subtype": "LOW_PRESSURE", "lat": 31.7, "lon": -101.8, "max_psi": 500, "manufacturer": "Ingersoll Rand"},
        
        # Legacy Tanks
        {"id": "TF-TK-401", "type": "TANK", "subtype": "OIL_STORAGE", "lat": 31.65, "lon": -101.75, "max_psi": 15, "manufacturer": "Unknown"},
        {"id": "TF-TK-402", "type": "TANK", "subtype": "WATER_STORAGE", "lat": 31.68, "lon": -101.78, "max_psi": 15, "manufacturer": "Unknown"},
        
        # Midland Hub (acquisition target)
        {"id": "TF-MID-HUB", "type": "PROCESSING_FACILITY", "subtype": "GATHERING_HUB", "lat": 31.78, "lon": -101.88, "max_psi": 800, "manufacturer": "Pioneer Legacy"},
        
        # Valves (critical control points)
        {"id": "TF-VALVE-101", "type": "VALVE", "subtype": "CONTROL", "lat": 31.82, "lon": -101.92, "max_psi": 550, "manufacturer": "Fisher"},  # Undersized!
        {"id": "TF-VALVE-102", "type": "VALVE", "subtype": "SAFETY", "lat": 31.79, "lon": -101.89, "max_psi": 600, "manufacturer": "Fisher"},
    ]
    
    # Build asset records
    for asset in snowcore_assets:
        assets.append({
            "ASSET_ID": asset["id"],
            "SOURCE_SYSTEM": "SNOWCORE",
            "ASSET_TYPE": asset["type"],
            "ASSET_SUBTYPE": asset["subtype"],
            "LATITUDE": asset["lat"],
            "LONGITUDE": asset["lon"],
            "MAX_PRESSURE_RATING_PSI": asset["max_psi"],
            "MANUFACTURER": asset["manufacturer"],
            "INSTALL_DATE": f"202{random.randint(0, 3)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "ZONE": "DELAWARE",
        })
    
    for asset in terafield_assets:
        assets.append({
            "ASSET_ID": asset["id"],
            "SOURCE_SYSTEM": "TERAFIELD",
            "ASSET_TYPE": asset["type"],
            "ASSET_SUBTYPE": asset["subtype"],
            "LATITUDE": asset["lat"],
            "LONGITUDE": asset["lon"],
            "MAX_PRESSURE_RATING_PSI": asset["max_psi"],
            "MANUFACTURER": asset["manufacturer"],
            "INSTALL_DATE": f"201{random.randint(0, 8)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "ZONE": "MIDLAND",
        })
    
    return assets


def generate_network_edges():
    """Generate NETWORK_EDGES table data.
    
    Defines pipeline connections between assets.
    Critical edge: SC-PAD-42 -> PIPE-88 -> TF-V-204 (the hidden bottleneck)
    """
    edges = [
        # SnowCore Internal Network
        {"segment_id": "PIPE-01", "source": "SC-PAD-42", "target": "SC-SEP-101", "diameter": 8, "max_psi": 1440, "status": "ACTIVE"},
        {"segment_id": "PIPE-02", "source": "SC-PAD-43", "target": "SC-SEP-101", "diameter": 8, "max_psi": 1440, "status": "ACTIVE"},
        {"segment_id": "PIPE-03", "source": "SC-PAD-44", "target": "SC-SEP-102", "diameter": 6, "max_psi": 1440, "status": "ACTIVE"},
        {"segment_id": "PIPE-04", "source": "SC-PAD-45", "target": "SC-SEP-101", "diameter": 8, "max_psi": 1440, "status": "ACTIVE"},
        {"segment_id": "PIPE-05", "source": "SC-SEP-101", "target": "SC-COMP-A", "diameter": 12, "max_psi": 1200, "status": "ACTIVE"},
        {"segment_id": "PIPE-06", "source": "SC-SEP-102", "target": "SC-COMP-A", "diameter": 10, "max_psi": 1200, "status": "ACTIVE"},
        {"segment_id": "PIPE-07", "source": "SC-COMP-A", "target": "SC-COMP-B", "diameter": 16, "max_psi": 1000, "status": "ACTIVE"},
        {"segment_id": "PIPE-08", "source": "SC-COMP-B", "target": "SC-CPF-01", "diameter": 20, "max_psi": 1000, "status": "ACTIVE"},
        
        # TeraField Internal Network (Legacy)
        {"segment_id": "PIPE-TF-01", "source": "TF-V-204", "target": "TF-VALVE-101", "diameter": 6, "max_psi": 550, "status": "ACTIVE"},
        {"segment_id": "PIPE-TF-02", "source": "TF-VALVE-101", "target": "TF-MID-HUB", "diameter": 8, "max_psi": 800, "status": "ACTIVE"},
        {"segment_id": "PIPE-TF-03", "source": "TF-V-205", "target": "TF-MID-HUB", "diameter": 6, "max_psi": 650, "status": "ACTIVE"},
        {"segment_id": "PIPE-TF-04", "source": "TF-H-301", "target": "TF-MID-HUB", "diameter": 8, "max_psi": 720, "status": "ACTIVE"},
        {"segment_id": "PIPE-TF-05", "source": "TF-MID-HUB", "target": "TF-COMP-LP-A", "diameter": 10, "max_psi": 500, "status": "ACTIVE"},
        {"segment_id": "PIPE-TF-06", "source": "TF-COMP-LP-A", "target": "TF-TK-401", "diameter": 8, "max_psi": 15, "status": "ACTIVE"},
        {"segment_id": "PIPE-TF-07", "source": "TF-MID-HUB", "target": "TF-TK-402", "diameter": 6, "max_psi": 15, "status": "ACTIVE"},
        
        # CRITICAL: Cross-network connection (the hidden dependency!)
        # This is the pipeline that connects SnowCore's new production to TeraField's legacy infrastructure
        {"segment_id": "PIPE-88", "source": "SC-SEP-101", "target": "TF-V-204", "diameter": 6, "max_psi": 600, "status": "ACTIVE"},
        
        # Additional cross-connections (discovered by link prediction)
        {"segment_id": "PIPE-89", "source": "SC-CPF-01", "target": "TF-MID-HUB", "diameter": 12, "max_psi": 800, "status": "PLANNED"},
    ]
    
    return [
        {
            "SEGMENT_ID": e["segment_id"],
            "SOURCE_ASSET_ID": e["source"],
            "TARGET_ASSET_ID": e["target"],
            "LINE_DIAMETER_INCHES": e["diameter"],
            "MAX_PRESSURE_RATING_PSI": e["max_psi"],
            "STATUS": e["status"],
            "LENGTH_MILES": round(random.uniform(0.5, 15.0), 2),
        }
        for e in edges
    ]


def generate_scada_telemetry(assets):
    """Generate SCADA_TELEMETRY time-series data.
    
    Creates 1-minute interval sensor readings with:
    - Normal operating patterns (sine wave + noise)
    - Anomaly injection at ANOMALY_EVENT_TIME
    - SnowCore: Clean signals, high frequency
    - TeraField: Noisier, with occasional gaps (legacy system artifacts)
    """
    telemetry = []
    
    current_time = START_TIME
    
    # Pre-calculate asset operating points
    asset_baselines = {}
    for asset in assets:
        asset_id = asset["ASSET_ID"]
        max_psi = asset["MAX_PRESSURE_RATING_PSI"]
        
        # Operating point is typically 60-80% of max rating
        baseline_pressure = max_psi * random.uniform(0.6, 0.75)
        baseline_flow = random.uniform(500, 2000)  # BOPD equivalent
        
        asset_baselines[asset_id] = {
            "pressure": baseline_pressure,
            "flow": baseline_flow,
            "is_snowcore": asset["SOURCE_SYSTEM"] == "SNOWCORE",
            "max_psi": max_psi,
        }
    
    # Time counter for sine wave patterns
    time_step = 0
    
    while current_time <= END_TIME:
        for asset in assets:
            asset_id = asset["ASSET_ID"]
            baseline = asset_baselines[asset_id]
            
            # TeraField assets have occasional communication gaps
            if not baseline["is_snowcore"] and random.random() < 0.02:
                continue  # Skip this reading (simulates comm failure)
            
            # Calculate time-varying values
            # Sine wave for daily operational patterns
            hour_angle = (current_time.hour + current_time.minute / 60) * (2 * math.pi / 24)
            daily_factor = 1 + 0.1 * math.sin(hour_angle)  # ±10% daily variation
            
            # Base values
            pressure = baseline["pressure"] * daily_factor
            flow = baseline["flow"] * daily_factor
            
            # Add noise (TeraField has more noise due to older sensors)
            noise_factor = 2 if baseline["is_snowcore"] else 8
            pressure += random.gauss(0, noise_factor)
            flow += random.gauss(0, baseline["flow"] * 0.02)
            
            # ANOMALY INJECTION: SC-PAD-42 ramps up production
            if current_time >= ANOMALY_EVENT_TIME:
                minutes_since_event = (current_time - ANOMALY_EVENT_TIME).total_seconds() / 60
                
                if asset_id == "SC-PAD-42":
                    # Ramp up flow by 50% over 30 minutes, then sustain
                    ramp_factor = min(1.5, 1.0 + 0.5 * (minutes_since_event / 30))
                    flow *= ramp_factor
                    pressure *= (1 + 0.3 * (ramp_factor - 1))  # Pressure increases with flow
                
                # Downstream effect: TF-V-204 sees pressure spike after 5-minute lag
                if asset_id == "TF-V-204" and minutes_since_event >= 5:
                    # Pressure spikes dangerously close to (and eventually exceeding) limit
                    lag_minutes = minutes_since_event - 5
                    spike = min(250, lag_minutes * 2)  # Ramps up to +250 PSI
                    pressure = baseline["pressure"] + spike
                    
                    # Cap at realistic but dangerous level (800 PSI vs 600 limit!)
                    pressure = min(pressure, 800)
            
            # Temperature (correlated with pressure)
            temperature = 120 + (pressure / 20) + random.gauss(0, 3)
            
            telemetry.append({
                "ASSET_ID": asset_id,
                "TIMESTAMP": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "FLOW_RATE_BOPD": round(max(0, flow), 2),
                "PRESSURE_PSI": round(max(0, pressure), 2),
                "TEMPERATURE_F": round(temperature, 1),
                "SOURCE_SYSTEM": asset["SOURCE_SYSTEM"],
            })
        
        current_time += timedelta(minutes=INTERVAL_MINUTES)
        time_step += 1
        
        # Progress indicator (every 24 hours of data)
        if time_step % 1440 == 0:
            print(f"  Generated {time_step // 1440} day(s) of telemetry data...")
    
    return telemetry


def generate_graph_predictions(assets, edges):
    """Generate pre-computed graph predictions for the demo.
    
    This simulates what the AutoGL model would produce:
    - pressure_anomaly_score: Risk of pressure-related issues
    - link_probability: Predicted hidden connections
    """
    predictions = []
    
    # Node-level predictions (pressure anomaly scores)
    for asset in assets:
        asset_id = asset["ASSET_ID"]
        
        # Calculate risk score based on asset characteristics
        base_risk = 0.1
        
        # Legacy assets have higher baseline risk
        if asset["SOURCE_SYSTEM"] == "TERAFIELD":
            base_risk += 0.2
        
        # Assets at the cross-network interface are higher risk
        if asset_id in ["TF-V-204", "TF-VALVE-101", "SC-SEP-101"]:
            base_risk += 0.4
        
        # The critical bottleneck
        if asset_id == "TF-V-204":
            base_risk = 0.92  # Very high risk!
        
        predictions.append({
            "PREDICTION_TYPE": "NODE_ANOMALY",
            "ENTITY_ID": asset_id,
            "RELATED_ENTITY_ID": None,
            "SCORE": round(min(1.0, base_risk + random.uniform(-0.05, 0.05)), 3),
            "CONFIDENCE": round(random.uniform(0.85, 0.98), 3),
            "EXPLANATION": f"Pressure anomaly risk for {asset_id}",
            "PREDICTION_TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    
    # Edge-level predictions (link probability for missing connections)
    # These are connections the model "discovers" between the two networks
    potential_links = [
        ("SC-COMP-B", "TF-COMP-LP-A", 0.78, "Potential parallel compression path"),
        ("SC-CPF-01", "TF-TK-401", 0.65, "Alternative oil storage routing"),
        ("SC-SEP-102", "TF-H-301", 0.72, "Cross-network separator link"),
        ("SC-PAD-45", "TF-V-205", 0.58, "Secondary well-to-separator path"),
    ]
    
    for source, target, prob, explanation in potential_links:
        predictions.append({
            "PREDICTION_TYPE": "LINK_PREDICTION",
            "ENTITY_ID": source,
            "RELATED_ENTITY_ID": target,
            "SCORE": round(prob + random.uniform(-0.05, 0.05), 3),
            "CONFIDENCE": round(random.uniform(0.80, 0.95), 3),
            "EXPLANATION": explanation,
            "PREDICTION_TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    
    return predictions


def write_csv(filename, data, fieldnames):
    """Write data to CSV file."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  Wrote {len(data)} rows to {filepath}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("SnowCore Permian Demo - Synthetic Data Generator")
    print(f"Random Seed: {RANDOM_SEED}")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    
    # Generate asset master
    print("\n[1/4] Generating ASSET_MASTER...")
    assets = generate_asset_master()
    write_csv(
        "asset_master.csv",
        assets,
        ["ASSET_ID", "SOURCE_SYSTEM", "ASSET_TYPE", "ASSET_SUBTYPE", 
         "LATITUDE", "LONGITUDE", "MAX_PRESSURE_RATING_PSI", 
         "MANUFACTURER", "INSTALL_DATE", "ZONE"]
    )
    
    # Generate network edges
    print("\n[2/4] Generating NETWORK_EDGES...")
    edges = generate_network_edges()
    write_csv(
        "network_edges.csv",
        edges,
        ["SEGMENT_ID", "SOURCE_ASSET_ID", "TARGET_ASSET_ID", 
         "LINE_DIAMETER_INCHES", "MAX_PRESSURE_RATING_PSI", 
         "STATUS", "LENGTH_MILES"]
    )
    
    # Generate SCADA telemetry
    print("\n[3/4] Generating SCADA_TELEMETRY (7 days of 1-minute data)...")
    telemetry = generate_scada_telemetry(assets)
    write_csv(
        "scada_telemetry.csv",
        telemetry,
        ["ASSET_ID", "TIMESTAMP", "FLOW_RATE_BOPD", "PRESSURE_PSI", 
         "TEMPERATURE_F", "SOURCE_SYSTEM"]
    )
    
    # Generate graph predictions
    print("\n[4/4] Generating GRAPH_PREDICTIONS (pre-computed ML results)...")
    predictions = generate_graph_predictions(assets, edges)
    write_csv(
        "graph_predictions.csv",
        predictions,
        ["PREDICTION_TYPE", "ENTITY_ID", "RELATED_ENTITY_ID", 
         "SCORE", "CONFIDENCE", "EXPLANATION", "PREDICTION_TIMESTAMP"]
    )
    
    print("\n" + "=" * 60)
    print("Data generation complete!")
    print(f"  Assets: {len(assets)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Telemetry records: {len(telemetry)}")
    print(f"  Predictions: {len(predictions)}")
    print("\nHidden Demo Pattern:")
    print("  - SC-PAD-42 -> PIPE-88 -> TF-V-204")
    print("  - TF-V-204 limit: 600 PSI")
    print("  - Anomaly at Day 5: Pressure spikes to 800 PSI!")
    print("=" * 60)


if __name__ == "__main__":
    main()

