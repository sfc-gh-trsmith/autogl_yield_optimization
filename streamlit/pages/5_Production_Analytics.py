"""
Production Analytics - Synergy KPI Dashboard
=============================================
Executive dashboard for tracking post-merger production metrics and synergy targets.

Business Story: The VP of Permian Integration can now see unified "Total Production"
from both SnowCore and TeraField networks, tracking toward $500M synergy target.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Production Analytics", page_icon="📊", layout="wide")

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
    
    .kpi-card {
        background: linear-gradient(135deg, var(--slate-800) 0%, rgba(30, 41, 59, 0.8) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--slate-700);
        position: relative;
        overflow: hidden;
        height: 100%;
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
        font-size: 2.5rem;
        font-weight: 700;
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
    
    .kpi-progress {
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--slate-700);
    }
    
    .metric-card {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--slate-700);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
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
    
    .synergy-callout {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(30, 41, 59, 0.9) 100%);
        border-left: 4px solid var(--risk-low);
        border-radius: 0 12px 12px 0;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    .synergy-title {
        color: var(--risk-low);
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--slate-800);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

# Header
st.markdown("""
<div class="page-header">
    <h1>Production Analytics</h1>
    <p>Unified production dashboard tracking post-merger synergy targets across SnowCore and TeraField networks</p>
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
def load_production_data():
    """Load production aggregates."""
    try:
        return session.sql(f"""
            SELECT 
                ASSET_ID,
                RECORD_DATE,
                SOURCE_SYSTEM,
                ZONE,
                ASSET_TYPE,
                AVG_FLOW_RATE_BOPD,
                TOTAL_PRODUCTION_BBL,
                AVG_GAS_FLOW_MCFD,
                TOTAL_GAS_MCF,
                GAS_OIL_RATIO,
                AVG_PRESSURE_PSI,
                MAX_PRESSURE_PSI,
                DOWNTIME_HOURS,
                READING_COUNT
            FROM {SCHEMA_PREFIX}.SCADA_AGGREGATES
            ORDER BY RECORD_DATE, ASSET_ID
        """).to_pandas()
    except Exception as e:
        st.error(f"Error loading production data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_asset_data():
    """Load asset master data."""
    try:
        return session.sql(f"""
            SELECT 
                ASSET_ID,
                SOURCE_SYSTEM,
                ASSET_TYPE,
                ZONE,
                MAX_PRESSURE_RATING_PSI
            FROM {SCHEMA_PREFIX}.ASSET_MASTER
        """).to_pandas()
    except Exception as e:
        st.error(f"Error loading asset data: {str(e)}")
        return pd.DataFrame()

production_df = load_production_data()
assets_df = load_asset_data()

# =============================================================================
# SECTION 1: SYNERGY KPI SCORECARD
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">01</span>
    <h2>Synergy KPI Scorecard</h2>
</div>
""", unsafe_allow_html=True)

if not production_df.empty:
    # Calculate KPIs
    total_production = production_df['TOTAL_PRODUCTION_BBL'].sum()
    total_downtime = production_df['DOWNTIME_HOURS'].sum()
    
    # Downtime by system
    sc_downtime = production_df[production_df['SOURCE_SYSTEM'] == 'SNOWCORE']['DOWNTIME_HOURS'].sum()
    tf_downtime = production_df[production_df['SOURCE_SYSTEM'] == 'TERAFIELD']['DOWNTIME_HOURS'].sum()
    
    # Estimated synergy calculation (illustrative)
    # Assume $50/barrel and 15% deferment reduction = $X savings
    deferment_reduction_target = 0.15
    current_deferment_reduction = 0.08  # Simulated progress
    synergy_progress = (current_deferment_reduction / deferment_reduction_target) * 100
    
    # Estimated value from reduced deferment
    avg_daily_production = production_df.groupby('RECORD_DATE')['TOTAL_PRODUCTION_BBL'].sum().mean()
    price_per_barrel = 75  # Illustrative
    potential_annual_savings = avg_daily_production * 365 * deferment_reduction_target * price_per_barrel
    current_annual_savings = avg_daily_production * 365 * current_deferment_reduction * price_per_barrel
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-target" style="color: #06b6d4;">$500M</div>
            <div class="kpi-label">Synergy Target</div>
            <div class="kpi-description">
                Optimize flow routing across the combined network without laying new pipe
            </div>
            <div class="kpi-progress">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                    <span>Progress</span>
                    <span style="color: #22c55e;">${current_annual_savings/1e6:.1f}M identified</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-target" style="color: #22c55e;">-15%</div>
            <div class="kpi-label">Deferment Reduction Target</div>
            <div class="kpi-description">
                Predict systemic pressure bottlenecks at SnowCore/TeraField interfaces
            </div>
            <div class="kpi-progress">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                    <span>Current</span>
                    <span style="color: #f59e0b;">-{current_deferment_reduction*100:.0f}% achieved</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-target" style="color: #0ea5e9;">{total_production/1e6:.2f}M</div>
            <div class="kpi-label">Total Production (BBL)</div>
            <div class="kpi-description">
                Combined output from SnowCore and TeraField gathering networks
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-target" style="color: #f59e0b;">{total_downtime:.0f}h</div>
            <div class="kpi-label">Total Downtime</div>
            <div class="kpi-description">
                Combined hours of equipment unavailability across both networks
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Synergy callout
    st.markdown(f"""
    <div class="synergy-callout">
        <div class="synergy-title">Synergy Opportunity Identified</div>
        <p style="color: #e2e8f0; margin: 0;">
            By routing additional {avg_daily_production:.0f} BOPD through under-utilized TeraField infrastructure 
            (identified via AutoGL link prediction), the integration team has identified 
            <strong>${current_annual_savings/1e6:.1f}M</strong> in annual savings without new capital expenditure.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SECTION 2: PRODUCTION BY SYSTEM
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">02</span>
    <h2>Production by Source System</h2>
</div>
""", unsafe_allow_html=True)

if not production_df.empty:
    # Daily production by system
    daily_by_system = production_df.groupby(['RECORD_DATE', 'SOURCE_SYSTEM']).agg({
        'TOTAL_PRODUCTION_BBL': 'sum',
        'TOTAL_GAS_MCF': 'sum',
        'DOWNTIME_HOURS': 'sum'
    }).reset_index()
    
    # Stacked area chart - Total Production
    fig_production = px.area(
        daily_by_system,
        x='RECORD_DATE',
        y='TOTAL_PRODUCTION_BBL',
        color='SOURCE_SYSTEM',
        color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
        title='Daily Oil Production by Source System'
    )
    
    fig_production.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#1e293b',
        font=dict(color='#94a3b8'),
        title_font=dict(color='#e2e8f0', size=14),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(30, 41, 59, 0.8)'
        ),
        xaxis=dict(gridcolor='#334155', title=''),
        yaxis=dict(gridcolor='#334155', title='Production (BBL)'),
        height=350
    )
    
    st.plotly_chart(fig_production, use_container_width=True)
    
    # System comparison metrics
    col1, col2 = st.columns(2)
    
    with col1:
        sc_data = production_df[production_df['SOURCE_SYSTEM'] == 'SNOWCORE']
        sc_total = sc_data['TOTAL_PRODUCTION_BBL'].sum()
        sc_avg_daily = sc_data.groupby('RECORD_DATE')['TOTAL_PRODUCTION_BBL'].sum().mean()
        sc_downtime_avg = sc_data.groupby('RECORD_DATE')['DOWNTIME_HOURS'].sum().mean()
        
        st.markdown(f"""
        <div class="system-card snowcore">
            <h4 style="color: #0ea5e9; margin: 0 0 1rem 0;">SnowCore Production</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0ea5e9; font-family: 'IBM Plex Mono', monospace;">{sc_total/1e6:.2f}M</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Total BBL</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0; font-family: 'IBM Plex Mono', monospace;">{sc_avg_daily:.0f}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Avg Daily BBL</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #22c55e; font-family: 'IBM Plex Mono', monospace;">{sc_downtime_avg:.1f}h</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Avg Daily Downtime</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0; font-family: 'IBM Plex Mono', monospace;">{len(sc_data['ASSET_ID'].unique())}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Active Assets</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tf_data = production_df[production_df['SOURCE_SYSTEM'] == 'TERAFIELD']
        tf_total = tf_data['TOTAL_PRODUCTION_BBL'].sum()
        tf_avg_daily = tf_data.groupby('RECORD_DATE')['TOTAL_PRODUCTION_BBL'].sum().mean()
        tf_downtime_avg = tf_data.groupby('RECORD_DATE')['DOWNTIME_HOURS'].sum().mean()
        
        st.markdown(f"""
        <div class="system-card terafield">
            <h4 style="color: #f43f5e; margin: 0 0 1rem 0;">TeraField Production</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f43f5e; font-family: 'IBM Plex Mono', monospace;">{tf_total/1e6:.2f}M</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Total BBL</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0; font-family: 'IBM Plex Mono', monospace;">{tf_avg_daily:.0f}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Avg Daily BBL</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f59e0b; font-family: 'IBM Plex Mono', monospace;">{tf_downtime_avg:.1f}h</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Avg Daily Downtime</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0; font-family: 'IBM Plex Mono', monospace;">{len(tf_data['ASSET_ID'].unique())}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Active Assets</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# SECTION 3: PRODUCTION BY ZONE
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">03</span>
    <h2>Production by Geographic Zone</h2>
</div>
""", unsafe_allow_html=True)

if not production_df.empty:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Production by zone - donut chart
        zone_production = production_df.groupby('ZONE')['TOTAL_PRODUCTION_BBL'].sum().reset_index()
        
        fig_zone = go.Figure(data=[go.Pie(
            labels=zone_production['ZONE'],
            values=zone_production['TOTAL_PRODUCTION_BBL'],
            hole=0.6,
            marker=dict(colors=['#0ea5e9', '#f43f5e']),
            textinfo='label+percent',
            textfont=dict(color='#e2e8f0')
        )])
        
        fig_zone.update_layout(
            title=dict(
                text='Production Split by Zone',
                font=dict(color='#e2e8f0', size=14),
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'),
            showlegend=False,
            height=300,
            annotations=[dict(
                text=f"{zone_production['TOTAL_PRODUCTION_BBL'].sum()/1e6:.1f}M<br>BBL",
                x=0.5, y=0.5,
                font_size=16,
                font_color='#e2e8f0',
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_zone, use_container_width=True)
    
    with col2:
        # Daily production by zone
        daily_by_zone = production_df.groupby(['RECORD_DATE', 'ZONE']).agg({
            'TOTAL_PRODUCTION_BBL': 'sum'
        }).reset_index()
        
        fig_zone_trend = px.line(
            daily_by_zone,
            x='RECORD_DATE',
            y='TOTAL_PRODUCTION_BBL',
            color='ZONE',
            color_discrete_map={'DELAWARE': '#0ea5e9', 'MIDLAND': '#f43f5e'},
            title='Daily Production Trend by Zone'
        )
        
        fig_zone_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title_font=dict(color='#e2e8f0', size=14),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(gridcolor='#334155', title=''),
            yaxis=dict(gridcolor='#334155', title='Production (BBL)'),
            height=300
        )
        
        st.plotly_chart(fig_zone_trend, use_container_width=True)

# =============================================================================
# SECTION 4: GAS-OIL RATIO ANALYSIS
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">04</span>
    <h2>Gas-Oil Ratio Analysis</h2>
</div>
""", unsafe_allow_html=True)

if not production_df.empty:
    # GOR by system over time
    daily_gor = production_df.groupby(['RECORD_DATE', 'SOURCE_SYSTEM']).agg({
        'GAS_OIL_RATIO': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_gor = px.line(
            daily_gor,
            x='RECORD_DATE',
            y='GAS_OIL_RATIO',
            color='SOURCE_SYSTEM',
            color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
            title='Gas-Oil Ratio Trend by Source System'
        )
        
        fig_gor.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title_font=dict(color='#e2e8f0', size=14),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(gridcolor='#334155', title=''),
            yaxis=dict(gridcolor='#334155', title='GOR (SCF/BBL)'),
            height=300
        )
        
        st.plotly_chart(fig_gor, use_container_width=True)
    
    with col2:
        # GOR statistics
        sc_gor = production_df[production_df['SOURCE_SYSTEM'] == 'SNOWCORE']['GAS_OIL_RATIO'].mean()
        tf_gor = production_df[production_df['SOURCE_SYSTEM'] == 'TERAFIELD']['GAS_OIL_RATIO'].mean()
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 1rem;">
            <div class="metric-value" style="color: #0ea5e9;">{sc_gor:.0f}</div>
            <div class="metric-label">SnowCore Avg GOR</div>
            <div class="metric-delta" style="color: #94a3b8;">SCF/BBL</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #f43f5e;">{tf_gor:.0f}</div>
            <div class="metric-label">TeraField Avg GOR</div>
            <div class="metric-delta" style="color: #94a3b8;">SCF/BBL</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# SECTION 5: DOWNTIME ANALYSIS
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">05</span>
    <h2>Downtime Analysis & Deferment Impact</h2>
</div>
""", unsafe_allow_html=True)

if not production_df.empty:
    # Downtime comparison
    daily_downtime = production_df.groupby(['RECORD_DATE', 'SOURCE_SYSTEM']).agg({
        'DOWNTIME_HOURS': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_downtime = px.bar(
            daily_downtime,
            x='RECORD_DATE',
            y='DOWNTIME_HOURS',
            color='SOURCE_SYSTEM',
            barmode='stack',
            color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
            title='Daily Downtime by Source System'
        )
        
        fig_downtime.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title_font=dict(color='#e2e8f0', size=14),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(gridcolor='#334155', title=''),
            yaxis=dict(gridcolor='#334155', title='Downtime (Hours)'),
            height=300
        )
        
        st.plotly_chart(fig_downtime, use_container_width=True)
    
    with col2:
        # Calculate deferment cost
        avg_daily_downtime = production_df.groupby('RECORD_DATE')['DOWNTIME_HOURS'].sum().mean()
        # Assume each hour of downtime = ~50 BOPD lost
        deferred_bopd = avg_daily_downtime * 50
        deferred_annual_value = deferred_bopd * 365 * 75  # $75/barrel
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 1rem;">
            <div class="metric-value" style="color: #ef4444;">{avg_daily_downtime:.1f}h</div>
            <div class="metric-label">Avg Daily Downtime</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 1rem;">
            <div class="metric-value" style="color: #f59e0b;">{deferred_bopd:.0f}</div>
            <div class="metric-label">Est. Deferred BOPD</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ef4444;">${deferred_annual_value/1e6:.1f}M</div>
            <div class="metric-label">Annual Deferment Cost</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# SECTION 6: ASSET PERFORMANCE RANKING
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">06</span>
    <h2>Asset Performance Ranking</h2>
</div>
""", unsafe_allow_html=True)

if not production_df.empty:
    # Calculate performance metrics by asset
    asset_performance = production_df.groupby(['ASSET_ID', 'SOURCE_SYSTEM', 'ASSET_TYPE']).agg({
        'TOTAL_PRODUCTION_BBL': 'sum',
        'AVG_FLOW_RATE_BOPD': 'mean',
        'DOWNTIME_HOURS': 'sum',
        'AVG_PRESSURE_PSI': 'mean'
    }).reset_index()
    
    # Calculate efficiency score
    asset_performance['EFFICIENCY_SCORE'] = (
        (asset_performance['AVG_FLOW_RATE_BOPD'] / asset_performance['AVG_FLOW_RATE_BOPD'].max()) * 50 +
        (1 - asset_performance['DOWNTIME_HOURS'] / asset_performance['DOWNTIME_HOURS'].max()) * 50
    )
    
    # Top performers
    top_performers = asset_performance.nlargest(10, 'TOTAL_PRODUCTION_BBL')
    
    # Bar chart
    colors = ['#0ea5e9' if sys == 'SNOWCORE' else '#f43f5e' for sys in top_performers['SOURCE_SYSTEM']]
    
    fig_ranking = go.Figure(data=[
        go.Bar(
            x=top_performers['ASSET_ID'],
            y=top_performers['TOTAL_PRODUCTION_BBL'],
            marker_color=colors,
            text=[f"{p:.0f}" for p in top_performers['TOTAL_PRODUCTION_BBL']],
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=10)
        )
    ])
    
    fig_ranking.update_layout(
        title=dict(
            text='Top 10 Assets by Total Production',
            font=dict(color='#e2e8f0', size=14),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#1e293b',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155', title='', tickangle=45),
        yaxis=dict(gridcolor='#334155', title='Total Production (BBL)'),
        height=350
    )
    
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    # Legend
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 0.5rem;">
        <span style="color: #94a3b8; font-size: 0.85rem;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #0ea5e9; border-radius: 2px; margin-right: 6px;"></span>
            SnowCore
        </span>
        <span style="color: #94a3b8; font-size: 0.85rem;">
            <span style="display: inline-block; width: 12px; height: 12px; background: #f43f5e; border-radius: 2px; margin-right: 6px;"></span>
            TeraField
        </span>
    </div>
    """, unsafe_allow_html=True)

# Teaching section
st.markdown("""
<div class="teaching-section" style="margin-top: 2rem;">
    <h3>Understanding Production Synergies</h3>
    <p>This dashboard demonstrates how unified visibility enables the VP of Permian Integration to:</p>
    <ul>
        <li><strong>Track combined production</strong> from both SnowCore and TeraField networks in real-time</li>
        <li><strong>Identify synergy opportunities</strong> by comparing performance across systems</li>
        <li><strong>Quantify deferment impact</strong> to prioritize maintenance and upgrades</li>
        <li><strong>Monitor GOR trends</strong> that affect processing capacity and revenue</li>
    </ul>
    <p>Before integration, these metrics existed in separate dashboards with incompatible data formats. 
    Now, leadership can make data-driven decisions about capital allocation and operational priorities.</p>
</div>
""", unsafe_allow_html=True)

