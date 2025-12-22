"""
Telemetry Explorer - Time-Series Analysis
==========================================
Demonstrates how AutoGL discovered hidden cross-network dependencies
by showing actual time-series correlations that were invisible before data unification.

Business Story: The "Anomaly Injection" - When SC-PAD-42 flow increases,
TF-V-204 pressure rises 5 minutes later, revealing the hidden PIPE-88 dependency.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Telemetry Explorer", page_icon="📈", layout="wide")

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
    
    .insight-card {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(30, 41, 59, 0.9) 100%);
        border-left: 4px solid var(--cortex-purple);
        border-radius: 0 12px 12px 0;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    .insight-title {
        color: var(--cortex-purple);
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .insight-content {
        color: var(--slate-200);
        font-size: 0.9rem;
        line-height: 1.6;
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
    
    .correlation-highlight {
        background: rgba(239, 68, 68, 0.15);
        border: 2px solid var(--risk-high);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .data-quality-card {
        background: var(--slate-800);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--slate-700);
        height: 100%;
    }
    
    .data-quality-card.snowcore {
        border-left: 4px solid var(--snowcore-blue);
    }
    
    .data-quality-card.terafield {
        border-left: 4px solid var(--terafield-red);
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
    <h1>Telemetry Explorer</h1>
    <p>Discover hidden correlations between SnowCore and TeraField sensor data that revealed the PIPE-88 dependency</p>
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
def load_telemetry_data():
    """Load SCADA telemetry for key assets."""
    try:
        # Load telemetry for the critical path assets
        telemetry = session.sql(f"""
            SELECT 
                ASSET_ID,
                TIMESTAMP,
                FLOW_RATE_BOPD,
                GAS_FLOW_MCFD,
                PRESSURE_PSI,
                TEMPERATURE_F,
                SOURCE_SYSTEM
            FROM {SCHEMA_PREFIX}.SCADA_TELEMETRY
            WHERE ASSET_ID IN ('SC-PAD-42', 'SC-SEP-101', 'TF-V-204', 'TF-VALVE-101', 'TF-MID-HUB')
            ORDER BY TIMESTAMP
        """).to_pandas()
        return telemetry
    except Exception as e:
        st.error(f"Error loading telemetry: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_aggregates():
    """Load daily aggregates for quality comparison."""
    try:
        return session.sql(f"""
            SELECT 
                ASSET_ID,
                RECORD_DATE,
                SOURCE_SYSTEM,
                AVG_FLOW_RATE_BOPD,
                AVG_PRESSURE_PSI,
                MAX_PRESSURE_PSI,
                PRESSURE_VARIANCE,
                READING_COUNT,
                DOWNTIME_HOURS
            FROM {SCHEMA_PREFIX}.SCADA_AGGREGATES
            ORDER BY RECORD_DATE, ASSET_ID
        """).to_pandas()
    except Exception as e:
        st.error(f"Error loading aggregates: {str(e)}")
        return pd.DataFrame()

telemetry_df = load_telemetry_data()
aggregates_df = load_aggregates()

# =============================================================================
# SECTION 1: THE DISCOVERY - TIME-LAGGED CORRELATION
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">01</span>
    <h2>The Hidden Correlation: SC-PAD-42 → TF-V-204</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
    <div class="insight-title">Key Discovery</div>
    <div class="insight-content">
        Before data unification, operators couldn't see that when <strong>SC-PAD-42</strong> flow increases, 
        <strong>TF-V-204</strong> pressure rises approximately <strong>5 minutes later</strong>. 
        This time-lagged correlation revealed the hidden PIPE-88 dependency connecting SnowCore and TeraField networks.
    </div>
</div>
""", unsafe_allow_html=True)

