"""
Simulation & Chat Page
======================
Production simulation controls with interactive map and AI Integration Assistant.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
import sys
sys.path.insert(0, '..')
from utils.chat_panel import render_chat_panel, add_simulation_result_to_chat

st.set_page_config(page_title="Simulation & Chat", page_icon="💬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    
    .page-header {
        background: linear-gradient(135deg, #11567F 0%, #1e293b 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #29B5E8;
    }
    
    .page-header h1 {
        color: #29B5E8;
        margin: 0;
        font-size: 1.75rem;
    }
    
    .simulation-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    
    .chat-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
        min-height: 500px;
    }
    
    .simulation-result {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }
    
    .result-approved {
        background: rgba(34, 197, 94, 0.1);
        border-left-color: #22c55e;
    }
    
    .result-denied {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
    }
    
    .selected-asset-card {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(30, 41, 59, 0.9) 100%);
        border: 2px solid #06b6d4;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    .legend-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        padding: 0.75rem 1rem;
        background: #1e293b;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border: 1px solid #334155;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8rem;
        color: #cbd5e1;
    }
    
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    
    /* Hide default page navigation to use custom navigation */
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CUSTOM SIDEBAR NAVIGATION
# =============================================================================

st.sidebar.markdown("""
<div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #334155; margin-bottom: 1rem;">
    <div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0;">Permian Command Center</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/1_Network_Map.py", label="Network Discovery Map", icon="🗺️")
st.sidebar.page_link("pages/2_Simulation_Chat.py", label="Simulation & Chat", icon="💬")
st.sidebar.page_link("pages/4_Telemetry_Explorer.py", label="Telemetry Explorer", icon="📈")
st.sidebar.page_link("pages/5_Production_Analytics.py", label="Production Analytics", icon="📊")
st.sidebar.page_link("pages/6_Document_Intelligence.py", label="Document Intelligence", icon="📄")
st.sidebar.markdown("---")
st.sidebar.page_link("pages/3_About.py", label="About", icon="ℹ️")

st.sidebar.markdown("---")

# Chat panel toggle (default to ON on this page)
if 'show_chat_panel' not in st.session_state:
    st.session_state.show_chat_panel = True

st.sidebar.markdown("#### AI Assistant")
if st.sidebar.button(
    "Show Chat" if not st.session_state.show_chat_panel else "Hide Chat",
    key="toggle_chat_sim",
    use_container_width=True
):
    st.session_state.show_chat_panel = not st.session_state.show_chat_panel
    st.rerun()

st.sidebar.markdown("---")

# Header
st.markdown("""
<div class="page-header">
    <h1>Simulation & Chat</h1>
</div>
""", unsafe_allow_html=True)

# Fully qualified table names
SCHEMA_PREFIX = "AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION"

# Session
@st.cache_resource
def get_session():
    return get_active_session()

session = get_session()

# Initialize chat history and context
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'selected_asset_context' not in st.session_state:
    st.session_state.selected_asset_context = None

