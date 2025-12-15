"""
Shared Chat Panel Component
===========================
Reusable right-side chat panel for AI Integration Assistant.
Can be included on any page for contextual assistance.
"""

import streamlit as st
import json


def get_chat_panel_css():
    """Return CSS for styling the chat panel."""
    return """
    <style>
        .chat-panel {
            background: #1e293b;
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid #334155;
            height: 100%;
        }
        
        .chat-panel-header {
            color: #29B5E8;
            font-size: 1rem;
            font-weight: 600;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #334155;
            margin-bottom: 0.75rem;
        }
        
        .user-msg {
            background: #3b82f6;
            color: white;
            padding: 0.6rem 0.8rem;
            border-radius: 10px 10px 4px 10px;
            margin: 0.4rem 0;
            margin-left: 15%;
            font-size: 0.85rem;
        }
        
        .assistant-msg {
            background: #334155;
            color: #e2e8f0;
            padding: 0.6rem 0.8rem;
            border-radius: 10px 10px 10px 4px;
            margin: 0.4rem 0;
            margin-right: 15%;
            border-left: 2px solid #29B5E8;
            font-size: 0.85rem;
        }
        
        .system-msg {
            background: rgba(168, 85, 247, 0.15);
            color: #a855f7;
            padding: 0.4rem 0.6rem;
            border-radius: 6px;
            margin: 0.3rem 0;
            font-size: 0.75rem;
            text-align: center;
        }
        
        .chat-welcome {
            color: #64748b;
            text-align: center;
            padding: 1rem;
            font-size: 0.85rem;
        }
        
        .chat-welcome ul {
            text-align: left;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        .chat-welcome li {
            margin: 0.25rem 0;
        }
        
        .context-badge {
            background: rgba(6, 182, 212, 0.15);
            border: 1px solid #06b6d4;
            color: #06b6d4;
            padding: 0.4rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """


