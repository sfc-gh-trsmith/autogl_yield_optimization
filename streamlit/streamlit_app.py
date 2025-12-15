"""
SnowCore Permian Command Center - Executive Dashboard
======================================================
Strategic visualization for the VP of Permian Integration.
Demonstrates how AutoGL + Cortex AI solves the post-merger data fragmentation challenge.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.chat_panel import render_chat_panel, get_chat_panel_css

# Page configuration
st.set_page_config(
    page_title="Permian Command Center",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive dashboard styling
st.markdown("""
<style>
    /* Import distinctive font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    /* Main theme colors - Industrial/Energy aesthetic */
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
        --accent-amber: #f59e0b;
    }
    
    * {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre, .stCode {
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    /* Dark theme background with subtle gradient */
    .stApp {
        background: linear-gradient(180deg, var(--slate-950) 0%, var(--slate-900) 100%);
    }
    
    /* Problem statement banner */
    .problem-banner {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .problem-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--terafield-red) 0%, var(--snowcore-blue) 100%);
    }
    
    .problem-banner h1 {
        color: var(--slate-200);
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        letter-spacing: -0.02em;
    }
    
    .problem-banner p {
        color: var(--slate-400);
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1.25rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--slate-700);
    }
    
    .section-header h2 {
        color: var(--slate-200);
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    .section-number {
        background: var(--slate-700);
        color: var(--accent-cyan);
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.625rem;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--slate-700);
        text-align: center;
        transition: border-color 0.2s;
    }
    
    .metric-card:hover {
        border-color: var(--slate-600);
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--slate-400);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.75rem;
        margin-top: 0.25rem;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    /* System comparison cards */
    .system-card {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--slate-700);
        height: 100%;
    }
    
    .system-card.snowcore {
        border-left: 4px solid var(--snowcore-blue);
    }
    
    .system-card.terafield {
        border-left: 4px solid var(--terafield-red);
    }
    
    .system-name {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .system-name.snowcore { color: var(--snowcore-blue); }
    .system-name.terafield { color: var(--terafield-red); }
    
    .system-subtitle {
        font-size: 0.85rem;
        color: var(--slate-400);
        margin-bottom: 1rem;
    }
    
    .system-stat {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--slate-700);
    }
    
    .system-stat:last-child {
        border-bottom: none;
    }
    
    .stat-label {
        color: var(--slate-400);
        font-size: 0.875rem;
    }
    
    .stat-value {
        color: var(--slate-200);
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    /* KPI target cards */
    .kpi-card {
        background: linear-gradient(135deg, var(--slate-800) 0%, rgba(30, 41, 59, 0.8) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--slate-700);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--cortex-purple) 100%);
    }
    
    .kpi-target {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-cyan);
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .kpi-label {
        font-size: 0.875rem;
        color: var(--slate-300);
        margin-top: 0.25rem;
    }
    
    .kpi-description {
        font-size: 0.8rem;
        color: var(--slate-400);
        margin-top: 0.75rem;
        line-height: 1.5;
    }
    
    /* Data quality indicator */
    .quality-good {
        color: var(--risk-low);
    }
    
    .quality-poor {
        color: var(--risk-high);
    }
    
    /* Teaching expandable section */
    .teaching-section {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--slate-700);
        margin-top: 1rem;
    }
    
    .teaching-section h3 {
        color: var(--cortex-purple);
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .teaching-section p, .teaching-section li {
        color: var(--slate-300);
        font-size: 0.9rem;
        line-height: 1.7;
    }
    
    /* Alert card */
    .alert-card {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--risk-high);
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }
    
    .alert-title {
        color: var(--risk-high);
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .alert-content {
        color: var(--slate-200);
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--slate-800);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--accent-cyan);
    }
    
    /* Data flow diagram */
    .flow-step {
        background: var(--slate-800);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid var(--slate-700);
        text-align: center;
    }
    
    .flow-arrow {
        color: var(--slate-600);
        font-size: 1.5rem;
        text-align: center;
        padding: 0.5rem 0;
    }
    
    /* Hide default Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide default page navigation to use custom navigation */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Right chat panel styling */
    .right-chat-panel {
        position: fixed;
        right: 20px;
        top: 80px;
        width: 320px;
        max-height: calc(100vh - 100px);
        background: var(--slate-800);
        border-radius: 12px;
        border: 1px solid var(--slate-700);
        box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        overflow: hidden;
    }
    
    .right-chat-panel-inner {
        padding: 1rem;
        height: 100%;
        overflow-y: auto;
    }
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
    key="toggle_chat_home",
    use_container_width=True
):
    st.session_state.show_chat_panel = not st.session_state.show_chat_panel
    st.rerun()

