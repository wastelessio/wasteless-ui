#!/usr/bin/env python3
"""
History Page
============

Complete audit trail of all remediation actions.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="History - Wasteless.io",
    page_icon="📜",
    layout="wide"
)

from utils.database import get_db_connection

st.title("📜 Action History")
st.markdown("Complete audit trail of all remediation actions")
st.markdown("---")

# Get database connection
conn = get_db_connection()
if not conn:
    st.error("❌ Cannot connect to database")
    st.stop()

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox(
        "Status",
        ["All", "success", "failed", "pending", "blocked"]
    )

with col2:
    action_filter = st.selectbox(
        "Action Type",
        ["All", "stop", "start", "terminate"]
    )

with col3:
    days_back = st.number_input(
        "Days Back",
        min_value=1,
        max_value=90,
        value=30
    )

with col4:
    dry_run_filter = st.selectbox(
        "Mode",
        ["All", "Dry-Run Only", "Production Only"]
    )

st.markdown("---")

# Build query
query = """
    SELECT
        a.id,
        a.resource_id,
        a.action_type,
        a.action_status,
        a.dry_run,
        a.action_date,
        a.error_message,
        a.executed_by,
        r.estimated_monthly_savings_eur
    FROM actions_log a
    LEFT JOIN recommendations r ON a.recommendation_id = r.id
    WHERE a.action_date >= NOW() - INTERVAL '%s days'
"""

params = [days_back]

if status_filter != "All":
    query += " AND a.action_status = %s"
    params.append(status_filter)

if action_filter != "All":
    query += " AND a.action_type = %s"
    params.append(action_filter)

if dry_run_filter == "Dry-Run Only":
    query += " AND a.dry_run = TRUE"
elif dry_run_filter == "Production Only":
    query += " AND a.dry_run = FALSE"

query += " ORDER BY a.action_date DESC LIMIT 100"

# Execute query
df = pd.read_sql(query, conn, params=tuple(params))

# Display summary
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Actions", len(df))

with col2:
    success_count = len(df[df['action_status'] == 'success']) if not df.empty else 0
    st.metric("✅ Successful", success_count)

with col3:
    failed_count = len(df[df['action_status'] == 'failed']) if not df.empty else 0
    st.metric("❌ Failed", failed_count)

with col4:
    total_savings = df['estimated_monthly_savings_eur'].sum() if not df.empty else 0
    st.metric("💰 Total Savings", f"€{total_savings:,.2f}/mo")

st.markdown("---")

# Display actions table
if df.empty:
    st.info("📭 No actions found matching your filters")
else:
    st.subheader(f"📋 {len(df)} Actions")

    # Add status emoji
    def status_icon(status):
        icons = {
            'success': '✅',
            'failed': '❌',
            'pending': '⏳',
            'blocked': '🛑'
        }
        return icons.get(status, '❓')

    df['status_display'] = df['action_status'].apply(status_icon)

    st.dataframe(
        df[[
            'id',
            'resource_id',
            'action_type',
            'status_display',
            'dry_run',
            'action_date',
            'estimated_monthly_savings_eur'
        ]],
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "resource_id": st.column_config.TextColumn("Instance", width="medium"),
            "action_type": st.column_config.TextColumn("Action", width="small"),
            "status_display": st.column_config.TextColumn("Status", width="small"),
            "dry_run": st.column_config.CheckboxColumn("Dry-Run", width="small"),
            "action_date": st.column_config.DatetimeColumn(
                "Date",
                format="DD/MM/YY HH:mm",
                width="medium"
            ),
            "estimated_monthly_savings_eur": st.column_config.NumberColumn(
                "💰 Savings",
                format="€%.2f",
                width="small"
            )
        },
        hide_index=True,
        width="stretch"
    )

    # Show errors if any
    errors = df[df['error_message'].notna()]
    if not errors.empty:
        st.markdown("---")
        st.subheader("❌ Actions with Errors")

        for _, row in errors.iterrows():
            with st.expander(f"Action #{row['id']} - {row['resource_id']}"):
                st.error(f"**Error:** {row['error_message']}")
                st.caption(f"Date: {row['action_date']}")

st.markdown("---")

# Rollback section
st.subheader("🔄 Rollback Available")

query = """
    SELECT
        rs.id,
        rs.resource_id,
        rs.created_at,
        rs.rollback_expiry,
        rs.can_rollback,
        a.action_type
    FROM rollback_snapshots rs
    JOIN actions_log a ON rs.action_log_id = a.id
    WHERE rs.can_rollback = TRUE
      AND rs.rollback_expiry > NOW()
    ORDER BY rs.created_at DESC
"""
df_rollback = pd.read_sql(query, conn)

if not df_rollback.empty:
    st.dataframe(
        df_rollback,
        column_config={
            "id": "Snapshot ID",
            "resource_id": "Instance",
            "action_type": "Action",
            "created_at": st.column_config.DatetimeColumn("Created"),
            "rollback_expiry": st.column_config.DatetimeColumn("Expires"),
            "can_rollback": st.column_config.CheckboxColumn("Available")
        },
        hide_index=True,
        width="stretch"
    )

    st.info("💡 Rollback functionality coming soon!")
else:
    st.info("No rollback snapshots available")
