"""
Database connection utility for Wasteless UI
"""
import os
import streamlit as st
import psycopg2
from pathlib import Path
from dotenv import load_dotenv


# Ensure environment variables are loaded
APP_DIR = Path(__file__).parent.parent
ENV_PATH = APP_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)


@st.cache_resource
def get_db_connection():
    """Get PostgreSQL database connection."""
    # Get database credentials
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'wasteless')
    db_user = os.getenv('DB_USER', 'wasteless')
    db_password = os.getenv('DB_PASSWORD')

    # Check if password is set
    if not db_password:
        st.error("❌ DB_PASSWORD environment variable is not set")
        st.info("💡 Please set DB_PASSWORD in your .env file for security")
        return None

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info(f"💡 Connection details: host={db_host}, port={db_port}, database={db_name}, user={db_user}")
        st.info("💡 Make sure PostgreSQL is running and credentials are correct in .env")
        return None