st.sidebar.markdown("---")

# Initialize Snowflake session
from snowflake.snowpark.context import get_active_session

# Fully qualified table names
SCHEMA_PREFIX = "AUTOGL_YIELD_OPTIMIZATION.AUTOGL_YIELD_OPTIMIZATION"

@st.cache_resource
def get_session():
    return get_active_session()

session = get_session()

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def load_asset_data():
    """Load asset master data with aggregations."""
    assets = session.sql(f"""
        SELECT 
            ASSET_ID,
            SOURCE_SYSTEM,
            ASSET_TYPE,
            ASSET_SUBTYPE,
            MAX_PRESSURE_RATING_PSI,
            MANUFACTURER,
            INSTALL_DATE,
            ZONE,
            LATITUDE,
            LONGITUDE
        FROM {SCHEMA_PREFIX}.ASSET_MASTER
    """).to_pandas()
    return assets

@st.cache_data(ttl=300)
def load_scada_aggregates():
    """Load SCADA aggregates for data quality analysis."""
    return session.sql(f"""
        SELECT 
            ASSET_ID,
            RECORD_DATE,
            SOURCE_SYSTEM,
            ZONE,
            ASSET_TYPE,
            AVG_FLOW_RATE_BOPD,
            TOTAL_PRODUCTION_BBL,
            AVG_PRESSURE_PSI,
            MAX_PRESSURE_PSI,
            PRESSURE_VARIANCE,
            AVG_TEMPERATURE_F,
            READING_COUNT,
            DOWNTIME_HOURS
        FROM {SCHEMA_PREFIX}.SCADA_AGGREGATES
        ORDER BY RECORD_DATE, ASSET_ID
    """).to_pandas()
    
@st.cache_data(ttl=300)
def load_network_edges():
    """Load network edge data."""
    return session.sql(f"""
        SELECT 
            SEGMENT_ID,
            SOURCE_ASSET_ID,
            TARGET_ASSET_ID,
            LINE_DIAMETER_INCHES,
            MAX_PRESSURE_RATING_PSI,
            STATUS,
            LENGTH_MILES
        FROM {SCHEMA_PREFIX}.NETWORK_EDGES
    """).to_pandas()
    
@st.cache_data(ttl=300)
def load_predictions():
    """Load graph predictions."""
    return session.sql(f"""
        SELECT 
            PREDICTION_TYPE,
            ENTITY_ID,
            RELATED_ENTITY_ID,
            SCORE,
            CONFIDENCE,
            EXPLANATION
        FROM {SCHEMA_PREFIX}.GRAPH_PREDICTIONS
    """).to_pandas()

# Load all data
assets_df = load_asset_data()
scada_df = load_scada_aggregates()
edges_df = load_network_edges()
predictions_df = load_predictions()

# =============================================================================
# SECTION 1: PROBLEM STATEMENT BANNER
# =============================================================================

