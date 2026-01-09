"""
Database connection utility for Wasteless UI
"""
import os
import streamlit as st
import psycopg2


@st.cache_resource
def get_db_connection():
    """Get PostgreSQL database connection."""
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
