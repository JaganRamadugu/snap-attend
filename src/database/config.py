"""
ATTENDX AI - Supabase Configuration Manager

This module handles connection credentials for the Supabase API. It prioritizes
retrieving configuration secrets from:
1. Streamlit Secrets (for production deployment context)
2. Environment Variables (for standard runtime environments)
3. Local .env file (resolved dynamically for local development convenience)
"""

import streamlit as st
import os
from supabase import create_client, Client

def get_secret(key):
    """
    Retrieves secret config values by polling Streamlit secrets,
    system environment variables, and the local .env file.

    Args:
        key (str): The configuration key name (e.g., 'SUPABASE_URL').

    Returns:
        str | None: The configuration value if located, otherwise None.
    """
    # 1. Try Streamlit secrets first (essential for Streamlit Cloud deployment)
    try:
        return st.secrets[key]
    except Exception:
        pass
    
    # 2. Try system environment variables
    val = os.environ.get(key)
    if val:
        return val
        
    # 3. Try reading from the local .env file
    # Dynamically resolve directory relative to this file to prevent absolute path lockups
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, ".env")
    
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == key:
                            return v.strip()
        except Exception:
            pass
            
    # Fallback to absolute legacy user path for compatibility
    legacy_env_path = "c:/Users/rjaga/OneDrive/Documents/PROJECTS/ATTENDX AI/.env"
    if os.path.exists(legacy_env_path):
        try:
            with open(legacy_env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == key:
                            return v.strip()
        except Exception:
            pass

    return None

# Load API endpoint and authorization keys
supabase_url = get_secret("SUPABASE_URL")
supabase_key = get_secret("SUPABASE_PUBLISHABLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY not found in Streamlit secrets, environment, or .env file. "
        "Please configure your secrets before running the application."
    )

# Initialize global Supabase Client
supabase: Client = create_client(supabase_url, supabase_key)

