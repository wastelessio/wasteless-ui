"""
Sidebar utilities for consistent navigation across pages
"""
import streamlit as st
import os


def setup_sidebar():
    """
    Setup consistent sidebar with database connection.

    Best practices:
    - Clean navigation without logo
    - Streamlit handles navigation automatically (no manual links needed)
    - Database status at bottom
    """
    # Connection status
    from utils.database import get_db_connection
    conn = get_db_connection()
    if conn:
        st.sidebar.success("✅ Database Connected")
        return conn
    else:
        st.sidebar.error("❌ Database Disconnected")
        return None