st.markdown("""
<div class="problem-banner">
    <h1>🛢️ SnowCore Permian Command Center</h1>
    <p>
        Following the acquisition of <strong>TeraField Resources</strong>, SnowCore Energy now operates two distinct, 
        disconnected gathering networks in the Permian Basin. Critical data regarding pipeline connectivity, 
        pressure ratings, and maintenance history is trapped in <strong>incompatible legacy SCADA systems</strong> 
        and static PDF P&IDs. This data fragmentation creates "blind spots," making it impossible to optimize 
        flow across the combined network or predict how new drilling in SnowCore zones will impact downstream 
        TeraField facilities.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECTION 2: ASSET REGISTRY COMPARISON
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">01</span>
    <h2>Asset Registry Comparison: Two Worlds, One Challenge</h2>
</div>
""", unsafe_allow_html=True)

# Calculate asset statistics
snowcore_assets = assets_df[assets_df['SOURCE_SYSTEM'] == 'SNOWCORE']
terafield_assets = assets_df[assets_df['SOURCE_SYSTEM'] == 'TERAFIELD']

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="system-card snowcore">
        <div class="system-name snowcore">SnowCore Energy</div>
        <div class="system-subtitle">Modern Infrastructure (2020-2023)</div>
        <div class="system-stat">
            <span class="stat-label">Total Assets</span>
            <span class="stat-value">{len(snowcore_assets)}</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">Data Source</span>
            <span class="stat-value">OSIsoft PI / AVEVA</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">ERP System</span>
            <span class="stat-value">SAP S/4HANA</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">Avg Pressure Rating</span>
            <span class="stat-value">{snowcore_assets['MAX_PRESSURE_RATING_PSI'].mean():.0f} PSI</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">Tag Convention</span>
            <span class="stat-value">ISA-95 Hierarchical</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="system-card terafield">
        <div class="system-name terafield">TeraField Resources (Acquired)</div>
        <div class="system-subtitle">Legacy Infrastructure (2011-2017)</div>
        <div class="system-stat">
            <span class="stat-label">Total Assets</span>
            <span class="stat-value">{len(terafield_assets)}</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">Data Source</span>
            <span class="stat-value">CygNet / Rockwell</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">ERP System</span>
            <span class="stat-value">IBM Maximo (Legacy)</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">Avg Pressure Rating</span>
            <span class="stat-value">{terafield_assets['MAX_PRESSURE_RATING_PSI'].mean():.0f} PSI</span>
        </div>
        <div class="system-stat">
            <span class="stat-label">Tag Convention</span>
            <span class="stat-value">Flat / Cryptic IDs</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Asset type breakdown chart
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Asset types by source system
    asset_types = assets_df.groupby(['SOURCE_SYSTEM', 'ASSET_TYPE']).size().reset_index(name='COUNT')
    
    fig_types = px.bar(
        asset_types,
        x='ASSET_TYPE',
        y='COUNT',
        color='SOURCE_SYSTEM',
        barmode='group',
        color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
        title='Asset Types by Source System'
    )
    fig_types.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        title_font=dict(color='#e2e8f0', size=14),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(gridcolor='#334155', title=''),
        yaxis=dict(gridcolor='#334155', title='Count'),
        height=300
    )
    st.plotly_chart(fig_types, use_container_width=True)

with col2:
    # Pressure rating distribution
    fig_pressure = go.Figure()
    
    fig_pressure.add_trace(go.Box(
        y=snowcore_assets['MAX_PRESSURE_RATING_PSI'],
        name='SnowCore',
        marker_color='#0ea5e9',
        boxmean=True
    ))
    
    fig_pressure.add_trace(go.Box(
        y=terafield_assets['MAX_PRESSURE_RATING_PSI'],
        name='TeraField',
        marker_color='#f43f5e',
        boxmean=True
    ))
    
    fig_pressure.update_layout(
        title='Pressure Rating Distribution (PSI)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        title_font=dict(color='#e2e8f0', size=14),
        yaxis=dict(gridcolor='#334155', title='Max PSI Rating'),
        xaxis=dict(title=''),
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig_pressure, use_container_width=True)

