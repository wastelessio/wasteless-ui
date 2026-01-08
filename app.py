#!/usr/bin/env python3
"""
Wasteless.io - Web UI
=====================

Main Streamlit application for Wasteless cloud cost optimization platform.

This provides a user-friendly interface for:
- Viewing cost optimization recommendations
- Approving/rejecting remediation actions
- Tracking verified savings
- Managing safeguard configurations

Author: Wasteless Team
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Wasteless.io - Cloud Cost Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database connection utility
@st.cache_resource
def get_db_connection():
    """Get PostgreSQL database connection."""
    import psycopg2

    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'wasteless'),
            user=os.getenv('DB_USER', 'wasteless'),
            password=os.getenv('DB_PASSWORD', 'wasteless_dev_2025')
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info("💡 Make sure PostgreSQL is running and credentials are correct in .env")
        return None

# Sidebar navigation
st.sidebar.image("https://via.placeholder.com/150x50/667eea/ffffff?text=Wasteless.io", use_container_width=True)
st.sidebar.title("🧭 Navigation")
st.sidebar.markdown("---")

# Connection status
conn = get_db_connection()
if conn:
    st.sidebar.success("✅ Database Connected")
else:
    st.sidebar.error("❌ Database Disconnected")
    st.stop()

# Main page content
st.markdown('<h1 class="main-header">💰 Wasteless.io</h1>', unsafe_allow_html=True)
st.markdown("**Autonomous cloud cost optimization. From detection to execution.**")
st.markdown("---")

# Welcome section
col1, col2, col3 = st.columns(3)

# Fetch key metrics
cursor = conn.cursor()

# Potential savings
cursor.execute("""
    SELECT COALESCE(SUM(estimated_monthly_savings_eur), 0) as total
    FROM recommendations
    WHERE status = 'pending'
""")
potential_savings = cursor.fetchone()[0]

# Pending recommendations count
cursor.execute("""
    SELECT COUNT(*)
    FROM recommendations
    WHERE status = 'pending'
""")
pending_count = cursor.fetchone()[0]

# Actions executed
cursor.execute("""
    SELECT COUNT(*)
    FROM actions_log
    WHERE action_status = 'success'
""")
actions_count = cursor.fetchone()[0]

cursor.close()

# Display metrics
with col1:
    st.metric(
        label="💵 Potential Monthly Savings",
        value=f"€{potential_savings:,.2f}",
        delta=f"€{potential_savings * 12:,.0f}/year"
    )

with col2:
    st.metric(
        label="📋 Pending Recommendations",
        value=f"{pending_count}",
        delta="Ready to review"
    )

with col3:
    st.metric(
        label="✅ Actions Executed",
        value=f"{actions_count}",
        delta="Successfully applied"
    )

st.markdown("---")

# Recent activity
st.subheader("📊 Recent Activity")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 Latest Waste Detected")

    query = """
        SELECT
            resource_id,
            waste_type,
            monthly_waste_eur,
            confidence_score,
            created_at
        FROM waste_detected
        ORDER BY created_at DESC
        LIMIT 5
    """
    df_waste = pd.read_sql(query, conn)

    if not df_waste.empty:
        st.dataframe(
            df_waste,
            column_config={
                "resource_id": "Instance",
                "waste_type": "Type",
                "monthly_waste_eur": st.column_config.NumberColumn(
                    "€/month",
                    format="€%.2f"
                ),
                "confidence_score": st.column_config.ProgressColumn(
                    "Confidence",
                    min_value=0,
                    max_value=1,
                ),
                "created_at": st.column_config.DatetimeColumn(
                    "Detected",
                    format="DD/MM/YY HH:mm"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No waste detected yet. Run the detection pipeline first.")

with col2:
    st.markdown("### 🚀 Latest Actions")

    query = """
        SELECT
            resource_id,
            action_type,
            action_status,
            action_date
        FROM actions_log
        ORDER BY action_date DESC
        LIMIT 5
    """
    df_actions = pd.read_sql(query, conn)

    if not df_actions.empty:
        # Add emoji based on status
        def status_emoji(status):
            return "✅" if status == "success" else "❌" if status == "failed" else "🔄"

        df_actions['status_display'] = df_actions['action_status'].apply(status_emoji)

        st.dataframe(
            df_actions[['resource_id', 'action_type', 'status_display', 'action_date']],
            column_config={
                "resource_id": "Instance",
                "action_type": "Action",
                "status_display": "Status",
                "action_date": st.column_config.DatetimeColumn(
                    "Date",
                    format="DD/MM/YY HH:mm"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No actions executed yet.")

st.markdown("---")

# Quick actions
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 View Recommendations", use_container_width=True):
        st.switch_page("pages/2_📋_Recommendations.py")

with col2:
    if st.button("📊 Open Dashboard", use_container_width=True):
        st.switch_page("pages/1_📊_Dashboard.py")

with col3:
    if st.button("📜 View History", use_container_width=True):
        st.switch_page("pages/3_📜_History.py")

with col4:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/4_⚙️_Settings.py")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>Wasteless.io</strong> - Stop monitoring waste. Start eliminating it.</p>
    <p style="font-size: 0.9rem;">
        Built with precision for CFOs who demand results. |
        <a href="https://github.com/wastelessio/wasteless-ui" target="_blank">GitHub</a> |
        <a href="mailto:wasteless.io.entreprise@gmail.com">Contact</a>
    </p>
</div>
""", unsafe_allow_html=True)
