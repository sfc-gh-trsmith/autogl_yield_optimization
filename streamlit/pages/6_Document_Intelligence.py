"""
Document Intelligence - P&ID and Maintenance Log Analysis
=========================================================
Showcases Cortex Search capability to extract "tribal knowledge" from
unstructured P&ID documents, maintenance logs, and shift reports.

Business Story: The Facilities Engineer can instantly access P&ID specs
and maintenance history without searching through shared drives.
"""

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from datetime import datetime

st.set_page_config(page_title="Document Intelligence", page_icon="📄", layout="wide")

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
    
    .document-card {
        background: var(--slate-800);
        border-radius: 12px;
        border: 1px solid var(--slate-700);
        overflow: hidden;
        height: 100%;
    }
    
    .document-header {
        background: linear-gradient(135deg, var(--slate-700) 0%, var(--slate-800) 100%);
        padding: 1rem 1.25rem;
        border-bottom: 1px solid var(--slate-700);
    }
    
    .document-title {
        color: var(--slate-200);
        font-weight: 600;
        font-size: 1rem;
        margin: 0 0 0.25rem 0;
    }
    
    .document-meta {
        color: var(--slate-400);
        font-size: 0.8rem;
    }
    
    .document-content {
        padding: 1.25rem;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        line-height: 1.6;
        color: var(--slate-300);
        white-space: pre-wrap;
        background: var(--slate-900);
    }
    
    .extraction-card {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, var(--slate-800) 100%);
        border-left: 4px solid var(--cortex-purple);
        border-radius: 0 12px 12px 0;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .extraction-label {
        color: var(--cortex-purple);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.25rem;
    }
    
    .extraction-value {
        color: var(--slate-200);
        font-size: 1.25rem;
        font-weight: 700;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .extraction-source {
        color: var(--slate-400);
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    
    .alert-extraction {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, var(--slate-800) 100%);
        border-left: 4px solid var(--risk-high);
    }
    
    .alert-extraction .extraction-label {
        color: var(--risk-high);
    }
    
    .alert-extraction .extraction-value {
        color: var(--risk-high);
    }
    
    .timeline-item {
        display: flex;
        gap: 1rem;
        padding: 1rem 0;
        border-bottom: 1px solid var(--slate-700);
    }
    
    .timeline-item:last-child {
        border-bottom: none;
    }
    
    .timeline-date {
        min-width: 100px;
        color: var(--slate-400);
        font-size: 0.85rem;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .timeline-type {
        min-width: 100px;
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        text-align: center;
    }
    
    .timeline-type.corrective {
        background: rgba(239, 68, 68, 0.2);
        color: var(--risk-high);
    }
    
    .timeline-type.preventive {
        background: rgba(34, 197, 94, 0.2);
        color: var(--risk-low);
    }
    
    .timeline-content {
        flex: 1;
        color: var(--slate-300);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .work-order-card {
        background: var(--slate-800);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid var(--slate-700);
        margin-bottom: 0.75rem;
    }
    
    .work-order-card.high-priority {
        border-left: 4px solid var(--risk-high);
    }
    
    .work-order-card.medium-priority {
        border-left: 4px solid var(--risk-medium);
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
    
    .highlight {
        background: rgba(245, 158, 11, 0.2);
        padding: 0.1rem 0.3rem;
        border-radius: 2px;
        color: var(--risk-medium);
    }
    
    .critical-highlight {
        background: rgba(239, 68, 68, 0.2);
        padding: 0.1rem 0.3rem;
        border-radius: 2px;
        color: var(--risk-high);
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
    <h1>Document Intelligence</h1>
    <p>Extract critical specifications and maintenance history from P&ID documents and shift reports using Cortex Search</p>
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
# DOCUMENT CONTENT (Simulated from files - in production these would be from Cortex Search)
# =============================================================================

# P&ID Document content
PID_DOCUMENT = """================================================================================
TERAFIELD RESOURCES - MIDLAND HUB PROCESS FLOW DIAGRAM
Document ID: PID-TF-MID-001
Revision: 3.2
Last Updated: 2019-06-15
================================================================================

FACILITY: Midland Central Gathering Hub
LOCATION: Section 14, Block 42, T1S, R34E, Midland County, TX
COORDINATES: 31.78°N, 101.88°W

================================================================================
EQUIPMENT SCHEDULE
================================================================================

TAG ID          DESCRIPTION                     DESIGN CONDITIONS
------          -----------                     -----------------
TF-V-204        2-Phase Vertical Separator      MAWP: 600 PSIG
                Manufacturer: Natco             Design Temp: 150°F
                Capacity: 5,000 BOPD            Year Installed: 2014
                
TF-V-205        2-Phase Vertical Separator      MAWP: 650 PSIG
                Manufacturer: Natco             Design Temp: 150°F
                Capacity: 4,500 BOPD            Year Installed: 2015

TF-H-301        2-Phase Horizontal Separator    MAWP: 720 PSIG
                Manufacturer: Cameron           Design Temp: 175°F
                Capacity: 8,000 BOPD            Year Installed: 2016

TF-VALVE-101    Pressure Control Valve          Rating: 550 PSI
                Manufacturer: Fisher            Type: Globe
                Size: 4"                        Cv: 125

TF-VALVE-102    Safety Relief Valve             Set Point: 600 PSI
                Manufacturer: Fisher            Type: PSV
                Size: 3"                        

TF-COMP-LP-A    Low Pressure Compressor         Max Discharge: 500 PSIG
                Manufacturer: Ingersoll Rand    HP: 350
                Year Installed: 2013

================================================================================
PROCESS NOTES
================================================================================

1. V-204 receives production from northern lease areas via 6" gathering line
   
2. CRITICAL: V-204 MAWP of 600 PSIG is the limiting factor for upstream
   pressure. Upstream facilities must not exceed 550 PSIG inlet pressure
   to maintain 50 PSI safety margin.

3. Bypass valve on V-204 has been reported to stick when pressure exceeds
   550 PSI. Maintenance ticket MT-2023-4421 pending replacement.

4. All flow from separators routes through TF-MID-HUB before compression
   at TF-COMP-LP-A.
"""

MAINTENANCE_LOG = """================================================================================
TERAFIELD RESOURCES - EQUIPMENT MAINTENANCE LOG
================================================================================

Equipment Tag: TF-V-204
Equipment Type: 2-Phase Vertical Separator
Location: Midland Hub
Manufacturer: Natco
Serial Number: NTC-2014-V-88421
Install Date: June 10, 2014

================================================================================
MAINTENANCE HISTORY
================================================================================

DATE        TYPE            DESCRIPTION                         TECHNICIAN
----        ----            -----------                         ----------

2023-10-15  CORRECTIVE      Bypass valve cycling - temporary    R. Garcia
                            fix applied. Valve sticking above
                            550 PSI. Full replacement scheduled.
                            
2023-09-01  PREVENTIVE      Annual inspection complete.          M. Williams
                            Internals in good condition.
                            Corrosion rate: 2.1 mpy (acceptable).
                            Relief valve tested - passed.
                            
2023-06-15  CORRECTIVE      Level transmitter replaced.          J. Martinez
                            LT-204A showing erratic readings.
                            Calibrated new unit to spec.
                            
2023-03-20  PREVENTIVE      Pressure safety valve (PSV)          External
                            recertification. Set point verified
                            at 600 PSIG. Certificate #PSV-2023-441.
                            
2022-09-01  PREVENTIVE      Annual inspection complete.          T. Brown
                            Minor pitting on inlet nozzle.
                            Recommend monitoring.

================================================================================
OUTSTANDING WORK ORDERS
================================================================================

WO Number       Priority    Description                     Due Date
---------       --------    -----------                     --------
MT-2023-4421    HIGH        Bypass valve replacement        2023-11-15
                            Valve sticks above 550 PSI.
                            SAFETY CONCERN - expedite.
                            
MT-2023-4489    MEDIUM      Inlet nozzle inspection         2024-03-01
                            Follow-up on pitting noted
                            in 2022 inspection.

================================================================================
CRITICAL EQUIPMENT PARAMETERS
================================================================================

Parameter                   Design Value    Current Limit   Last Reading
---------                   ------------    -------------   ------------
Max Allowable WP (MAWP)     600 PSIG        600 PSIG        N/A
Operating Pressure          400-550 PSIG    550 PSIG MAX    512 PSIG
Operating Temperature       100-150°F       150°F MAX       128°F
Corrosion Rate             <5 mpy          <5 mpy          2.1 mpy
"""

SHIFT_REPORT = """================================================================================
TERAFIELD RESOURCES - DAILY SHIFT HANDOVER REPORT
================================================================================

Date: October 12, 2023
Shift: Day Shift (06:00 - 18:00)
Operator: Mike Johnson
Relief Operator: Sarah Chen
Weather: Clear, 78°F

================================================================================
FACILITY STATUS SUMMARY
================================================================================

Midland Hub Status: OPERATIONAL
Overall Production: 12,450 BOPD (97% of target)

Equipment Status:
- TF-V-204: OPERATIONAL (watching closely - see notes)
- TF-V-205: OPERATIONAL  
- TF-H-301: OPERATIONAL
- TF-COMP-LP-A: OPERATIONAL (vibration within limits)
- TF-MID-HUB: OPERATIONAL

================================================================================
OPERATOR NOTES - IMPORTANT
================================================================================

1. VALVE ISSUE - TF-V-204
   Operator Note: Bypass valve on V-204 sticks when pressure exceeds 550. 
   Recommend replacement. Had to manually cycle it twice this shift when 
   upstream pressure spiked to 560 PSI around 14:30.
   
   Action: Called maintenance, they will inspect during next turnaround.
   Workaround: Reduced choke on northern wells to keep inlet < 540 PSI.

2. COMPRESSOR VIBRATION
   TF-COMP-LP-A showing 0.35 in/sec vibration on bearing #2.
   Within limits (0.5 max) but trending up from 0.28 last week.
   Recommend predictive maintenance check within 2 weeks.

================================================================================
PRODUCTION DATA
================================================================================

Well Pad        Status      Oil (BOPD)    Gas (MCFD)    Water (BWPD)
--------        ------      ----------    ----------    -----------
North Lease 1   Producing   2,100         4,200         850
North Lease 2   Producing   1,850         3,700         720
North Lease 3   Producing   2,400         4,800         1,100
East Block      Producing   3,200         6,400         1,450
South Wells     Producing   2,900         5,800         980
--------        ------      ----------    ----------    -----------
TOTAL                       12,450        24,900        5,100

================================================================================
ITEMS FOR INCOMING SHIFT
================================================================================

1. Monitor V-204 inlet pressure closely - keep below 540 PSI
2. Check compressor vibration readings at 20:00 and 02:00
3. Expect tanker truck at 22:00 for water disposal
4. Engineering team visiting tomorrow AM for integration assessment
"""

# =============================================================================
# SECTION 1: KEY EXTRACTIONS
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">01</span>
    <h2>AI-Extracted Critical Information</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color: #94a3b8; margin-bottom: 1.5rem;">
    Cortex Search automatically extracts key specifications and alerts from unstructured P&ID documents, 
    maintenance logs, and shift reports. These extractions power the risk assessments shown elsewhere in the application.
</p>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="extraction-card alert-extraction">
        <div class="extraction-label">Critical Equipment Limit</div>
        <div class="extraction-value">600 PSI</div>
        <div style="color: #e2e8f0; font-size: 0.9rem; margin-top: 0.25rem;">TF-V-204 MAWP</div>
        <div class="extraction-source">Source: P&ID TF-MID-001</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="extraction-card alert-extraction">
        <div class="extraction-label">Operating Constraint</div>
        <div class="extraction-value">550 PSI MAX</div>
        <div style="color: #e2e8f0; font-size: 0.9rem; margin-top: 0.25rem;">Inlet pressure limit</div>
        <div class="extraction-source">Source: Process Notes</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="extraction-card alert-extraction">
        <div class="extraction-label">Open Work Order</div>
        <div class="extraction-value">MT-2023-4421</div>
        <div style="color: #e2e8f0; font-size: 0.9rem; margin-top: 0.25rem;">Bypass valve replacement</div>
        <div class="extraction-source">Priority: HIGH</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="extraction-card">
        <div class="extraction-label">Design Capacity</div>
        <div class="extraction-value">5,000 BOPD</div>
        <div style="color: #e2e8f0; font-size: 0.9rem; margin-top: 0.25rem;">TF-V-204 throughput</div>
        <div class="extraction-source">Source: Equipment Schedule</div>
    </div>
    """, unsafe_allow_html=True)

# Insight callout
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(30, 41, 59, 0.9) 100%); 
            border-left: 4px solid #ef4444; border-radius: 0 12px 12px 0; padding: 1.25rem; margin: 1.5rem 0;">
    <div style="color: #ef4444; font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem;">
        Cross-Reference Alert: Integration Risk Identified
    </div>
    <p style="color: #e2e8f0; margin: 0; line-height: 1.6;">
        AutoGL detected that <strong>SC-PAD-42</strong> production increases could push TF-V-204 inlet pressure 
        above <strong>550 PSI</strong>. P&ID extraction confirms this is the maximum safe operating pressure, 
        and maintenance logs show the bypass valve has <strong>known issues above 550 PSI</strong>. 
        Work order MT-2023-4421 is pending but not yet completed.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECTION 2: P&ID DOCUMENT VIEWER
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">02</span>
    <h2>P&ID Document: Midland Hub Process Flow</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="document-card">
    <div class="document-header">
        <div class="document-title">PID-TF-MID-001 - TeraField Midland Hub Process Flow Diagram</div>
        <div class="document-meta">Rev 3.2 | Last Updated: 2019-06-15 | Status: Current</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Display document with highlighting
doc_display = PID_DOCUMENT.replace(
    "MAWP: 600 PSIG", 
    '<span class="critical-highlight">MAWP: 600 PSIG</span>'
).replace(
    "550 PSIG", 
    '<span class="highlight">550 PSIG</span>'
).replace(
    "MT-2023-4421",
    '<span class="critical-highlight">MT-2023-4421</span>'
).replace(
    "Bypass valve on V-204 has been reported to stick",
    '<span class="critical-highlight">Bypass valve on V-204 has been reported to stick</span>'
)

st.markdown(f"""
<div style="background: #0f172a; border-radius: 0 0 12px 12px; border: 1px solid #334155; border-top: none; 
            padding: 1.25rem; max-height: 400px; overflow-y: auto;">
    <pre style="font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; line-height: 1.6; 
                color: #cbd5e1; white-space: pre-wrap; margin: 0;">{doc_display}</pre>
</div>
""", unsafe_allow_html=True)

# Teaching section
st.markdown("""
<div class="teaching-section">
    <h3>How Cortex Search Works</h3>
    <p>Cortex Search indexes unstructured documents (PDFs, text files) and enables natural language queries:</p>
    <ul>
        <li><strong>Query:</strong> "What is the maximum pressure rating for V-204?"</li>
        <li><strong>Result:</strong> Retrieves relevant chunks from P&ID: "MAWP: 600 PSIG"</li>
        <li><strong>Application:</strong> Used by AI Agent to validate simulation requests against equipment limits</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECTION 3: MAINTENANCE HISTORY TIMELINE
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">03</span>
    <h2>Maintenance History: TF-V-204</h2>
</div>
""", unsafe_allow_html=True)

# Maintenance timeline
maintenance_events = [
    {"date": "2023-10-15", "type": "CORRECTIVE", "desc": "Bypass valve cycling - temporary fix applied. Valve sticking above 550 PSI.", "tech": "R. Garcia"},
    {"date": "2023-09-01", "type": "PREVENTIVE", "desc": "Annual inspection complete. Corrosion rate: 2.1 mpy (acceptable).", "tech": "M. Williams"},
    {"date": "2023-06-15", "type": "CORRECTIVE", "desc": "Level transmitter LT-204A replaced - erratic readings.", "tech": "J. Martinez"},
    {"date": "2023-03-20", "type": "PREVENTIVE", "desc": "PSV recertification. Set point verified at 600 PSIG.", "tech": "External"},
    {"date": "2022-09-01", "type": "PREVENTIVE", "desc": "Annual inspection. Minor pitting on inlet nozzle noted.", "tech": "T. Brown"},
]

st.markdown("""
<div style="background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 1.5rem;">
    <h4 style="color: #e2e8f0; margin: 0 0 1rem 0;">Maintenance Timeline</h4>
""", unsafe_allow_html=True)

for event in maintenance_events:
    type_class = "corrective" if event["type"] == "CORRECTIVE" else "preventive"
    st.markdown(f"""
    <div class="timeline-item">
        <div class="timeline-date">{event['date']}</div>
        <div class="timeline-type {type_class}">{event['type']}</div>
        <div class="timeline-content">
            {event['desc']}
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.25rem;">Technician: {event['tech']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Outstanding Work Orders
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Outstanding Work Orders")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="work-order-card high-priority">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span style="color: #ef4444; font-weight: 600;">MT-2023-4421</span>
            <span style="background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 0.2rem 0.5rem; 
                         border-radius: 4px; font-size: 0.75rem;">HIGH PRIORITY</span>
        </div>
        <div style="color: #e2e8f0; font-weight: 500; margin-bottom: 0.5rem;">Bypass Valve Replacement</div>
        <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5;">
            Valve sticks above 550 PSI. <strong style="color: #ef4444;">SAFETY CONCERN - expedite.</strong>
        </div>
        <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.75rem;">Due: 2023-11-15</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="work-order-card medium-priority">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span style="color: #f59e0b; font-weight: 600;">MT-2023-4489</span>
            <span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 0.2rem 0.5rem; 
                         border-radius: 4px; font-size: 0.75rem;">MEDIUM</span>
        </div>
        <div style="color: #e2e8f0; font-weight: 500; margin-bottom: 0.5rem;">Inlet Nozzle Inspection</div>
        <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5;">
            Follow-up on pitting noted in 2022 annual inspection.
        </div>
        <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.75rem;">Due: 2024-03-01</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SECTION 4: SHIFT REPORT VIEWER
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">04</span>
    <h2>Shift Report: October 12, 2023</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="document-card">
    <div class="document-header">
        <div class="document-title">Daily Shift Handover Report - Midland Hub</div>
        <div class="document-meta">Day Shift (06:00 - 18:00) | Operator: Mike Johnson | Status: OPERATIONAL</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Key operator notes - highlighted
st.markdown("""
<div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; 
            border-radius: 0 8px 8px 0; padding: 1rem 1.25rem; margin: 1rem 0;">
    <div style="color: #f59e0b; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; 
                letter-spacing: 0.05em; margin-bottom: 0.5rem;">Operator Note Extracted</div>
    <p style="color: #e2e8f0; margin: 0; line-height: 1.6;">
        "<strong>Bypass valve on V-204 sticks when pressure exceeds 550.</strong> Recommend replacement. 
        Had to manually cycle it twice this shift when upstream pressure spiked to 560 PSI around 14:30."
    </p>
    <p style="color: #94a3b8; font-size: 0.85rem; margin: 0.75rem 0 0 0;">
        <strong>Action taken:</strong> Reduced choke on northern wells to keep inlet &lt; 540 PSI.
    </p>
</div>
""", unsafe_allow_html=True)

# Display shift report
shift_display = SHIFT_REPORT.replace(
    "Bypass valve on V-204 sticks when pressure exceeds 550",
    '<span class="critical-highlight">Bypass valve on V-204 sticks when pressure exceeds 550</span>'
).replace(
    "560 PSI",
    '<span class="critical-highlight">560 PSI</span>'
).replace(
    "keep inlet < 540 PSI",
    '<span class="highlight">keep inlet &lt; 540 PSI</span>'
)

st.markdown(f"""
<div style="background: #0f172a; border-radius: 0 0 12px 12px; border: 1px solid #334155; border-top: none; 
            padding: 1.25rem; max-height: 350px; overflow-y: auto;">
    <pre style="font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; line-height: 1.6; 
                color: #cbd5e1; white-space: pre-wrap; margin: 0;">{shift_display}</pre>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECTION 5: DOCUMENT SEARCH
# =============================================================================

st.markdown("""
<div class="section-header">
    <span class="section-number">05</span>
    <h2>Document Search (Cortex Search)</h2>
</div>
""", unsafe_allow_html=True)

# Sample queries
sample_queries = [
    "What is the MAWP for TF-V-204?",
    "Are there any open work orders for the bypass valve?",
    "What is the operating pressure limit for V-204?",
    "Who performed the last inspection on V-204?"
]

selected_query = st.selectbox(
    "Select a sample query or type your own:",
    [""] + sample_queries,
    index=0
)

custom_query = st.text_input(
    "Or enter custom query:",
    placeholder="e.g., What safety issues have been reported?"
)

query = custom_query if custom_query else selected_query

if query:
    st.markdown(f"""
    <div style="background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 1.5rem; margin-top: 1rem;">
        <div style="color: #a855f7; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
            Cortex Search Result
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">
            Query: <em>"{query}"</em>
        </div>
    """, unsafe_allow_html=True)
    
    # Simulated responses based on query
    if "MAWP" in query.upper() or "pressure rating" in query.lower():
        st.markdown("""
        <div style="color: #e2e8f0; line-height: 1.7;">
            <strong>Answer:</strong> The Maximum Allowable Working Pressure (MAWP) for TF-V-204 is <strong style="color: #ef4444;">600 PSIG</strong>.<br><br>
            <strong>Source:</strong> P&ID Document PID-TF-MID-001, Equipment Schedule section.<br><br>
            <strong>Additional Context:</strong> Process notes indicate that upstream inlet pressure should not exceed 550 PSIG to maintain a 50 PSI safety margin.
        </div>
        """, unsafe_allow_html=True)
    elif "work order" in query.lower() or "bypass valve" in query.lower():
        st.markdown("""
        <div style="color: #e2e8f0; line-height: 1.7;">
            <strong>Answer:</strong> Yes, work order <strong style="color: #ef4444;">MT-2023-4421</strong> is open for bypass valve replacement on TF-V-204.<br><br>
            <strong>Priority:</strong> HIGH<br>
            <strong>Issue:</strong> Valve sticks above 550 PSI - SAFETY CONCERN<br>
            <strong>Due Date:</strong> 2023-11-15<br><br>
            <strong>Source:</strong> Maintenance Log, Outstanding Work Orders section.
        </div>
        """, unsafe_allow_html=True)
    elif "operating" in query.lower() or "limit" in query.lower():
        st.markdown("""
        <div style="color: #e2e8f0; line-height: 1.7;">
            <strong>Answer:</strong> The maximum operating inlet pressure for TF-V-204 is <strong style="color: #f59e0b;">550 PSIG</strong>.<br><br>
            <strong>Reason:</strong> This maintains a 50 PSI safety margin below the 600 PSI MAWP.<br><br>
            <strong>Current Workaround:</strong> Operators are keeping inlet below 540 PSI due to known bypass valve issue.<br><br>
            <strong>Sources:</strong> P&ID Process Notes, Shift Report 2023-10-12.
        </div>
        """, unsafe_allow_html=True)
    elif "inspection" in query.lower():
        st.markdown("""
        <div style="color: #e2e8f0; line-height: 1.7;">
            <strong>Answer:</strong> The last inspection on TF-V-204 was performed on <strong>2023-09-01</strong> by <strong>M. Williams</strong>.<br><br>
            <strong>Type:</strong> Annual Preventive Inspection<br>
            <strong>Findings:</strong> Internals in good condition. Corrosion rate: 2.1 mpy (acceptable). Relief valve tested - passed.<br><br>
            <strong>Source:</strong> Maintenance Log, Maintenance History section.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="color: #e2e8f0; line-height: 1.7;">
            <strong>Answer:</strong> Searching indexed documents for relevant information...<br><br>
            <em style="color: #94a3b8;">In production, Cortex Search would return relevant document chunks matching your query.</em>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Final teaching section
st.markdown("""
<div class="teaching-section" style="margin-top: 2rem;">
    <h3>The Value of Document Intelligence</h3>
    <p>This page demonstrates how Cortex Search transforms "tribal knowledge" trapped in PDFs and text files into actionable intelligence:</p>
    <ul>
        <li><strong>Instant Access:</strong> Engineers no longer search shared drives for P&ID specs when an alarm sounds</li>
        <li><strong>Cross-Reference:</strong> AI automatically links maintenance history to equipment specifications</li>
        <li><strong>Risk Validation:</strong> Simulation results are validated against extracted equipment limits</li>
        <li><strong>Knowledge Preservation:</strong> Operator notes and shift reports become searchable institutional memory</li>
    </ul>
    <p>Without this capability, the connection between the bypass valve issue (from maintenance logs), the 550 PSI operating limit 
    (from P&ID), and the AutoGL-predicted pressure risk would remain hidden in separate documents.</p>
</div>
""", unsafe_allow_html=True)

