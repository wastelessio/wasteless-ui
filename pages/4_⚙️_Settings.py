#!/usr/bin/env python3
"""
Settings Page
=============

Manage safeguards and auto-remediation configuration.
"""

import streamlit as st
import yaml
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Settings - Wasteless.io",
    page_icon="⚙️",
    layout="wide"
)

from app import get_db_connection

st.title("⚙️ Settings & Configuration")
st.markdown("Manage auto-remediation policies and safeguards")
st.markdown("---")

# Get database connection
conn = get_db_connection()
if not conn:
    st.error("❌ Cannot connect to database")
    st.stop()

# Note about config file
st.info("""
📝 **Note:** This page shows current configuration.
To modify settings, edit `config/remediation.yaml` in the main wasteless repo.
""")

st.markdown("---")

# Load config from main repo (if accessible)
config_path = "/Users/peco3k/Documents/wasteless/wasteless/config/remediation.yaml"

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Auto-remediation status
    st.subheader("🤖 Auto-Remediation Status")

    auto_enabled = config.get('auto_remediation', {}).get('enabled', False)

    col1, col2 = st.columns(2)

    with col1:
        if auto_enabled:
            st.error("⚠️ **AUTO-REMEDIATION IS ENABLED**")
            st.warning("Real AWS actions will be executed!")
        else:
            st.success("✅ **AUTO-REMEDIATION IS DISABLED**")
            st.info("Only dry-run mode is active (safe)")

    with col2:
        dry_run_days = config.get('auto_remediation', {}).get('dry_run_days', 7)
        st.metric("Mandatory Dry-Run Period", f"{dry_run_days} days")

    st.markdown("---")

    # Safeguards
    st.subheader("🛡️ Safeguard Configuration")

    protection = config.get('protection', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Min Instance Age",
            f"{protection.get('min_instance_age_days', 30)} days",
            help="Instances must be older than this"
        )

    with col2:
        st.metric(
            "Min Idle Days",
            f"{protection.get('min_idle_days', 14)} days",
            help="Instance must be idle for this long"
        )

    with col3:
        st.metric(
            "Min Confidence",
            f"{protection.get('min_confidence_score', 0.8):.0%}",
            help="Detection confidence threshold"
        )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Max Instances Per Run",
            protection.get('max_instances_per_run', 3),
            help="Blast radius control"
        )

    st.markdown("---")

    # Whitelist
    st.subheader("🔒 Protected Resources")

    whitelist = config.get('whitelist', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Protected Instance IDs:**")
        instance_ids = whitelist.get('instance_ids', [])
        if instance_ids:
            for instance_id in instance_ids:
                st.code(instance_id)
        else:
            st.info("No specific instances whitelisted")

    with col2:
        st.markdown("**Protected Tags:**")
        tags = whitelist.get('tags', [])
        if tags:
            for tag in tags:
                st.code(f"{tag.get('key')} = {tag.get('value')}")
        else:
            st.info("No tag-based protection configured")

    st.markdown("---")

    # Schedule
    st.subheader("⏰ Execution Schedule")

    schedule = config.get('schedule', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        allowed_days = schedule.get('allowed_days', [])
        st.markdown("**Allowed Days:**")
        if allowed_days:
            for day in allowed_days:
                st.write(f"• {day}")
        else:
            st.info("No restrictions")

    with col2:
        allowed_hours = schedule.get('allowed_hours', [])
        st.markdown("**Allowed Hours:**")
        if allowed_hours:
            hours_str = ', '.join([f"{h}:00" for h in allowed_hours])
            st.write(hours_str)
        else:
            st.info("No restrictions")

    with col3:
        timezone = schedule.get('timezone', 'UTC')
        st.metric("Timezone", timezone)

    st.markdown("---")

    # Notifications
    st.subheader("📧 Notifications")

    notifications = config.get('notifications', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Email:**")
        email = notifications.get('email', '')
        if email:
            st.code(email)
        else:
            st.info("No email configured")

    with col2:
        st.markdown("**Slack Webhook:**")
        slack = notifications.get('slack_webhook', '')
        if slack:
            st.code("Configured ✅")
        else:
            st.info("Not configured")

    notify_before = notifications.get('notify_before_action', False)
    notify_after = notifications.get('notify_after_action', False)
    notify_error = notifications.get('notify_on_error', False)

    st.checkbox("Notify before action", value=notify_before, disabled=True)
    st.checkbox("Notify after action", value=notify_after, disabled=True)
    st.checkbox("Notify on error", value=notify_error, disabled=True)

else:
    st.warning("""
    ⚠️ Configuration file not found at:
    `/Users/peco3k/Documents/wasteless/wasteless/config/remediation.yaml`

    Make sure the main wasteless repo is cloned and configured.
    """)

st.markdown("---")

# Database stats
st.subheader("💾 Database Statistics")

cursor = conn.cursor()

stats = {}

tables = ['ec2_metrics', 'waste_detected', 'recommendations', 'actions_log', 'savings_realized']

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    stats[table] = cursor.fetchone()[0]

cursor.close()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Metrics", stats['ec2_metrics'])

with col2:
    st.metric("Waste", stats['waste_detected'])

with col3:
    st.metric("Recommendations", stats['recommendations'])

with col4:
    st.metric("Actions", stats['actions_log'])

with col5:
    st.metric("Savings", stats['savings_realized'])

st.markdown("---")

# Help
with st.expander("ℹ️ Help - Modifying Configuration"):
    st.markdown("""
    ### How to Modify Settings

    1. Navigate to the main wasteless repo:
       ```bash
       cd /Users/peco3k/Documents/wasteless/wasteless
       ```

    2. Edit the configuration file:
       ```bash
       nano config/remediation.yaml
       ```

    3. Modify the desired settings

    4. Refresh this page to see changes

    ### Important Notes

    - **enabled: false** is the safe default (dry-run only)
    - Always test with dry-run before enabling production mode
    - Whitelist your production/critical instances
    - Start with conservative safeguards
    - Monitor the first few executions closely
    """)