def render_chat_panel(session, schema_prefix: str, assets_df=None, panel_key: str = "main"):
    """
    Render the chat panel component.
    
    Args:
        session: Snowflake session object
        schema_prefix: Fully qualified schema prefix (e.g., "DB.SCHEMA")
        assets_df: Optional DataFrame with asset data for lookups
        panel_key: Unique key prefix to avoid widget conflicts across pages
    """
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize selected asset context (can be set from other pages)
    if 'selected_asset_context' not in st.session_state:
        st.session_state.selected_asset_context = None
    
    # Inject CSS
    st.markdown(get_chat_panel_css(), unsafe_allow_html=True)
    
    # Panel header
    st.markdown("""
    <div class="chat-panel-header">💬 AI Integration Assistant</div>
    """, unsafe_allow_html=True)
    
    # Show selected asset context if available
    if st.session_state.selected_asset_context:
        ctx = st.session_state.selected_asset_context
        st.markdown(f"""
        <div class="context-badge">
            🎯 <strong>{ctx.get('asset_id', 'Unknown')}</strong> 
            ({ctx.get('source_system', '')} {ctx.get('asset_type', '')})
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✕ Clear", key=f"clear_ctx_{panel_key}", help="Clear asset context"):
            st.session_state.selected_asset_context = None
            st.rerun()
    
    # Chat history display
    chat_container = st.container(height=280)
    
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="chat-welcome">
                <p>👋 Hello! I'm the Permian Integration Assistant.</p>
                <p>Ask me about:</p>
                <ul>
                    <li>Asset risk assessments</li>
                    <li>Equipment specifications</li>
                    <li>Production routing</li>
                    <li>Network comparisons</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
                elif msg['role'] == 'assistant':
                    st.markdown(f'<div class="assistant-msg">{msg["content"]}</div>', unsafe_allow_html=True)
                elif msg['role'] == 'system':
                    st.markdown(f'<div class="system-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Quick prompts - context-aware if asset is selected
    if st.session_state.selected_asset_context:
        asset_id = st.session_state.selected_asset_context.get('asset_id', '')
        prompts = [
            f"What is the pressure rating for {asset_id}?",
            f"Why is {asset_id} flagged as high risk?",
            f"What downstream assets are affected by {asset_id}?"
        ]
    else:
        prompts = [
            "What is the pressure rating for V-204?",
            "Which assets have high risk scores?",
            "Compare SnowCore vs TeraField downtime"
        ]
    
    selected = st.selectbox(
        "Quick prompts:",
        [""] + prompts,
        key=f"prompts_{panel_key}",
        label_visibility="collapsed"
    )
    
    # Chat input
    user_input = st.text_input(
        "Ask:",
        value=selected if selected else "",
        placeholder="Type your question...",
        key=f"chat_input_{panel_key}",
        label_visibility="collapsed"
    )
    
    # Send / Clear buttons
    col_send, col_clear = st.columns([3, 1])
    
    with col_send:
        if st.button("📤 Send", key=f"send_{panel_key}", use_container_width=True):
            if user_input:
                _process_chat_message(session, schema_prefix, user_input, assets_df)
    
    with col_clear:
        if st.button("🗑️", key=f"clear_{panel_key}", use_container_width=True, help="Clear chat"):
            st.session_state.chat_history = []
            st.rerun()


def _process_chat_message(session, schema_prefix: str, user_input: str, assets_df=None):
    """Process a chat message and get response."""
    # Add user message
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Build context-aware prompt with asset context if available
    context_prefix = ""
    if st.session_state.selected_asset_context:
        asset_ctx = st.session_state.selected_asset_context
        context_prefix = f"Context: The user has selected asset {asset_ctx.get('asset_id', 'unknown')} " \
                       f"(Type: {asset_ctx.get('asset_type', 'unknown')}, " \
                       f"System: {asset_ctx.get('source_system', 'unknown')}, " \
                       f"Risk Score: {asset_ctx.get('risk_score', 0):.2f}). "
    
    full_prompt = context_prefix + user_input
    
    # Call Cortex Agent with Analyst + Search tools
    try:
        # Use the actual Cortex Agent which has access to both Analyst and Search
        agent_response = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.AGENT(
                '{schema_prefix}.AUTOGL_YIELD_OPTIMIZATION_AGENT',
                '{full_prompt.replace("'", "''")}'
            ) AS RESPONSE
        """).to_pandas()
        
        # Parse the agent response (may be JSON with multiple tool calls)
        raw_response = agent_response['RESPONSE'].values[0]
        
        # Try to extract text from potential JSON response
        try:
            parsed = json.loads(raw_response) if isinstance(raw_response, str) and raw_response.startswith('{') else None
            if parsed and 'text' in parsed:
                assistant_response = parsed['text']
            elif parsed and 'content' in parsed:
                assistant_response = parsed['content']
            else:
                assistant_response = str(raw_response)
        except (json.JSONDecodeError, TypeError):
            assistant_response = str(raw_response)
            
    except Exception as agent_error:
        # Fallback to COMPLETE if Agent fails (e.g., not yet deployed)
        try:
            response = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-large2',
                    'You are the Permian Integration Assistant. You help with asset risk assessments, equipment specifications from P&IDs, production routing, and network comparisons. {context_prefix}Answer concisely: {user_input.replace("'", "''")}'
                ) AS RESPONSE
            """).to_pandas()
            assistant_response = response['RESPONSE'].values[0]
        except Exception as complete_error:
            # Final fallback with hardcoded responses
            assistant_response = _get_fallback_response(user_input, assets_df)
    
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': assistant_response
    })
    
    st.rerun()


def _get_fallback_response(user_input: str, assets_df=None):
    """Get a fallback response when Cortex is unavailable."""
    user_lower = user_input.lower()
    
    if 'v-204' in user_lower or 'pressure rating' in user_lower:
        return "Based on the P&ID document, **TF-V-204** has a Maximum Allowable Working Pressure (MAWP) of **600 PSIG**. This is a 2-Phase Vertical Separator manufactured by Natco, installed in 2014. Note: There's an open maintenance ticket (MT-2023-4421) for the bypass valve which sticks above 550 PSI."
    
    elif 'high risk' in user_lower or 'risk score' in user_lower:
        if assets_df is not None:
            high_risk = assets_df[assets_df['RISK_SCORE'] > 0.7][['ASSET_ID', 'RISK_SCORE']].to_dict('records')
            if high_risk:
                asset_list = ", ".join([f"**{a['ASSET_ID']}** ({a['RISK_SCORE']:.2f})" for a in high_risk])
                return f"The following assets have high risk scores: {asset_list}. These assets are flagged by the AutoGL model as having elevated pressure anomaly risk."
        return "Currently, no assets have risk scores above 0.7. The network appears to be operating within normal parameters."
    
    elif 'downtime' in user_lower or 'compare' in user_lower:
        return "Based on SCADA aggregates, TeraField (legacy) assets show approximately 15% higher downtime compared to SnowCore assets over the past 7 days. This is likely due to older equipment and communication gaps in the legacy historian system."
    
    else:
        return "I can help you with asset risk assessments, equipment specifications, production routing, and network comparisons. Could you provide more specific details about what you'd like to know?"


def add_simulation_result_to_chat(result_type: str, message: str):
    """Add a simulation result to the chat history."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.session_state.chat_history.append({
        'role': 'system',
        'content': f"🔬 Simulation: {message}"
    })

