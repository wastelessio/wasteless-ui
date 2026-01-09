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
from utils.database import get_db_connection

# Import remediator integration
from utils.remediator import RemediatorProxy, check_backend_available, get_backend_path
from utils.config_manager import ConfigManager

st.title("📋 Cost Optimization Recommendations")
st.markdown("Review and manage idle resource recommendations")

# =============================================================================
# ACTIONABLE ALERTS - Configuration Status with Interactive Toggle
# =============================================================================

# Check current configuration
try:
    config_manager = ConfigManager()
    config = config_manager.load_config()
    auto_enabled = config.get('auto_remediation', {}).get('enabled', False)

    # Show status alert with interactive toggle
    col_status, col_toggle, col_settings = st.columns([3, 1, 1])

    with col_status:
        if not auto_enabled:
            st.success("✅ **AUTO-REMEDIATION IS DISABLED** - Only dry-run mode is active (safe)")
        else:
            st.error("⚠️ **AUTO-REMEDIATION IS ENABLED** - Real AWS actions will be executed!")

    with col_toggle:
        st.markdown("###")  # Spacing
        new_enabled = st.toggle(
            "Enable Auto-Remediation",
            value=auto_enabled,
            key="auto_remediation_toggle_recommendations",
            help="⚠️ When enabled, 'Approve (Execute)' will perform REAL AWS actions"
        )

        # Save if changed
        if new_enabled != auto_enabled:
            with st.spinner("Saving configuration..."):
                if config_manager.set_auto_remediation_enabled(new_enabled):
                    st.success("✅ Saved!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save")

    with col_settings:
        st.markdown("###")  # Spacing
        if st.button("⚙️ All Settings", key="goto_settings_btn", width="stretch"):
            st.switch_page("pages/4_⚙️_Settings.py")

    # Schedule restrictions info and toggle
    schedule = config.get('schedule', {})
    allowed_days = schedule.get('allowed_days', [])
    allowed_hours = schedule.get('allowed_hours', [])
    schedule_enabled = bool(allowed_days) and bool(allowed_hours)

    if schedule_enabled:
        st.info(f"⏰ **Schedule Restrictions Active**: Only {', '.join(allowed_days)} at {', '.join([f'{h}:00' for h in allowed_hours])} ({schedule.get('timezone', 'UTC')})")

        col_schedule_msg, col_schedule_toggle = st.columns([4, 1])

        with col_schedule_msg:
            st.caption("💡 Schedule safeguard prevents execution outside maintenance windows")

        with col_schedule_toggle:
            if st.button("🔓 Disable Schedule", key="disable_schedule_btn", width="stretch", type="secondary"):
                if config_manager.disable_schedule_restrictions():
                    st.success("✅ Schedule restrictions disabled - execution allowed anytime!")
                    st.rerun()
                else:
                    st.error("❌ Failed to disable schedule")
    else:
        st.warning("⚠️ **Schedule Restrictions Disabled** - Execution allowed at any time")

        col_schedule_msg, col_schedule_toggle = st.columns([4, 1])

        with col_schedule_msg:
            st.caption("ℹ️ For production, consider enabling schedule restrictions")

        with col_schedule_toggle:
            if st.button("🔒 Enable Schedule", key="enable_schedule_btn", width="stretch", type="secondary"):
                # Restore default schedule (weekends, 2-5am)
                if config_manager.enable_schedule_restrictions(
                    days=["Saturday", "Sunday"],
                    hours=[2, 3, 4]
                ):
                    st.success("✅ Schedule restored to safe defaults (weekends 2-5am)")
                    st.rerun()
                else:
                    st.error("❌ Failed to enable schedule")

