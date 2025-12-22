"""
About Page - Permian Command Center

Comprehensive documentation for business and technical audiences following
the Snowflake Streamlit About Section Guide framework.
"""

import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Typography */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    :root {
        --snowcore-blue: #1e40af;
        --snowcore-blue-light: #3b82f6;
        --terafield-red: #b45309;
        --terafield-orange: #f59e0b;
        --model-green: #166534;
        --model-green-light: #22c55e;
        --slate-950: #020617;
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --slate-500: #64748b;
        --slate-400: #94a3b8;
        --slate-300: #cbd5e1;
        --slate-200: #e2e8f0;
        --slate-100: #f1f5f9;
    }
    
    .stApp {
        background: linear-gradient(180deg, var(--slate-950) 0%, var(--slate-900) 100%);
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3 {
        color: var(--slate-100) !important;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600;
    }
    
    h1 { font-size: 2.25rem !important; letter-spacing: -0.025em; }
    h2 { font-size: 1.5rem !important; margin-top: 2rem !important; }
    h3 { font-size: 1.25rem !important; color: var(--slate-200) !important; }
    
    p, li, span {
        color: var(--slate-400) !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    strong { color: var(--slate-200) !important; }
    
    /* Badge System */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.625rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: white;
        margin-right: 0.5rem;
    }
    
    .badge-snowcore { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); }
    .badge-terafield { background: linear-gradient(135deg, #b45309 0%, #f59e0b 100%); }
    .badge-model { background: linear-gradient(135deg, #166534 0%, #22c55e 100%); }
    .badge-cortex { background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%); }
    
    /* Tech Badge Pills */
    .tech-badge {
        background: rgba(71, 85, 105, 0.4);
        border: 1px solid var(--slate-600);
        color: var(--slate-200) !important;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.25rem 0.25rem 0.25rem 0;
        display: inline-block;
        transition: all 0.2s ease;
    }
    
    .tech-badge:hover {
        background: rgba(71, 85, 105, 0.6);
        border-color: var(--slate-500);
    }
    
    /* Data Source Cards */
    .data-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid var(--slate-700);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .data-card:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: var(--slate-600);
    }
    
    .data-card-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--slate-200) !important;
        margin-bottom: 0.25rem;
    }
    
    .data-card-desc {
        font-size: 0.8rem;
        color: var(--slate-400) !important;
        margin: 0;
    }
    
    /* Value Cards */
    .value-card {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.2) 0%, rgba(30, 64, 175, 0.05) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .value-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
    }
    
    .value-card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--slate-100) !important;
        margin-bottom: 0.5rem;
    }
    
    .value-card-metric {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--snowcore-blue-light) !important;
        margin-bottom: 0.25rem;
    }
    
    .value-card-desc {
        font-size: 0.8rem;
        color: var(--slate-400) !important;
    }
    
    /* Workflow Steps */
    .workflow-step {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: rgba(30, 41, 59, 0.4);
        border-radius: 6px;
        border-left: 3px solid var(--snowcore-blue);
    }
    
    .workflow-number {
        background: var(--snowcore-blue);
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.75rem;
        flex-shrink: 0;
    }
    
    /* Code blocks */
    .mono {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        background: rgba(30, 41, 59, 0.8);
        padding: 0.125rem 0.375rem;
        border-radius: 4px;
        color: var(--slate-300) !important;
    }
    
    /* Algorithm box */
    .algo-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid var(--slate-700);
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1rem 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        color: var(--slate-300) !important;
        overflow-x: auto;
    }
    
    /* Hide default page navigation */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(30, 41, 59, 0.4);
        padding: 0.25rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid var(--slate-700);
        margin: 2rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Page link cards */
    .page-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid var(--slate-700);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .page-card:hover {
        background: rgba(30, 41, 59, 0.7);
        border-color: var(--slate-600);
    }
    
    .page-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .page-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--slate-200) !important;
        margin-bottom: 0.25rem;
    }
    
    .page-desc {
        font-size: 0.8rem;
        color: var(--slate-400) !important;
    }
    
    /* Limitation cards */
    .limitation-item {
        background: rgba(180, 83, 9, 0.1);
        border-left: 3px solid var(--terafield-orange);
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
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


def main():
    # ========================================================================
    # 1. HEADER
    # ========================================================================
    st.title("About Permian Command Center")
    st.markdown("""
    *Intelligent yield optimization unifying SnowCore and TeraField gathering networks 
    through Graph Neural Networks and Cortex AI*
    """)
    
    # Version info
    st.markdown("""
    <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
        <span class="tech-badge">v1.0.0</span>
        <span class="tech-badge">Snowflake Native App</span>
        <span class="tech-badge">Python 3.11</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # 2. OVERVIEW (Problem + Solution)
    # ========================================================================
    st.header("Overview")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("The Problem")
        st.markdown("""
        Following the acquisition of **TeraField Resources**, SnowCore Energy faces a critical 
        **data visibility gap** across its Permian Basin operations. The challenge is multi-dimensional:
        
        **Data Fragmentation**
        - **SnowCore assets**: Monitored via high-frequency OSIsoft PI System (1-second resolution)
        - **TeraField assets**: Legacy CygNet SCADA with 1-minute polling and frequent data gaps
        - **Two incompatible asset registries**: SAP S/4HANA vs. IBM Maximo with different naming conventions
        
        **The "Iceberg Problem"**
        
        Your ERP and SCADA systems show you the **10% above the waterline**—your documented pipeline 
        connections. But **90% of your operational risk** lurks below: undocumented TeraField connections, 
        pressure dependencies that cross network boundaries, and equipment specifications trapped in 
        legacy PDF P&IDs that no current engineer has reviewed.
        
        **Business Impact of Status Quo**
        - Engineers cannot see how new TeraField wells connect to existing SnowCore separators
        - Risk of **systemic over-pressurization events** at network boundaries
        - Manual topology mapping takes weeks and is outdated by completion time
        - Critical equipment specs (pressure ratings, valve limits) are buried in unstructured documents
        """)
    
    with col2:
        st.subheader("The Solution")
        st.markdown("""
        The Permian Command Center unifies both networks through AI-powered discovery:
        """)
        
        st.markdown("""
        <div class="value-card" style="margin-bottom: 0.75rem;">
            <div class="value-card-title">Auto-Discovery</div>
            <div class="value-card-desc">Graph Neural Networks infer hidden pipeline connections from flow correlation patterns</div>
        </div>
        
        <div class="value-card" style="margin-bottom: 0.75rem;">
            <div class="value-card-title">Unified View</div>
            <div class="value-card-desc">Single geospatial map for all assets with AI-enhanced topology overlay</div>
        </div>
        
        <div class="value-card" style="margin-bottom: 0.75rem;">
            <div class="value-card-title">Risk Prediction</div>
            <div class="value-card-desc">Simulate flow changes and catch pressure anomalies before equipment failure</div>
        </div>
        
        <div class="value-card" style="margin-bottom: 0.75rem;">
            <div class="value-card-title">Instant Access</div>
            <div class="value-card-desc">Chat with engineering docs via Cortex AI to retrieve specs in seconds</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # 3. BUSINESS IMPACT
    # ========================================================================
    st.header("Business Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="value-card">
            <div class="value-card-metric">$500M</div>
            <div class="value-card-title">Synergy Target</div>
            <div class="value-card-desc">Optimized flow routing across combined network without new infrastructure</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-card">
            <div class="value-card-metric">15%</div>
            <div class="value-card-title">Deferment Reduction</div>
            <div class="value-card-desc">Predict systemic pressure bottlenecks at network interfaces</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="value-card">
            <div class="value-card-metric">&lt;5 min</div>
            <div class="value-card-title">Graph Inference</div>
            <div class="value-card-desc">Complete topology reconstruction vs. weeks of manual mapping</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="value-card">
            <div class="value-card-metric">N-Tier</div>
            <div class="value-card-title">Visibility</div>
            <div class="value-card-desc">See beyond direct connections to discover hidden dependencies</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # 4. DATA ARCHITECTURE
    # ========================================================================
    st.header("Data Architecture")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<span class="badge badge-snowcore">Internal / SnowCore</span>', unsafe_allow_html=True)
        st.markdown("##### Modern Infrastructure Data")
        
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">ASSET_MASTER</div>
            <div class="data-card-desc">Unified asset registry with location, type, and specifications</div>
        </div>
        
        <div class="data-card">
            <div class="data-card-title">SCADA_TELEMETRY</div>
            <div class="data-card-desc">High-frequency sensor readings (flow, pressure, temperature)</div>
        </div>
        
        <div class="data-card">
            <div class="data-card-title">NETWORK_EDGES</div>
            <div class="data-card-desc">Known pipeline segments with diameter and pressure ratings</div>
        </div>
        
        <div class="data-card">
            <div class="data-card-title">SCADA_AGGREGATES</div>
            <div class="data-card-desc">Daily rollups for production analytics and trending</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("Source: OSIsoft PI System, SAP S/4HANA")
        st.caption("Refresh: Real-time (1-second resolution)")
    
    with col2:
        st.markdown('<span class="badge badge-terafield">External / Legacy</span>', unsafe_allow_html=True)
        st.markdown("##### TeraField Brownfield Data")
        
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">CygNet SCADA Feeds</div>
            <div class="data-card-desc">Lower-frequency polling with deadband artifacts and data gaps</div>
        </div>
        
        <div class="data-card">
            <div class="data-card-title">IBM Maximo Dump</div>
            <div class="data-card-desc">Legacy asset registry (flat naming: TF_MID_HUB_V204_P)</div>
        </div>
        
        <div class="data-card">
            <div class="data-card-title">LEGACY_DOCUMENTS</div>
            <div class="data-card-desc">P&ID PDFs, maintenance logs, shift reports, vendor manuals</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("Source: CygNet, Maximo, File Shares")
        st.caption("Refresh: 1-minute polling, batch document loads")
        
        st.markdown("---")
        st.markdown("##### Document Types Indexed")
        st.markdown("""
        - **P&ID Drawings**: Process flow with equipment tags
        - **Shift Reports**: Operator notes and observations
        - **Maintenance Logs**: Work history and known issues
        """)
    
    with col3:
        st.markdown('<span class="badge badge-model">Model Outputs</span>', unsafe_allow_html=True)
        st.markdown("##### AI/ML Predictions")
        
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">GRAPH_PREDICTIONS</div>
            <div class="data-card-desc">Link probabilities and node anomaly scores from AutoGL</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Prediction Types:**")
        st.markdown("""
        | Type | Description |
        |------|-------------|
        | `NODE_ANOMALY` | Risk score (0-1) per asset |
        | `LINK_PREDICTION` | Hidden connection probability |
        """)
        
        st.markdown("---")
        
        st.markdown('<span class="badge badge-cortex">Cortex AI</span>', unsafe_allow_html=True)
        st.markdown("##### Cortex Services")
        
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">DOCS_SEARCH</div>
            <div class="data-card-desc">Cortex Search service for RAG over legacy documents</div>
        </div>
        
        <div class="data-card">
            <div class="data-card-title">Semantic View</div>
            <div class="data-card-desc">Cortex Analyst semantic model for natural language queries</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    # ========================================================================
    # 5. HOW IT WORKS (Tabbed)
    # ========================================================================
    st.header("How It Works")
    
    exec_tab, tech_tab, cortex_tab = st.tabs([
        "Executive Overview", 
        "Technical Deep-Dive", 
        "Cortex AI Integration"
    ])
    
    with exec_tab:
        st.markdown("### Bridging the Knowledge Gap")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            Imagine trying to navigate a city where your GPS only shows main highways 
            (SnowCore data) but misses all the side streets (TeraField data). You know 
            traffic is flowing, but you can't see where it's coming from or where 
            bottlenecks might form.
            
            **AutoGL acts as a predictive GPS.** By analyzing flow patterns at the 
            "intersections" (known connection points), it deduces where the missing 
            side streets must be:
            
            - If a central processing facility receives more volume than its known pipes 
              can deliver, the AI infers a hidden connection from a nearby legacy well
            - If pressure at a SnowCore asset consistently spikes 5 minutes after flow 
              increases at a TeraField asset, the model learns this time-lagged dependency
            - The result: a complete "digital twin" of the network that includes both 
              documented and discovered connections
            """)
        
        with col2:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 1rem; border: 1px solid #334155;">
                <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem;">The "Wow" Moment</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">
                    View two disconnected clusters on the map. Click "Run AutoGL." 
                    Watch new edges appear connecting the networks. A "High Risk" alert 
                    pulses on a legacy TeraField valve. Ask "Why?" and the AI explains 
                    the pressure rating mismatch.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### The False Diversification Trap")
        st.markdown("""
        Traditional risk assessments score assets independently—like grading students 
        without knowing they all copied from the same source. You might have 5 wells 
        feeding 5 different separators, each with a "low risk" score. But if they all 
        ultimately flow through the same legacy TeraField valve with an undocumented 
        600 PSI limit, you don't have resilience—you have **concentrated risk with extra steps**.
        
        This solution reveals those hidden convergence points and flags them before they 
        become operational failures.
        """)
        
        st.markdown("### Why Traditional Approaches Fall Short")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="data-card">
                <div class="data-card-title">Traditional SCADA</div>
                <div class="data-card-desc">
                    Monitors each asset independently. Completely misses network effects 
                    and cross-system dependencies.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="data-card">
                <div class="data-card-title">Manual Mapping</div>
                <div class="data-card-desc">
                    Walk-down surveys take weeks. Data is outdated by completion time. 
                    Expensive and incomplete.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="data-card">
                <div class="data-card-title">AutoGL Approach</div>
                <div class="data-card-desc">
                    Combines telemetry + graph structure. AI discovers hidden patterns. 
                    Automated, scalable, continuously updated.
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tech_tab:
        st.markdown("### Graph Neural Network Architecture")
        
        st.markdown("""
        The core of the system is a **GraphSAGE** (Graph SAmple and aggreGatE) encoder 
        that learns node embeddings through iterative neighborhood aggregation.
        """)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("#### Model Architecture")
            st.markdown("""
            <div class="algo-box">
Input Features (N × 16)          Node Embeddings (N × 64)
       │                                    │
       ▼                                    ▼
┌─────────────────────┐            ┌─────────────────────┐
│  SAGEConv (32)      │───────────▶│  SAGEConv (64)      │
│  + ReLU             │            │                     │
│  + Dropout(0.3)     │            │                     │
└─────────────────────┘            └─────────────────────┘
                                           │
                          ┌────────────────┴────────────────┐
                          ▼                                 ▼
                  ┌─────────────┐                   ┌─────────────┐
                  │    Link     │                   │   Anomaly   │
                  │  Predictor  │                   │  Predictor  │
                  │   (MLP)     │                   │   (MLP)     │
                  └─────────────┘                   └─────────────┘
                          │                                 │
                          ▼                                 ▼
                  P(edge exists)                    Risk Score [0,1]
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Hyperparameters")
            st.markdown("""
            | Parameter | Value | Purpose |
            |-----------|-------|---------|
            | `embedding_dim` | 64 | Node representation size |
            | `hidden_dim` | 32 | Intermediate layer size |
            | `dropout` | 0.3 | Regularization |
            | `learning_rate` | 0.01 | Optimization step size |
            | `epochs` | 100 | Training iterations |
            | `negative_ratio` | 1:1 | Neg samples per edge |
            """)
        
        st.markdown("#### Message Passing Formulation")
        st.markdown("""
        At each layer $k$, the embedding of node $v$ is computed as:
        """)
        
        st.latex(r"h_v^{(k)} = \sigma\left(W^{(k)} \cdot \text{CONCAT}\left(h_v^{(k-1)}, \text{MEAN}_{u \in N(v)}(h_u^{(k-1)})\right)\right)")
        
        st.markdown("""
        Where:
        - $h_v^{(k)}$ = embedding of node $v$ at layer $k$
        - $N(v)$ = neighbors of node $v$  
        - $W^{(k)}$ = learnable weight matrix
        - $\sigma$ = ReLU activation
        - With **2 layers**, each node's embedding captures 2-hop neighborhood information
        """)
        
        st.markdown("#### Self-Supervised Training")
        st.markdown("""
        We train using **link prediction** as a proxy task (no labeled anomaly data required):
        
        - **Positive samples**: Real edges from the documented network (label = 1)
        - **Negative samples**: Randomly sampled non-edges (label = 0)
        
        **Loss Function** (Binary Cross-Entropy):
        """)
        
        st.latex(r"\mathcal{L} = -\sum_{(u,v) \in E} \log P(u,v) - \sum_{(u,v) \notin E} \log(1 - P(u,v))")
        
        st.markdown("""
        **Link Probability** (dot-product decoder):
        """)
        
        st.latex(r"P(u,v) = \sigma(z_u^T \cdot z_v)")
        
        st.markdown("#### Node Features")
        st.markdown("""
        Each node (asset) is represented by a 16-dimensional feature vector:
        
        | Feature Category | Fields |
        |-----------------|--------|
        | **Location** | Latitude, Longitude |
        | **Specifications** | Max Pressure Rating (PSI) |
        | **Source System** | SnowCore (1) / TeraField (0) |
        | **Zone** | Delaware (1) / Midland (0) |
        | **Telemetry** | Avg Flow, Avg Pressure, Max Pressure, Pressure Std, Avg Temp |
        | **Asset Type** | One-hot: WELL, SEPARATOR, COMPRESSOR, PIPELINE, VALVE |
        """)
        
        st.markdown("#### Training Pipeline")
        st.markdown("""
        <div class="workflow-step">
            <div class="workflow-number">1</div>
            <div>
                <strong>Data Ingestion</strong><br/>
                Load ASSET_MASTER, NETWORK_EDGES, and 7-day SCADA telemetry aggregates from Snowflake
            </div>
        </div>
        
        <div class="workflow-step">
            <div class="workflow-number">2</div>
            <div>
                <strong>Graph Construction</strong><br/>
                Build PyTorch Geometric Data object with node features and bidirectional edge index
            </div>
        </div>
        
        <div class="workflow-step">
            <div class="workflow-number">3</div>
            <div>
                <strong>Model Training</strong><br/>
                100 epochs of self-supervised link prediction with Adam optimizer and diversity regularization
            </div>
        </div>
        
        <div class="workflow-step">
            <div class="workflow-number">4</div>
            <div>
                <strong>Inference</strong><br/>
                Generate node anomaly scores and cross-network link predictions (probability > 0.5)
            </div>
        </div>
        
        <div class="workflow-step">
            <div class="workflow-number">5</div>
            <div>
                <strong>Persistence</strong><br/>
                Write predictions to GRAPH_PREDICTIONS table for dashboard consumption
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Evaluation Metrics")
        st.markdown("""
        | Metric | Target | Purpose |
        |--------|--------|---------|
        | **Training AUC** | > 0.85 | Link prediction discrimination |
        | **Diversity Loss** | < -0.1 | Anomaly score spread |
        | **Inference Time** | < 5 min | End-to-end pipeline |
        """)
    
    with cortex_tab:
        st.markdown("### Snowflake Cortex AI Integration")
        
        st.markdown("""
        The application leverages three Cortex capabilities to bridge structured data, 
        unstructured documents, and AI reasoning:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Cortex Search (RAG)")
            st.markdown("""
            **Purpose**: Enable natural language queries over legacy TeraField documents
            
            **Service**: `AUTOGL_YIELD_OPTIMIZATION_DOCS_SEARCH`
            
            **Indexed Content**:
            - P&ID process flow diagrams (text extracted)
            - Shift handover reports
            - Maintenance logs with equipment history
            - Vendor specification sheets
            
            **Configuration**:
            - Searchable column: `CONTENT` (full document text)
            - Filter attributes: `TAG_ID`, `DOCUMENT_TYPE`, `FACILITY`
            - Target lag: 1 hour refresh
            
            **Sample Queries**:
            - *"What is the maximum pressure rating for V-204?"*
            - *"Are there any known issues with the bypass valve?"*
            - *"What did the operator note about V-204 sticking?"*
            """)
            
            st.markdown("---")
            
            st.markdown("#### Cortex Analyst")
            st.markdown("""
            **Purpose**: Natural language to SQL for structured data queries
            
            **Semantic Model**: `AUTOGL_YIELD_OPTIMIZATION_ANALYTICS_VIEW`
            
            **Tables in Scope**:
            - `SCADA_AGGREGATES` - Daily production metrics
            - `ASSET_MASTER` - Equipment specifications
            - `GRAPH_PREDICTIONS` - ML model outputs
            
            **Key Measures**:
            - Total Production (BBL), Gas Flow (MCFD)
            - Average/Max Pressure (PSI)
            - Downtime Hours, Gas-Oil Ratio
            - Anomaly Scores, Link Confidence
            
            **Sample Queries**:
            - *"Compare downtime between SnowCore and TeraField assets"*
            - *"Which assets have the highest pressure readings?"*
            - *"Show me high-risk assets from the ML predictions"*
            """)
        
        with col2:
            st.markdown("#### Integration Assistant (Agent)")
            st.markdown("""
            **Purpose**: Orchestrate multi-source queries combining Analyst + Search + Model
            
            **LLM Model**: `mistral-large` (via Cortex)
            
            **Agent Workflow Example**:
            
            <div class="workflow-step">
                <div class="workflow-number">1</div>
                <div>
                    <strong>User asks:</strong><br/>
                    "Can I route 5k extra barrels through the Midland Hub?"
                </div>
            </div>
            
            <div class="workflow-step">
                <div class="workflow-number">2</div>
                <div>
                    <strong>Agent checks AutoGL Model:</strong><br/>
                    "Model predicts pressure will rise to 650 PSI"
                </div>
            </div>
            
            <div class="workflow-step">
                <div class="workflow-number">3</div>
                <div>
                    <strong>Agent checks Cortex Search:</strong><br/>
                    "P&ID shows Midland Hub piping rated for 600 PSIG"
                </div>
            </div>
            
            <div class="workflow-step">
                <div class="workflow-number">4</div>
                <div>
                    <strong>Agent Conclusion:</strong><br/>
                    "No. Routing denied. Predicted pressure (650 PSI) exceeds design rating (600 PSI). 
                    Additionally, shift report notes bypass valve sticks above 550 PSI."
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("#### Key Integration Pattern")
            st.markdown("""
            The power of Cortex comes from combining capabilities:
            
            | Query Type | Tool Used |
            |------------|-----------|
            | Structured metrics | Cortex Analyst → SQL |
            | Document lookup | Cortex Search → RAG |
            | Risk reasoning | Agent + Model predictions |
            | Combined analysis | Agent orchestration |
            
            **Context Awareness**: When a user clicks an asset on the map and asks a question, 
            the agent receives the asset ID as context and can:
            1. Query its telemetry from Analyst
            2. Find related documents from Search
            3. Check its risk score from GRAPH_PREDICTIONS
        """)
    
    st.divider()
    
    # ========================================================================
    # 6. APPLICATION PAGES
    # ========================================================================
    st.header("Application Pages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="page-card">
            <div class="page-icon"></div>
            <div class="page-title">Home</div>
            <div class="page-desc">
                Executive dashboard with network health overview, integration KPIs, 
                and active risk alerts. Start here for a high-level pulse check.
            </div>
        </div>
        
        <div class="page-card">
            <div class="page-icon"></div>
            <div class="page-title">Network Discovery Map</div>
            <div class="page-desc">
                Interactive geospatial visualization with toggle between "as-documented" 
                and "AI-enhanced" topology. Click assets to view details and discovered connections.
            </div>
        </div>
        
        <div class="page-card">
            <div class="page-icon"></div>
            <div class="page-title">Simulation & Chat</div>
            <div class="page-desc">
                Operational tool for "what-if" scenarios. Simulate production changes and 
                chat with the Cortex AI assistant about asset specs and predicted impacts.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="page-card">
            <div class="page-icon"></div>
            <div class="page-title">Telemetry Explorer</div>
            <div class="page-desc">
                Time-series analysis tool showing how AutoGL discovered cross-network correlations 
                (e.g., the 5-minute lag between SC-PAD-42 flow and TF-V-204 pressure).
            </div>
        </div>
        
        <div class="page-card">
            <div class="page-icon"></div>
            <div class="page-title">Production Analytics</div>
            <div class="page-desc">
                VP-level dashboard tracking unified production metrics, synergy KPIs, and 
                deferment costs. Compare SnowCore vs TeraField performance.
            </div>
        </div>
        
        <div class="page-card">
            <div class="page-icon"></div>
            <div class="page-title">Document Intelligence</div>
            <div class="page-desc">
                Showcases Cortex Search capability to extract specs from P&IDs, maintenance logs, 
                and shift reports. Ask questions about legacy equipment in natural language.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()

    # ========================================================================
    # 7. TECHNOLOGY STACK
    # ========================================================================
    st.header("Technology Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Snowflake Platform")
        st.markdown("""
        <span class="tech-badge">Snowflake Notebooks</span>
        <span class="tech-badge">Cortex AI (LLM)</span>
        <span class="tech-badge">Cortex Search (RAG)</span>
        <span class="tech-badge">Cortex Analyst</span>
        <span class="tech-badge">Snowpark Python</span>
        <span class="tech-badge">Streamlit in Snowflake</span>
        """, unsafe_allow_html=True)
        
        st.markdown("#### ML & Data Science")
        st.markdown("""
        <span class="tech-badge">PyTorch</span>
        <span class="tech-badge">PyTorch Geometric</span>
        <span class="tech-badge">NetworkX</span>
        <span class="tech-badge">scikit-learn</span>
        <span class="tech-badge">pandas</span>
        <span class="tech-badge">NumPy</span>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Visualization")
        st.markdown("""
        <span class="tech-badge">PyDeck</span>
        <span class="tech-badge">Plotly</span>
        <span class="tech-badge">Matplotlib</span>
        <span class="tech-badge">Altair</span>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Infrastructure")
        st.markdown("""
        <span class="tech-badge">SPCS (Containers)</span>
        <span class="tech-badge">External Access</span>
        <span class="tech-badge">Internal Stage</span>
        <span class="tech-badge">Dynamic Tables</span>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # 8. KNOWN LIMITATIONS
    # ========================================================================
    st.header("Known Limitations & Considerations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="limitation-item">
            <strong>Self-Supervised Learning</strong><br/>
            Anomaly scores are relative, not absolute risk measures. High scores indicate 
            deviation from learned patterns, not guaranteed failures.
        </div>
        
        <div class="limitation-item">
            <strong>Static Snapshot</strong><br/>
            The GNN uses a point-in-time graph. Real networks change; predictions should be 
            refreshed periodically (recommended: daily).
        </div>
        
        <div class="limitation-item">
            <strong>Telemetry Data Quality</strong><br/>
            TeraField legacy SCADA has gaps and deadband artifacts. Model accuracy depends 
            on data completeness; assets with >20% missing data may have lower confidence.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="limitation-item">
            <strong>Link Prediction Validation</strong><br/>
            Predicted hidden connections are probabilistic. Field verification is recommended 
            for high-stakes operational decisions before relying on inferred topology.
        </div>
        
        <div class="limitation-item">
            <strong>Document Coverage</strong><br/>
            Cortex Search indexes loaded documents only. Unscanned P&IDs in file shares 
            won't be searchable until ingested into LEGACY_DOCUMENTS table.
        </div>
        
        <div class="limitation-item">
            <strong>LLM Response Accuracy</strong><br/>
            Cortex AI responses are generated, not retrieved facts. For safety-critical specs, 
            always verify against source documents.
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # 9. GETTING STARTED
    # ========================================================================
    st.header("Getting Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recommended Workflow")
        st.markdown("""
        1. **Explore the Network** → Go to **Network Discovery Map** and toggle "After AutoGL" 
           to see hidden connections discovered by the GNN
        
        2. **Identify Risks** → Look for yellow/red nodes indicating pressure anomalies or 
           high-risk scores from the model
        
        3. **Run a Simulation** → Navigate to **Simulation & Chat**, select a well pad, and 
           simulate a production increase to test network capacity
        
        4. **Ask the Assistant** → Use the chat panel to ask questions like:
           - *"What is the pressure rating for V-204?"*
           - *"Why is this asset flagged as high risk?"*
           - *"Can I route 5k extra barrels through Midland Hub?"*
        
        5. **Deep Dive** → Use **Telemetry Explorer** to see the time-series correlations 
           that led to link predictions
        """)
    
    with col2:
        st.markdown("#### Key Reference Information")
        
        st.markdown("**Risk Score Interpretation**")
        st.markdown("""
        | Score Range | Risk Level | Action |
        |-------------|------------|--------|
        | 0.0 - 0.4 | Low | Normal operation |
        | 0.4 - 0.7 | Moderate | Monitor closely |
        | 0.7 - 1.0 | High | Investigate immediately |
        """)
        
        st.markdown("**Link Prediction Confidence**")
        st.markdown("""
        | Probability | Interpretation |
        |-------------|----------------|
        | > 0.5 | Potential hidden connection |
        | > 0.8 | Strong evidence of dependency |
        | > 0.9 | High confidence; verify in field |
        """)
        
        st.markdown("**Sample Questions for Cortex**")
        st.markdown("""
        - *"Compare downtime between SnowCore and TeraField assets"*
        - *"What's the GOR trend for Delaware basin this month?"*
        - *"Find maintenance history for separator V-204"*
        """)
    
    st.divider()
    
    # ========================================================================
    # 10. FOOTER
    # ========================================================================
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; border-top: 1px solid #334155;">
        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 0.5rem;">
            Permian Command Center • Powered by Snowflake
        </div>
        <div style="color: #475569; font-size: 0.75rem;">
            Built with Streamlit in Snowflake • Graph Neural Networks via PyTorch Geometric • 
            Natural Language via Cortex AI
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
