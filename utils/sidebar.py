"""
Sidebar utilities for consistent navigation across pages
"""
import streamlit as st
import os


def setup_sidebar():
    """
    Setup consistent sidebar with logo and database connection.

    Best practices:
    - Logo at top of sidebar
    - Consistent branding across all pages
    - Streamlit handles navigation automatically (no manual links needed)
    """
    # Get absolute path to logo
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(current_dir, "static", "images", "logo.svg")

    if os.path.exists(logo_path):
        # Display logo
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        st.sidebar.title("Wasteless")

    st.sidebar.markdown("---")

    # Connection status at bottom of sidebar
    from utils.database import get_db_connection
    conn = get_db_connection()
    if conn:
        st.sidebar.success("✅ Database Connected")
        return conn
    else:
        st.sidebar.error("❌ Database Disconnected")
        return None