# Expandable teaching section
with st.expander("📚 Why This Matters: The Pressure Mismatch Problem"):
    st.markdown("""
    **The Hidden Risk:** SnowCore's modern equipment operates at **1,000-1,500 PSI**, while TeraField's legacy 
    separators and valves are rated for only **500-800 PSI**. When production from new SnowCore wells flows 
    into acquired TeraField infrastructure, pressure mismatches can cause:
    
    - **Equipment failures** from exceeding design limits
    - **Unplanned flaring** when safety systems activate
    - **Production deferment** while repairs are made
    
    **The Challenge:** Without unified visibility across both systems, operators cannot predict these 
    interactions until an alarm sounds.
    """)

# =============================================================================
# SECTION 3: DATA QUALITY DASHBOARD
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">02</span>
    <h2>Data Quality: The Legacy System Challenge</h2>
</div>
""", unsafe_allow_html=True)

# Calculate data quality metrics by source system
snowcore_scada = scada_df[scada_df['SOURCE_SYSTEM'] == 'SNOWCORE']
terafield_scada = scada_df[scada_df['SOURCE_SYSTEM'] == 'TERAFIELD']

# Expected readings per day per asset = 1440 (1-minute intervals)
EXPECTED_READINGS_PER_DAY = 1440

col1, col2, col3, col4 = st.columns(4)

with col1:
    sc_completeness = (snowcore_scada['READING_COUNT'].mean() / EXPECTED_READINGS_PER_DAY) * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value quality-good">{sc_completeness:.1f}%</div>
        <div class="metric-label">SnowCore Data Completeness</div>
        <div class="metric-delta quality-good">✓ High-frequency sampling</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    tf_completeness = (terafield_scada['READING_COUNT'].mean() / EXPECTED_READINGS_PER_DAY) * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value quality-poor">{tf_completeness:.1f}%</div>
        <div class="metric-label">TeraField Data Completeness</div>
        <div class="metric-delta quality-poor">⚠ Communication gaps</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    sc_downtime = snowcore_scada.groupby('RECORD_DATE')['DOWNTIME_HOURS'].sum().mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #0ea5e9;">{sc_downtime:.1f}h</div>
        <div class="metric-label">SnowCore Avg Daily Downtime</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    tf_downtime = terafield_scada.groupby('RECORD_DATE')['DOWNTIME_HOURS'].sum().mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #f43f5e;">{tf_downtime:.1f}h</div>
        <div class="metric-label">TeraField Avg Daily Downtime</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Telemetry quality comparison chart
col1, col2 = st.columns(2)

with col1:
    # Pressure variance comparison (indicator of signal noise)
    daily_pressure = scada_df.groupby(['RECORD_DATE', 'SOURCE_SYSTEM']).agg({
        'AVG_PRESSURE_PSI': 'mean',
        'PRESSURE_VARIANCE': 'mean'
    }).reset_index()
    
    fig_variance = px.line(
        daily_pressure,
        x='RECORD_DATE',
        y='PRESSURE_VARIANCE',
        color='SOURCE_SYSTEM',
        color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
        title='Signal Noise: Pressure Variance Over Time'
    )
    fig_variance.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        title_font=dict(color='#e2e8f0', size=14),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(gridcolor='#334155', title=''),
        yaxis=dict(gridcolor='#334155', title='Variance'),
        height=280
    )
    st.plotly_chart(fig_variance, use_container_width=True)

with col2:
    # Reading count over time (data completeness)
    daily_readings = scada_df.groupby(['RECORD_DATE', 'SOURCE_SYSTEM'])['READING_COUNT'].sum().reset_index()
    
    fig_readings = px.area(
        daily_readings,
        x='RECORD_DATE',
        y='READING_COUNT',
        color='SOURCE_SYSTEM',
        color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
        title='Data Completeness: Reading Count by Day'
    )
    fig_readings.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        title_font=dict(color='#e2e8f0', size=14),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(gridcolor='#334155', title=''),
        yaxis=dict(gridcolor='#334155', title='Total Readings'),
        height=280
    )
    st.plotly_chart(fig_readings, use_container_width=True)

# Teaching section on data quality
with st.expander("📚 Understanding the Data Quality Gap"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **SnowCore (Modern):**
        - 1-second sampling rate from OSIsoft PI
        - Clean digital signals with low noise
        - Hierarchical ISA-95 tag naming
        - Example: `DELAWARE/PAD_42/SEP_V101/PRESS_PV`
        """)
    
    with col2:
        st.markdown("""
        **TeraField (Legacy):**
        - 1-minute polling from CygNet
        - Higher noise, "deadband" artifacts
        - Flat cryptic tag naming
        - Example: `TF_MID_HUB_V204_P`
        - Communication failure gaps (2% of readings missing)
        """)

