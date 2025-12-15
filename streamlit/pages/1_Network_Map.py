"""
Network Map Page - Discovery Visualization
==========================================
Before/after AutoGL toggle showing how graph neural networks
discover hidden dependencies between SnowCore and TeraField networks.
"""

import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import pydeck as pdk
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
import sys
sys.path.insert(0, '..')
from utils.chat_panel import render_chat_panel

st.set_page_config(page_title="Network Map", page_icon="🗺️", layout="wide")

# Custom CSS matching main app styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    :root {
        --snowcore-blue: #0ea5e9;
        --terafield-red: #f43f5e;
        --cortex-purple: #a855f7;
        --slate-950: #020617;
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --slate-400: #94a3b8;
        --slate-300: #cbd5e1;
        --slate-200: #e2e8f0;
        --risk-high: #ef4444;
        --risk-medium: #f59e0b;
        --risk-low: #22c55e;
        --accent-cyan: #06b6d4;
        --link-discovered: #a855f7;
    }
    
    * {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre {
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    .stApp {
        background: linear-gradient(180deg, var(--slate-950) 0%, var(--slate-900) 100%);
    }
    
    .page-header {
        background: linear-gradient(135deg, #11567F 0%, #1e293b 100%);
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--accent-cyan);
    }
    
    .page-header h1 {
        color: var(--accent-cyan);
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .page-header p {
        color: var(--slate-400);
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Mode toggle styling */
    .mode-toggle {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border: 1px solid var(--slate-700);
        margin-bottom: 1rem;
    }
    
    /* Legend styling */
    .legend-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        padding: 1rem;
        background: var(--slate-800);
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: var(--slate-300);
    }
    
    .legend-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }
    
    .legend-line {
        width: 24px;
        height: 3px;
        border-radius: 2px;
    }
    
    .legend-line-dashed {
        width: 24px;
        height: 3px;
        border-top: 3px dashed;
    }
    
    /* Discovery card styling */
    .discovery-card {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--slate-700);
        border-left: 4px solid var(--cortex-purple);
        margin-bottom: 1rem;
    }
    
    .discovery-title {
        color: var(--cortex-purple);
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    
    .discovery-content {
        color: var(--slate-300);
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .discovery-score {
        display: inline-block;
        background: rgba(168, 85, 247, 0.2);
        color: var(--cortex-purple);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    
    /* Stats card */
    .stats-card {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid var(--slate-700);
        text-align: center;
    }
    
    .stats-value {
        font-size: 1.75rem;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .stats-label {
        font-size: 0.75rem;
        color: var(--slate-400);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.25rem;
    }
    
    /* Risk path visualization */
    .risk-path-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin-top: 1rem;
    }
    
    .risk-path-title {
        color: var(--risk-high);
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    .path-node {
        display: inline-flex;
        align-items: center;
        background: var(--slate-800);
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        margin: 0.25rem;
        font-size: 0.85rem;
        color: var(--slate-200);
    }
    
    .path-arrow {
        color: var(--slate-600);
        margin: 0 0.5rem;
    }
    
    /* Bottleneck highlight */
    .bottleneck-card {
        background: rgba(239, 68, 68, 0.15);
        border: 2px solid var(--risk-high);
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        box-sizing: border-box;
    }
    
    .bottleneck-title {
        color: var(--risk-high);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Info card */
    .info-card {
        background: var(--slate-800);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid var(--slate-700);
        margin-bottom: 1rem;
    }
    
    /* Teaching section */
    .teaching-panel {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--slate-700);
        border-left: 4px solid var(--accent-cyan);
        height: 100%;
        box-sizing: border-box;
    }
    
    .teaching-panel h4 {
        color: var(--accent-cyan);
        margin: 0 0 1rem 0;
        font-size: 1rem;
    }
    
    .teaching-panel p, .teaching-panel li {
        color: var(--slate-300);
        font-size: 0.9rem;
        line-height: 1.7;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--slate-800);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide default page navigation to use custom navigation */
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CUSTOM SIDEBAR NAVIGATION
# =============================================================================

st.sidebar.markdown("""
<div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #334155; margin-bottom: 1rem;">
    <div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0;">🛢️ Permian Command Center</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/1_Network_Map.py", label="Network Discovery Map", icon="🗺️")
st.sidebar.page_link("pages/2_Simulation_Chat.py", label="Simulation & Chat", icon="💬")

st.sidebar.markdown("---")

# Chat panel toggle
if 'show_chat_panel' not in st.session_state:
    st.session_state.show_chat_panel = False

st.sidebar.markdown("#### 💬 AI Assistant")
if st.sidebar.button(
    "Show Chat" if not st.session_state.show_chat_panel else "Hide Chat",
    key="toggle_chat_network",
    use_container_width=True
):
    st.session_state.show_chat_panel = not st.session_state.show_chat_panel
    st.rerun()

st.sidebar.markdown("---")

# Header
st.markdown("""
<div class="page-header">
    <h1>🗺️ Network Discovery Map</h1>
    <p>Toggle between "Before" and "After" AutoGL to see how graph neural networks discover hidden dependencies</p>
</div>
""", unsafe_allow_html=True)

# Fully qualified table names
SCHEMA_PREFIX = "AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION"

# Session
@st.cache_resource
def get_session():
    return get_active_session()

session = get_session()

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data(ttl=300)
def load_network_data():
    assets = session.sql(f"""
        SELECT 
            a.ASSET_ID,
            a.SOURCE_SYSTEM,
            a.ASSET_TYPE,
            a.ASSET_SUBTYPE,
            a.LATITUDE,
            a.LONGITUDE,
            a.MAX_PRESSURE_RATING_PSI,
            a.MANUFACTURER,
            a.INSTALL_DATE,
            a.ZONE,
            COALESCE(p.SCORE, 0) as RISK_SCORE,
            p.EXPLANATION as RISK_EXPLANATION
        FROM {SCHEMA_PREFIX}.ASSET_MASTER a
        LEFT JOIN {SCHEMA_PREFIX}.GRAPH_PREDICTIONS p 
            ON a.ASSET_ID = p.ENTITY_ID 
            AND p.PREDICTION_TYPE = 'NODE_ANOMALY'
    """).to_pandas()
    
    edges = session.sql(f"""
        SELECT 
            SEGMENT_ID,
            SOURCE_ASSET_ID,
            TARGET_ASSET_ID,
            LINE_DIAMETER_INCHES,
            MAX_PRESSURE_RATING_PSI,
            STATUS,
            LENGTH_MILES
        FROM {SCHEMA_PREFIX}.NETWORK_EDGES
        WHERE STATUS = 'ACTIVE'
    """).to_pandas()
    
    predicted_links = session.sql(f"""
        SELECT 
            ENTITY_ID as SOURCE,
            RELATED_ENTITY_ID as TARGET,
            SCORE,
            CONFIDENCE,
            EXPLANATION
        FROM {SCHEMA_PREFIX}.GRAPH_PREDICTIONS
        WHERE PREDICTION_TYPE = 'LINK_PREDICTION' AND SCORE > 0.5
    """).to_pandas()
    
    return assets, edges, predicted_links

assets_df, edges_df, predicted_links_df = load_network_data()

# Initialize session state for asset selection
if 'selected_asset_context' not in st.session_state:
    st.session_state.selected_asset_context = None

# =============================================================================
# MAIN CONTENT - CONTROLS ABOVE MAP
# =============================================================================

# View Mode Toggle Row
col_mode, col_stats = st.columns([3, 1])

with col_mode:
    view_mode = st.radio(
        "Network View Mode",
        ["Before AutoGL", "After AutoGL (Links Discovered)"],
        index=1,
        horizontal=True,
        help="Toggle to see how AutoGL discovers hidden connections"
    )

is_after_mode = "After" in view_mode

with col_stats:
    total_edges = len(edges_df)
    discovered_links = len(predicted_links_df) if is_after_mode else 0
    
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-value" style="color: {'#a855f7' if is_after_mode else '#0ea5e9'};">
            {total_edges + discovered_links}
        </div>
        <div class="stats-label">Total Connections</div>
    </div>
    """, unsafe_allow_html=True)

# Display Options Row
st.markdown("""
<div style="background: var(--slate-800); border-radius: 8px; padding: 0.5rem 1rem; margin: 0.5rem 0; border: 1px solid var(--slate-700);">
    <span style="color: var(--slate-400); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;">Display Filters</span>
</div>
""", unsafe_allow_html=True)

filter_cols = st.columns(4)
with filter_cols[0]:
    show_snowcore = st.checkbox("SnowCore Assets", value=True)
with filter_cols[1]:
    show_terafield = st.checkbox("TeraField Assets", value=True)
with filter_cols[2]:
    show_edges = st.checkbox("Pipelines", value=True)
with filter_cols[3]:
    highlight_risk = st.checkbox("Highlight Risk", value=True)

# Initialize selected_asset_id (will be set below the map)
selected_asset_id = ""

# Legend
st.markdown("""
<div class="legend-container">
    <div class="legend-item">
        <div class="legend-dot" style="background: #0ea5e9;"></div>
        <span>SnowCore Assets</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #f43f5e;"></div>
        <span>TeraField Assets</span>
    </div>
    <div class="legend-item">
        <div class="legend-dot" style="background: #fbbf24;"></div>
        <span>High Risk</span>
    </div>
    <div class="legend-item">
        <div class="legend-line" style="background: #475569;"></div>
        <span>Existing Pipeline</span>
    </div>
    <div class="legend-item">
        <div class="legend-line" style="background: #f59e0b;"></div>
        <span>Cross-Network Link</span>
    </div>
    <div class="legend-item">
        <div class="legend-line-dashed" style="border-color: #a855f7;"></div>
        <span>ML-Discovered Link</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# NETWORK VISUALIZATION (PyDeck Map)
# =============================================================================

# Filter assets
filtered_assets = assets_df.copy()
if not show_snowcore:
    filtered_assets = filtered_assets[filtered_assets['SOURCE_SYSTEM'] != 'SNOWCORE']
if not show_terafield:
    filtered_assets = filtered_assets[filtered_assets['SOURCE_SYSTEM'] != 'TERAFIELD']

# Prepare asset data as list of dicts for PyDeck (avoids serialization issues)
asset_data = []
for _, row in filtered_assets.iterrows():
    risk = row['RISK_SCORE']
    is_selected = (selected_asset_id and row['ASSET_ID'] == selected_asset_id)
    
    # Determine color based on state
    if is_selected:
        color = [34, 211, 238, 255]  # Cyan for selected
    elif highlight_risk and risk > 0.7:
        color = [251, 191, 36, 255]  # Yellow for high risk
    elif highlight_risk and risk > 0.4:
        color = [249, 115, 22, 255]  # Orange for elevated
    elif row['SOURCE_SYSTEM'] == 'SNOWCORE':
        color = [14, 165, 233, 230]  # Blue for SnowCore
    else:
        color = [244, 63, 94, 230]  # Red for TeraField
    
    # Determine radius
    if is_selected:
        radius = 1200
    elif risk > 0.7:
        radius = 1000
    else:
        radius = 700
    
    asset_data.append({
        'ASSET_ID': row['ASSET_ID'],
        'SOURCE_SYSTEM': row['SOURCE_SYSTEM'],
        'ASSET_TYPE': row['ASSET_TYPE'],
        'LATITUDE': float(row['LATITUDE']),
        'LONGITUDE': float(row['LONGITUDE']),
        'MAX_PRESSURE_RATING_PSI': float(row['MAX_PRESSURE_RATING_PSI']) if pd.notna(row['MAX_PRESSURE_RATING_PSI']) else 0,
        'RISK_SCORE': float(row['RISK_SCORE']),
        'color': color,
        'radius': radius
    })

# Prepare pipeline edges data
pipeline_data = []
if show_edges:
    for _, edge in edges_df.iterrows():
        src = assets_df[assets_df['ASSET_ID'] == edge['SOURCE_ASSET_ID']]
        tgt = assets_df[assets_df['ASSET_ID'] == edge['TARGET_ASSET_ID']]
        
        if len(src) > 0 and len(tgt) > 0:
            src_system = src['SOURCE_SYSTEM'].values[0]
            tgt_system = tgt['SOURCE_SYSTEM'].values[0]
            
            # Cross-network = amber, SnowCore = blue, TeraField = red
            if src_system != tgt_system:
                color = [245, 158, 11, 200]  # Amber
                width = 4
            elif src_system == 'SNOWCORE':
                color = [14, 165, 233, 150]  # Blue
                width = 3
            else:
                color = [244, 63, 94, 150]  # Red
                width = 3
            
            pipeline_data.append({
                'start_lon': float(src['LONGITUDE'].values[0]),
                'start_lat': float(src['LATITUDE'].values[0]),
                'end_lon': float(tgt['LONGITUDE'].values[0]),
                'end_lat': float(tgt['LATITUDE'].values[0]),
                'color': color,
                'width': width
            })

# Prepare ML-discovered links (only in "After" mode)
ml_links_data = []
if is_after_mode and len(predicted_links_df) > 0:
    for _, link in predicted_links_df.iterrows():
        src = assets_df[assets_df['ASSET_ID'] == link['SOURCE']]
        tgt = assets_df[assets_df['ASSET_ID'] == link['TARGET']]
        
        if len(src) > 0 and len(tgt) > 0:
            ml_links_data.append({
                'start_lon': float(src['LONGITUDE'].values[0]),
                'start_lat': float(src['LATITUDE'].values[0]),
                'end_lon': float(tgt['LONGITUDE'].values[0]),
                'end_lat': float(tgt['LATITUDE'].values[0]),
                'source': link['SOURCE'],
                'target': link['TARGET'],
                'score': float(link['SCORE'])
            })

# Create PyDeck layers
layers = []

# Layer 1: Existing pipeline connections
if len(pipeline_data) > 0:
    line_layer = pdk.Layer(
        'LineLayer',
        data=pipeline_data,
        get_source_position='[start_lon, start_lat]',
        get_target_position='[end_lon, end_lat]',
        get_color='color',
        get_width='width',
        pickable=True,
        auto_highlight=True
    )
    layers.append(line_layer)

# Layer 2: ML-discovered links (ArcLayer for visual distinction)
if len(ml_links_data) > 0:
    arc_layer = pdk.Layer(
        'ArcLayer',
        data=ml_links_data,
        get_source_position='[start_lon, start_lat]',
        get_target_position='[end_lon, end_lat]',
        get_source_color=[168, 85, 247, 255],  # Purple
        get_target_color=[168, 85, 247, 255],
        get_width=4,
        pickable=True,
        auto_highlight=True
    )
    layers.append(arc_layer)

# Layer 3: Asset nodes (ScatterplotLayer)
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

# Layer 4: Asset labels
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
center_lat = filtered_assets['LATITUDE'].mean()
center_lon = filtered_assets['LONGITUDE'].mean()

view_state = pdk.ViewState(
    latitude=float(center_lat),
    longitude=float(center_lon),
    zoom=9,
    pitch=45,
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

# Create the deck with map_style=None (critical for Snowflake Streamlit!)
deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=None,  # Required for Snowflake Streamlit
    tooltip=tooltip_config
)

# Title above map
st.markdown(f"""
<div style="text-align: center; color: #e2e8f0; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">
    Permian Basin Network Topology {'(AI-Enhanced)' if is_after_mode else '(Baseline)'}
</div>
""", unsafe_allow_html=True)

st.pydeck_chart(deck, use_container_width=True)

# Map legend
st.markdown("""
<div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 0.5rem; flex-wrap: wrap; font-size: 0.8rem;">
    <span style="color: #94a3b8;">
        <span style="display: inline-block; width: 10px; height: 10px; background: #0ea5e9; border-radius: 50%; margin-right: 4px;"></span>
        SnowCore
    </span>
    <span style="color: #94a3b8;">
        <span style="display: inline-block; width: 10px; height: 10px; background: #f43f5e; border-radius: 50%; margin-right: 4px;"></span>
        TeraField
    </span>
    <span style="color: #94a3b8;">
        <span style="display: inline-block; width: 10px; height: 10px; background: #fbbf24; border-radius: 50%; margin-right: 4px;"></span>
        High Risk
    </span>
    <span style="color: #94a3b8;">
        <span style="display: inline-block; width: 16px; height: 3px; background: #f59e0b; margin-right: 4px; vertical-align: middle;"></span>
        Cross-Network
    </span>
    <span style="color: #94a3b8;">
        <span style="display: inline-block; width: 16px; height: 3px; background: #a855f7; margin-right: 4px; vertical-align: middle;"></span>
        ML-Discovered
    </span>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# ASSET SELECTOR (Below Map)
# =============================================================================

st.markdown("<br>", unsafe_allow_html=True)

asset_col1, asset_col2, asset_col3 = st.columns([2, 3, 1])

with asset_col1:
    asset_list = assets_df['ASSET_ID'].tolist()
    selected_asset_id = st.selectbox(
        "🎯 Select Asset for Details",
        [""] + asset_list,
        index=0,
        help="Select an asset to view details and navigate to AI assistant"
    )

with asset_col2:
    if selected_asset_id:
        asset_row = assets_df[assets_df['ASSET_ID'] == selected_asset_id].iloc[0]
        system_color = '#0ea5e9' if asset_row['SOURCE_SYSTEM'] == 'SNOWCORE' else '#f43f5e'
        risk_color = '#ef4444' if asset_row['RISK_SCORE'] > 0.7 else '#f59e0b' if asset_row['RISK_SCORE'] > 0.4 else '#22c55e'
        
        st.markdown(f"""
        <div style="background: var(--slate-800); border-radius: 8px; padding: 0.75rem 1rem; border: 1px solid var(--slate-700); display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="color: {system_color}; font-weight: 600; font-size: 1rem;">{selected_asset_id}</span>
                <span style="color: var(--slate-400); font-size: 0.85rem; margin-left: 0.5rem;">{asset_row['ASSET_TYPE']}</span>
            </div>
            <div style="color: var(--slate-400); font-size: 0.85rem;">
                <span style="color: {system_color};">●</span> {asset_row['SOURCE_SYSTEM']} 
                <span style="margin-left: 1rem;">Max PSI: <strong style="color: var(--slate-200);">{asset_row['MAX_PRESSURE_RATING_PSI']:.0f}</strong></span>
                <span style="margin-left: 1rem;">Risk: <strong style="color: {risk_color};">{asset_row['RISK_SCORE']:.2f}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: var(--slate-800); border-radius: 8px; padding: 0.75rem 1rem; border: 1px solid var(--slate-700); color: var(--slate-500); font-size: 0.85rem;">
            Select an asset from the dropdown to view details
        </div>
        """, unsafe_allow_html=True)

with asset_col3:
    if selected_asset_id:
        asset_row = assets_df[assets_df['ASSET_ID'] == selected_asset_id].iloc[0]
        if st.button("💬 Ask AI", use_container_width=True, type="primary"):
            st.session_state.selected_asset_context = {
                'asset_id': selected_asset_id,
                'asset_type': asset_row['ASSET_TYPE'],
                'source_system': asset_row['SOURCE_SYSTEM'],
                'risk_score': float(asset_row['RISK_SCORE']),
                'max_pressure_rating': float(asset_row['MAX_PRESSURE_RATING_PSI']) if pd.notna(asset_row['MAX_PRESSURE_RATING_PSI']) else None,
                'latitude': float(asset_row['LATITUDE']),
                'longitude': float(asset_row['LONGITUDE'])
            }
            # Open the chat panel instead of navigating away
            st.session_state.show_chat_panel = True
            st.rerun()

# =============================================================================
# DISCOVERY DETAILS (only in After mode)
# =============================================================================

if is_after_mode:
    st.markdown("### 🧠 AutoGL Discovered Links")
    
    st.markdown("""
    <div class="teaching-panel">
        <h4>How Link Prediction Works</h4>
        <p>
            The AutoGL model encodes each asset as a 64-dimensional vector based on:
            <strong>node features</strong> (pressure rating, location, telemetry stats) and 
            <strong>neighborhood structure</strong> (connected assets). Assets with similar embeddings
            likely share operational dependencies, even if not documented in the pipeline registry.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if len(predicted_links_df) > 0:
        cols = st.columns(2)
        
        for i, (_, link) in enumerate(predicted_links_df.iterrows()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="discovery-card">
                    <div class="discovery-title">
                        {link['SOURCE']} ↔ {link['TARGET']}
                    </div>
                    <div class="discovery-content">
                        <span class="discovery-score">Score: {link['SCORE']:.2f}</span>
                        <span class="discovery-score">Confidence: {link['CONFIDENCE']:.2f}</span>
                        <br><br>
                        {link['EXPLANATION']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No additional links discovered above the 0.5 probability threshold.")

# =============================================================================
# RISK PROPAGATION PATH
# =============================================================================

st.markdown("### 🚨 Critical Risk Path: The Hidden Bottleneck")

st.markdown("""
<div class="risk-path-card">
    <div class="risk-path-title">Pressure Cascade: SC-PAD-42 → TF-V-204</div>
    <p style="color: #94a3b8; margin-bottom: 1rem;">
        This flow path crosses the network boundary through PIPE-88. When SnowCore production ramps up,
        pressure propagates to legacy TeraField equipment with lower ratings.
    </p>
</div>
""", unsafe_allow_html=True)

# Create pressure path visualization
path_assets = ['SC-PAD-42', 'SC-SEP-101', 'TF-V-204', 'TF-VALVE-101', 'TF-MID-HUB']
path_data = []

for asset_id in path_assets:
    asset = assets_df[assets_df['ASSET_ID'] == asset_id]
    if len(asset) > 0:
        path_data.append({
            'Asset': asset_id,
            'System': asset['SOURCE_SYSTEM'].values[0],
            'Type': asset['ASSET_TYPE'].values[0],
            'Max PSI': asset['MAX_PRESSURE_RATING_PSI'].values[0],
            'Risk Score': asset['RISK_SCORE'].values[0]
        })

path_df = pd.DataFrame(path_data)

# Pressure capacity chart
fig_path = go.Figure()

colors = ['#0ea5e9' if row['System'] == 'SNOWCORE' else '#f43f5e' for _, row in path_df.iterrows()]
border_colors = ['#fbbf24' if row['Risk Score'] > 0.7 else color for (_, row), color in zip(path_df.iterrows(), colors)]

fig_path.add_trace(go.Bar(
    x=path_df['Asset'],
    y=path_df['Max PSI'],
        marker=dict(
            color=colors,
        line=dict(color=border_colors, width=3)
    ),
    text=[f"{psi:.0f} PSI" for psi in path_df['Max PSI']],
    textposition='outside',
    textfont=dict(color='#e2e8f0', size=11),
    hovertemplate='<b>%{x}</b><br>Max Rating: %{y:.0f} PSI<extra></extra>'
))

# Add danger line at 800 PSI (projected pressure)
fig_path.add_hline(
    y=800,
    line_dash="dash",
    line_color="#ef4444",
    annotation_text="Projected Pressure: 800 PSI",
    annotation_position="top right",
    annotation_font=dict(color='#ef4444', size=11)
)

fig_path.update_layout(
    title=dict(
        text='Pressure Rating Along Flow Path',
        font=dict(color='#e2e8f0', size=14),
        x=0.5
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#1e293b',
    font=dict(color='#94a3b8'),
    xaxis=dict(
        title='',
        gridcolor='#334155',
        tickfont=dict(color='#e2e8f0')
    ),
    yaxis=dict(
        title='Max Pressure Rating (PSI)',
        gridcolor='#334155',
        range=[0, 1800]
    ),
    height=350,
    showlegend=False
)

st.plotly_chart(fig_path, use_container_width=True)

# Bottleneck explanation
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="bottleneck-card">
        <div class="bottleneck-title">⚠️ TF-V-204: The Critical Bottleneck</div>
        <p style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.7;">
            <strong>Equipment:</strong> TeraField 2-Phase Vertical Separator<br>
            <strong>Manufacturer:</strong> Natco (2012)<br>
            <strong>Max Rating:</strong> 600 PSI (MAWP)<br>
            <strong>Projected Pressure:</strong> 800 PSI 🔴<br><br>
            <strong>Source:</strong> P&ID Document TF-MID-001<br>
            <strong>Known Issue:</strong> Bypass valve sticks above 550 PSI (Maintenance ticket MT-2023-4421)
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="teaching-panel">
        <h4>Why This Couldn't Be Found Before</h4>
        <p>
            <strong>The Problem:</strong> PIPE-88 connects SnowCore's separator (SC-SEP-101) to 
            TeraField's legacy equipment (TF-V-204), but this connection was only documented 
            in TeraField's local SCADA system.
        </p>
        <p>
            <strong>The Solution:</strong> AutoGL analyzes telemetry correlations across both 
            networks. When SC-PAD-42 flow increases, TF-V-204 pressure rises 5 minutes later — 
            a time-lagged correlation that revealed the hidden dependency.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# NETWORK STATISTICS COMPARISON
# =============================================================================

st.markdown("### 📊 Network Statistics: Before vs After AutoGL")

col1, col2, col3, col4 = st.columns(4)

# Calculate graph metrics
G_before = nx.Graph()
for _, edge in edges_df.iterrows():
    G_before.add_edge(edge['SOURCE_ASSET_ID'], edge['TARGET_ASSET_ID'])

G_after = G_before.copy()
for _, link in predicted_links_df.iterrows():
    G_after.add_edge(link['SOURCE'], link['TARGET'])

components_before = nx.number_connected_components(G_before)
components_after = nx.number_connected_components(G_after)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-value" style="color: #64748b;">{len(edges_df)}</div>
        <div class="stats-label">Edges (Before)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-value" style="color: #a855f7;">{len(edges_df) + len(predicted_links_df)}</div>
        <div class="stats-label">Edges (After)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-value" style="color: #64748b;">{components_before}</div>
        <div class="stats-label">Connected Components (Before)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-value" style="color: #22c55e;">{components_after}</div>
        <div class="stats-label">Connected Components (After)</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ASSET DETAILS TABLE
# =============================================================================

st.markdown("### 📋 Equipment Registry Comparison")

# Add filters
col1, col2, col3 = st.columns(3)

with col1:
    system_filter = st.selectbox("Filter by System", ["All", "SNOWCORE", "TERAFIELD"])

with col2:
    type_filter = st.selectbox("Filter by Type", ["All"] + list(assets_df['ASSET_TYPE'].unique()))

with col3:
    risk_filter = st.selectbox("Filter by Risk", ["All", "High Risk (>0.7)", "Elevated (>0.4)", "Normal"])

# Apply filters
display_df = assets_df.copy()

if system_filter != "All":
    display_df = display_df[display_df['SOURCE_SYSTEM'] == system_filter]

if type_filter != "All":
    display_df = display_df[display_df['ASSET_TYPE'] == type_filter]

if risk_filter == "High Risk (>0.7)":
    display_df = display_df[display_df['RISK_SCORE'] > 0.7]
elif risk_filter == "Elevated (>0.4)":
    display_df = display_df[display_df['RISK_SCORE'] > 0.4]
elif risk_filter == "Normal":
    display_df = display_df[display_df['RISK_SCORE'] <= 0.4]

# Format for display
display_df = display_df[['ASSET_ID', 'SOURCE_SYSTEM', 'ASSET_TYPE', 'MAX_PRESSURE_RATING_PSI', 'INSTALL_DATE', 'RISK_SCORE', 'ZONE']].copy()
display_df = display_df.sort_values('RISK_SCORE', ascending=False)
display_df['RISK_SCORE'] = display_df['RISK_SCORE'].apply(lambda x: f"{x:.2f}")
display_df['MAX_PRESSURE_RATING_PSI'] = display_df['MAX_PRESSURE_RATING_PSI'].apply(lambda x: f"{x:.0f}")
display_df.columns = ['Asset ID', 'System', 'Type', 'Max PSI', 'Install Date', 'Risk Score', 'Zone']

st.dataframe(
    display_df,
    use_container_width=True,
    height=350,
    column_config={
        "Asset ID": st.column_config.TextColumn("Asset ID", width="medium"),
        "System": st.column_config.TextColumn("System", width="small"),
        "Type": st.column_config.TextColumn("Type", width="medium"),
        "Max PSI": st.column_config.TextColumn("Max PSI", width="small"),
        "Install Date": st.column_config.DateColumn("Install Date", width="small"),
        "Risk Score": st.column_config.TextColumn("Risk Score", width="small"),
        "Zone": st.column_config.TextColumn("Zone", width="small")
    }
)

# High risk quick select
high_risk_assets = assets_df[assets_df['RISK_SCORE'] > 0.7].nlargest(3, 'RISK_SCORE')

if len(high_risk_assets) > 0:
    st.markdown("#### ⚠️ Quick Actions: High Risk Assets")
    
    cols = st.columns(len(high_risk_assets))
    
    for i, (_, hr_asset) in enumerate(high_risk_assets.iterrows()):
        with cols[i]:
            if st.button(
                f"🔴 {hr_asset['ASSET_ID']} ({hr_asset['RISK_SCORE']:.2f})",
                key=f"hr_{hr_asset['ASSET_ID']}",
                use_container_width=True
            ):
                st.session_state.selected_asset_context = {
                    'asset_id': hr_asset['ASSET_ID'],
                    'asset_type': hr_asset['ASSET_TYPE'],
                    'source_system': hr_asset['SOURCE_SYSTEM'],
                    'risk_score': float(hr_asset['RISK_SCORE']),
                    'max_pressure_rating': float(hr_asset['MAX_PRESSURE_RATING_PSI']) if pd.notna(hr_asset['MAX_PRESSURE_RATING_PSI']) else None,
                    'latitude': float(hr_asset['LATITUDE']),
                    'longitude': float(hr_asset['LONGITUDE'])
                }
                # Open chat panel instead of navigating
                st.session_state.show_chat_panel = True
                st.rerun()

# =============================================================================
# RIGHT CHAT PANEL
# =============================================================================

if st.session_state.get('show_chat_panel', False):
    with st.container():
        st.markdown("---")
        st.markdown("### 💬 AI Integration Assistant")
        render_chat_panel(session, SCHEMA_PREFIX, assets_df, panel_key="network")