except Exception as e:
    st.warning(f"⚠️ Could not load configuration status: {e}")

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
        (w.metadata->>'cpu_avg_7d')::numeric as cpu_avg
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
        width="stretch"
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

        # Check if backend is available
        backend_available = check_backend_available()
        if not backend_available:
            st.warning(f"""
            ⚠️ **Backend not found at:** `{get_backend_path()}`

            To execute actions, make sure the wasteless backend is cloned:
            ```bash
            cd {os.path.dirname(get_backend_path())}
            git clone https://github.com/wastelessio/wasteless.git
            ```
            """)

        # Special handling for Production mode - show confirmation BEFORE button
        if action_type == "Approve (Execute)":
            st.warning("⚠️ **PRODUCTION MODE** - This will execute REAL AWS actions!")
            st.error("🔒 This will STOP or TERMINATE instances on your AWS account!")

            confirm_production = st.checkbox(
                "✅ I understand this will modify my AWS infrastructure",
                key="confirm_prod_checkbox"
            )
        else:
            confirm_production = True  # Not needed for other actions

        col1, col2, col3 = st.columns(3)

        with col1:
            # Disable button if production mode and not confirmed
            button_disabled = not backend_available or (action_type == "Approve (Execute)" and not confirm_production)

            button_label = "✅ Execute Selected" if action_type != "Approve (Execute)" else "⚡ EXECUTE ON AWS"
            button_type = "primary" if action_type != "Approve (Execute)" else "secondary"

            if st.button(button_label, type=button_type, width="stretch", disabled=button_disabled, key="execute_btn"):
                if action_type == "Reject":
                    # Reject recommendations
                    try:
                        remediator = RemediatorProxy()
                        result = remediator.reject_recommendations(conn, selected_ids)

                        if result['success']:
                            st.success(f"✅ {result['rejected_count']} recommendation(s) rejected!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to reject: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

                elif action_type == "Approve (Dry-Run)":
                    # Execute in dry-run mode
                    st.info("🧪 **DRY-RUN MODE** - No actual AWS actions will be executed")

                    try:
                        with st.spinner("🔄 Executing actions in dry-run mode..."):
                            remediator = RemediatorProxy(dry_run=True)
                            results = remediator.execute_recommendations(conn, selected_ids)

                        # Display results
                        success_count = len([r for r in results if r.get('success', False)])
                        failed_count = len(results) - success_count

                        if success_count > 0:
                            st.success(f"✅ {success_count}/{len(results)} actions completed successfully!")

                        if failed_count > 0:
                            st.warning(f"⚠️ {failed_count}/{len(results)} actions failed")

                        # Detailed results
                        st.markdown("### 📋 Execution Details")
                        for r in results:
                            with st.expander(f"{'✅' if r.get('success') else '❌'} Recommendation #{r['recommendation_id']} - {r.get('instance_id', 'unknown')}"):
                                st.json(r)

                        if success_count > 0:
                            st.balloons()
                            if st.button("🔄 Refresh Page"):
                                st.rerun()

                    except Exception as e:
                        st.error(f"❌ Execution failed: {e}")
                        import traceback
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())

                else:  # Approve (Execute)
                    # Production mode - execute real actions
                    st.info("⚡ **EXECUTING REAL AWS ACTIONS...**")

                    try:
                        with st.spinner("⚡ Executing REAL AWS actions..."):
                            remediator = RemediatorProxy(dry_run=False)
                            results = remediator.execute_recommendations(conn, selected_ids)

                        # Display results
                        success_count = len([r for r in results if r.get('success', False)])
                        failed_count = len(results) - success_count

                        if success_count > 0:
                            st.success(f"✅ {success_count}/{len(results)} REAL actions executed!")

                        if failed_count > 0:
                            st.error(f"❌ {failed_count}/{len(results)} actions failed")

                        # Detailed results
                        st.markdown("### 📋 Execution Results")
                        for r in results:
                            with st.expander(f"{'✅' if r.get('success') else '❌'} {r.get('instance_id', 'unknown')}"):
                                st.json(r)

                        if success_count > 0:
                            st.balloons()
                            st.info("💡 Check the History page for complete audit trail")

                    except Exception as e:
                        st.error(f"❌ Execution failed: {e}")
                        import traceback
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())

        with col2:
            if st.button("📊 View Details", width="stretch"):
                if selected_ids:
                    st.markdown("### 📋 Selected Recommendations Details")
                    for rec_id in selected_ids:
                        rec_data = df[df['id'] == rec_id].iloc[0]
                        with st.expander(f"Recommendation #{rec_id}"):
                            st.write(f"**Instance:** {rec_data['resource_id']}")
                            st.write(f"**Type:** {rec_data['recommendation_type']}")
                            st.write(f"**Instance Type:** {rec_data.get('instance_type', 'N/A')}")

                            # Safely convert to float for formatting
                            cpu_avg = rec_data.get('cpu_avg', 0)
                            cpu_avg = float(cpu_avg) if cpu_avg is not None else 0.0
                            st.write(f"**CPU Avg:** {cpu_avg:.2f}%")

                            savings = float(rec_data['estimated_monthly_savings_eur'])
                            st.write(f"**Savings:** €{savings:.2f}/month")

                            confidence = float(rec_data['confidence_score'])
                            st.write(f"**Confidence:** {confidence:.0%}")

        with col3:
            if st.button("🔄 Refresh Data", width="stretch"):
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