# =============================================================================
# SECTION 4: NETWORK CONNECTIVITY - THE GAP
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">03</span>
    <h2>Network Connectivity: The Integration Gap</h2>
</div>
""", unsafe_allow_html=True)

# Calculate network statistics
active_edges = edges_df[edges_df['STATUS'] == 'ACTIVE']
planned_edges = edges_df[edges_df['STATUS'] == 'PLANNED']

# Count cross-network edges
cross_network_edges = []
for _, edge in active_edges.iterrows():
    src_system = assets_df[assets_df['ASSET_ID'] == edge['SOURCE_ASSET_ID']]['SOURCE_SYSTEM'].values
    tgt_system = assets_df[assets_df['ASSET_ID'] == edge['TARGET_ASSET_ID']]['SOURCE_SYSTEM'].values
    if len(src_system) > 0 and len(tgt_system) > 0:
        if src_system[0] != tgt_system[0]:
            cross_network_edges.append(edge)

col1, col2, col3 = st.columns(3)

with col1:
    snowcore_internal = len(active_edges) - len(cross_network_edges) - len(terafield_scada['ASSET_ID'].unique()) // 2
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #0ea5e9;">8</div>
        <div class="metric-label">SnowCore Internal Pipelines</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #f43f5e;">7</div>
        <div class="metric-label">TeraField Internal Pipelines</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #f59e0b;">{len(cross_network_edges)}</div>
        <div class="metric-label">Known Cross-Network Links</div>
        <div class="metric-delta" style="color: #a855f7;">+{len(predictions_df[predictions_df['PREDICTION_TYPE'] == 'LINK_PREDICTION'])} discovered by AutoGL</div>
    </div>
    """, unsafe_allow_html=True)

# Network visualization showing two clusters on actual map
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #e2e8f0; font-size: 1rem; font-weight: 600; margin-bottom: 0.75rem;">
    Permian Basin Network: Two Disconnected Clusters
