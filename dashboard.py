"""
Streamlit dashboard for SOC Alert Triage
Interactive filtering and exploration of prioritized alerts
"""

import streamlit as st
import pandas as pd
from data_loader import load_alerts
from scoring_engine import ScoringEngine


# Page configuration
st.set_page_config(
    page_title="SOC Alert Triage Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .critical { border-left-color: #e74c3c; }
    .high { border-left-color: #f39c12; }
    .medium { border-left-color: #3498db; }
    .low { border-left-color: #27ae60; }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🚨 SOC Alert Triage Dashboard")
st.markdown("**Interactive alert filtering and risk assessment**")

# Load data once (cached for performance)
@st.cache_data
def load_and_score_alerts():
    try:
        alerts = load_alerts("mock_alerts.json")
        engine = ScoringEngine(
            severity_weights={'low': 20, 'medium': 50, 'high': 90},
            asset_weights={'standard': 10, 'important': 50, 'critical': 100},
            frequency_factor=0.1,
            risk_threshold=60.0
        )
        scored_alerts = engine.score_alerts(alerts)
        return scored_alerts
    except Exception as e:
        st.error(f"Error loading alerts: {e}")
        return []

scored_alerts = load_and_score_alerts()

if not scored_alerts:
    st.error("No alerts loaded. Check mock_alerts.json")
    st.stop()

# Convert to DataFrame for easier filtering
df = pd.DataFrame([
    {
        'Alert ID': sa.alert['alert_id'],
        'Risk Score': sa.risk_score,
        'Priority': sa.priority,
        'Severity': sa.alert['severity'].upper(),
        'Asset Type': sa.alert['asset_type'],
        'Frequency': sa.alert['frequency'],
        'Source': sa.alert['source'],
        'Timestamp': sa.alert['timestamp'],
        'Reason': sa.explanation
    }
    for sa in scored_alerts
])

# Sidebar filters
st.sidebar.header("🎯 Filters")

# Risk Score Threshold Slider
risk_threshold = st.sidebar.slider(
    "Risk Score Threshold",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
    help="Show alerts with risk score >= this value"
)

# Severity Filter
severities = st.sidebar.multiselect(
    "Severity Level",
    options=sorted(df['Severity'].unique()),
    default=sorted(df['Severity'].unique()),
    help="Filter by alert severity"
)

# Asset Type Filter
asset_types = st.sidebar.multiselect(
    "Asset Type",
    options=sorted(df['Asset Type'].unique()),
    default=sorted(df['Asset Type'].unique()),
    help="Filter by asset type"
)

# Priority Filter
priorities = st.sidebar.multiselect(
    "Priority Level",
    options=['Critical', 'High', 'Medium', 'Low'],
    default=['Critical', 'High', 'Medium', 'Low'],
    help="Filter by triage priority"
)

# Source Filter
sources = st.sidebar.multiselect(
    "Alert Source",
    options=sorted(df['Source'].unique()),
    default=sorted(df['Source'].unique()),
    help="Filter by alert source (IDS, EDR, SIEM, etc.)"
)

# Apply filters
filtered_df = df[
    (df['Risk Score'] >= risk_threshold) &
    (df['Severity'].isin(severities)) &
    (df['Asset Type'].isin(asset_types)) &
    (df['Priority'].isin(priorities)) &
    (df['Source'].isin(sources))
]

# Display summary metrics
st.header("📊 Summary")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    critical_count = len(filtered_df[filtered_df['Priority'] == 'Critical'])
    st.metric("🔴 Critical", critical_count)

with col2:
    high_count = len(filtered_df[filtered_df['Priority'] == 'High'])
    st.metric("🟠 High", high_count)

with col3:
    medium_count = len(filtered_df[filtered_df['Priority'] == 'Medium'])
    st.metric("🔵 Medium", medium_count)

with col4:
    low_count = len(filtered_df[filtered_df['Priority'] == 'Low'])
    st.metric("🟢 Low", low_count)

with col5:
    avg_risk = filtered_df['Risk Score'].mean() if len(filtered_df) > 0 else 0
    st.metric("📈 Avg Risk", f"{avg_risk:.1f}")

st.divider()

# Display filtered alerts
st.header(f"🔍 Alerts ({len(filtered_df)} results)")

if len(filtered_df) == 0:
    st.warning("No alerts match the selected filters.")
else:
    # Sort by risk score descending
    filtered_df_sorted = filtered_df.sort_values('Risk Score', ascending=False)
    
    # Display as expandable cards
    for idx, row in filtered_df_sorted.iterrows():
        # Color code by priority
        priority_color = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🔵',
            'Low': '🟢'
        }
        
        with st.expander(
            f"{priority_color.get(row['Priority'], '⚪')} {row['Alert ID']} | "
            f"Risk: {row['Risk Score']:.1f} | {row['Priority'].upper()}"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Risk Score:** {row['Risk Score']:.1f}/100")
                st.write(f"**Severity:** {row['Severity']}")
                st.write(f"**Frequency:** {row['Frequency']} occurrences")
                st.write(f"**Timestamp:** {row['Timestamp']}")
            
            with col2:
                st.write(f"**Priority:** {row['Priority']}")
                st.write(f"**Asset Type:** {row['Asset Type']}")
                st.write(f"**Source:** {row['Source']}")
            
            st.markdown("---")
            st.write(f"**Explanation:** {row['Reason']}")
    
    # Option to download filtered data
    st.divider()
    csv = filtered_df_sorted.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Alerts (CSV)",
        data=csv,
        file_name="filtered_alerts.csv",
        mime="text/csv"
    )

# Footer
st.divider()
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>"
    "AI-Assisted SOC Alert Triage Prototype</p>",
    unsafe_allow_html=True
)
