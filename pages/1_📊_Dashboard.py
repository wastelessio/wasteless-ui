#!/usr/bin/env python3
"""
Dashboard Page
==============

Executive dashboard with KPIs, charts, and trends.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Dashboard - Wasteless.io",
    page_icon="static/images/favicon.svg",
    layout="wide"
)

from utils.sidebar import setup_sidebar

st.title("📊 Executive Dashboard")
st.markdown("Real-time cloud cost optimization metrics")
st.markdown("---")

# Setup sidebar and get database connection
conn = setup_sidebar()
if not conn:
    st.error("❌ Cannot connect to database")
    st.stop()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)

cursor = conn.cursor()

# Total potential savings
cursor.execute("""
    SELECT COALESCE(SUM(estimated_monthly_savings_eur), 0)
    FROM recommendations WHERE status='pending'
""")
potential_monthly = cursor.fetchone()[0]

# Total verified savings
cursor.execute("""
    SELECT COALESCE(SUM(actual_savings_eur), 0)
    FROM savings_realized
""")
verified_savings = cursor.fetchone()[0]

# Total waste detected
cursor.execute("SELECT COUNT(*) FROM waste_detected")
waste_count = cursor.fetchone()[0]

# Success rate
cursor.execute("""
    SELECT
        COUNT(CASE WHEN action_status='success' THEN 1 END)::float /
        NULLIF(COUNT(*), 0) * 100
    FROM actions_log
""")
success_rate = cursor.fetchone()[0] or 0

with col1:
    st.metric(
        "💰 Potential Savings/Month",
        f"€{potential_monthly:,.2f}",
        delta=f"€{potential_monthly * 12:,.0f}/year"
    )

with col2:
    st.metric(
        "✅ Verified Savings",
        f"€{verified_savings:,.2f}",
        delta="Confirmed by AWS"
    )

with col3:
    st.metric(
        "🔍 Waste Detected",
        f"{waste_count}",
        delta="Instances"
    )

with col4:
    st.metric(
        "🎯 Success Rate",
        f"{success_rate:.1f}%",
        delta="Actions executed"
    )

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Waste Detection Over Time")

    query = """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as count,
            SUM(monthly_waste_eur) as total_waste
        FROM waste_detected
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """
    df = pd.read_sql(query, conn)

    if not df.empty:
        fig = px.line(df, x='date', y='total_waste',
                     title="Daily Waste Detected (€/month)",
                     labels={'total_waste': 'Waste (€/month)', 'date': 'Date'})
        fig.update_traces(line_color='#ff6b6b')
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No data available yet")

with col2:
    st.subheader("📊 Recommendations by Type")

    query = """
        SELECT
            recommendation_type,
            COUNT(*) as count
        FROM recommendations
        WHERE status = 'pending'
        GROUP BY recommendation_type
    """
    df = pd.read_sql(query, conn)

    if not df.empty:
        fig = px.pie(df, values='count', names='recommendation_type',
                    title="Recommendation Distribution")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No pending recommendations")

st.markdown("---")

# Recent waste detected
st.subheader("🔍 Latest Waste Detected")

query = """
    SELECT
        resource_id,
        waste_type,
        monthly_waste_eur,
        confidence_score,
        created_at
    FROM waste_detected
    ORDER BY created_at DESC
    LIMIT 10
"""
df = pd.read_sql(query, conn)

if not df.empty:
    st.dataframe(
        df,
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
                max_value=1
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Detected",
                format="DD/MM/YY HH:mm"
            )
        },
        hide_index=True,
        width="stretch"
    )
else:
    st.info("No waste detected yet")

cursor.close()