</div>
""", unsafe_allow_html=True)

# Prepare data for PyDeck visualization as lists of dicts (avoids serialization issues)
# Asset nodes with color based on source system
asset_data = []
for _, row in assets_df.iterrows():
    color = [14, 165, 233, 220] if row['SOURCE_SYSTEM'] == 'SNOWCORE' else [244, 63, 94, 220]
    asset_data.append({
        'ASSET_ID': row['ASSET_ID'],
        'SOURCE_SYSTEM': row['SOURCE_SYSTEM'],
        'ASSET_TYPE': row['ASSET_TYPE'],
        'LATITUDE': float(row['LATITUDE']),
        'LONGITUDE': float(row['LONGITUDE']),
        'MAX_PRESSURE_RATING_PSI': float(row['MAX_PRESSURE_RATING_PSI']) if pd.notna(row['MAX_PRESSURE_RATING_PSI']) else 0,
        'color': color,
        'radius': 800
    })

# Prepare pipeline edges data for LineLayer
pipeline_data = []
for _, edge in active_edges.iterrows():
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
        pickable=True
    )
    layers.append(line_layer)

# Layer 2: Asset nodes (ScatterplotLayer)
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

    # Layer 3: Asset labels using TextLayer
    text_layer = pdk.Layer(
        'TextLayer',
        data=asset_data,
        get_position='[LONGITUDE, LATITUDE]',
        get_text='ASSET_ID',
        get_size=12,
        get_color=[226, 232, 240, 255],  # slate-200
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
    zoom=8.5,
    pitch=45,
    bearing=0
)

# Create the deck with map_style=None (critical for Snowflake Streamlit!)
deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=None,  # Required for Snowflake Streamlit - lets platform pick appropriate provider
    tooltip={
        'html': '<b>{ASSET_ID}</b><br>System: {SOURCE_SYSTEM}<br>Type: {ASSET_TYPE}<br>Max PSI: {MAX_PRESSURE_RATING_PSI}',
        'style': {
            'backgroundColor': '#1e293b',
            'color': '#e2e8f0',
            'borderRadius': '8px',
            'padding': '8px',
            'border': '1px solid #334155'
        }
    }
)

st.pydeck_chart(deck, use_container_width=True)

# Legend for the map
st.markdown("""
<div style="display: flex; justify-content: center; gap: 2rem; margin-top: 0.75rem; flex-wrap: wrap;">
    <span style="color: #94a3b8; font-size: 0.85rem;">
        <span style="display: inline-block; width: 12px; height: 12px; background: #0ea5e9; border-radius: 50%; margin-right: 6px;"></span>
        SnowCore Assets
    </span>
    <span style="color: #94a3b8; font-size: 0.85rem;">
        <span style="display: inline-block; width: 12px; height: 12px; background: #f43f5e; border-radius: 50%; margin-right: 6px;"></span>
        TeraField Assets
    </span>
    <span style="color: #94a3b8; font-size: 0.85rem;">
        <span style="display: inline-block; width: 20px; height: 3px; background: #f59e0b; margin-right: 6px; vertical-align: middle;"></span>
        Cross-Network Pipeline
    </span>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECTION 5: BUSINESS KPIs - SYNERGY TARGETS
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">04</span>
    <h2>Business KPIs: Integration Synergy Targets</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Calculate production totals
latest_date = scada_df['RECORD_DATE'].max()
daily_production = scada_df[scada_df['RECORD_DATE'] == latest_date]['TOTAL_PRODUCTION_BBL'].sum()

# Risk counts from predictions
node_anomalies = predictions_df[predictions_df['PREDICTION_TYPE'] == 'NODE_ANOMALY']
high_risk_count = len(node_anomalies[node_anomalies['SCORE'] > 0.7])
link_predictions = predictions_df[predictions_df['PREDICTION_TYPE'] == 'LINK_PREDICTION']

with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-target">$500M</div>
        <div class="kpi-label">Synergy Target</div>
        <div class="kpi-description">
            Optimize flow routing across the combined network without laying new pipe
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-target">-15%</div>
        <div class="kpi-label">Deferment Reduction</div>
        <div class="kpi-description">
            Predict systemic pressure bottlenecks at SnowCore/TeraField interfaces
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-target" style="color: {'#ef4444' if high_risk_count > 0 else '#22c55e'};">{high_risk_count}</div>
        <div class="kpi-label">High-Risk Assets Identified</div>
        <div class="kpi-description">
            AutoGL detected pressure anomaly risks requiring attention
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-target" style="color: #a855f7;">{len(link_predictions)}</div>
        <div class="kpi-label">Hidden Links Discovered</div>
        <div class="kpi-description">
            Cross-network dependencies identified by graph neural network
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SECTION 6: THE SOLUTION - HOW IT WORKS
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">05</span>
    <h2>The Solution: AutoGL + Cortex AI Integration</h2>