# Time-series comparison chart
if not telemetry_df.empty:
    # Get data for the two key assets
    sc_pad_42 = telemetry_df[telemetry_df['ASSET_ID'] == 'SC-PAD-42'].copy()
    tf_v_204 = telemetry_df[telemetry_df['ASSET_ID'] == 'TF-V-204'].copy()
    
    if not sc_pad_42.empty and not tf_v_204.empty:
        # Sample to first 500 points for performance
        sc_pad_42 = sc_pad_42.head(500)
        tf_v_204 = tf_v_204.head(500)
        
        # Create dual-axis time series chart
        fig_correlation = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=('SC-PAD-42: Flow Rate (SnowCore)', 'TF-V-204: Pressure Response (TeraField)')
        )
        
        # SC-PAD-42 Flow Rate
        fig_correlation.add_trace(
            go.Scatter(
                x=sc_pad_42['TIMESTAMP'],
                y=sc_pad_42['FLOW_RATE_BOPD'],
                name='SC-PAD-42 Flow',
                line=dict(color='#0ea5e9', width=2),
                fill='tozeroy',
                fillcolor='rgba(14, 165, 233, 0.2)'
            ),
            row=1, col=1
        )
        
        # TF-V-204 Pressure
        fig_correlation.add_trace(
            go.Scatter(
                x=tf_v_204['TIMESTAMP'],
                y=tf_v_204['PRESSURE_PSI'],
                name='TF-V-204 Pressure',
                line=dict(color='#f43f5e', width=2),
                fill='tozeroy',
                fillcolor='rgba(244, 63, 94, 0.2)'
            ),
            row=2, col=1
        )
        
        # Add danger threshold line on pressure chart
        fig_correlation.add_hline(
            y=550, line_dash="dash", line_color="#f59e0b",
            annotation_text="Operating Limit: 550 PSI",
            row=2, col=1
        )
        
        fig_correlation.add_hline(
            y=600, line_dash="dash", line_color="#ef4444",
            annotation_text="MAWP: 600 PSI",
            row=2, col=1
        )
        
        fig_correlation.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title=dict(
                text='Cross-Network Correlation: Flow-to-Pressure Dependency',
                font=dict(color='#e2e8f0', size=14),
                x=0.5
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                bgcolor='rgba(30, 41, 59, 0.8)'
            ),
            hovermode='x unified'
        )
        
        fig_correlation.update_xaxes(gridcolor='#334155', showgrid=True)
        fig_correlation.update_yaxes(gridcolor='#334155', showgrid=True)
        fig_correlation.update_yaxes(title_text='Flow (BOPD)', row=1, col=1)
        fig_correlation.update_yaxes(title_text='Pressure (PSI)', row=2, col=1)
        
        st.plotly_chart(fig_correlation, use_container_width=True)

# Teaching section
st.markdown("""
<div class="teaching-section">
    <h3>Understanding the Time-Lagged Correlation</h3>
    <p><strong>The Physics:</strong> When production from SC-PAD-42 increases, additional fluid enters the gathering system. 
    This fluid travels through SC-SEP-101 and crosses into TeraField via PIPE-88, eventually reaching TF-V-204.</p>
    <ul>
        <li><strong>Travel time:</strong> ~5 minutes based on pipeline length and flow velocity</li>
        <li><strong>Pressure impact:</strong> Higher flow volume creates backpressure at TF-V-204</li>
        <li><strong>Risk factor:</strong> TF-V-204 is rated for only 600 PSI (MAWP)</li>
    </ul>
    <p><strong>Why it was hidden:</strong> SnowCore data lives in OSIsoft PI, TeraField data in CygNet. 
    Without unification, no one could correlate events across system boundaries.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECTION 2: DATA QUALITY COMPARISON
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">02</span>
    <h2>Data Quality: Modern vs Legacy Systems</h2>
</div>
""", unsafe_allow_html=True)