# Initialize simulation selected asset
if 'sim_selected_asset' not in st.session_state:
    st.session_state.sim_selected_asset = None

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data(ttl=300)
def load_simulation_data():
    """Load asset data with location info for map and simulation."""
    try:
        assets = session.sql(f"""
            SELECT 
                a.ASSET_ID,
                a.SOURCE_SYSTEM,
                a.ASSET_TYPE,
                a.MAX_PRESSURE_RATING_PSI,
                a.LATITUDE,
                a.LONGITUDE,
                COALESCE(p.SCORE, 0) as RISK_SCORE,
                agg.AVG_PRESSURE_PSI,
                agg.AVG_FLOW_RATE_BOPD
            FROM {SCHEMA_PREFIX}.ASSET_MASTER a
            LEFT JOIN {SCHEMA_PREFIX}.GRAPH_PREDICTIONS p 
                ON a.ASSET_ID = p.ENTITY_ID 
                AND p.PREDICTION_TYPE = 'NODE_ANOMALY'
            LEFT JOIN (
                SELECT ASSET_ID, AVG_PRESSURE_PSI, AVG_FLOW_RATE_BOPD
                FROM {SCHEMA_PREFIX}.SCADA_AGGREGATES
                WHERE RECORD_DATE = (SELECT MAX(RECORD_DATE) FROM {SCHEMA_PREFIX}.SCADA_AGGREGATES)
            ) agg ON a.ASSET_ID = agg.ASSET_ID
        """).to_pandas()
        return assets
    except Exception as e:
        st.error(f"Error loading simulation data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_network_edges():
    """Load network edge data for map visualization."""
    try:
        return session.sql(f"""
            SELECT 
                SEGMENT_ID,
                SOURCE_ASSET_ID,
                TARGET_ASSET_ID,
                STATUS
            FROM {SCHEMA_PREFIX}.NETWORK_EDGES
            WHERE STATUS = 'ACTIVE'
        """).to_pandas()
    except Exception as e:
        st.error(f"Error loading network edges: {str(e)}")
        return pd.DataFrame()

assets_df = load_simulation_data()
edges_df = load_network_edges()

# =============================================================================
# PRODUCTION SIMULATION - MAP SELECTION
# =============================================================================

st.markdown("### Production Simulation")
st.markdown("**Click an asset on the map or use the dropdown to select a source for simulation.**")

# Get current selection
selected_asset_id = st.session_state.sim_selected_asset

# Legend
st.markdown("""
<div class="legend-container">
    <div class="legend-item">
        <div class="legend-dot" style="background: #0ea5e9;"></div>
        <span>SnowCore</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #f43f5e;"></div>
        <span>TeraField</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #22d3ee; border: 2px solid #fff;"></div>
        <span>Selected</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #fbbf24;"></div>
        <span>High Risk</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MAP VISUALIZATION
# =============================================================================

# Prepare asset data for PyDeck
asset_data = []
for _, row in assets_df.iterrows():
    risk = row['RISK_SCORE']
    is_selected = (selected_asset_id and row['ASSET_ID'] == selected_asset_id)
    
    # Determine color based on state
    if is_selected:
        color = [34, 211, 238, 255]  # Cyan for selected
    elif risk > 0.7:
        color = [251, 191, 36, 255]  # Yellow for high risk
    elif row['SOURCE_SYSTEM'] == 'SNOWCORE':
        color = [14, 165, 233, 230]  # Blue for SnowCore
    else:
        color = [244, 63, 94, 230]  # Red for TeraField
    
    # Determine radius
    if is_selected:
        radius = 1200
    elif risk > 0.7:
        radius = 900
    else:
        radius = 700
    
    asset_data.append({
        'ASSET_ID': row['ASSET_ID'],
        'SOURCE_SYSTEM': row['SOURCE_SYSTEM'],
        'ASSET_TYPE': row['ASSET_TYPE'],
        'LATITUDE': float(row['LATITUDE']) if pd.notna(row['LATITUDE']) else 0,
        'LONGITUDE': float(row['LONGITUDE']) if pd.notna(row['LONGITUDE']) else 0,
        'MAX_PRESSURE_RATING_PSI': float(row['MAX_PRESSURE_RATING_PSI']) if pd.notna(row['MAX_PRESSURE_RATING_PSI']) else 0,
        'RISK_SCORE': float(row['RISK_SCORE']),
        'color': color,
        'radius': radius
    })

# Prepare pipeline edges data
pipeline_data = []
for _, edge in edges_df.iterrows():
    src = assets_df[assets_df['ASSET_ID'] == edge['SOURCE_ASSET_ID']]
    tgt = assets_df[assets_df['ASSET_ID'] == edge['TARGET_ASSET_ID']]
    
    if len(src) > 0 and len(tgt) > 0:
        src_system = src['SOURCE_SYSTEM'].values[0]
        tgt_system = tgt['SOURCE_SYSTEM'].values[0]
        
        # Cross-network = amber, SnowCore = blue, TeraField = red
        if src_system != tgt_system:
            color = [245, 158, 11, 200]  # Amber
        elif src_system == 'SNOWCORE':
            color = [14, 165, 233, 150]  # Blue
        else:
            color = [244, 63, 94, 150]  # Red
        
        pipeline_data.append({
            'start_lon': float(src['LONGITUDE'].values[0]),
            'start_lat': float(src['LATITUDE'].values[0]),
            'end_lon': float(tgt['LONGITUDE'].values[0]),
            'end_lat': float(tgt['LATITUDE'].values[0]),
            'color': color
        })

# Create PyDeck layers
layers = []

# Layer 1: Pipeline connections
if len(pipeline_data) > 0:
    line_layer = pdk.Layer(
        'LineLayer',
        data=pipeline_data,
        get_source_position='[start_lon, start_lat]',
        get_target_position='[end_lon, end_lat]',
        get_color='color',
        get_width=3,
        pickable=False
    )
    layers.append(line_layer)

# Layer 2: Asset nodes
if len(asset_data) > 0:
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=asset_data,
        get_position='[LONGITUDE, LATITUDE]',
        get_fill_color='color',
        get_radius='radius',
        pickable=True,
        auto_highlight=True,
        highlight_color=[255, 255, 255, 100]
    )
    layers.append(scatter_layer)

# Layer 3: Asset labels
if len(asset_data) > 0:
    text_layer = pdk.Layer(
        'TextLayer',
        data=asset_data,
        get_position='[LONGITUDE, LATITUDE]',
        get_text='ASSET_ID',
        get_size=11,
        get_color=[226, 232, 240, 255],
        get_angle=0,
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
        pickable=False
    )
    layers.append(text_layer)

# Calculate center of all assets for view state
center_lat = assets_df['LATITUDE'].mean()
center_lon = assets_df['LONGITUDE'].mean()

view_state = pdk.ViewState(
    latitude=float(center_lat),
    longitude=float(center_lon),
    zoom=9,
    pitch=40,
    bearing=0
)

# Build tooltip
tooltip_config = {
    'html': '<b>{ASSET_ID}</b><br>System: {SOURCE_SYSTEM}<br>Type: {ASSET_TYPE}<br>Max PSI: {MAX_PRESSURE_RATING_PSI}<br>Risk: {RISK_SCORE}',
    'style': {
        'backgroundColor': '#1e293b',
        'color': '#e2e8f0',
        'borderRadius': '8px',
        'padding': '8px',
        'border': '1px solid #334155'
    }
}

# Create the deck
deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=None,  # Required for Snowflake Streamlit
    tooltip=tooltip_config
)

st.pydeck_chart(deck, use_container_width=True, height=350)

# =============================================================================
# ASSET SELECTOR (Below Map)
# =============================================================================

st.markdown("<br>", unsafe_allow_html=True)

asset_col1, asset_col2 = st.columns([2, 3])

with asset_col1:
    # Filter to show only well pads as source options
    well_pad_options = assets_df[assets_df['ASSET_TYPE'] == 'WELL_PAD']['ASSET_ID'].tolist()
    all_options = [""] + well_pad_options
    
    # Find current index
    current_idx = 0
    if selected_asset_id and selected_asset_id in well_pad_options:
        current_idx = all_options.index(selected_asset_id)
    
    new_selection = st.selectbox(
        "Select Source Asset (Well Pad)",
        all_options,
        index=current_idx,
        help="Select a well pad to simulate production increase"
    )
    
    if new_selection != selected_asset_id:
        st.session_state.sim_selected_asset = new_selection if new_selection else None
        st.rerun()

with asset_col2:
    if selected_asset_id:
        asset_row = assets_df[assets_df['ASSET_ID'] == selected_asset_id]
        if len(asset_row) > 0:
            asset_row = asset_row.iloc[0]
            system_color = '#0ea5e9' if asset_row['SOURCE_SYSTEM'] == 'SNOWCORE' else '#f43f5e'
            
            pressure = asset_row['AVG_PRESSURE_PSI'] if pd.notna(asset_row['AVG_PRESSURE_PSI']) else 0
            flow = asset_row['AVG_FLOW_RATE_BOPD'] if pd.notna(asset_row['AVG_FLOW_RATE_BOPD']) else 0
            
            st.markdown(f"""
            <div class="selected-asset-card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <span style="color: {system_color}; font-weight: 700; font-size: 1.1rem;">{selected_asset_id}</span>
                        <span style="color: #94a3b8; margin-left: 0.5rem;">{asset_row['ASSET_TYPE']}</span>
                    </div>
                    <div style="display: flex; gap: 1.5rem; font-size: 0.9rem;">
                        <span style="color: #94a3b8;">Pressure: <strong style="color: #e2e8f0;">{pressure:.0f} PSI</strong></span>
                        <span style="color: #94a3b8;">Flow: <strong style="color: #e2e8f0;">{flow:.0f} BOPD</strong></span>
                        <span style="color: #94a3b8;">Risk: <strong style="color: {'#ef4444' if asset_row['RISK_SCORE'] > 0.7 else '#22c55e'};">{asset_row['RISK_SCORE']:.2f}</strong></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Select a well pad from the dropdown or click on the map to begin simulation")

# =============================================================================
# SIMULATION CONTROLS
# =============================================================================

if selected_asset_id:
    st.markdown("---")
    st.markdown("#### Simulation Parameters")
    
    sim_col1, sim_col2 = st.columns([2, 1])
    
    with sim_col1:
        production_increase = st.slider(
            "Additional Production (BOPD)",
            min_value=0,
            max_value=10000,
            value=2500,
            step=500
        )
    
    with sim_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        run_sim = st.button("Run Simulation", use_container_width=True, type="primary")
    
    # Run simulation
    if run_sim:
        try:
            asset_info = assets_df[assets_df['ASSET_ID'] == selected_asset_id].iloc[0]
            
            # Simulate pressure impact
            current_pressure = asset_info['AVG_PRESSURE_PSI'] if pd.notna(asset_info['AVG_PRESSURE_PSI']) else 500
            # Simple linear model: pressure increases ~0.03 PSI per additional BOPD
            projected_pressure = current_pressure + (production_increase * 0.03)
            
            # Find downstream assets using Recursive CTE for cascade analysis
            with st.spinner("Simulating pressure propagation..."):
                downstream = session.sql(f"""
                    WITH RECURSIVE propagation AS (
                        -- Base case
                        SELECT 
                            target_asset_id,
                            length_miles as total_distance,
                            1 as hops
                        FROM {SCHEMA_PREFIX}.NETWORK_EDGES
                        WHERE source_asset_id = '{selected_asset_id}' AND status = 'ACTIVE'
                        
                        UNION ALL
                        
                        -- Recursive step
                        SELECT 
                            e.target_asset_id,
                            p.total_distance + e.length_miles,
                            p.hops + 1
                        FROM {SCHEMA_PREFIX}.NETWORK_EDGES e
                        JOIN propagation p ON e.source_asset_id = p.target_asset_id
                        WHERE e.status = 'ACTIVE' AND p.hops < 5
                    )
                    SELECT 
                        p.target_asset_id,
                        p.total_distance,
                        p.hops,
                        a.max_pressure_rating_psi,
                        a.asset_type,
                        a.source_system
                    FROM propagation p
                    LEFT JOIN {SCHEMA_PREFIX}.ASSET_MASTER a ON p.target_asset_id = a.asset_id
                """).to_pandas()

            # Calculate Time to Impact (assuming ~2 mins/mile for pressure wave)
            if not downstream.empty:
                downstream['TIME_TO_IMPACT_MIN'] = downstream['TOTAL_DISTANCE'] * 2
            else:
                downstream['TIME_TO_IMPACT_MIN'] = 0
            
            # Check for pressure violations
            violations = []
            downstream['VIOLATION'] = False
            
            for idx, row in downstream.iterrows():
                limit = row['MAX_PRESSURE_RATING_PSI']
                if pd.notna(limit) and projected_pressure > limit:
                    violations.append({
                        'asset': row['TARGET_ASSET_ID'],
                        'type': row['ASSET_TYPE'],
                        'system': row['SOURCE_SYSTEM'],
                        'limit': limit,
                        'projected': projected_pressure,
                        'time': row['TIME_TO_IMPACT_MIN']
                    })
                    downstream.at[idx, 'VIOLATION'] = True
            
            # Display result
            if violations:
                st.markdown(f"""
                <div class="simulation-result result-denied">
                    <strong style="color: #ef4444; font-size: 1.1rem;">ROUTING DENIED</strong><br><br>
                    <span style="color: #e2e8f0;">Projected pressure <strong>{projected_pressure:.0f} PSI</strong> would exceed equipment limits:</span>
                </div>
                """, unsafe_allow_html=True)
                
                for v in violations:
                    st.error(f"**{v['asset']}** ({v['type']}): Limit {v['limit']:.0f} PSI < Projected {v['projected']:.0f} PSI (Impact in {v['time']:.1f} min)")
                
                # Add to chat
                add_simulation_result_to_chat(
                    "DENIED",
                    f"Adding {production_increase} BOPD from {selected_asset_id} was DENIED due to pressure violations on: {[v['asset'] for v in violations]}"
                )
            else:
                st.markdown(f"""
                <div class="simulation-result result-approved">
                    <strong style="color: #22c55e; font-size: 1.1rem;">ROUTING APPROVED</strong><br><br>
                    <span style="color: #e2e8f0;">Projected pressure: <strong>{projected_pressure:.0f} PSI</strong></span><br>
                    <span style="color: #94a3b8;">All downstream assets within limits. {len(downstream)} assets checked.</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to chat
                add_simulation_result_to_chat(
                    "APPROVED",
                    f"Adding {production_increase} BOPD from {selected_asset_id} was APPROVED. Projected pressure: {projected_pressure:.0f} PSI"
                )

            # Cascade Propagation Timeline
            if not downstream.empty:
                st.markdown("### Cascade Propagation Timeline")
                
                # Format data for Plotly
                timeline_df = downstream.sort_values('TIME_TO_IMPACT_MIN', ascending=True)
                timeline_df['Status'] = timeline_df['VIOLATION'].map({True: 'Violation', False: 'Safe'})
                
                fig = px.bar(
                    timeline_df,
                    x='TIME_TO_IMPACT_MIN',
                    y='TARGET_ASSET_ID',
                    orientation='h',
                    color='Status',
                    color_discrete_map={'Violation': '#ef4444', 'Safe': '#22c55e'},
                    text='TOTAL_DISTANCE',
                    title='Pressure Wave Propagation Time'
                )
                
                fig.update_traces(
                    texttemplate='%{text:.1f} miles',
                    textposition='outside'
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8'),
                    xaxis_title="Time to Impact (Minutes)",
                    yaxis_title="Downstream Asset",
                    yaxis=dict(categoryorder='total descending'),
                    height=max(400, len(downstream) * 40)
                )
                
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Simulation failed: {str(e)}")

# =============================================================================
# CHAT PANEL (at bottom)
# =============================================================================

if st.session_state.get('show_chat_panel', True):
    with st.container():
        st.markdown("---")
        st.markdown("### AI Integration Assistant")
        render_chat_panel(session, SCHEMA_PREFIX, assets_df, panel_key="simulation")