</div>
""", unsafe_allow_html=True)

# Solution overview in tabs
tab1, tab2, tab3 = st.tabs(["🔗 Data Integration", "🧠 AI Capabilities", "🎯 Key Discovery"])

with tab1:
    st.markdown("""
    ### From Fragmented Data to Unified Intelligence
    
    The Snowflake platform unifies both data sources into a single, queryable environment:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="teaching-section">
            <h3>📥 Data Ingestion</h3>
            <p><strong>SnowCore Sources:</strong></p>
            <ul>
                <li>OSIsoft PI Historian → SCADA_TELEMETRY</li>
                <li>SAP ERP → ASSET_MASTER</li>
            </ul>
            <p><strong>TeraField Sources:</strong></p>
            <ul>
                <li>CygNet SCADA → SCADA_TELEMETRY</li>
                <li>IBM Maximo → ASSET_MASTER</li>
                <li>PDF P&IDs → DOCS_STAGE</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="teaching-section">
            <h3>🔄 Unified Schema</h3>
            <p>All data normalized to common tables:</p>
            <ul>
                <li><code>ASSET_MASTER</code> - Equipment registry</li>
                <li><code>NETWORK_EDGES</code> - Pipeline connections</li>
                <li><code>SCADA_TELEMETRY</code> - Sensor time-series</li>
                <li><code>SCADA_AGGREGATES</code> - Daily rollups</li>
            </ul>
            <p><code>SOURCE_SYSTEM</code> column preserves lineage.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="teaching-section">
            <h3>📊 Analysis Ready</h3>
            <p>Cross-system queries now possible:</p>
            <ul>
                <li>Compare downtime by source</li>
                <li>Track pressure across boundaries</li>
                <li>Correlate flow patterns</li>
                <li>Identify bottlenecks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    ### Three AI Services Working Together
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="teaching-section" style="border-left: 4px solid #0ea5e9;">
            <h3>🔍 Cortex Search</h3>
            <p><strong>Purpose:</strong> Extract knowledge from unstructured P&ID documents</p>
            <p><strong>Example Query:</strong></p>
            <p><em>"What is the maximum pressure rating for Separator V-204?"</em></p>
            <p><strong>Result:</strong> Extracts "MAWP: 600 PSIG" from TeraField P&ID PDF</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="teaching-section" style="border-left: 4px solid #a855f7;">
            <h3>📈 Cortex Analyst</h3>
            <p><strong>Purpose:</strong> Natural language to SQL for structured data</p>
            <p><strong>Example Query:</strong></p>
            <p><em>"Compare downtime between legacy and acquired assets"</em></p>
            <p><strong>Result:</strong> Generates SQL against SCADA_AGGREGATES</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="teaching-section" style="border-left: 4px solid #f43f5e;">
            <h3>🤖 Cortex Agent</h3>
            <p><strong>Purpose:</strong> Reason across both structured and unstructured data</p>
            <p><strong>Example:</strong></p>
            <p><em>"Can I route 5k extra barrels through Midland Hub?"</em></p>
            <p><strong>Result:</strong> Checks model predictions AND P&ID specs to approve/deny</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="teaching-section" style="border-left: 4px solid #06b6d4;">
        <h3>🧬 AutoGL Graph Neural Network</h3>
        <p><strong>Purpose:</strong> Learn hidden patterns in the network topology</p>
        <ul>
            <li><strong>Link Prediction:</strong> Discovers probable connections between assets that aren't in the edge table</li>
            <li><strong>Node Anomaly Detection:</strong> Predicts which assets are at risk based on their position in the graph and telemetry patterns</li>
        </ul>
        <p>The model encodes each asset as a vector based on its features (pressure rating, location, telemetry stats) and its neighbors in the graph. 
        Assets with similar vectors likely share hidden dependencies.</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    ### The Critical Discovery: TF-V-204
    
    AutoGL's most important finding is a hidden pressure cascade risk:
    """)
    
    # Get TF-V-204 prediction
    tf_v204_pred = node_anomalies[node_anomalies['ENTITY_ID'] == 'TF-V-204']
    
    if len(tf_v204_pred) > 0:
        risk_score = tf_v204_pred['SCORE'].values[0]
        explanation = tf_v204_pred['EXPLANATION'].values[0]
        
        st.markdown(f"""
        <div class="alert-card" style="background: rgba(239, 68, 68, 0.15); border-left-color: #ef4444;">
            <div class="alert-title">🚨 HIGH RISK DETECTED: TF-V-204</div>
            <div class="alert-content">
                <strong>Risk Score:</strong> {risk_score:.2f}<br><br>
                <strong>Analysis:</strong> {explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **The Flow Path:**
        ```
        SC-PAD-42 (1500 PSI rating)
            ↓ PIPE-01
        SC-SEP-101 (1440 PSI rating)
            ↓ PIPE-88 (cross-network!)
        TF-V-204 (600 PSI rating) ⚠️
            ↓ PIPE-TF-01
        TF-VALVE-101 (550 PSI rating) ⚠️
        ```
        """)
    
    with col2:
        st.markdown("""
        **Why This Matters:**
        
        When SnowCore Pad 42 ramps production, pressure propagates through PIPE-88 
        to TeraField's legacy separator TF-V-204. The model detected:
        
        - TF-V-204 is rated for only **600 PSI**
        - Projected pressure could reach **800 PSI**
        - Bypass valve has known issues (per maintenance logs)
        
        **Without AutoGL:** This risk was invisible because the cross-network 
        connection wasn't documented in either system's asset registry.
        """)

# =============================================================================
# ACTIVE ALERTS
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">06</span>
    <h2>Active Risk Alerts</h2>
</div>
""", unsafe_allow_html=True)

