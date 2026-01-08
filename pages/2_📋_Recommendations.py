#!/usr/bin/env python3
"""
Recommendations Page
====================

View, filter, and manage cost optimization recommendations.
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add parent directory to path to import app utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Recommendations - Wasteless.io",
    page_icon="📋",
    layout="wide"
)

# Import database connection from main app
from app import get_db_connection

st.title("📋 Cost Optimization Recommendations")
st.markdown("Review and manage idle resource recommendations")
st.markdown("---")

# Get database connection
conn = get_db_connection()
if not conn:
    st.error("❌ Cannot connect to database")
    st.stop()

# Filters
st.subheader("🔍 Filters")
col1, col2, col3 = st.columns(3)

with col1:
    rec_type_filter = st.selectbox(
        "Recommendation Type",
        ["All", "stop_instance", "terminate_instance", "downsize_instance"]
    )

with col2:
    min_savings = st.slider(
        "Min Monthly Savings (€)",
        min_value=0,
        max_value=100,
        value=0,
        step=5
    )

with col3:
    min_confidence = st.slider(
        "Min Confidence Score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )

st.markdown("---")

# Build query
query = """
    SELECT
        r.id,
        r.recommendation_type,
        w.resource_id,
        r.estimated_monthly_savings_eur,
        w.confidence_score,
        r.action_required,
        r.status,
        r.created_at,
        w.metadata->>'instance_type' as instance_type,
        w.metadata->>'cpu_avg_7d' as cpu_avg
    FROM recommendations r
    JOIN waste_detected w ON r.waste_id = w.id
    WHERE r.status = 'pending'
"""

# Apply filters
params = []
if rec_type_filter != "All":
    query += " AND r.recommendation_type = %s"
    params.append(rec_type_filter)

if min_savings > 0:
    query += " AND r.estimated_monthly_savings_eur >= %s"
    params.append(min_savings)

if min_confidence > 0:
    query += " AND w.confidence_score >= %s"
    params.append(min_confidence)

query += " ORDER BY r.estimated_monthly_savings_eur DESC"

# Execute query
df = pd.read_sql(query, conn, params=params if params else None)

# Display summary
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💼 Filtered Recommendations",
        len(df)
    )

with col2:
    total_savings = df['estimated_monthly_savings_eur'].sum() if not df.empty else 0
    st.metric(
        "💰 Total Potential Savings",
        f"€{total_savings:,.2f}/month",
        delta=f"€{total_savings * 12:,.0f}/year"
    )

with col3:
    avg_confidence = df['confidence_score'].mean() if not df.empty else 0
    st.metric(
        "🎯 Average Confidence",
        f"{avg_confidence:.1%}"
    )

st.markdown("---")

# Display recommendations table
if df.empty:
    st.info("📭 No recommendations match your filters")
else:
    st.subheader(f"📊 {len(df)} Recommendations")

    # Format dataframe for display
    df_display = df.copy()
    df_display['cpu_avg'] = pd.to_numeric(df_display['cpu_avg'], errors='coerce')

    st.dataframe(
        df_display[[
            'id',
            'resource_id',
            'recommendation_type',
            'instance_type',
            'cpu_avg',
            'estimated_monthly_savings_eur',
            'confidence_score',
            'created_at'
        ]],
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "resource_id": st.column_config.TextColumn("Instance ID", width="medium"),
            "recommendation_type": st.column_config.TextColumn("Action", width="medium"),
            "instance_type": st.column_config.TextColumn("Type", width="small"),
            "cpu_avg": st.column_config.NumberColumn(
                "Avg CPU %",
                format="%.2f%%",
                width="small"
            ),
            "estimated_monthly_savings_eur": st.column_config.NumberColumn(
                "💰 Savings/mo",
                format="€%.2f",
                width="medium"
            ),
            "confidence_score": st.column_config.ProgressColumn(
                "🎯 Confidence",
                min_value=0,
                max_value=1,
                width="medium"
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Created",
                format="DD/MM/YY",
                width="small"
            )
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # Action section
    st.subheader("🚀 Take Action")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_ids = st.multiselect(
            "Select recommendation IDs to process",
            options=df['id'].tolist(),
            help="You can select multiple recommendations"
        )

    with col2:
        st.markdown("###")  # Spacing
        action_type = st.radio(
            "Action",
            ["Approve (Dry-Run)", "Approve (Execute)", "Reject"],
            help="Dry-run simulates the action without executing"
        )

    if selected_ids:
        st.info(f"📌 {len(selected_ids)} recommendation(s) selected: {selected_ids}")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Execute Selected", type="primary", use_container_width=True):
                if action_type == "Reject":
                    # Reject recommendations
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE recommendations
                        SET status = 'rejected',
                            updated_at = NOW()
                        WHERE id = ANY(%s)
                        """,
                        (selected_ids,)
                    )
                    conn.commit()
                    cursor.close()

                    st.success(f"✅ {len(selected_ids)} recommendation(s) rejected!")
                    st.rerun()

                elif action_type == "Approve (Dry-Run)":
                    st.info("🧪 **DRY-RUN MODE** - No actual AWS actions will be executed")
                    st.warning("⚠️ This would normally call EC2Remediator in dry-run mode")
                    st.code(f"remediator.process_recommendations(ids={selected_ids}, dry_run=True)")

                else:  # Approve (Execute)
                    st.warning("⚠️ **PRODUCTION MODE** - This will execute real AWS actions!")
                    st.error("🔒 Auto-remediation must be enabled in config/remediation.yaml")
                    st.code(f"remediator.process_recommendations(ids={selected_ids}, dry_run=False)")

        with col2:
            if st.button("📊 View Details", use_container_width=True):
                st.info("Detail view coming soon...")

        with col3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

    else:
        st.warning("⚠️ Please select at least one recommendation")

st.markdown("---")

# Help section
with st.expander("ℹ️ Help - Understanding Recommendations"):
    st.markdown("""
    ### Recommendation Types

    - **stop_instance**: Stop the instance (reversible, no data loss)
    - **terminate_instance**: Permanently delete the instance (irreversible)
    - **downsize_instance**: Change to a smaller instance type

    ### Confidence Score

    - **0.9-1.0**: Very high confidence (safe to auto-apply)
    - **0.8-0.9**: High confidence (review recommended)
    - **0.7-0.8**: Medium confidence (manual review required)
    - **<0.7**: Low confidence (investigate before acting)

    ### Safety

    All recommendations are filtered through 7-layer safeguards before execution.
    Protected instances (production, critical tags) are never recommended.
    """)