if not aggregates_df.empty:
    # Calculate quality metrics by system
    snowcore_agg = aggregates_df[aggregates_df['SOURCE_SYSTEM'] == 'SNOWCORE']
    terafield_agg = aggregates_df[aggregates_df['SOURCE_SYSTEM'] == 'TERAFIELD']
    
    EXPECTED_READINGS = 1440  # Per day at 1-minute intervals
    
    sc_completeness = (snowcore_agg['READING_COUNT'].mean() / EXPECTED_READINGS) * 100
    tf_completeness = (terafield_agg['READING_COUNT'].mean() / EXPECTED_READINGS) * 100
    
    sc_variance = snowcore_agg['PRESSURE_VARIANCE'].mean()
    tf_variance = terafield_agg['PRESSURE_VARIANCE'].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="data-quality-card snowcore">
            <h4 style="color: #0ea5e9; margin: 0 0 1rem 0;">SnowCore (Modern)</h4>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Data Source</span>
                    <span style="color: #e2e8f0; font-weight: 600;">OSIsoft PI System</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Sampling Rate</span>
                    <span style="color: #e2e8f0; font-weight: 600;">1 second (high-frequency)</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Data Completeness</span>
                    <span style="color: #22c55e; font-weight: 600;">{sc_completeness:.1f}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Signal Noise (Variance)</span>
                    <span style="color: #22c55e; font-weight: 600;">{sc_variance:.1f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span style="color: #94a3b8;">Tag Convention</span>
                    <span style="color: #e2e8f0; font-weight: 600;">ISA-95 Hierarchical</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="data-quality-card terafield">
            <h4 style="color: #f43f5e; margin: 0 0 1rem 0;">TeraField (Legacy)</h4>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Data Source</span>
                    <span style="color: #e2e8f0; font-weight: 600;">CygNet / Rockwell</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Sampling Rate</span>
                    <span style="color: #f59e0b; font-weight: 600;">1 minute (polling)</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Data Completeness</span>
                    <span style="color: #f59e0b; font-weight: 600;">{tf_completeness:.1f}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">Signal Noise (Variance)</span>
                    <span style="color: #f59e0b; font-weight: 600;">{tf_variance:.1f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span style="color: #94a3b8;">Tag Convention</span>
                    <span style="color: #e2e8f0; font-weight: 600;">Flat / Cryptic IDs</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Signal quality over time
    st.markdown("<br>", unsafe_allow_html=True)
    
    daily_quality = aggregates_df.groupby(['RECORD_DATE', 'SOURCE_SYSTEM']).agg({
        'PRESSURE_VARIANCE': 'mean',
        'READING_COUNT': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_variance = px.line(
            daily_quality,
            x='RECORD_DATE',
            y='PRESSURE_VARIANCE',
            color='SOURCE_SYSTEM',
            color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
            title='Signal Noise: Pressure Variance Over Time'
        )
        fig_variance.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title_font=dict(color='#e2e8f0', size=14),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(gridcolor='#334155', title=''),
            yaxis=dict(gridcolor='#334155', title='Variance'),
            height=300
        )
        st.plotly_chart(fig_variance, use_container_width=True)
    
    with col2:
        fig_readings = px.area(
            daily_quality,
            x='RECORD_DATE',
            y='READING_COUNT',
            color='SOURCE_SYSTEM',
            color_discrete_map={'SNOWCORE': '#0ea5e9', 'TERAFIELD': '#f43f5e'},
            title='Data Volume: Total Readings by Day'
        )
        fig_readings.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title_font=dict(color='#e2e8f0', size=14),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(gridcolor='#334155', title=''),
            yaxis=dict(gridcolor='#334155', title='Readings'),
            height=300
        )
        st.plotly_chart(fig_readings, use_container_width=True)

# =============================================================================
# SECTION 3: PRESSURE PROFILES ACROSS THE FLOW PATH
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">03</span>
    <h2>Pressure Profile: The Critical Flow Path</h2>
</div>
""", unsafe_allow_html=True)

if not aggregates_df.empty:
    # Get average pressure by asset along the critical path
    path_assets = ['SC-PAD-42', 'SC-SEP-101', 'TF-V-204', 'TF-VALVE-101', 'TF-MID-HUB']
    path_data = aggregates_df[aggregates_df['ASSET_ID'].isin(path_assets)].groupby('ASSET_ID').agg({
        'AVG_PRESSURE_PSI': 'mean',
        'MAX_PRESSURE_PSI': 'max',
        'SOURCE_SYSTEM': 'first'
    }).reset_index()
    
    # Order by path sequence
    path_order = {asset: i for i, asset in enumerate(path_assets)}
    path_data['ORDER'] = path_data['ASSET_ID'].map(path_order)
    path_data = path_data.sort_values('ORDER')
    
    # Create pressure profile chart
    colors = ['#0ea5e9' if sys == 'SNOWCORE' else '#f43f5e' for sys in path_data['SOURCE_SYSTEM']]
    
    fig_profile = go.Figure()
    
    # Average pressure bars
    fig_profile.add_trace(go.Bar(
        x=path_data['ASSET_ID'],
        y=path_data['AVG_PRESSURE_PSI'],
        name='Average Pressure',
        marker_color=colors,
        text=[f"{p:.0f}" for p in path_data['AVG_PRESSURE_PSI']],
        textposition='outside',
        textfont=dict(color='#e2e8f0')
    ))
    
    # Max pressure line
    fig_profile.add_trace(go.Scatter(
        x=path_data['ASSET_ID'],
        y=path_data['MAX_PRESSURE_PSI'],
        name='Peak Pressure',
        mode='markers+lines',
        marker=dict(color='#f59e0b', size=10),
        line=dict(color='#f59e0b', dash='dash')
    ))
    
    # Add pressure rating reference for TF-V-204
    fig_profile.add_hline(
        y=600, line_dash="dot", line_color="#ef4444",
        annotation_text="TF-V-204 MAWP: 600 PSI",
        annotation_position="top right",
        annotation_font=dict(color='#ef4444')
    )
    
    fig_profile.update_layout(
        title=dict(
            text='Pressure Along the Critical Flow Path',
            font=dict(color='#e2e8f0', size=14),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#1e293b',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='#334155', title=''),
        yaxis=dict(gridcolor='#334155', title='Pressure (PSI)', range=[0, 1200]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400,
        barmode='group'
    )
    
    st.plotly_chart(fig_profile, use_container_width=True)
    
    # Flow path diagram
    st.markdown("""
    <div style="background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; margin-top: 1rem;">
        <h4 style="color: #e2e8f0; margin: 0 0 1rem 0;">Flow Path Schematic</h4>
        <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; flex-wrap: wrap; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;">
            <span style="background: #0ea5e9; color: white; padding: 0.5rem 1rem; border-radius: 8px;">SC-PAD-42</span>
            <span style="color: #64748b;">→</span>
            <span style="background: #0ea5e9; color: white; padding: 0.5rem 1rem; border-radius: 8px;">SC-SEP-101</span>
            <span style="color: #f59e0b; font-weight: bold;">→ PIPE-88 →</span>
            <span style="background: #f43f5e; color: white; padding: 0.5rem 1rem; border-radius: 8px; border: 2px solid #fbbf24;">TF-V-204 [RISK]</span>
            <span style="color: #64748b;">→</span>
            <span style="background: #f43f5e; color: white; padding: 0.5rem 1rem; border-radius: 8px;">TF-VALVE-101</span>
            <span style="color: #64748b;">→</span>
            <span style="background: #f43f5e; color: white; padding: 0.5rem 1rem; border-radius: 8px;">TF-MID-HUB</span>
        </div>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 1rem; text-align: center;">
            <span style="color: #0ea5e9;">■</span> SnowCore (Modern) &nbsp;&nbsp;
            <span style="color: #f43f5e;">■</span> TeraField (Legacy) &nbsp;&nbsp;
            <span style="color: #f59e0b;">━</span> Cross-Network Link
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SECTION 4: ASSET TELEMETRY DEEP DIVE
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">04</span>
    <h2>Asset Telemetry Deep Dive</h2>
</div>
""", unsafe_allow_html=True)

# Asset selector
available_assets = telemetry_df['ASSET_ID'].unique().tolist() if not telemetry_df.empty else []
selected_asset = st.selectbox(
    "Select asset to explore:",
    available_assets,
    index=available_assets.index('TF-V-204') if 'TF-V-204' in available_assets else 0
)

if selected_asset and not telemetry_df.empty:
    asset_data = telemetry_df[telemetry_df['ASSET_ID'] == selected_asset].head(1000)
    
    if not asset_data.empty:
        source_system = asset_data['SOURCE_SYSTEM'].iloc[0]
        system_color = '#0ea5e9' if source_system == 'SNOWCORE' else '#f43f5e'
        
        # Multi-metric chart
        fig_asset = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Pressure (PSI)', 'Flow Rate (BOPD)', 'Temperature (°F)')
        )
        
        # Pressure
        fig_asset.add_trace(
            go.Scatter(
                x=asset_data['TIMESTAMP'],
                y=asset_data['PRESSURE_PSI'],
                name='Pressure',
                line=dict(color=system_color, width=1.5)
            ),
            row=1, col=1
        )
        
        # Flow rate
        fig_asset.add_trace(
            go.Scatter(
                x=asset_data['TIMESTAMP'],
                y=asset_data['FLOW_RATE_BOPD'],
                name='Flow Rate',
                line=dict(color='#22c55e', width=1.5)
            ),
            row=2, col=1
        )
        
        # Temperature
        fig_asset.add_trace(
            go.Scatter(
                x=asset_data['TIMESTAMP'],
                y=asset_data['TEMPERATURE_F'],
                name='Temperature',
                line=dict(color='#f59e0b', width=1.5)
            ),
            row=3, col=1
        )
        
        fig_asset.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1e293b',
            font=dict(color='#94a3b8'),
            title=dict(
                text=f'Telemetry: {selected_asset} ({source_system})',
                font=dict(color='#e2e8f0', size=14),
                x=0.5
            ),
            showlegend=False,
            hovermode='x unified'
        )
        
        fig_asset.update_xaxes(gridcolor='#334155')
        fig_asset.update_yaxes(gridcolor='#334155')
        
        st.plotly_chart(fig_asset, use_container_width=True)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {system_color};">{asset_data['PRESSURE_PSI'].mean():.0f}</div>
                <div class="metric-label">Avg Pressure (PSI)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ef4444;">{asset_data['PRESSURE_PSI'].max():.0f}</div>
                <div class="metric-label">Peak Pressure (PSI)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #22c55e;">{asset_data['FLOW_RATE_BOPD'].mean():.0f}</div>
                <div class="metric-label">Avg Flow (BOPD)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #f59e0b;">{asset_data['TEMPERATURE_F'].mean():.0f}°</div>
                <div class="metric-label">Avg Temp (°F)</div>
            </div>
            """, unsafe_allow_html=True)

# Footer teaching section
st.markdown("""
<div class="teaching-section" style="margin-top: 2rem;">
    <h3>Key Insights from Telemetry Analysis</h3>
    <p>This page demonstrates how unifying telemetry data across SnowCore and TeraField systems revealed:</p>
    <ul>
        <li><strong>Time-lagged correlations</strong> that indicate physical dependencies (PIPE-88)</li>
        <li><strong>Data quality gaps</strong> in legacy systems that could hide anomalies</li>
        <li><strong>Pressure propagation patterns</strong> that help predict downstream impacts</li>
    </ul>
    <p>The AutoGL model uses these correlations as features for link prediction, automatically discovering 
    connections that weren't documented in either system's asset registry.</p>
</div>
""", unsafe_allow_html=True)