# Get high-risk predictions with asset details
high_risk = node_anomalies[node_anomalies['SCORE'] > 0.5].sort_values('SCORE', ascending=False)

if len(high_risk) > 0:
    for _, alert in high_risk.head(5).iterrows():
        asset_info = assets_df[assets_df['ASSET_ID'] == alert['ENTITY_ID']]
        if len(asset_info) > 0:
            asset = asset_info.iloc[0]
            severity = "HIGH" if alert['SCORE'] > 0.7 else "MEDIUM"
            color = "#ef4444" if severity == "HIGH" else "#f59e0b"
            bg_color = "rgba(239, 68, 68, 0.1)" if severity == "HIGH" else "rgba(245, 158, 11, 0.1)"
            
            st.markdown(f"""
            <div class="alert-card" style="border-left-color: {color}; background: {bg_color};">
                <div class="alert-title" style="color: {color};">🚨 {severity} RISK - {alert['ENTITY_ID']}</div>
                <div class="alert-content">
                    <strong>Risk Score:</strong> {alert['SCORE']:.2f} | 
                    <strong>System:</strong> {asset['SOURCE_SYSTEM']} | 
                    <strong>Type:</strong> {asset['ASSET_TYPE']} |
                    <strong>Max PSI:</strong> {asset['MAX_PRESSURE_RATING_PSI']:.0f}<br>
                    {alert['EXPLANATION']}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("No high-risk alerts at this time.")

# =============================================================================
# NAVIGATION
# =============================================================================

st.markdown("---")

st.markdown("### 📍 Continue Exploring")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗺️ View Network Map", use_container_width=True, help="Interactive map with before/after AutoGL toggle"):
        st.switch_page("pages/1_Network_Map.py")

with col2:
    if st.button("💬 Open AI Chat", use_container_width=True, help="Chat with AI about risks and routing"):
        st.session_state.show_chat_panel = True
        st.rerun()

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("""
---
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1rem 0;">
    <p>SnowCore Permian Command Center | Powered by Snowflake Cortex AI + AutoGL Graph Neural Networks</p>
    <p style="font-size: 0.75rem; color: #475569;">Demo data represents synthetic scenarios for illustration purposes</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# RIGHT CHAT PANEL
# =============================================================================

if st.session_state.get('show_chat_panel', False):
    # Create a floating right panel using columns
    # Using a placeholder at the bottom with custom positioning
    st.markdown("""
    <style>
        .chat-float-container {
            position: fixed;
            right: 20px;
            bottom: 20px;
            width: 340px;
            max-height: 550px;
            background: #1e293b;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: -4px 4px 20px rgba(0, 0, 0, 0.4);
            z-index: 1000;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("---")
        st.markdown("### 💬 AI Integration Assistant")
        render_chat_panel(session, SCHEMA_PREFIX, assets_df, panel_key="home")
